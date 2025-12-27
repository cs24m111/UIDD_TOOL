"""
Sample script to test the IT Rules 2021 Compliance Checker API

Usage:
    python test_api.py
"""

import requests
import json
from typing import Dict


def check_platform_compliance(
    privacy_policy_url: str,
    homepage_url: str,
    platform_name: str = "Test Platform",
    api_url: str = "http://localhost:5000/api/check-compliance"
) -> Dict:
    """
    Check platform compliance using the API

    Args:
        privacy_policy_url: URL to privacy policy
        homepage_url: URL to homepage
        platform_name: Name of the platform
        api_url: API endpoint URL

    Returns:
        Dictionary with compliance results
    """
    payload = {
        "privacy_policy_url": privacy_policy_url,
        "homepage_url": homepage_url,
        "platform_name": platform_name
    }

    try:
        print(f"Checking compliance for: {platform_name}")
        print(f"Privacy Policy: {privacy_policy_url}")
        print(f"Homepage: {homepage_url}")
        print("-" * 60)

        response = requests.post(api_url, json=payload, timeout=120)
        response.raise_for_status()

        results = response.json()

        if results.get('success'):
            print_results(results)
            return results
        else:
            print(f"Error: {results.get('error', 'Unknown error')}")
            return results

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return {"success": False, "error": str(e)}


def print_results(results: Dict):
    """Pretty print compliance results"""

    print(f"\n✓ Analysis completed successfully!\n")
    print(f"Platform: {results['platform_name']}")
    print(f"Overall Score: {results['overall_score']:.2f}%")
    print(f"Status: {results['overall_status']}")
    print(f"Summary: {results['summary']}")
    print("\n" + "=" * 60)
    print("INDIVIDUAL RULE SCORES")
    print("=" * 60)

    for rule_key, rule_data in results['rules'].items():
        status_icon = {
            'Pass': '✓',
            'Partial': '⚠',
            'Fail': '✗'
        }.get(rule_data['status'], '?')

        print(f"\n{status_icon} {rule_data['rule']} - {rule_data['status']}")
        print(f"   Score: {rule_data['score']:.0f}%")
        print(f"   Description: {rule_data['description']}")

        if rule_data.get('findings'):
            print("   Findings:")
            for finding in rule_data['findings'][:3]:  # Show first 3
                print(f"     • {finding}")

    print("\n" + "=" * 60)

    # Image analysis
    if results.get('image_analysis') and results['image_analysis'].get('success'):
        img = results['image_analysis']
        print("\nIMAGE ANALYSIS")
        print("=" * 60)
        print(f"AI Label Detected: {'Yes' if img['has_label'] else 'No'}")
        print(f"Label Coverage: {img['label_coverage']:.2f}%")
        print(f"Meets 10% Requirement: {'Yes' if img['complies_with_10_percent'] else 'No'}")

    print("\n" + "=" * 60)


def main():
    """Main function to run tests"""

    # Example 1: Test with Facebook
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Facebook Compliance Check")
    print("=" * 60)

    facebook_results = check_platform_compliance(
        privacy_policy_url="https://www.facebook.com/privacy/policy",
        homepage_url="https://www.facebook.com",
        platform_name="Facebook"
    )

    # Save results to file
    if facebook_results.get('success'):
        with open('facebook_compliance_report.json', 'w') as f:
            json.dump(facebook_results, f, indent=2)
        print("\n✓ Results saved to: facebook_compliance_report.json")

    # Example 2: Test with another platform (commented out)
    # print("\n\n" + "=" * 60)
    # print("EXAMPLE 2: Twitter Compliance Check")
    # print("=" * 60)
    #
    # twitter_results = check_platform_compliance(
    #     privacy_policy_url="https://twitter.com/en/privacy",
    #     homepage_url="https://twitter.com",
    #     platform_name="Twitter/X"
    # )


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     IT Rules 2021 Compliance Checker - API Test Script      ║
    ║                                                              ║
    ║  This script demonstrates how to use the compliance API     ║
    ║  programmatically to check platform compliance.             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Check if server is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✓ Server is running\n")
    except requests.exceptions.RequestException:
        print("✗ Error: Flask server is not running!")
        print("Please start the server first:")
        print("  python app.py")
        print("\nThen run this script again.\n")
        exit(1)

    main()

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60 + "\n")
