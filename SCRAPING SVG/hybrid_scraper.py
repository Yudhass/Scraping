#!/usr/bin/env python3
"""
Hybrid Web Scraper - Bisa pakai Selenium atau fallback ke requests
Otomatis detect dan pilih method terbaik yang tersedia
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

class HybridWebScraper:
    def __init__(self, base_url, download_dir="hybrid_download", use_selenium=True):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        self.visited_urls = set()
        self.downloaded_files = set()
        self.failed_urls = set()
        self.pending_urls = set([base_url])
        
        # Determine scraping method
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.method = "Selenium WebDriver" if self.use_selenium else "Requests + BeautifulSoup"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('hybrid_scraper.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup browser if available
        if self.use_selenium:
            self.setup_webdriver()
        
        # Setup session untuk download file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Statistics
        self.stats = {
            'pages_visited': 0,
            'pages_downloaded': 0,
            'assets_downloaded': 0,
            'links_found': 0,
            'errors': 0,
            'method_used': self.method
        }
        
        self.logger.info(f"🔧 Scraping method: {self.method}")
    
    def setup_webdriver(self):
        """Setup Chrome WebDriver jika tersedia"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.logger.info("✅ Chrome WebDriver initialized")
            
        except Exception as e:
            self.logger.warning(f"⚠️ WebDriver setup failed: {e}")
            self.logger.info("🔄 Falling back to requests method")
            self.use_selenium = False
            self.method = "Requests + BeautifulSoup (Fallback)"
            self.stats['method_used'] = self.method
    
    def get_page_content(self, url):
        """Get page content menggunakan method yang tersedia"""
        if self.use_selenium:
            return self.get_page_with_selenium(url)
        else:
            return self.get_page_with_requests(url)
    
    def get_page_with_selenium(self, url):
        """Get page content dengan Selenium"""
        try:
            self.logger.info(f"🌐 [Selenium] Visiting: {url}")
            self.driver.get(url)
            
            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)  # Additional wait for dynamic content
            
            page_source = self.driver.page_source
            page_title = self.driver.title
            current_url = self.driver.current_url
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            return {
                'url': current_url,
                'title': page_title,
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
            self.logger.info(f"🌐 [Requests] Fetching: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                'url': response.url,
                'title': soup.title.string if soup.title else 'No Title',
                'html': response.text,
                'soup': soup,
                'method': 'requests'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Requests error on {url}: {e}")
            return None
    
    def extract_all_links(self, page_data):
        """Extract semua link dari halaman"""
        if not page_data:
            return []
        
        soup = page_data['soup']
        base_url = page_data['url']
        links = []
        
        # Find all links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            absolute_url = urljoin(base_url, href)
            
            # Check if same domain
            if urlparse(absolute_url).netloc == self.domain:
                links.append({
                    'url': absolute_url,
                    'text': a_tag.get_text(strip=True)[:100],
                    'source_page': base_url
                })
        
        # Also extract from navigation, menus, etc
        nav_selectors = [
            'nav a[href]',
            '.menu a[href]',
            '.navigation a[href]',
            '.navbar a[href]',
            '.sidebar a[href]'
        ]
        
        for selector in nav_selectors:
            for a_tag in soup.select(selector):
                href = a_tag.get('href', '').strip()
                if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    absolute_url = urljoin(base_url, href)
                    if urlparse(absolute_url).netloc == self.domain:
                        links.append({
                            'url': absolute_url,
                            'text': a_tag.get_text(strip=True)[:100],
                            'source_page': base_url
                        })
        
        # Remove duplicates
        unique_links = []
        seen_urls = set()
        for link in links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        self.stats['links_found'] += len(unique_links)
        self.logger.info(f"🔗 Found {len(unique_links)} unique links")
        
        return unique_links
    
    def save_page_html(self, page_data):
        """Save halaman HTML"""
        if not page_data:
            return False
        
        try:
            url_path = urlparse(page_data['url']).path
            
            # Generate filename
            if not url_path or url_path == '/':
                filename = 'index.html'
            else:
                # Clean path for filename
                clean_path = url_path.strip('/').replace('/', '_')
                # Remove or replace invalid characters
                clean_path = ''.join(c for c in clean_path if c.isalnum() or c in '._-')
                filename = f"{clean_path}.html" if clean_path else f"page_{len(self.visited_urls)}.html"
            
            file_path = self.download_dir / filename
            
            # Save HTML
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(page_data['html'])
            
            self.stats['pages_downloaded'] += 1
            self.logger.info(f"💾 Saved: {file_path}")
            
            # Save metadata
            meta_file = file_path.with_suffix('.json')
            metadata = {
                'original_url': page_data['url'],
                'title': page_data['title'],
                'method': page_data['method'],
                'saved_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error saving {page_data['url']}: {e}")
            return False
    
    def extract_and_download_assets(self, page_data):
        """Extract dan download assets"""
        if not page_data:
            return
        
        soup = page_data['soup']
        base_url = page_data['url']
        
        # Asset selectors with priorities
        assets = []
        
        # CSS files
        for link in soup.find_all('link', rel=lambda x: x and 'stylesheet' in x):
            href = link.get('href')
            if href:
                assets.append(('css', href, 'CSS'))
        
        # JavaScript files  
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                assets.append(('js', src, 'JavaScript'))
        
        # Images
        for img in soup.find_all('img'):
            for attr in ['src', 'data-src', 'data-original']:
                src = img.get(attr)
                if src:
                    assets.append(('img', src, 'Image'))
                    break
        
        # Icons and fonts
        for link in soup.find_all('link', rel=lambda x: x and any(r in x for r in ['icon', 'shortcut'])):
            href = link.get('href')
            if href:
                assets.append(('icon', href, 'Icon'))
        
        # Background images in CSS
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            if 'background-image:' in style or 'background:' in style:
                # Simple extraction - could be enhanced
                import re
                urls = re.findall(r'url\(["\']?([^"\']+)["\']?\)', style)
                for url in urls:
                    assets.append(('bg', url, 'Background'))
        
        self.logger.info(f"📦 Found {len(assets)} assets to download")
        
        # Download assets
        for asset_type, asset_url, description in assets:
            self.download_single_asset(asset_url, base_url, asset_type, description)
    
    def download_single_asset(self, asset_url, base_url, asset_type, description):
        """Download single asset file"""
        try:
            # Skip if already downloaded
            if asset_url in self.downloaded_files:
                return
            
            # Resolve URL
            absolute_url = urljoin(base_url, asset_url)
            
            # Skip external domains
            if urlparse(absolute_url).netloc != self.domain:
                return
            
            # Skip data URLs
            if absolute_url.startswith('data:'):
                return
            
            self.logger.info(f"📥 Downloading {description}: {absolute_url}")
            
            response = self.session.get(absolute_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Determine save path
            url_path = urlparse(absolute_url).path
            if url_path:
                # Preserve directory structure
                save_path = self.download_dir / url_path.lstrip('/')
                save_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                # Generate filename
                ext = self.guess_extension(response.headers.get('content-type', ''), asset_url)
                save_path = self.download_dir / f"assets/asset_{len(self.downloaded_files)}{ext}"
                save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.downloaded_files.add(asset_url)
            self.stats['assets_downloaded'] += 1
            self.logger.info(f"✅ Saved: {save_path}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to download {absolute_url}: {e}")
    
    def guess_extension(self, content_type, url):
        """Guess file extension"""
        # From content type
        type_map = {
            'text/css': '.css',
            'application/javascript': '.js',
            'text/javascript': '.js',
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/gif': '.gif',
            'image/svg+xml': '.svg',
            'font/woff': '.woff',
            'font/woff2': '.woff2',
        }
        
        ct = content_type.split(';')[0].strip()
        if ct in type_map:
            return type_map[ct]
        
        # From URL
        if '.' in url:
            return '.' + url.split('.')[-1].split('?')[0]
        
        return ''
    
    def crawl_website(self, max_pages=30, delay=1):
        """Main crawling function"""
        self.logger.info(f"🚀 Starting hybrid crawling of {self.base_url}")
        self.logger.info(f"🔧 Method: {self.method}")
        self.logger.info(f"📁 Output: {self.download_dir.absolute()}")
        
        pages_processed = 0
        
        try:
            while self.pending_urls and pages_processed < max_pages:
                # Get next URL
                url = self.pending_urls.pop()
                
                if url in self.visited_urls:
                    continue
                
                # Visit page
                page_data = self.get_page_content(url)
                
                if page_data:
                    self.visited_urls.add(url)
                    self.stats['pages_visited'] += 1
                    
                    # Save HTML page
                    self.save_page_html(page_data)
                    
                    # Download assets
                    self.extract_and_download_assets(page_data)
                    
                    # Extract new links for crawling
                    links = self.extract_all_links(page_data)
                    
                    # Add new URLs to pending
                    for link in links:
                        if link['url'] not in self.visited_urls:
                            self.pending_urls.add(link['url'])
                    
                    pages_processed += 1
                    
                    # Progress report
                    if pages_processed % 3 == 0:
                        self.print_progress()
                
                else:
                    self.failed_urls.add(url)
                    self.stats['errors'] += 1
                
                # Delay between requests
                time.sleep(delay)
                
        except KeyboardInterrupt:
            self.logger.info("⏹️ Crawling interrupted by user")
        
        finally:
            self.cleanup()
    
    def print_progress(self):
        """Print progress"""
        self.logger.info(f"📊 Progress: {self.stats['pages_visited']} pages, "
                        f"{self.stats['assets_downloaded']} assets, "
                        f"{len(self.pending_urls)} pending URLs")
    
    def cleanup(self):
        """Cleanup and final report"""
        if hasattr(self, 'driver'):
            self.driver.quit()
        
        self.save_final_report()
        self.print_final_summary()
    
    def save_final_report(self):
        """Save final crawling report"""
        report = {
            'base_url': self.base_url,
            'crawl_completed': time.strftime('%Y-%m-%d %H:%M:%S'),
            'method_used': self.method,
            'statistics': self.stats,
            'pages_visited': list(self.visited_urls),
            'failed_urls': list(self.failed_urls),
            'pending_urls': list(self.pending_urls),
            'total_files_downloaded': len(self.downloaded_files)
        }
        
        report_file = self.download_dir / 'hybrid_crawling_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📋 Report saved: {report_file}")
    
    def print_final_summary(self):
        """Print final summary"""
        self.logger.info("\n" + "="*60)
        self.logger.info("🎉 HYBRID CRAWLING COMPLETED!")
        self.logger.info("="*60)
        self.logger.info(f"🔧 Method Used: {self.method}")
        self.logger.info(f"🌐 Pages Visited: {self.stats['pages_visited']}")
        self.logger.info(f"💾 HTML Files: {self.stats['pages_downloaded']}")
        self.logger.info(f"📦 Assets Downloaded: {self.stats['assets_downloaded']}")
        self.logger.info(f"🔗 Links Found: {self.stats['links_found']}")
        self.logger.info(f"❌ Errors: {self.stats['errors']}")
        self.logger.info(f"📁 Output: {self.download_dir.absolute()}")
        
        if self.use_selenium:
            self.logger.info("✨ JavaScript-rendered pages captured!")
        else:
            self.logger.info("💡 Static HTML parsing used")
            
        self.logger.info("="*60)

def main():
    """Main function dengan opsi"""
    import argparse
    
    parser = argparse.ArgumentParser(description='🔀 Hybrid Web Scraper (Selenium + Requests)')
    parser.add_argument('--url', '-u',
                       default='https://admin.pixelstrap.net/mofi/template/',
                       help='Target URL')
    parser.add_argument('--output', '-o',
                       default='hybrid_download',
                       help='Output directory')
    parser.add_argument('--max-pages', '-m',
                       type=int, default=20,
                       help='Maximum pages to crawl')
    parser.add_argument('--delay', '-d',
                       type=float, default=1.0,
                       help='Delay between requests')
    parser.add_argument('--no-selenium',
                       action='store_true',
                       help='Force use requests only (no Selenium)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🔀 HYBRID WEB SCRAPER")
    print("="*70)
    print(f"Target: {args.url}")
    print(f"Output: {args.output}")
    print(f"Max Pages: {args.max_pages}")
    print(f"Delay: {args.delay}s")
    print(f"Selenium Available: {SELENIUM_AVAILABLE}")
    print(f"Force Requests Only: {args.no_selenium}")
    print("="*70)
    
    try:
        scraper = HybridWebScraper(
            base_url=args.url,
            download_dir=args.output,
            use_selenium=not args.no_selenium
        )
        
        scraper.crawl_website(
            max_pages=args.max_pages,
            delay=args.delay
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
