"""
Web scraping utilities for fetching and parsing web pages
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Optional, Tuple


class WebScraper:
    """Handles web scraping operations for compliance checking"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def validate_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate if URL is properly formatted

        Args:
            url: URL string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):
                if result.scheme not in ['http', 'https']:
                    return False, "URL must use HTTP or HTTPS protocol"
                return True, ""
            return False, "Invalid URL format"
        except Exception as e:
            return False, f"URL validation error: {str(e)}"

    def fetch_page(self, url: str) -> Dict:
        """
        Fetch a web page and return its content

        Args:
            url: URL to fetch

        Returns:
            Dictionary with status, content, error, and soup object
        """
        is_valid, error = self.validate_url(url)
        if not is_valid:
            return {
                'success': False,
                'error': error,
                'content': None,
                'soup': None,
                'url': url
            }

        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            return {
                'success': True,
                'error': None,
                'content': response.text,
                'soup': soup,
                'url': response.url,
                'status_code': response.status_code
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timed out. Please try again.',
                'content': None,
                'soup': None,
                'url': url
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Failed to connect to the URL. Please check the URL and your internet connection.',
                'content': None,
                'soup': None,
                'url': url
            }
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'error': f'HTTP Error: {e.response.status_code}',
                'content': None,
                'soup': None,
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error fetching page: {str(e)}',
                'content': None,
                'soup': None,
                'url': url
            }

    def extract_text(self, soup: BeautifulSoup) -> str:
        """
        Extract clean text from BeautifulSoup object

        Args:
            soup: BeautifulSoup object

        Returns:
            Cleaned text content
        """
        if not soup:
            return ""

        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    def find_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Find all images in the page

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs

        Returns:
            List of absolute image URLs
        """
        if not soup:
            return []

        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, src)
                images.append(absolute_url)

        return images

    def find_links(self, soup: BeautifulSoup, base_url: str, keywords: List[str] = None) -> Dict[str, str]:
        """
        Find links containing specific keywords

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs
            keywords: List of keywords to search for in link text/href

        Returns:
            Dictionary mapping link text to URL
        """
        if not soup:
            return {}

        if keywords is None:
            keywords = ['privacy', 'policy', 'terms', 'complaint', 'grievance', 'guidelines']

        links = {}
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            text = a.get_text().strip().lower()

            # Check if any keyword is in the link text or href
            for keyword in keywords:
                if keyword.lower() in text or keyword.lower() in href.lower():
                    absolute_url = urljoin(base_url, href)
                    links[a.get_text().strip()] = absolute_url
                    break

        return links

    def search_text_patterns(self, text: str, patterns: List[str]) -> List[Dict]:
        """
        Search for text patterns in content

        Args:
            text: Text to search
            patterns: List of regex patterns or keywords

        Returns:
            List of dictionaries with match information
        """
        matches = []
        text_lower = text.lower()

        for pattern in patterns:
            # Try as regex first, then as simple keyword
            try:
                regex_matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in regex_matches:
                    # Get context (100 chars before and after)
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].strip()

                    matches.append({
                        'pattern': pattern,
                        'match': match.group(),
                        'context': context,
                        'position': match.start()
                    })
            except re.error:
                # If regex fails, treat as simple keyword
                if pattern.lower() in text_lower:
                    index = text_lower.find(pattern.lower())
                    start = max(0, index - 100)
                    end = min(len(text), index + len(pattern) + 100)
                    context = text[start:end].strip()

                    matches.append({
                        'pattern': pattern,
                        'match': text[index:index+len(pattern)],
                        'context': context,
                        'position': index
                    })

        return matches

    def download_image(self, image_url: str, save_path: str) -> bool:
        """
        Download an image from URL

        Args:
            image_url: URL of the image
            save_path: Path to save the image

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(image_url, headers=self.headers, timeout=self.timeout, verify=False, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return False
