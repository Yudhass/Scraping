#!/usr/bin/env python3
"""
Comprehensive SVG Downloader
Berdasarkan penemuan bahwa icon-sprite.svg ada di path yang tepat
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

class ComprehensiveSVGDownloader:
    def __init__(self, base_url, output_dir="svg_complete"):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.downloaded_svgs = []
        self.visited_pages = set()
        self.tested_urls = set()
        
        print(f"🎨 Comprehensive SVG Downloader")
        print(f"🎯 Target: {base_url}")
        print(f"📁 Output: {self.output_dir.absolute()}")
    
    def download_svg_file(self, svg_url, custom_name=None):
        """Download SVG file"""
        try:
            if svg_url in [svg['url'] for svg in self.downloaded_svgs]:
                return True
            
            print(f"📥 Downloading: {svg_url}")
            
            response = self.session.get(svg_url, timeout=15)
            response.raise_for_status()
            
            # Determine filename
            if custom_name:
                filename = custom_name
            else:
                filename = Path(urlparse(svg_url).path).name
                if not filename or not filename.endswith('.svg'):
                    filename = f"svg_{len(self.downloaded_svgs) + 1}.svg"
            
            # Ensure unique filename
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
                # Count symbols/icons in sprite
                symbol_count = len(re.findall(r'<symbol', svg_content, re.IGNORECASE))
                use_count = len(re.findall(r'<use', svg_content, re.IGNORECASE))
                path_count = len(re.findall(r'<path', svg_content, re.IGNORECASE))
            except:
                symbol_count = use_count = path_count = 0
            
            svg_info = {
                'url': svg_url,
                'filename': svg_file.name,
                'size_bytes': file_size,
                'size_kb': round(file_size / 1024, 2),
                'content_type': response.headers.get('content-type', ''),
                'symbols_count': symbol_count,
                'use_count': use_count,
                'path_count': path_count,
                'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.downloaded_svgs.append(svg_info)
            
            print(f"✅ Saved: {svg_file}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            if symbol_count > 0:
                print(f"   Contains: {symbol_count} symbols/icons")
            
            # Save metadata
            with open(svg_file.with_suffix('.json'), 'w') as f:
                json.dump(svg_info, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {svg_url}: {e}")
            return False
    
    def test_svg_url(self, svg_url):
        """Test if SVG URL exists"""
        if svg_url in self.tested_urls:
            return False
        
        self.tested_urls.add(svg_url)
        
        try:
            response = self.session.head(svg_url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def discover_svg_paths(self):
        """Discover SVG files using various strategies"""
        
        # Strategy 1: Known locations
        print(f"\n🔍 Strategy 1: Testing known SVG locations...")
        
        base_paths = [
            f"{self.base_url}/assets/svg/",
            f"{self.base_url}/assets/icons/",
            f"{self.base_url}/assets/images/svg/",
            f"{self.base_url}/svg/",
            f"{self.base_url}/icons/",
        ]
        
        common_svg_names = [
            "icon-sprite.svg",
            "icons.svg",
            "sprite.svg",
            "icon.svg",
            "symbols.svg",
            "fontawesome.svg",
            "feather.svg",
            "bootstrap-icons.svg",
            "material-icons.svg"
        ]
        
        for base_path in base_paths:
            for svg_name in common_svg_names:
                svg_url = base_path + svg_name
                if self.test_svg_url(svg_url):
                    print(f"✅ Found: {svg_url}")
                    self.download_svg_file(svg_url)
        
        # Strategy 2: Scan HTML pages for SVG references
        print(f"\n🔍 Strategy 2: Scanning HTML pages for SVG references...")
        
        pages_to_scan = [
            f"{self.base_url}/template/",
            f"{self.base_url}/template/index.html",
            f"{self.base_url}/template/general-widget.html",
            f"{self.base_url}/template/form-wizard.html",
            f"{self.base_url}/template/cart.html",
            f"{self.base_url}/template/login-bs-tt-validation.html",
        ]
        
        for page_url in pages_to_scan:
            self.scan_page_for_svgs(page_url)
            time.sleep(0.5)
        
        # Strategy 3: Pattern-based discovery
        print(f"\n🔍 Strategy 3: Pattern-based SVG discovery...")
        
        # Try numeric patterns
        for i in range(1, 10):
            test_urls = [
                f"{self.base_url}/assets/svg/icon-sprite{i}.svg",
                f"{self.base_url}/assets/svg/icons{i}.svg",
                f"{self.base_url}/assets/svg/sprite{i}.svg",
            ]
            
            for svg_url in test_urls:
                if self.test_svg_url(svg_url):
                    print(f"✅ Found numbered: {svg_url}")
                    self.download_svg_file(svg_url)
        
        # Strategy 4: CSS scanning
        print(f"\n🔍 Strategy 4: Scanning CSS files for SVG references...")
        self.scan_css_for_svgs()
    
    def scan_page_for_svgs(self, page_url):
        """Scan single page for SVG references"""
        try:
            if page_url in self.visited_pages:
                return
            
            print(f"🌐 Scanning: {page_url}")
            self.visited_pages.add(page_url)
            
            response = self.session.get(page_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = str(soup)
            
            # Find SVG references
            svg_patterns = [
                r'["\']([^"\']*\.svg(?:#[^"\']*)?)["\']',  # Quoted SVG paths
                r'src=["\']([^"\']*\.svg[^"\']*)["\']',     # src attributes
                r'href=["\']([^"\']*\.svg[^"\']*)["\']',    # href attributes
                r'xlink:href=["\']([^"\']*\.svg[^"\']*)["\']',  # xlink:href
                r'url\(["\']?([^"\']*\.svg[^"\']*)["\']?\)',    # CSS url()
            ]
            
            found_svgs = set()
            
            for pattern in svg_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    if match and not match.startswith('#'):
                        # Clean URL (remove fragment)
                        clean_url = match.split('#')[0]
                        absolute_url = urljoin(page_url, clean_url)
                        if urlparse(absolute_url).netloc == self.domain:
                            found_svgs.add(absolute_url)
            
            # Test and download found SVGs
            for svg_url in found_svgs:
                if self.test_svg_url(svg_url):
                    print(f"   ✅ Found SVG: {svg_url}")
                    self.download_svg_file(svg_url)
                    
        except Exception as e:
            print(f"❌ Error scanning {page_url}: {e}")
    
    def scan_css_for_svgs(self):
        """Scan CSS files for SVG references"""
        try:
            css_urls = [
                f"{self.base_url}/assets/css/style.css",
                f"{self.base_url}/assets/css/responsive.css",
                f"{self.base_url}/assets/css/color-1.css",
            ]
            
            for css_url in css_urls:
                try:
                    print(f"🎨 Scanning CSS: {css_url}")
                    response = self.session.get(css_url, timeout=10)
                    if response.status_code == 200:
                        css_content = response.text
                        
                        # Find SVG references in CSS
                        svg_matches = re.findall(r'url\(["\']?([^"\']*\.svg[^"\']*)["\']?\)', css_content)
                        
                        for match in svg_matches:
                            absolute_url = urljoin(css_url, match)
                            if urlparse(absolute_url).netloc == self.domain:
                                if self.test_svg_url(absolute_url):
                                    print(f"   ✅ Found in CSS: {absolute_url}")
                                    self.download_svg_file(absolute_url)
                                    
                except Exception as e:
                    print(f"   ❌ Error scanning CSS {css_url}: {e}")
                    
        except Exception as e:
            print(f"❌ Error in CSS scanning: {e}")
    
    def run_comprehensive_download(self):
        """Run comprehensive SVG download"""
        print("🚀 Starting comprehensive SVG download...")
        print("="*60)
        
        self.discover_svg_paths()
        
        # Final summary
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print final summary"""
        print("\n" + "="*60)
        print("🎨 SVG DOWNLOAD COMPLETED")
        print("="*60)
        
        if self.downloaded_svgs:
            print(f"✅ Successfully downloaded {len(self.downloaded_svgs)} SVG files!")
            
            total_size = sum(svg['size_bytes'] for svg in self.downloaded_svgs)
            total_symbols = sum(svg.get('symbols_count', 0) for svg in self.downloaded_svgs)
            
            print(f"💾 Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
            print(f"🎯 Total icons/symbols: {total_symbols}")
            print(f"📁 Location: {self.output_dir.absolute()}")
            
            print(f"\n📋 Downloaded SVG files:")
            for i, svg in enumerate(self.downloaded_svgs, 1):
                print(f"{i:2d}. {svg['filename']}")
                print(f"     Source: {svg['url']}")
                print(f"     Size: {svg['size_bytes']:,} bytes")
                if svg.get('symbols_count', 0) > 0:
                    print(f"     Icons: {svg['symbols_count']} symbols")
                print()
        
        else:
            print("❌ No SVG files found")
        
        # Save comprehensive report
        report = {
            'download_completed': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url,
            'pages_scanned': list(self.visited_pages),
            'urls_tested': len(self.tested_urls),
            'svgs_downloaded': len(self.downloaded_svgs),
            'total_size_bytes': sum(svg['size_bytes'] for svg in self.downloaded_svgs) if self.downloaded_svgs else 0,
            'svg_files': self.downloaded_svgs
        }
        
        report_file = self.output_dir / 'comprehensive_svg_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Full report: {report_file}")
        print("="*60)

def main():
    # Target URL
    base_url = "https://admin.pixelstrap.net/mofi"
    
    downloader = ComprehensiveSVGDownloader(base_url)
    downloader.run_comprehensive_download()

if __name__ == "__main__":
    main()
