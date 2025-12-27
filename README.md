# IT Rules 2021 Compliance Checker

A comprehensive Flask web application for analyzing social media platform compliance with Indian IT Rules 2021 amendments related to synthetically generated information (AI-generated content).

## Overview

This tool automatically checks social media platforms against 6 key IT Rules 2021 amendments that govern AI-generated content, deepfakes, and synthetic media. It analyzes both privacy policies and actual platform content to provide a detailed compliance report.

## Features

- **Automated Compliance Checking**: Analyzes privacy policies and terms of service against 6 specific IT Rules
- **AI Label Detection**: Scans homepage images for AI-generated content labels and watermarks
- **Detailed Scoring**: Provides overall compliance score (0-100%) with rule-by-rule breakdown
- **Evidence Extraction**: Quotes relevant policy sections that indicate compliance or non-compliance
- **Image Analysis**: Uses OCR, metadata checking, and computer vision to detect AI labels
- **Professional Reports**: Generates comprehensive, printable compliance reports
- **RESTful API**: JSON API endpoint for programmatic access

## IT Rules 2021 Amendments Covered

### 1. Rule 2(1)(wa) - Definition of Synthetically Generated Information
Checks if the platform clearly defines "synthetically generated information" as:
> "Information that is artificially or algorithmically created, generated, modified or altered using a computer resource, in a manner that appears reasonably authentic or true"

### 2. Rule 4(2) - Automated Detection Tools
Verifies deployment of automated tools to detect harmful synthetic content.

### 3. Rule 4(4) - Complaint Handling Mechanism
Ensures complaints about AI-generated content are handled with same priority as other content.

### 4. Rule 3(1)(b) Proviso - Prohibition of Harmful AI Content
Checks that harmful AI-generated content (deepfakes, misleading info) is explicitly prohibited while maintaining Section 79 immunity.

### 5. Rule 3(3) - Due Diligence for Synthetic Content Labeling
Verifies four requirements:
- Platform requires AI content to be labeled with metadata/identifier
- Label must cover 10% surface area (images) or 10% duration (audio)
- Label enables immediate identification
- Platform prohibits label modification/removal

### 6. Rule 4(1A) - SSMI Requirements (50 Lakh+ Users)
For Significant Social Media Intermediaries:
- Obtains user declaration on synthetic vs authentic content
- Deploys technical verification measures
- Ensures synthetic content labeling

## Project Structure

```
KP_Final/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── utils/
│   ├── __init__.py            # Package initialization
│   ├── scraper.py             # Web scraping utilities
│   ├── analyzer.py            # Compliance analysis logic
│   └── image_checker.py       # Image analysis & AI label detection
├── templates/
│   ├── index.html             # Main input form
│   └── results.html           # Compliance report display
└── static/
    └── css/
        └── style.css          # Custom styling
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR (optional, for enhanced image text detection)

### Step 1: Clone or Download

```bash
cd KP_Final
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Tesseract OCR (Optional)

For enhanced image text detection:

**Windows:**
1. Download installer from https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

## Usage

### Running the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Web Interface

1. Open browser to `http://localhost:5000`
2. Enter platform information:
   - **Platform Name** (optional): e.g., "Facebook", "Twitter"
   - **Privacy Policy URL** (required): Full URL to privacy/terms page
   - **Homepage URL** (required): Platform homepage URL
3. Click "Check Compliance"
4. Review detailed compliance report
5. Print or save report as needed

### API Usage

**Endpoint:** `POST /api/check-compliance`

**Request:**
```json
{
  "privacy_policy_url": "https://example.com/privacy",
  "homepage_url": "https://example.com",
  "platform_name": "Example Platform"
}
```

**Response:**
```json
{
  "success": true,
  "platform_name": "Example Platform",
  "timestamp": "2025-12-24T10:30:00",
  "overall_score": 75.5,
  "overall_status": "Compliant",
  "summary": "Overall Compliance Score: 75.50% | Passed: 4/6 | Partial: 1/6 | Failed: 1/6",
  "rules": {
    "rule_2_1_wa": {
      "rule": "Rule 2(1)(wa)",
      "description": "Definition of Synthetically Generated Information",
      "score": 85,
      "status": "Pass",
      "findings": [...],
      "evidence": [...],
      "recommendation": "..."
    },
    ...
  },
  "image_analysis": {
    "success": true,
    "has_label": true,
    "label_coverage": 12.5,
    "complies_with_10_percent": true,
    ...
  }
}
```

## Compliance Scoring Algorithm

### Overall Score Calculation
- Each rule contributes equally: 100% / 6 rules = 16.67% per rule
- Overall score is the average of all 6 rule scores
- **Compliant**: 70%+ overall
- **Partially Compliant**: 40-70% overall
- **Non-Compliant**: <40% overall

### Individual Rule Scoring

**Rule 2(1)(wa) - Definition (100 points)**
- 20 points: Keyword matching (synthetic, AI, algorithmic, etc.)
- 80 points: Definition similarity to official text (fuzzy matching)

**Rule 4(2) - Automated Tools (100 points)**
- 60 points: Pattern matching for automation mentions
- 40 points: Keyword presence

