# Quick Start Guide

Get the IT Rules 2021 Compliance Checker running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Internet connection
- Web browser

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd C:\Upendra\IITT\KP_Final
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

### 5. Open in Browser

Navigate to: `http://localhost:5000`

## First Compliance Check

1. Enter a platform name (e.g., "Facebook")
2. Enter privacy policy URL (e.g., `https://www.facebook.com/privacy/policy`)
3. Enter homepage URL (e.g., `https://www.facebook.com`)
4. Click "Check Compliance"
5. Review the detailed report

## Example URLs to Test

### Facebook
- Privacy Policy: `https://www.facebook.com/privacy/policy`
- Homepage: `https://www.facebook.com`

### Twitter/X
- Privacy Policy: `https://twitter.com/en/privacy`
- Homepage: `https://twitter.com`

### Instagram
- Privacy Policy: `https://help.instagram.com/519522125107875`
- Homepage: `https://www.instagram.com`

## Optional: Enhanced OCR

For better image text detection, install Tesseract:

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH

**Linux (Ubuntu):**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

## API Usage (Optional)

Test the API endpoint using curl:

```bash
curl -X POST http://localhost:5000/api/check-compliance \
  -H "Content-Type: application/json" \
  -d '{
    "privacy_policy_url": "https://www.facebook.com/privacy/policy",
    "homepage_url": "https://www.facebook.com",
    "platform_name": "Facebook"
  }'
```

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
python app.py --port 5001
```

Or modify `app.py` line 168:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Module Not Found
```bash
# Ensure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

### SSL Certificate Error
This is normal for some sites. The app handles it automatically.

## Next Steps

- Read full documentation in `README.md`
- Customize scoring in `utils/analyzer.py`
- Enhance image detection in `utils/image_checker.py`
- Add more rules as regulations evolve

## Need Help?

Check the main `README.md` file for:
- Detailed documentation
- Architecture overview
- Scoring algorithms
- Troubleshooting guide
- API reference

---

Happy compliance checking!
