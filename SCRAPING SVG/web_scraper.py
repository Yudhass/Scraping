#!/usr/bin/env python3
"""
Web Scraper untuk mengunduh semua halaman HTML dan resource
dari https://admin.pixelstrap.net/mofi/template/
"""

import os
import re
import sys
import time
import requests
from urllib.parse import urljoin, urlparse, unquote
from urllib.robotparser import RobotFileParser
import threading
from queue import Queue
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import mimetypes
from collections import defaultdict

class WebScraper:
    def __init__(self, base_url, download_dir="downloaded_site", max_workers=5):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.download_dir = Path(download_dir)
        self.downloaded_urls = set()
        self.failed_urls = set()
        self.url_queue = Queue()
        self.resource_queue = Queue()
        self.max_workers = max_workers
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # File extensions untuk resource
        self.resource_extensions = {
            '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', 
            '.woff', '.woff2', '.ttf', '.eot', '.otf', '.webp', '.bmp',
            '.pdf', '.zip', '.rar', '.mp3', '.mp4', '.avi', '.mov'
        }
        
        # HTML extensions
        self.html_extensions = {'.html', '.htm', '.php', '.asp', '.aspx', '.jsp'}
        
        # Headers untuk request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Session untuk connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def create_directory_structure(self, url_path):
        """Membuat struktur direktori berdasarkan URL path"""
        # Parse URL untuk mendapatkan path
        parsed_url = urlparse(url_path)
        path = unquote(parsed_url.path)
        
        # Bersihkan path
        if path.startswith('/'):
            path = path[1:]
        
        # Jika path kosong atau hanya '/', gunakan index.html
        if not path or path == '/':
            path = 'index.html'
        
        # Jika path berakhir dengan '/', tambahkan index.html
        if path.endswith('/'):
            path += 'index.html'
        
        # Buat path lengkap
        full_path = self.download_dir / path
        
        # Buat direktori jika belum ada
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        return full_path
    
    def is_same_domain(self, url):
        """Cek apakah URL masih dalam domain yang sama"""
        return urlparse(url).netloc == self.domain
    
    def get_file_extension(self, url):
        """Dapatkan ekstensi file dari URL"""
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        return Path(path).suffix.lower()
    
    def is_valid_url(self, url):
        """Validasi URL"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme)
        except:
            return False
    
    def download_file(self, url, file_path, is_html=False):
        """Download file dari URL ke path yang ditentukan"""
        try:
            if url in self.downloaded_urls:
                return True
                
            self.logger.info(f"Downloading: {url}")
            
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Tulis file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.downloaded_urls.add(url)
            self.logger.info(f"✓ Downloaded: {file_path}")
            
            # Jika ini HTML, parse untuk mencari resource dan link lain
            if is_html:
                self.parse_html_for_resources(file_path, url)
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"✗ Failed to download {url}: {e}")
            self.failed_urls.add(url)
            return False
        except Exception as e:
            self.logger.error(f"✗ Error downloading {url}: {e}")
            self.failed_urls.add(url)
            return False
    
    def parse_html_for_resources(self, html_file_path, base_url):
        """Parse HTML untuk mencari semua resource dan link"""
        try:
            with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Dictionary untuk berbagai jenis tag dan atribut
            resource_selectors = {
                'link': ['href'],           # CSS, favicon, dll
                'script': ['src'],          # JavaScript
                'img': ['src', 'data-src'], # Gambar
                'source': ['src', 'srcset'], # Media sources
                'video': ['src', 'poster'], # Video
                'audio': ['src'],           # Audio
                'iframe': ['src'],          # Embedded content
                'object': ['data'],         # Objects
                'embed': ['src'],           # Embedded content
                'form': ['action'],         # Form actions
                'a': ['href'],              # Links
                'area': ['href'],           # Image map areas
            }
            
            # Parse semua resource
            for tag_name, attributes in resource_selectors.items():
                tags = soup.find_all(tag_name)
                for tag in tags:
                    for attr in attributes:
                        if tag.has_attr(attr):
                            resource_url = tag[attr]
                            if resource_url:
                                # Handle multiple URLs (seperti srcset)
                                if attr == 'srcset':
                                    urls = [url.strip().split(' ')[0] for url in resource_url.split(',')]
                                    for url in urls:
                                        self.process_resource_url(url, base_url)
                                else:
                                    self.process_resource_url(resource_url, base_url)
            
            # Parse inline CSS untuk resource
            self.parse_css_resources(content, base_url)
            
            # Parse style tags
            style_tags = soup.find_all('style')
            for style_tag in style_tags:
                if style_tag.string:
                    self.parse_css_resources(style_tag.string, base_url)
                    
        except Exception as e:
            self.logger.error(f"Error parsing HTML {html_file_path}: {e}")
    
    def parse_css_resources(self, css_content, base_url):
        """Parse CSS untuk mencari resource seperti gambar, font, dll"""
        try:
            # Pattern untuk mencari URL dalam CSS
            url_pattern = re.compile(r'url\s*\(\s*["\']?([^"\'\)]+)["\']?\s*\)', re.IGNORECASE)
            urls = url_pattern.findall(css_content)
            
            for url in urls:
                url = url.strip()
                if url:
                    self.process_resource_url(url, base_url)
                    
        except Exception as e:
            self.logger.error(f"Error parsing CSS: {e}")
    
    def process_resource_url(self, url, base_url):
        """Proses URL resource dan tambahkan ke queue jika valid"""
        try:
            # Skip data URLs, javascript, dan mailto
            if url.startswith(('data:', 'javascript:', 'mailto:', '#')):
                return
            
            # Resolve relative URLs
            absolute_url = urljoin(base_url, url)
            
            # Skip jika bukan domain yang sama
            if not self.is_same_domain(absolute_url):
                return
            
            # Skip jika sudah didownload
            if absolute_url in self.downloaded_urls:
                return
            
            # Tentukan apakah ini HTML atau resource
            extension = self.get_file_extension(absolute_url)
            
            if extension in self.html_extensions or not extension:
                # Ini kemungkinan halaman HTML
                self.url_queue.put(absolute_url)
            else:
                # Ini resource (CSS, JS, gambar, dll)
                self.resource_queue.put(absolute_url)
                
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {e}")
    
    def worker_html(self):
        """Worker thread untuk download halaman HTML"""
        while True:
            try:
                url = self.url_queue.get(timeout=5)
                if url is None:
                    break
                
                file_path = self.create_directory_structure(url)
                
                # Pastikan file memiliki ekstensi HTML
                if not file_path.suffix:
                    file_path = file_path.with_suffix('.html')
                
                self.download_file(url, file_path, is_html=True)
                self.url_queue.task_done()
                
            except:
                break
    
    def worker_resource(self):
        """Worker thread untuk download resource"""
        while True:
            try:
                url = self.resource_queue.get(timeout=5)
                if url is None:
                    break
                
                file_path = self.create_directory_structure(url)
                self.download_file(url, file_path, is_html=False)
                self.resource_queue.task_done()
                
            except:
                break
    
    def start_scraping(self):
        """Mulai proses scraping"""
        self.logger.info(f"Starting scraping of {self.base_url}")
        self.logger.info(f"Download directory: {self.download_dir.absolute()}")
        
        # Buat direktori download
        self.download_dir.mkdir(exist_ok=True)
        
        # Tambahkan URL utama ke queue
        self.url_queue.put(self.base_url)
        
        # Start worker threads
        html_workers = []
        resource_workers = []
        
        # Worker untuk HTML
        for i in range(2):  # 2 worker untuk HTML
            worker = threading.Thread(target=self.worker_html)
            worker.daemon = True
            worker.start()
            html_workers.append(worker)
        
        # Worker untuk resource
        for i in range(self.max_workers):  # Lebih banyak worker untuk resource
            worker = threading.Thread(target=self.worker_resource)
            worker.daemon = True
            worker.start()
            resource_workers.append(worker)
        
        # Monitor progress
        try:
            while True:
                html_remaining = self.url_queue.qsize()
                resource_remaining = self.resource_queue.qsize()
                
                if html_remaining == 0 and resource_remaining == 0:
                    time.sleep(2)  # Wait a bit untuk memastikan tidak ada yang ditambahkan
                    if self.url_queue.qsize() == 0 and self.resource_queue.qsize() == 0:
                        break
                
                self.logger.info(f"Queue status - HTML: {html_remaining}, Resources: {resource_remaining}, Downloaded: {len(self.downloaded_urls)}")
                time.sleep(5)
                
        except KeyboardInterrupt:
            self.logger.info("Scraping interrupted by user")
        
        # Wait for all tasks to complete
        self.url_queue.join()
        self.resource_queue.join()
        
        # Stop workers
        for _ in html_workers:
            self.url_queue.put(None)
        for _ in resource_workers:
            self.resource_queue.put(None)
        
        # Wait for workers to finish
        for worker in html_workers + resource_workers:
            worker.join()
        
        self.print_summary()
    
    def print_summary(self):
        """Print summary hasil scraping"""
        self.logger.info("\n" + "="*50)
        self.logger.info("SCRAPING SUMMARY")
        self.logger.info("="*50)
        self.logger.info(f"Total files downloaded: {len(self.downloaded_urls)}")
        self.logger.info(f"Failed downloads: {len(self.failed_urls)}")
        self.logger.info(f"Download directory: {self.download_dir.absolute()}")
        
        if self.failed_urls:
            self.logger.info("\nFailed URLs:")
            for url in list(self.failed_urls)[:10]:  # Show first 10 failed URLs
                self.logger.info(f"  - {url}")
            if len(self.failed_urls) > 10:
                self.logger.info(f"  ... and {len(self.failed_urls) - 10} more")

def main():
    """Main function"""
    base_url = "https://admin.pixelstrap.net/mofi/template/"
    download_dir = "mofi_template_downloaded"
    
    print("="*60)
    print("WEB SCRAPER - MOFI TEMPLATE")
    print("="*60)
    print(f"Target URL: {base_url}")
    print(f"Download Directory: {download_dir}")
    print("="*60)
    
    scraper = WebScraper(base_url, download_dir, max_workers=8)
    
    try:
        scraper.start_scraping()
        print("\n✓ Scraping completed successfully!")
        print(f"Check the '{download_dir}' directory for downloaded files.")
        
    except Exception as e:
        print(f"\n✗ Error during scraping: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
