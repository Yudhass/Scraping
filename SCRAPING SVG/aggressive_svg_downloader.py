#!/usr/bin/env python3
"""
Aggressive SVG Downloader - Download SEMUA file SVG yang ada
Tidak berhenti sampai semua SVG ditemukan dan didownload
"""

import os
import sys
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Try import Selenium for deep scanning
SELENIUM_AVAILABLE = False
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    pass

class AggressiveSVGDownloader:
    def __init__(self, base_url, output_dir="all_svg_download"):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Collections
        self.all_svg_urls = set()
        self.downloaded_svgs = []
        self.failed_downloads = []
        self.visited_pages = set()
        self.scanned_directories = set()
        self.css_files = set()
        self.js_files = set()
        
        # Selenium setup
        self.use_selenium = SELENIUM_AVAILABLE
        if self.use_selenium:
            self.setup_selenium()
        
        print(f"🎨 Aggressive SVG Downloader - FIND ALL SVGs!")
        print(f"🎯 Target: {base_url}")
        print(f"📁 Output: {self.output_dir.absolute()}")
        print(f"🔧 Selenium: {'✅ Available' if self.use_selenium else '❌ Not available'}")
        print("="*70)
    
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Selenium WebDriver ready for deep scanning")
        except Exception as e:
            print(f"⚠️ Selenium setup failed: {e}")
            self.use_selenium = False
    
    def test_url_exists(self, url):
        """Test if URL exists"""
        try:
            response = self.session.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def download_svg_file(self, svg_url):
        """Download single SVG file"""
        try:
            if svg_url in [svg['url'] for svg in self.downloaded_svgs]:
                return True
            
            print(f"📥 Downloading: {svg_url}")
            
            response = self.session.get(svg_url, timeout=15)
            response.raise_for_status()
            
            # Verify it's actually SVG content
            content_type = response.headers.get('content-type', '').lower()
            if 'svg' not in content_type and not response.text.strip().startswith('<svg'):
                print(f"⚠️ Not SVG content: {svg_url}")
                return False
            
            # Generate filename
            url_path = urlparse(svg_url).path
            filename = Path(url_path).name
            if not filename or not filename.endswith('.svg'):
                filename = f"svg_{len(self.downloaded_svgs) + 1}.svg"
            
            # Handle duplicates
            svg_file = self.output_dir / filename
            counter = 1
            original_stem = svg_file.stem
            while svg_file.exists():
                svg_file = self.output_dir / f"{original_stem}_{counter}.svg"
                counter += 1
            
            # Save SVG
            with open(svg_file, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            
            # Analyze SVG content
            try:
                svg_content = response.text
                symbol_count = len(re.findall(r'<symbol', svg_content, re.IGNORECASE))
                path_count = len(re.findall(r'<path', svg_content, re.IGNORECASE))
                g_count = len(re.findall(r'<g\s', svg_content, re.IGNORECASE))
                circle_count = len(re.findall(r'<circle', svg_content, re.IGNORECASE))
                rect_count = len(re.findall(r'<rect', svg_content, re.IGNORECASE))
            except:
                symbol_count = path_count = g_count = circle_count = rect_count = 0
            
            svg_info = {
                'url': svg_url,
                'filename': svg_file.name,
                'size_bytes': file_size,
                'size_kb': round(file_size / 1024, 2),
                'content_type': content_type,
                'symbols': symbol_count,
                'paths': path_count,
                'groups': g_count,
                'circles': circle_count,
                'rectangles': rect_count,
                'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.downloaded_svgs.append(svg_info)
            
            print(f"✅ Saved: {svg_file.name}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            if symbol_count > 0:
                print(f"   Symbols: {symbol_count}")
            if path_count > 0:
                print(f"   Paths: {path_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {svg_url}: {e}")
            self.failed_downloads.append({'url': svg_url, 'error': str(e)})
            return False
    
    def scan_directory_listings(self):
        """Scan for directory listings with SVG files"""
        print(f"\n🔍 STRATEGY 1: Directory Listings Scan")
        print("-" * 50)
        
        # Common SVG directories
        svg_directories = [
            f"{self.base_url}/assets/svg/",
            f"{self.base_url}/assets/icons/",
            f"{self.base_url}/assets/images/svg/",
            f"{self.base_url}/assets/images/icons/",
            f"{self.base_url}/assets/img/svg/",
            f"{self.base_url}/assets/img/icons/",
            f"{self.base_url}/svg/",
            f"{self.base_url}/icons/",
            f"{self.base_url}/images/svg/",
            f"{self.base_url}/img/svg/",
            f"{self.base_url}/static/svg/",
            f"{self.base_url}/static/icons/",
            f"{self.base_url}/public/svg/",
            f"{self.base_url}/public/icons/",
        ]
        
        for dir_url in svg_directories:
            if dir_url in self.scanned_directories:
                continue
            
            self.scanned_directories.add(dir_url)
            
            try:
                print(f"🔍 Checking directory: {dir_url}")
                response = self.session.get(dir_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for SVG file links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.endswith('.svg') or '.svg' in href:
                            svg_url = urljoin(dir_url, href)
                            if urlparse(svg_url).netloc == self.domain:
                                print(f"   📎 Found: {svg_url}")
                                self.all_svg_urls.add(svg_url)
                    
                    # Also look for any mention of .svg in text
                    page_text = response.text
                    svg_mentions = re.findall(r'["\']([^"\']*\.svg[^"\']*)["\']', page_text)
                    for mention in svg_mentions:
                        if not mention.startswith('#'):
                            svg_url = urljoin(dir_url, mention)
                            if urlparse(svg_url).netloc == self.domain:
                                print(f"   📎 Found mention: {svg_url}")
                                self.all_svg_urls.add(svg_url)
                                
            except Exception as e:
                print(f"   ❌ Error checking {dir_url}: {e}")
    
    def scan_html_pages_deep(self):
        """Deep scan HTML pages for SVG references"""
        print(f"\n🔍 STRATEGY 2: Deep HTML Pages Scan")
        print("-" * 50)
        
        # Get list of all HTML pages from previous downloads
        html_pages = []
        
        # Common pages
        common_pages = [
            f"{self.base_url}/template/",
            f"{self.base_url}/template/index.html",
            f"{self.base_url}/",
        ]
        
        # Add pages from hybrid download if exists
        hybrid_dir = Path("hybrid_download")
        if hybrid_dir.exists():
            for html_file in hybrid_dir.glob("*.html"):
                if html_file.name.startswith("mofi_template_"):
                    page_name = html_file.name.replace("mofi_template_", "").replace(".html.html", ".html")
                    page_url = f"{self.base_url}/template/{page_name}"
                    html_pages.append(page_url)
        
        # Scan with Selenium if available
        if self.use_selenium:
            print("🌐 Using Selenium for JavaScript-rendered content")
            for page_url in common_pages + html_pages:
                self.scan_page_with_selenium(page_url)
        else:
            print("🌐 Using requests for static content")
            for page_url in common_pages + html_pages:
                self.scan_page_with_requests(page_url)
    
    def scan_page_with_selenium(self, page_url):
        """Scan page using Selenium"""
        try:
            if page_url in self.visited_pages:
                return
            
            print(f"🌐 [Selenium] Scanning: {page_url}")
            self.visited_pages.add(page_url)
            
            self.driver.get(page_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)  # Wait for dynamic content
            
            page_source = self.driver.page_source
            self.extract_svg_references_from_html(page_source, page_url)
            
        except Exception as e:
            print(f"❌ Selenium error on {page_url}: {e}")
    
    def scan_page_with_requests(self, page_url):
        """Scan page using requests"""
        try:
            if page_url in self.visited_pages:
                return
            
            print(f"🌐 [Requests] Scanning: {page_url}")
            self.visited_pages.add(page_url)
            
            response = self.session.get(page_url, timeout=15)
            response.raise_for_status()
            
            self.extract_svg_references_from_html(response.text, page_url)
            
        except Exception as e:
            print(f"❌ Requests error on {page_url}: {e}")
    
    def extract_svg_references_from_html(self, html_content, base_url):
        """Extract SVG references from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Method 1: Direct SVG elements and attributes
        svg_selectors = [
            ('img', 'src'),
            ('image', 'href'),
            ('image', 'xlink:href'),
            ('use', 'href'),
            ('use', 'xlink:href'),
            ('link', 'href'),
            ('object', 'data'),
            ('embed', 'src'),
        ]
        
        for tag, attr in svg_selectors:
            elements = soup.find_all(tag)
            for element in elements:
                url = element.get(attr, '').strip()
                if url and '.svg' in url:
                    clean_url = url.split('#')[0]
                    absolute_url = urljoin(base_url, clean_url)
                    if urlparse(absolute_url).netloc == self.domain:
                        self.all_svg_urls.add(absolute_url)
        
        # Method 2: CSS styles
        for style_element in soup.find_all(['style', '[style]']):
            if style_element.name == 'style':
                css_content = style_element.get_text()
            else:
                css_content = style_element.get('style', '')
            
            self.extract_svg_from_css(css_content, base_url)
        
        # Method 3: JavaScript content
        for script in soup.find_all('script'):
            script_content = script.get_text()
            svg_matches = re.findall(r'["\']([^"\']*\.svg[^"\']*)["\']', script_content)
            for match in svg_matches:
                if '/' in match:
                    clean_url = match.split('#')[0]
                    absolute_url = urljoin(base_url, clean_url)
                    if urlparse(absolute_url).netloc == self.domain:
                        self.all_svg_urls.add(absolute_url)
        
        # Method 4: Data attributes
        for element in soup.find_all(attrs=lambda x: x and any(key.startswith('data-') for key in x.keys())):
            for attr, value in element.attrs.items():
                if isinstance(value, str) and '.svg' in value:
                    clean_url = value.split('#')[0]
                    absolute_url = urljoin(base_url, clean_url)
                    if urlparse(absolute_url).netloc == self.domain:
                        self.all_svg_urls.add(absolute_url)
        
        # Method 5: Text pattern matching
        svg_patterns = [
            r'["\']([^"\']*\.svg(?:\?[^"\']*)?(?:#[^"\']*)?)["\']',
            r'url\(["\']?([^"\']*\.svg[^"\']*)["\']?\)',
            r'href=["\']([^"\']*\.svg[^"\']*)["\']',
            r'src=["\']([^"\']*\.svg[^"\']*)["\']',
        ]
        
        for pattern in svg_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if not match.startswith('#'):
                    clean_url = match.split('#')[0]
                    absolute_url = urljoin(base_url, clean_url)
                    if urlparse(absolute_url).netloc == self.domain:
                        self.all_svg_urls.add(absolute_url)
    
    def extract_svg_from_css(self, css_content, base_url):
        """Extract SVG URLs from CSS content"""
        svg_matches = re.findall(r'url\(["\']?([^"\']*\.svg[^"\']*)["\']?\)', css_content)
        for match in svg_matches:
            clean_url = match.split('#')[0]
            absolute_url = urljoin(base_url, clean_url)
            if urlparse(absolute_url).netloc == self.domain:
                self.all_svg_urls.add(absolute_url)
    
    def scan_css_files(self):
        """Scan CSS files for SVG references"""
        print(f"\n🔍 STRATEGY 3: CSS Files Scan")
        print("-" * 50)
        
        css_urls = [
            f"{self.base_url}/assets/css/style.css",
            f"{self.base_url}/assets/css/responsive.css",
            f"{self.base_url}/assets/css/color-1.css",
            f"{self.base_url}/assets/css/font-awesome.css",
            f"{self.base_url}/assets/css/vendors/bootstrap.css",
            f"{self.base_url}/assets/css/vendors/fontawesome.css",
        ]
        
        for css_url in css_urls:
            if css_url in self.css_files:
                continue
            
            try:
                print(f"🎨 Scanning CSS: {css_url}")
                self.css_files.add(css_url)
                
                response = self.session.get(css_url, timeout=10)
                if response.status_code == 200:
                    self.extract_svg_from_css(response.text, css_url)
                    print(f"   ✅ Scanned: {css_url}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def brute_force_svg_discovery(self):
        """Brute force common SVG file names"""
        print(f"\n🔍 STRATEGY 4: Brute Force SVG Discovery")
        print("-" * 50)
        
        # Common SVG file names
        common_svg_names = [
            "icon-sprite.svg", "icons.svg", "sprite.svg", "symbols.svg",
            "fontawesome.svg", "feather.svg", "bootstrap-icons.svg",
            "material-icons.svg", "hero-icons.svg", "lucide.svg",
            "tabler-icons.svg", "phosphor.svg", "iconify.svg",
            "eva-icons.svg", "ant-design.svg", "carbon.svg",
            "logos.svg", "brands.svg", "social.svg", "ui.svg",
            "interface.svg", "system.svg", "outline.svg", "solid.svg",
            "line.svg", "fill.svg", "duotone.svg", "light.svg",
            "regular.svg", "bold.svg", "thin.svg"
        ]
        
        # Numbered variants
        for i in range(1, 20):
            common_svg_names.extend([
                f"icon-sprite{i}.svg", f"icons{i}.svg", f"sprite{i}.svg",
                f"icon-sprite-{i}.svg", f"icons-{i}.svg", f"sprite-{i}.svg"
            ])
        
        # Base paths
        base_paths = [
            f"{self.base_url}/assets/svg/",
            f"{self.base_url}/assets/icons/",
            f"{self.base_url}/assets/images/svg/",
            f"{self.base_url}/assets/img/svg/",
            f"{self.base_url}/svg/",
            f"{self.base_url}/icons/",
        ]
        
        total_tests = len(base_paths) * len(common_svg_names)
        current_test = 0
        
        print(f"🎯 Testing {total_tests} potential SVG URLs...")
        
        # Use threading for faster testing
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for base_path in base_paths:
                for svg_name in common_svg_names:
                    svg_url = base_path + svg_name
                    future = executor.submit(self.test_and_add_svg, svg_url)
                    futures.append(future)
            
            for future in as_completed(futures):
                current_test += 1
                if current_test % 50 == 0:
                    print(f"   📊 Progress: {current_test}/{total_tests} URLs tested")
    
    def test_and_add_svg(self, svg_url):
        """Test SVG URL and add if exists"""
        try:
            response = self.session.head(svg_url, timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'svg' in content_type or 'xml' in content_type:
                    print(f"   ✅ Found SVG: {svg_url}")
                    self.all_svg_urls.add(svg_url)
                    return True
        except:
            pass
        return False
    
    def crawl_all_pages_for_svgs(self):
        """Crawl all pages found to extract more SVG references"""
        print(f"\n🔍 STRATEGY 5: Full Site Crawl for SVGs")
        print("-" * 50)
        
        # Start from main template pages
        pages_to_crawl = [
            f"{self.base_url}/template/",
            f"{self.base_url}/template/index.html",
        ]
        
        crawled_count = 0
        max_crawl = 50  # Limit to prevent infinite crawling
        
        while pages_to_crawl and crawled_count < max_crawl:
            page_url = pages_to_crawl.pop(0)
            
            if page_url in self.visited_pages:
                continue
            
            try:
                print(f"🕷️ Crawling: {page_url}")
                response = self.session.get(page_url, timeout=15)
                
                if response.status_code == 200:
                    self.visited_pages.add(page_url)
                    crawled_count += 1
                    
                    # Extract SVG references
                    self.extract_svg_references_from_html(response.text, page_url)
                    
                    # Find more pages to crawl
                    soup = BeautifulSoup(response.content, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href and not href.startswith(('#', 'javascript:', 'mailto:')):
                            absolute_url = urljoin(page_url, href)
                            if (urlparse(absolute_url).netloc == self.domain and
                                absolute_url not in self.visited_pages and
                                (absolute_url.endswith('.html') or '.' not in Path(urlparse(absolute_url).path).name)):
                                pages_to_crawl.append(absolute_url)
                
                time.sleep(0.3)  # Be nice to server
                
            except Exception as e:
                print(f"❌ Crawl error on {page_url}: {e}")
        
        print(f"📊 Crawled {crawled_count} pages")
    
    def download_all_found_svgs(self):
        """Download all found SVG files"""
        print(f"\n📥 DOWNLOADING ALL FOUND SVGs")
        print("-" * 50)
        
        if not self.all_svg_urls:
            print("❌ No SVG URLs found to download")
            return
        
        print(f"🎯 Found {len(self.all_svg_urls)} potential SVG URLs")
        
        # Download with threading for speed
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.download_svg_file, svg_url): svg_url 
                      for svg_url in self.all_svg_urls}
            
            for future in as_completed(futures):
                svg_url = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Download failed for {svg_url}: {e}")
    
    def run_aggressive_download(self):
        """Run all strategies to find and download ALL SVGs"""
        print("🚀 STARTING AGGRESSIVE SVG DOWNLOAD")
        print("🎯 GOAL: Find and download ALL SVG files")
        print("⚡ Will not stop until all SVGs are found!")
        print("="*70)
        
        # Strategy 1: Directory listings
        self.scan_directory_listings()
        
        # Strategy 2: Deep HTML scan
        self.scan_html_pages_deep()
        
        # Strategy 3: CSS files scan
        self.scan_css_files()
        
        # Strategy 4: Brute force discovery
        self.brute_force_svg_discovery()
        
        # Strategy 5: Full site crawl
        self.crawl_all_pages_for_svgs()
        
        # Download all found SVGs
        self.download_all_found_svgs()
        
        # Final summary
        self.print_final_summary()
        
        # Cleanup
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def print_final_summary(self):
        """Print comprehensive final summary"""
        print("\n" + "="*70)
        print("🎨 AGGRESSIVE SVG DOWNLOAD COMPLETED!")
        print("="*70)
        
        print(f"📊 DISCOVERY STATISTICS:")
        print(f"   🌐 Pages scanned: {len(self.visited_pages)}")
        print(f"   📁 Directories checked: {len(self.scanned_directories)}")
        print(f"   🎨 CSS files scanned: {len(self.css_files)}")
        print(f"   🔍 Total SVG URLs found: {len(self.all_svg_urls)}")
        
        print(f"\n📥 DOWNLOAD RESULTS:")
        print(f"   ✅ Successfully downloaded: {len(self.downloaded_svgs)}")
        print(f"   ❌ Failed downloads: {len(self.failed_downloads)}")
        
        if self.downloaded_svgs:
            total_size = sum(svg['size_bytes'] for svg in self.downloaded_svgs)
            total_symbols = sum(svg.get('symbols', 0) for svg in self.downloaded_svgs)
            total_paths = sum(svg.get('paths', 0) for svg in self.downloaded_svgs)
            
            print(f"   💾 Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
            print(f"   🎯 Total symbols: {total_symbols}")
            print(f"   🎨 Total paths: {total_paths}")
            print(f"   📁 Location: {self.output_dir.absolute()}")
            
            print(f"\n📋 DOWNLOADED SVG FILES:")
            for i, svg in enumerate(self.downloaded_svgs, 1):
                print(f"{i:2d}. {svg['filename']}")
                print(f"     📏 Size: {svg['size_bytes']:,} bytes")
                print(f"     🔗 URL: {svg['url']}")
                if svg.get('symbols', 0) > 0:
                    print(f"     🎯 Symbols: {svg['symbols']}")
                if svg.get('paths', 0) > 0:
                    print(f"     🎨 Paths: {svg['paths']}")
                print()
        
        else:
            print("❌ No SVG files successfully downloaded")
            print("💡 Possible reasons:")
            print("   • SVG files are embedded inline in HTML")
            print("   • SVG files are generated dynamically")
            print("   • SVG files require authentication")
            print("   • SVG files are located in non-standard paths")
        
        if self.failed_downloads:
            print(f"\n❌ FAILED DOWNLOADS ({len(self.failed_downloads)}):")
            for fail in self.failed_downloads[:10]:  # Show first 10
                print(f"   • {fail['url']}: {fail['error']}")
            if len(self.failed_downloads) > 10:
                print(f"   ... and {len(self.failed_downloads) - 10} more")
        
        # Save comprehensive report
        report = {
            'download_completed': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url,
            'discovery_stats': {
                'pages_scanned': len(self.visited_pages),
                'directories_checked': len(self.scanned_directories),
                'css_files_scanned': len(self.css_files),
                'svg_urls_found': len(self.all_svg_urls)
            },
            'download_results': {
                'successful_downloads': len(self.downloaded_svgs),
                'failed_downloads': len(self.failed_downloads),
                'total_size_bytes': sum(svg['size_bytes'] for svg in self.downloaded_svgs) if self.downloaded_svgs else 0
            },
            'all_svg_urls_found': list(self.all_svg_urls),
            'downloaded_svgs': self.downloaded_svgs,
            'failed_downloads': self.failed_downloads,
            'visited_pages': list(self.visited_pages)
        }
        
        report_file = self.output_dir / 'aggressive_svg_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Full report saved: {report_file}")
        print("="*70)
        
        if self.downloaded_svgs:
            print("🎉 SUCCESS: SVG files found and downloaded!")
        else:
            print("⚠️ No SVG files downloaded. Try manual inspection.")

def main():
    # Target URL (base Mofi website)
    base_url = "https://admin.pixelstrap.net/mofi"
    
    downloader = AggressiveSVGDownloader(base_url, "all_svg_download")
    downloader.run_aggressive_download()

if __name__ == "__main__":
    main()
