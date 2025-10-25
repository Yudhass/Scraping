#!/usr/bin/env python3
"""
SVG Scraper - Khusus untuk mencari dan mendownload semua file SVG
Scan semua halaman HTML dan extract semua referensi SVG
"""

import os
import sys
import time
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup
import logging
import json
import re
from collections import defaultdict

# Try import Selenium
SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    pass

class SVGScraper:
    def __init__(self, base_url, download_dir="svg_download", use_selenium=True):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # SVG specific directories
        self.svg_dir = self.download_dir / "svg_files"
        self.html_dir = self.download_dir / "html_pages"
        self.svg_dir.mkdir(exist_ok=True)
        self.html_dir.mkdir(exist_ok=True)
        
        self.visited_urls = set()
        self.svg_urls = set()
        self.downloaded_svgs = set()
        self.failed_urls = set()
        self.pending_urls = set([base_url])
        
        # SVG detection patterns
        self.svg_patterns = [
            r'\.svg(?:\?[^"\']*)?(?:["\'])',  # .svg files
            r'icon-sprite\.svg',              # Common sprite files
            r'icons?[-_].*?\.svg',            # Icon files
        ]
        
        # Determine scraping method
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.method = "Selenium WebDriver" if self.use_selenium else "Requests + BeautifulSoup"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('svg_scraper.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup browser if available
        if self.use_selenium:
            self.setup_webdriver()
        
        # Setup session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Statistics
        self.stats = {
            'pages_scanned': 0,
            'svg_files_found': 0,
            'svg_files_downloaded': 0,
            'svg_total_size': 0,
            'errors': 0,
            'method_used': self.method
        }
        
        self.logger.info(f"🎨 SVG Scraper initialized")
        self.logger.info(f"🔧 Method: {self.method}")
        self.logger.info(f"📁 SVG Output: {self.svg_dir.absolute()}")
    
    def setup_webdriver(self):
        """Setup Chrome WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("✅ Chrome WebDriver initialized for SVG scraping")
            
        except Exception as e:
            self.logger.warning(f"⚠️ WebDriver setup failed: {e}")
            self.logger.info("🔄 Falling back to requests method")
            self.use_selenium = False
            self.method = "Requests + BeautifulSoup (Fallback)"
            self.stats['method_used'] = self.method
    
    def get_page_content(self, url):
        """Get page content dengan method yang tersedia"""
        if self.use_selenium:
            return self.get_page_with_selenium(url)
        else:
            return self.get_page_with_requests(url)
    
    def get_page_with_selenium(self, url):
        """Get page content dengan Selenium"""
        try:
            self.logger.info(f"🌐 [Selenium] Scanning: {url}")
            self.driver.get(url)
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(1)  # Wait for dynamic content
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            return {
                'url': self.driver.current_url,
                'html': page_source,
                'soup': soup,
                'method': 'selenium'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Selenium error on {url}: {e}")
            return None
    
    def get_page_with_requests(self, url):
        """Get page content dengan requests"""
        try:
            self.logger.info(f"🌐 [Requests] Scanning: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                'url': response.url,
                'html': response.text,
                'soup': soup,
                'method': 'requests'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Requests error on {url}: {e}")
            return None
    
    def extract_svg_references(self, page_data):
        """Extract semua referensi SVG dari halaman"""
        if not page_data:
            return []
        
        soup = page_data['soup']
        base_url = page_data['url']
        svg_refs = set()
        
        self.logger.info(f"🔍 Extracting SVG references from {base_url}")
        
        # 1. SVG tags dengan src/href
        selectors = [
            'img[src*=".svg"]',           # <img src="file.svg">
            'image[href*=".svg"]',        # <image href="file.svg"> (SVG internal)
            'image[xlink:href*=".svg"]',  # <image xlink:href="file.svg">
            'use[href*=".svg"]',          # <use href="sprite.svg#icon">
            'use[xlink:href*=".svg"]',    # <use xlink:href="sprite.svg#icon">
            'link[href*=".svg"]',         # <link rel="icon" href="favicon.svg">
            'object[data*=".svg"]',       # <object data="file.svg">
            'embed[src*=".svg"]',         # <embed src="file.svg">
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                for attr in ['src', 'href', 'xlink:href', 'data']:
                    svg_url = element.get(attr)
                    if svg_url and '.svg' in svg_url:
                        # Clean URL (remove fragment identifiers)
                        clean_url = svg_url.split('#')[0]
                        absolute_url = urljoin(base_url, clean_url)
                        svg_refs.add(absolute_url)
        
        # 2. CSS background-image dengan SVG
        style_elements = soup.find_all(['style', '[style]'])
        for element in style_elements:
            style_content = ''
            if element.name == 'style':
                style_content = element.get_text()
            else:
                style_content = element.get('style', '')
            
            # Find SVG URLs in CSS
            svg_matches = re.findall(r'url\(["\']?([^"\']*\.svg[^"\']*)["\']?\)', style_content)
            for match in svg_matches:
                clean_url = match.split('#')[0]
                absolute_url = urljoin(base_url, clean_url)
                svg_refs.add(absolute_url)
        
        # 3. JavaScript strings containing SVG URLs
        script_elements = soup.find_all('script')
        for script in script_elements:
            script_content = script.get_text()
            svg_matches = re.findall(r'["\']([^"\']*\.svg[^"\']*)["\']', script_content)
            for match in svg_matches:
                if '/' in match:  # Likely a URL path
                    clean_url = match.split('#')[0]
                    absolute_url = urljoin(base_url, clean_url)
                    svg_refs.add(absolute_url)
        
        # 4. Data attributes
        elements_with_data = soup.find_all(attrs={"data-icon": True, "data-svg": True, "data-src": True})
        for element in elements_with_data:
            for attr, value in element.attrs.items():
                if isinstance(value, str) and '.svg' in value:
                    clean_url = value.split('#')[0]
                    absolute_url = urljoin(base_url, clean_url)
                    svg_refs.add(absolute_url)
        
        # 5. Look for common SVG sprite patterns in any text
        page_text = str(soup)
        for pattern in self.svg_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                # Extract just the .svg part
                svg_part = re.search(r'[^"\'\s]*\.svg[^"\'\s]*', match)
                if svg_part:
                    clean_url = svg_part.group().replace('"', '').replace("'", '').split('#')[0]
                    absolute_url = urljoin(base_url, clean_url)
                    svg_refs.add(absolute_url)
        
        # Filter only same-domain SVGs
        same_domain_svgs = []
        for svg_url in svg_refs:
            if urlparse(svg_url).netloc == self.domain:
                same_domain_svgs.append(svg_url)
                self.svg_urls.add(svg_url)
        
        self.logger.info(f"🎨 Found {len(same_domain_svgs)} SVG references on this page")
        self.stats['svg_files_found'] += len(same_domain_svgs)
        
        return same_domain_svgs
    
    def download_svg(self, svg_url):
        """Download single SVG file"""
        if svg_url in self.downloaded_svgs:
            return True
        
        try:
            self.logger.info(f"📥 Downloading SVG: {svg_url}")
            
            response = self.session.get(svg_url, timeout=15)
            response.raise_for_status()
            
            # Determine filename
            url_path = urlparse(svg_url).path
            if url_path:
                filename = Path(url_path).name
                if not filename.endswith('.svg'):
                    filename += '.svg'
            else:
                filename = f"svg_{len(self.downloaded_svgs)}.svg"
            
            # Save SVG
            svg_file_path = self.svg_dir / filename
            
            # Handle duplicate names
            counter = 1
            original_name = svg_file_path.stem
            while svg_file_path.exists():
                svg_file_path = self.svg_dir / f"{original_name}_{counter}.svg"
                counter += 1
            
            with open(svg_file_path, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            self.stats['svg_total_size'] += file_size
            self.stats['svg_files_downloaded'] += 1
            self.downloaded_svgs.add(svg_url)
            
            self.logger.info(f"✅ Saved SVG: {svg_file_path} ({file_size:,} bytes)")
            
            # Save metadata
            svg_info = {
                'original_url': svg_url,
                'filename': filename,
                'size_bytes': file_size,
                'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'content_type': response.headers.get('content-type', '')
            }
            
            metadata_file = svg_file_path.with_suffix('.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(svg_info, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to download SVG {svg_url}: {e}")
            self.stats['errors'] += 1
            return False
    
    def extract_page_links(self, page_data):
        """Extract links untuk crawling lebih lanjut"""
        if not page_data:
            return []
        
        soup = page_data['soup']
        base_url = page_data['url']
        links = []
        
        # Find all HTML page links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            absolute_url = urljoin(base_url, href)
            
            # Check if same domain and likely HTML
            if (urlparse(absolute_url).netloc == self.domain and
                (absolute_url.endswith('.html') or 
                 not '.' in Path(urlparse(absolute_url).path).name or
                 absolute_url.endswith('/'))):
                links.append(absolute_url)
        
        return list(set(links))  # Remove duplicates
    
    def save_page_for_reference(self, page_data):
        """Save HTML page for reference"""
        if not page_data:
            return
        
        try:
            url_path = urlparse(page_data['url']).path
            if not url_path or url_path == '/':
                filename = 'index.html'
            else:
                clean_path = url_path.strip('/').replace('/', '_')
                clean_path = ''.join(c for c in clean_path if c.isalnum() or c in '._-')
                filename = f"{clean_path}.html" if clean_path else f"page_{len(self.visited_urls)}.html"
            
            html_file = self.html_dir / filename
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(page_data['html'])
            
            self.logger.info(f"📄 Saved page reference: {html_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving page {page_data['url']}: {e}")
    
    def scan_for_svgs(self, max_pages=30, delay=1):
        """Main SVG scanning function"""
        self.logger.info(f"🎨 Starting SVG scanning of {self.base_url}")
        self.logger.info(f"🎯 Target: Find and download ALL .svg files")
        
        pages_scanned = 0
        
        try:
            while self.pending_urls and pages_scanned < max_pages:
                url = self.pending_urls.pop()
                
                if url in self.visited_urls:
                    continue
                
                # Get page content
                page_data = self.get_page_content(url)
                
                if page_data:
                    self.visited_urls.add(url)
                    self.stats['pages_scanned'] += 1
                    pages_scanned += 1
                    
                    # Save page for reference
                    self.save_page_for_reference(page_data)
                    
                    # Extract SVG references
                    svg_refs = self.extract_svg_references(page_data)
                    
                    # Download all found SVGs
                    for svg_url in svg_refs:
                        self.download_svg(svg_url)
                    
                    # Extract more page links
                    new_links = self.extract_page_links(page_data)
                    for link in new_links:
                        if link not in self.visited_urls:
                            self.pending_urls.add(link)
                    
                    # Progress report
                    if pages_scanned % 3 == 0:
                        self.print_progress()
                
                else:
                    self.failed_urls.add(url)
                    self.stats['errors'] += 1
                
                time.sleep(delay)
                
        except KeyboardInterrupt:
            self.logger.info("⏹️ SVG scanning interrupted by user")
        
        finally:
            self.cleanup()
    
    def print_progress(self):
        """Print progress"""
        self.logger.info(f"📊 Progress: {self.stats['pages_scanned']} pages scanned, "
                        f"{self.stats['svg_files_found']} SVGs found, "
                        f"{self.stats['svg_files_downloaded']} SVGs downloaded")
    
    def cleanup(self):
        """Cleanup and generate reports"""
        if hasattr(self, 'driver'):
            self.driver.quit()
        
        self.save_svg_report()
        self.print_final_summary()
    
    def save_svg_report(self):
        """Save detailed SVG report"""
        report = {
            'scan_completed': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url,
            'method_used': self.method,
            'statistics': self.stats,
            'pages_scanned': list(self.visited_urls),
            'svg_urls_found': list(self.svg_urls),
            'downloaded_svgs': list(self.downloaded_svgs),
            'failed_urls': list(self.failed_urls),
            'svg_files_info': {
                'total_count': len(self.downloaded_svgs),
                'total_size_bytes': self.stats['svg_total_size'],
                'total_size_mb': round(self.stats['svg_total_size'] / (1024*1024), 2),
                'download_location': str(self.svg_dir.absolute())
            }
        }
        
        report_file = self.download_dir / 'svg_scraping_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📋 SVG Report saved: {report_file}")
        
        # Also create a simple SVG list
        svg_list_file = self.download_dir / 'svg_files_list.txt'
        with open(svg_list_file, 'w', encoding='utf-8') as f:
            f.write(f"SVG Files Downloaded from {self.base_url}\n")
            f.write(f"Scan completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total SVG files: {len(self.downloaded_svgs)}\n\n")
            
            for svg_url in sorted(self.downloaded_svgs):
                f.write(f"{svg_url}\n")
        
        self.logger.info(f"📝 SVG List saved: {svg_list_file}")
    
    def print_final_summary(self):
        """Print final summary"""
        self.logger.info("\n" + "="*70)
        self.logger.info("🎨 SVG SCRAPING COMPLETED!")
        self.logger.info("="*70)
        self.logger.info(f"🔧 Method: {self.method}")
        self.logger.info(f"📄 Pages Scanned: {self.stats['pages_scanned']}")
        self.logger.info(f"🎨 SVG Files Found: {self.stats['svg_files_found']}")
        self.logger.info(f"📥 SVG Files Downloaded: {self.stats['svg_files_downloaded']}")
        self.logger.info(f"💾 Total SVG Size: {self.stats['svg_total_size']:,} bytes ({self.stats['svg_total_size']/(1024*1024):.2f} MB)")
        self.logger.info(f"❌ Errors: {self.stats['errors']}")
        self.logger.info(f"📁 SVG Files Location: {self.svg_dir.absolute()}")
        self.logger.info(f"📄 HTML References: {self.html_dir.absolute()}")
        self.logger.info("="*70)
        
        if self.downloaded_svgs:
            self.logger.info("🎯 SUCCESS: SVG files downloaded and ready to use!")
        else:
            self.logger.info("⚠️  No SVG files found. Check the target website.")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='🎨 SVG Scraper - Find and download all SVG files')
    parser.add_argument('--url', '-u',
                       default='https://admin.pixelstrap.net/mofi/template/',
                       help='Target URL to scan for SVGs')
    parser.add_argument('--output', '-o',
                       default='svg_download',
                       help='Output directory')
    parser.add_argument('--max-pages', '-m',
                       type=int, default=25,
                       help='Maximum pages to scan')
    parser.add_argument('--delay', '-d',
                       type=float, default=1.0,
                       help='Delay between requests')
    parser.add_argument('--no-selenium',
                       action='store_true',
                       help='Force use requests only')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🎨 SVG SCRAPER")
    print("="*70)
    print(f"Target: {args.url}")
    print(f"Output: {args.output}")
    print(f"Max Pages: {args.max_pages}")
    print(f"Delay: {args.delay}s")
    print(f"Selenium Available: {SELENIUM_AVAILABLE}")
    print("="*70)
    
    try:
        scraper = SVGScraper(
            base_url=args.url,
            download_dir=args.output,
            use_selenium=not args.no_selenium
        )
        
        scraper.scan_for_svgs(
            max_pages=args.max_pages,
            delay=args.delay
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
