#!/usr/bin/env python3
"""
Enhanced Web Scraper dengan Selenium WebDriver
Untuk scraping website yang lebih komprehensif seperti browsing sungguhan
"""

import os
import sys
import time
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import threading
from queue import Queue
import json
from collections import defaultdict

class EnhancedWebScraper:
    def __init__(self, base_url, download_dir="enhanced_download", headless=True):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        self.visited_urls = set()
        self.downloaded_files = set()
        self.failed_urls = set()
        self.url_queue = Queue()
        self.headless = headless
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('enhanced_scraper.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup Selenium WebDriver
        self.setup_webdriver()
        
        # Session untuk download file
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
            'errors': 0
        }
    
    def setup_webdriver(self):
        """Setup Chrome WebDriver dengan opsi optimal"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Disable images dan CSS untuk loading lebih cepat (opsional)
        # chrome_options.add_argument('--disable-images')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.logger.info("✅ Chrome WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize WebDriver: {e}")
            self.logger.info("💡 Install ChromeDriver: sudo apt install chromium-chromedriver")
            sys.exit(1)
    
    def visit_page(self, url):
        """Kunjungi halaman dengan Selenium dan ambil semua informasi"""
        if url in self.visited_urls:
            return None
        
        try:
            self.logger.info(f"🌐 Visiting: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            self.visited_urls.add(url)
            self.stats['pages_visited'] += 1
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            page_title = self.driver.title
            current_url = self.driver.current_url
            
            # Parse dengan BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            return {
                'url': current_url,
                'title': page_title,
                'html': page_source,
                'soup': soup,
                'original_url': url
            }
            
        except TimeoutException:
            self.logger.warning(f"⏰ Timeout loading: {url}")
            self.failed_urls.add(url)
            return None
        except WebDriverException as e:
            self.logger.error(f"❌ WebDriver error on {url}: {e}")
            self.failed_urls.add(url)
            return None
        except Exception as e:
            self.logger.error(f"❌ Error visiting {url}: {e}")
            self.failed_urls.add(url)
            return None
    
    def extract_links_from_page(self, page_data):
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
            
            # Resolve to absolute URL
            absolute_url = urljoin(base_url, href)
            
            # Check if same domain
            if urlparse(absolute_url).netloc == self.domain:
                links.append({
                    'url': absolute_url,
                    'text': a_tag.get_text(strip=True)[:100],
                    'source_page': base_url
                })
        
        self.stats['links_found'] += len(links)
        self.logger.info(f"🔗 Found {len(links)} same-domain links on {base_url}")
        
        return links
    
    def save_page_html(self, page_data):
        """Save halaman HTML ke file"""
        if not page_data:
            return False
        
        try:
            url_path = urlparse(page_data['url']).path
            if not url_path or url_path == '/':
                filename = 'index.html'
            else:
                filename = url_path.strip('/').replace('/', '_') + '.html'
                if not filename.endswith('.html'):
                    filename += '.html'
            
            file_path = self.download_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(page_data['html'])
            
            self.stats['pages_downloaded'] += 1
            self.logger.info(f"💾 Saved page: {file_path}")
            
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error saving page {page_data['url']}: {e}")
            return False
    
    def extract_and_download_assets(self, page_data):
        """Extract dan download semua asset dari halaman"""
        if not page_data:
            return
        
        soup = page_data['soup']
        base_url = page_data['url']
        
        # Asset selectors
        asset_selectors = {
            'css': [
                ('link', 'href', lambda tag: tag.get('rel') and 'stylesheet' in tag.get('rel', [])),
            ],
            'js': [
                ('script', 'src', lambda tag: tag.has_attr('src')),
            ],
            'images': [
                ('img', 'src', lambda tag: tag.has_attr('src')),
                ('img', 'data-src', lambda tag: tag.has_attr('data-src')),
            ],
            'icons': [
                ('link', 'href', lambda tag: tag.get('rel') and any(x in tag.get('rel', []) for x in ['icon', 'shortcut'])),
            ],
            'fonts': [
                ('link', 'href', lambda tag: tag.get('href') and any(ext in tag.get('href', '') for ext in ['.woff', '.woff2', '.ttf', '.eot'])),
            ]
        }
        
        for asset_type, selectors in asset_selectors.items():
            for tag_name, attr_name, condition in selectors:
                tags = soup.find_all(tag_name)
                for tag in tags:
                    if condition(tag):
                        asset_url = tag.get(attr_name)
                        if asset_url:
                            self.download_asset(asset_url, base_url, asset_type)
    
    def download_asset(self, asset_url, base_url, asset_type):
        """Download single asset"""
        try:
            # Skip if already downloaded
            if asset_url in self.downloaded_files:
                return
            
            # Resolve to absolute URL
            absolute_url = urljoin(base_url, asset_url)
            
            # Skip external domains
            if urlparse(absolute_url).netloc != self.domain:
                return
            
            # Skip data URLs
            if absolute_url.startswith('data:'):
                return
            
            self.logger.info(f"📥 Downloading {asset_type}: {absolute_url}")
            
            response = self.session.get(absolute_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Determine file path
            url_path = urlparse(absolute_url).path
            if url_path:
                file_path = self.download_dir / url_path.lstrip('/')
                file_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                # Fallback filename
                extension = self.get_extension_from_content_type(response.headers.get('content-type', ''))
                file_path = self.download_dir / f"asset_{len(self.downloaded_files)}{extension}"
            
            # Download file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.downloaded_files.add(asset_url)
            self.stats['assets_downloaded'] += 1
            self.logger.info(f"✅ Saved {asset_type}: {file_path}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to download asset {absolute_url}: {e}")
    
    def get_extension_from_content_type(self, content_type):
        """Get file extension dari content type"""
        extensions = {
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
        return extensions.get(content_type.split(';')[0], '')
    
    def crawl_website(self, max_pages=50, delay=2):
        """Main crawling function"""
        self.logger.info(f"🚀 Starting enhanced crawling of {self.base_url}")
        self.logger.info(f"📁 Download directory: {self.download_dir.absolute()}")
        
        # Add starting URL to queue
        self.url_queue.put(self.base_url)
        
        pages_crawled = 0
        
        try:
            while not self.url_queue.empty() and pages_crawled < max_pages:
                url = self.url_queue.get()
                
                if url in self.visited_urls:
                    continue
                
                # Visit page with browser
                page_data = self.visit_page(url)
                
                if page_data:
                    # Save HTML
                    self.save_page_html(page_data)
                    
                    # Extract and download assets
                    self.extract_and_download_assets(page_data)
                    
                    # Extract links for further crawling
                    links = self.extract_links_from_page(page_data)
                    
                    # Add new links to queue
                    for link in links:
                        if link['url'] not in self.visited_urls:
                            self.url_queue.put(link['url'])
                    
                    pages_crawled += 1
                    
                    # Progress report
                    if pages_crawled % 5 == 0:
                        self.print_progress()
                
                # Delay between requests
                time.sleep(delay)
                
        except KeyboardInterrupt:
            self.logger.info("⏹️ Crawling interrupted by user")
        
        finally:
            self.cleanup()
    
    def print_progress(self):
        """Print progress statistics"""
        self.logger.info(f"📊 Progress: {self.stats['pages_visited']} pages visited, "
                        f"{self.stats['pages_downloaded']} HTML saved, "
                        f"{self.stats['assets_downloaded']} assets downloaded")
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()
        
        # Save final report
        self.save_final_report()
        self.print_final_summary()
    
    def save_final_report(self):
        """Save detailed crawling report"""
        report = {
            'base_url': self.base_url,
            'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': self.stats,
            'visited_urls': list(self.visited_urls),
            'failed_urls': list(self.failed_urls),
            'downloaded_files_count': len(self.downloaded_files)
        }
        
        report_file = self.download_dir / 'crawling_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📋 Report saved: {report_file}")
    
    def print_final_summary(self):
        """Print final summary"""
        self.logger.info("\n" + "="*60)
        self.logger.info("🎉 ENHANCED CRAWLING COMPLETED!")
        self.logger.info("="*60)
        self.logger.info(f"🌐 Pages Visited: {self.stats['pages_visited']}")
        self.logger.info(f"💾 HTML Files Saved: {self.stats['pages_downloaded']}")
        self.logger.info(f"📦 Assets Downloaded: {self.stats['assets_downloaded']}")
        self.logger.info(f"🔗 Links Found: {self.stats['links_found']}")
        self.logger.info(f"❌ Failed URLs: {len(self.failed_urls)}")
        self.logger.info(f"📁 Output Directory: {self.download_dir.absolute()}")
        self.logger.info("="*60)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='🚀 Enhanced Web Scraper with Selenium')
    parser.add_argument('--url', '-u', 
                       default='https://admin.pixelstrap.net/mofi/template/',
                       help='Target URL')
    parser.add_argument('--output', '-o',
                       default='enhanced_download',
                       help='Output directory')
    parser.add_argument('--max-pages', '-m',
                       type=int, default=20,
                       help='Maximum pages to crawl (default: 20)')
    parser.add_argument('--delay', '-d',
                       type=float, default=2.0,
                       help='Delay between requests (default: 2.0)')
    parser.add_argument('--no-headless',
                       action='store_true',
                       help='Run browser in non-headless mode (show GUI)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🚀 ENHANCED WEB SCRAPER WITH SELENIUM")
    print("="*70)
    print(f"Target: {args.url}")
    print(f"Output: {args.output}")
    print(f"Max Pages: {args.max_pages}")
    print(f"Delay: {args.delay}s")
    print(f"Headless: {not args.no_headless}")
    print("="*70)
    
    try:
        scraper = EnhancedWebScraper(
            base_url=args.url,
            download_dir=args.output,
            headless=not args.no_headless
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
