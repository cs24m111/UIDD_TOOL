"""
Image analysis utilities for AI label detection
"""
import os
from typing import Dict, Optional, Tuple
from PIL import Image, ExifTags
import cv2
import numpy as np


class ImageAnalyzer:
    """Analyzes images for AI-generated content labels and watermarks"""

    def __init__(self):
        self.ai_keywords = [
            'ai', 'generated', 'synthetic', 'artificial', 'deepfake',
            'created by ai', 'ai-generated', 'made with ai', 'dall-e',
            'midjourney', 'stable diffusion', 'generated image'
        ]

    def analyze_image(self, image_path: str) -> Dict:
        """
        Perform comprehensive analysis of an image

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary with analysis results
        """
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': 'Image file not found',
                'has_label': False,
                'label_coverage': 0,
                'metadata_check': {},
                'ocr_results': [],
                'visual_analysis': {}
            }

        try:
            # Load image
            img = Image.open(image_path)

            # Perform various checks
            metadata_results = self._check_metadata(img)
            visual_results = self._check_visual_labels(image_path)
            ocr_results = self._perform_ocr(image_path)

            # Determine if AI label is present
            has_label = (
                metadata_results.get('has_ai_indicator', False) or
                visual_results.get('has_watermark', False) or
                self._check_ocr_for_ai_labels(ocr_results)
            )

            # Calculate label coverage
            label_coverage = self._calculate_label_coverage(visual_results, ocr_results, img.size)

            return {
                'success': True,
                'error': None,
                'has_label': has_label,
                'label_coverage': label_coverage,
                'metadata_check': metadata_results,
                'ocr_results': ocr_results,
                'visual_analysis': visual_results,
                'image_dimensions': img.size,
                'complies_with_10_percent': label_coverage >= 10.0
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error analyzing image: {str(e)}',
                'has_label': False,
                'label_coverage': 0,
                'metadata_check': {},
                'ocr_results': [],
                'visual_analysis': {}
            }

    def _check_metadata(self, img: Image) -> Dict:
        """
        Check image EXIF/metadata for AI generation indicators

        Args:
            img: PIL Image object

        Returns:
            Dictionary with metadata findings
        """
        metadata_info = {
            'has_exif': False,
            'has_ai_indicator': False,
            'software': None,
            'description': None,
            'ai_related_fields': []
        }

        try:
            # Get EXIF data
            exif_data = img._getexif()

            if exif_data:
                metadata_info['has_exif'] = True

                # Map EXIF tags to readable names
                exif_readable = {}
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_readable[tag] = value

                # Check specific fields
                ai_related_tags = ['Software', 'ImageDescription', 'Artist', 'Copyright', 'UserComment']

                for tag in ai_related_tags:
                    if tag in exif_readable:
                        value_str = str(exif_readable[tag]).lower()
                        metadata_info[tag.lower()] = exif_readable[tag]

                        # Check if value contains AI-related keywords
                        if any(keyword in value_str for keyword in self.ai_keywords):
                            metadata_info['has_ai_indicator'] = True
                            metadata_info['ai_related_fields'].append({
                                'field': tag,
                                'value': exif_readable[tag]
                            })

            # Also check PNG info (for PNG files)
            if hasattr(img, 'info') and img.info:
                for key, value in img.info.items():
                    value_str = str(value).lower()
                    if any(keyword in value_str for keyword in self.ai_keywords):
                        metadata_info['has_ai_indicator'] = True
                        metadata_info['ai_related_fields'].append({
                            'field': key,
                            'value': value
                        })

        except Exception as e:
            metadata_info['error'] = str(e)

        return metadata_info

    def _check_visual_labels(self, image_path: str) -> Dict:
        """
        Check for visual watermarks or labels using computer vision

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with visual analysis results
        """
        visual_info = {
            'has_watermark': False,
            'watermark_regions': [],
            'corner_analysis': {},
            'brightness_anomalies': False
        }

        try:
            # Load image with OpenCV
            img = cv2.imread(image_path)
            if img is None:
                return visual_info

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape

            # Check corners for watermarks (common location)
            corner_size = int(min(height, width) * 0.15)  # 15% of smallest dimension

            corners = {
                'top_left': gray[0:corner_size, 0:corner_size],
                'top_right': gray[0:corner_size, width-corner_size:width],
                'bottom_left': gray[height-corner_size:height, 0:corner_size],
                'bottom_right': gray[height-corner_size:height, width-corner_size:width]
            }

            for corner_name, corner_region in corners.items():
                # Check if corner has significantly different brightness
                corner_mean = np.mean(corner_region)
                overall_mean = np.mean(gray)

                if abs(corner_mean - overall_mean) > 30:  # Threshold for anomaly
                    visual_info['corner_analysis'][corner_name] = {
                        'has_anomaly': True,
                        'brightness_diff': abs(corner_mean - overall_mean)
                    }
                    visual_info['brightness_anomalies'] = True

            # Check for overlay/watermark using edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Look for rectangular regions (potential watermarks)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                total_area = width * height

                # If region is 5-20% of image and has text-like aspect ratio
                if 0.05 <= (area / total_area) <= 0.20 and 0.2 <= (h / w) <= 5:
                    visual_info['has_watermark'] = True
                    visual_info['watermark_regions'].append({
                        'x': x, 'y': y, 'width': w, 'height': h,
                        'coverage_percent': (area / total_area) * 100
                    })

        except Exception as e:
            visual_info['error'] = str(e)

        return visual_info

    def _perform_ocr(self, image_path: str) -> list:
        """
        Perform OCR on image to detect text labels

        Args:
            image_path: Path to image file

        Returns:
            List of detected text strings
        """
        ocr_results = []

        try:
            # Try to import pytesseract
            import pytesseract

            # Perform OCR
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)

            # Split into lines and clean
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            ocr_results = lines

        except ImportError:
            # Pytesseract not available, return empty list
            ocr_results = []
        except Exception as e:
            # OCR failed, return empty
            ocr_results = []

        return ocr_results

    def _check_ocr_for_ai_labels(self, ocr_results: list) -> bool:
        """
        Check if OCR results contain AI-related labels

        Args:
            ocr_results: List of text strings from OCR

        Returns:
            True if AI labels found
        """
        if not ocr_results:
            return False

        combined_text = ' '.join(ocr_results).lower()

        return any(keyword in combined_text for keyword in self.ai_keywords)

    def _calculate_label_coverage(self, visual_results: Dict, ocr_results: list, image_size: Tuple[int, int]) -> float:
        """
        Calculate approximate percentage of image covered by labels

        Args:
            visual_results: Visual analysis results
            ocr_results: OCR results
            image_size: (width, height) tuple

        Returns:
            Approximate coverage percentage
        """
        total_coverage = 0.0
        width, height = image_size
        total_area = width * height

        # Add coverage from detected watermark regions
        if visual_results.get('watermark_regions'):
            for region in visual_results['watermark_regions']:
                region_area = region['width'] * region['height']
                total_coverage += (region_area / total_area) * 100

        # Add coverage estimate from corner anomalies (rough estimate)
        corner_anomalies = sum(1 for corner in visual_results.get('corner_analysis', {}).values()
                             if corner.get('has_anomaly', False))

        if corner_anomalies > 0:
            # Estimate 5% coverage per anomalous corner
            total_coverage += corner_anomalies * 5

        # Add coverage estimate from OCR text (rough estimate)
        if self._check_ocr_for_ai_labels(ocr_results):
            # If AI labels detected in OCR, estimate at least 5% coverage
            total_coverage = max(total_coverage, 5.0)

        # Cap at 100%
        return min(total_coverage, 100.0)

    def generate_report(self, analysis_results: Dict) -> str:
        """
        Generate a human-readable report from analysis results

        Args:
            analysis_results: Results from analyze_image()

        Returns:
            Formatted report string
        """
        if not analysis_results.get('success'):
            return f"Image analysis failed: {analysis_results.get('error', 'Unknown error')}"

        report = []
        report.append("=== AI Label Detection Report ===")
        report.append("")

        # Label presence
        if analysis_results['has_label']:
            report.append("✓ AI label detected")
        else:
            report.append("✗ No AI label detected")

        # Coverage
        coverage = analysis_results['label_coverage']
        report.append(f"Label coverage: {coverage:.2f}%")

        if analysis_results['complies_with_10_percent']:
            report.append("✓ Meets 10% coverage requirement")
        else:
            report.append("✗ Does not meet 10% coverage requirement")

        report.append("")

        # Metadata findings
        metadata = analysis_results['metadata_check']
        if metadata.get('has_ai_indicator'):
            report.append("Metadata Analysis:")
            for field in metadata.get('ai_related_fields', []):
                report.append(f"  - {field['field']}: {field['value']}")
            report.append("")

        # OCR findings
        if self._check_ocr_for_ai_labels(analysis_results['ocr_results']):
            report.append("Text Detection (OCR):")
            report.append("  AI-related text found in image:")
            for text in analysis_results['ocr_results'][:5]:  # Show first 5 lines
                if any(kw in text.lower() for kw in self.ai_keywords):
                    report.append(f"    '{text}'")
            report.append("")

        # Visual findings
        visual = analysis_results['visual_analysis']
        if visual.get('has_watermark'):
            report.append("Visual Analysis:")
            report.append(f"  {len(visual['watermark_regions'])} potential watermark region(s) detected")
            report.append("")

        return "\n".join(report)


def analyze_image_file(image_path: str) -> Dict:
    """
    Convenience function to analyze an image file

    Args:
        image_path: Path to image file

    Returns:
        Analysis results dictionary
    """
    analyzer = ImageAnalyzer()
    return analyzer.analyze_image(image_path)