**Rule 4(4) - Complaint Mechanism (100 points)**
- 40 points: Complaint mechanism exists
- 60 points: AI content mentioned in complaint context

**Rule 3(1)(b) - Prohibited Content (100 points)**
- 30 points: Prohibited content section exists
- 35 points: Deepfakes mentioned
- 20 points: Misleading AI content mentioned
- 15 points: Section 79 mentioned

**Rule 3(3) - Labeling Requirements (100 points)**
- 25 points each for 4 sub-requirements:
  - Labeling/metadata requirement
  - 10% surface area/duration
  - Immediate identification
  - Prohibition of modification/removal

**Rule 4(1A) - SSMI Requirements (100 points)**
- 33.33 points each for 3 sub-requirements:
  - User declaration
  - Technical verification
  - Synthetic labeling

## Image Analysis

The tool performs comprehensive image analysis:

### 1. Metadata Checking
- Extracts EXIF data
- Checks for AI-related fields (Software, Artist, Description)
- Scans PNG info chunks

### 2. Visual Analysis
- Detects watermarks using edge detection
- Analyzes corner regions for labels
- Identifies brightness anomalies

### 3. OCR Text Detection
- Extracts text from images using Tesseract
- Searches for AI-related keywords
- Estimates label coverage area

### 4. Compliance Verification
- Calculates approximate label coverage percentage
- Checks if coverage meets 10% requirement
- Provides detailed technical findings

## Technical Details

### Technologies Used

**Backend:**
- Flask 3.0 - Web framework
- BeautifulSoup4 - HTML parsing
- requests - HTTP client
- Pillow - Image processing
- OpenCV - Computer vision
- pytesseract - OCR

**Frontend:**
- Bootstrap 5 - Responsive UI
- Font Awesome - Icons
- Jinja2 - Templating

### Key Components

**WebScraper (`utils/scraper.py`)**
- URL validation and fetching
- HTML parsing and text extraction
- Image discovery and downloading
- Pattern matching

**ComplianceAnalyzer (`utils/analyzer.py`)**
- Rule-specific checking functions
- Keyword and pattern matching
- Fuzzy text similarity
- Evidence extraction
- Scoring algorithms

**ImageAnalyzer (`utils/image_checker.py`)**
- Metadata extraction
- Visual watermark detection
- OCR processing
- Coverage calculation

## Configuration

### Environment Variables

Create a `.env` file (optional):

```
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

### Tesseract Configuration

If Tesseract is not in PATH, configure in `utils/image_checker.py`:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Error Handling

The application handles:
- Invalid or malformed URLs
- Network timeouts and connection errors
- HTTP errors (404, 403, 500, etc.)
- Missing images
- OCR failures (graceful degradation)
- Malformed HTML structures

## Limitations

1. **Automated Analysis**: This tool provides automated analysis which may not catch nuanced legal language
2. **Not Legal Advice**: Results are informational only and don't constitute legal advice
3. **OCR Accuracy**: Text detection depends on image quality and Tesseract installation
4. **Dynamic Content**: May not analyze JavaScript-loaded content
5. **Language**: Currently optimized for English text

## Best Practices

1. **Test Multiple Pages**: Check both privacy policy and terms of service
2. **Review Evidence**: Always review extracted evidence quotes
3. **Manual Verification**: Use results as guidance, verify manually
4. **Regular Checks**: Policies change, re-check periodically
5. **Legal Counsel**: Consult lawyers for official compliance

## Troubleshooting

### Issue: "Failed to fetch URL"
- Check internet connection
- Verify URL is accessible
- Check if site blocks automated requests

### Issue: "No images found"
- Homepage may not have images
- Images may be loaded via JavaScript
- Check different page with visible images

### Issue: OCR not working
- Install Tesseract OCR
- Configure Tesseract path in code
- Check image quality

### Issue: Low compliance scores
- Verify correct policy URL
- Check if policy uses different terminology
- Review evidence for false negatives

## Contributing

Contributions welcome! Areas for improvement:
- Support for more languages
- Enhanced AI detection algorithms
- PDF report generation
- Batch processing
- Historical tracking

## Legal Disclaimer

This tool is provided for **educational and informational purposes only**. It does not constitute legal advice or create an attorney-client relationship. Compliance with IT Rules 2021 requires professional legal review. The developers assume no liability for actions taken based on this tool's output.

## License

This project is provided as-is for educational purposes. Ensure compliance with all applicable laws when using this tool.

## References

- [Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021](https://www.meity.gov.in/writereaddata/files/Information%20Technology%20%28Intermediary%20Guidelines%20and%20Digital%20Media%20Ethics%20Code%29%20Rules%2C%202021%20%281%29_0.pdf)
- [2023 Amendments on Synthetic Content](https://www.meity.gov.in/)

## Support

For issues or questions:
1. Check troubleshooting section
2. Review error messages carefully
3. Verify all dependencies are installed
4. Check Python version compatibility

---

**Built for compliance monitoring and educational purposes**

Version: 1.0.0
Last Updated: December 2024
