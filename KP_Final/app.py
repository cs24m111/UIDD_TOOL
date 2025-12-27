"""
Flask application for Indian IT Rules 2021 Compliance Checker
"""
from flask import Flask, render_template, request, jsonify, session
import os
import tempfile
import uuid
from datetime import datetime
from utils import ImageAnalyzer, ComplianceAnalyzer, WebScraper
import urllib3

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure upload folder for temporary image storage
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    """Render the main form page"""
    return render_template('index.html')


@app.route('/check-compliance', methods=['POST'])
def check_compliance():
    """
    Main endpoint for compliance checking

    Expected form data:
    - privacy_policy_url: URL to privacy policy page
    - homepage_url: URL to homepage
    - platform_name: (optional) Name of the platform
    """
    try:
        # Get form data
        privacy_policy_url = request.form.get('privacy_policy_url', '').strip()
        homepage_url = request.form.get('homepage_url', '').strip()
        platform_name = request.form.get('platform_name', 'Unknown Platform').strip()

        # Validate inputs
        if not privacy_policy_url:
            return render_template('results.html',
                                 error='Privacy Policy URL is required',
                                 platform_name=platform_name)

        if not homepage_url:
            return render_template('results.html',
                                 error='Homepage URL is required',
                                 platform_name=platform_name)

        # Initialize components
        scraper = WebScraper()
        analyzer = ComplianceAnalyzer()
        image_analyzer = ImageAnalyzer()

        # Fetch privacy policy
        privacy_result = scraper.fetch_page(privacy_policy_url)
        if not privacy_result['success']:
            return render_template('results.html',
                                 error=f"Failed to fetch privacy policy: {privacy_result['error']}",
                                 platform_name=platform_name)

        # Extract privacy policy text
        privacy_text = scraper.extract_text(privacy_result['soup'])

        # Fetch homepage
        homepage_result = scraper.fetch_page(homepage_url)
        homepage_images = []
        image_analysis = None

        if homepage_result['success']:
            # Extract images from homepage
            homepage_images = scraper.find_images(homepage_result['soup'], homepage_url)

            # Analyze first image if available
            if homepage_images:
                first_image_url = homepage_images[0]

                # Download image
                image_filename = f"{uuid.uuid4()}.jpg"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

                if scraper.download_image(first_image_url, image_path):
                    # Analyze image
                    image_analysis = image_analyzer.analyze_image(image_path)
                    image_analysis['image_url'] = first_image_url

                    # Clean up
                    try:
                        os.remove(image_path)
                    except:
                        pass

        # Perform compliance analysis
        compliance_results = analyzer.analyze_compliance(privacy_text)

        # Prepare results for template
        results = {
            'platform_name': platform_name,
            'privacy_policy_url': privacy_policy_url,
            'homepage_url': homepage_url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': compliance_results['overall_score'],
            'overall_status': compliance_results['overall_status'],
            'status_color': compliance_results['status_color'],
            'summary': compliance_results['summary'],
            'rules': compliance_results['rules'],
            'image_analysis': image_analysis,
            'total_images_found': len(homepage_images),
            'error': None
        }

        return render_template('results.html', **results)

    except Exception as e:
        return render_template('results.html',
                             error=f"An unexpected error occurred: {str(e)}",
                             platform_name=platform_name if 'platform_name' in locals() else 'Unknown')


@app.route('/api/check-compliance', methods=['POST'])
def api_check_compliance():
    """
    API endpoint for compliance checking (returns JSON)

    Expected JSON data:
    {
        "privacy_policy_url": "https://...",
        "homepage_url": "https://...",
        "platform_name": "Optional Platform Name"
    }
    """
    try:
        data = request.get_json()

        privacy_policy_url = data.get('privacy_policy_url', '').strip()
        homepage_url = data.get('homepage_url', '').strip()
        platform_name = data.get('platform_name', 'Unknown Platform').strip()

        if not privacy_policy_url or not homepage_url:
            return jsonify({
                'success': False,
                'error': 'Both privacy_policy_url and homepage_url are required'
            }), 400

        # Initialize components
        scraper = WebScraper()
        analyzer = ComplianceAnalyzer()
        image_analyzer = ImageAnalyzer()

        # Fetch privacy policy
        privacy_result = scraper.fetch_page(privacy_policy_url)
        if not privacy_result['success']:
            return jsonify({
                'success': False,
                'error': f"Failed to fetch privacy policy: {privacy_result['error']}"
            }), 400

        # Extract privacy policy text
        privacy_text = scraper.extract_text(privacy_result['soup'])

        # Fetch homepage
        homepage_result = scraper.fetch_page(homepage_url)
        image_analysis = None

        if homepage_result['success']:
            homepage_images = scraper.find_images(homepage_result['soup'], homepage_url)

            if homepage_images:
                first_image_url = homepage_images[0]
                image_filename = f"{uuid.uuid4()}.jpg"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

                if scraper.download_image(first_image_url, image_path):
                    image_analysis = image_analyzer.analyze_image(image_path)

                    try:
                        os.remove(image_path)
                    except:
                        pass

        # Perform compliance analysis
        compliance_results = analyzer.analyze_compliance(privacy_text)

        # Prepare response
        response = {
            'success': True,
            'platform_name': platform_name,
            'timestamp': datetime.now().isoformat(),
            'overall_score': compliance_results['overall_score'],
            'overall_status': compliance_results['overall_status'],
            'summary': compliance_results['summary'],
            'rules': compliance_results['rules'],
            'image_analysis': image_analysis
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/about')
def about():
    """About page explaining the IT Rules 2021"""
    return render_template('about.html')


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('index.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('index.html', error='Internal server error'), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)

    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
