#!/usr/bin/env python3
"""
Simple SVG Finder - Cari dan download semua file SVG dari website
Focus pada detection dan download SVG files
"""

import os
import sys
import time
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import json

class SimpleSVGFinder:
    def __init__(self, base_url, output_dir="svg_results"):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.svg_dir = self.output_dir / "svg_files"
        self.svg_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
        self.found_svgs = set()
        self.downloaded_svgs = []
        self.visited_pages = set()
        
        print(f"🎨 SVG Finder initialized")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
    
    def find_svg_references(self, html_content, base_url):
        """Find all SVG references in HTML"""
        svg_urls = set()
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print(f"🔍 Scanning for SVG references...")
        
        # 1. Direct SVG tags and attributes
        selectors_and_attrs = [
            ('img', 'src'),
            ('image', 'href'),
            ('image', 'xlink:href'),
            ('use', 'href'),
            ('use', 'xlink:href'),
            ('link', 'href'),
            ('object', 'data'),
            ('embed', 'src'),
        ]
        
        for tag, attr in selectors_and_attrs:
            elements = soup.find_all(tag)
            for element in elements:
                url = element.get(attr, '').strip()
                if url and '.svg' in url:
                    clean_url = url.split('#')[0]  # Remove fragment
                    absolute_url = urljoin(base_url, clean_url)
                    if urlparse(absolute_url).netloc == self.domain:
                        svg_urls.add(absolute_url)
                        print(f"   Found in <{tag} {attr}>: {absolute_url}")
        
        # 2. CSS background-image
        style_elements = soup.find_all('style')
        for style in style_elements:
            css_content = style.get_text()
            svg_matches = re.findall(r'url\(["\']?([^"\']*\.svg[^"\']*)["\']?\)', css_content)
            for match in svg_matches:
                clean_url = match.split('#')[0]
                absolute_url = urljoin(base_url, clean_url)
                if urlparse(absolute_url).netloc == self.domain:
                    svg_urls.add(absolute_url)
                    print(f"   Found in CSS: {absolute_url}")
        
        # 3. Inline style attributes
        style_elements = soup.find_all(attrs={'style': True})
        for element in style_elements:
            style_attr = element.get('style', '')
            svg_matches = re.findall(r'url\(["\']?([^"\']*\.svg[^"\']*)["\']?\)', style_attr)
            for match in svg_matches:
                clean_url = match.split('#')[0]
                absolute_url = urljoin(base_url, clean_url)
                if urlparse(absolute_url).netloc == self.domain:
                    svg_urls.add(absolute_url)
                    print(f"   Found in style attr: {absolute_url}")
        
        # 4. JavaScript strings
        script_elements = soup.find_all('script')
        for script in script_elements:
            script_content = script.get_text()
            # Look for SVG file paths in quotes
            svg_matches = re.findall(r'["\']([^"\']*\.svg[^"\']*)["\']', script_content)
            for match in svg_matches:
                if '/' in match:  # Likely a path
                    clean_url = match.split('#')[0]
                    absolute_url = urljoin(base_url, clean_url)
                    if urlparse(absolute_url).netloc == self.domain:
                        svg_urls.add(absolute_url)
                        print(f"   Found in JS: {absolute_url}")
        
        # 5. Data attributes
        data_elements = soup.find_all(attrs=lambda x: x and any(key.startswith('data-') for key in x.keys()))
        for element in data_elements:
            for attr, value in element.attrs.items():
                if isinstance(value, str) and '.svg' in value:
                    clean_url = value.split('#')[0]
                    absolute_url = urljoin(base_url, clean_url)
                    if urlparse(absolute_url).netloc == self.domain:
                        svg_urls.add(absolute_url)
                        print(f"   Found in {attr}: {absolute_url}")
        
        # 6. Text search for common SVG patterns
        html_text = str(soup)
        common_patterns = [
            r'icon-sprite\.svg',
            r'icons?[-_][^"\']*\.svg',
            r'sprite[-_][^"\']*\.svg',
            r'/assets/[^"\']*\.svg',
            r'/svg/[^"\']*\.svg',
        ]
        
        for pattern in common_patterns:
            matches = re.findall(pattern, html_text, re.IGNORECASE)
            for match in matches:
                absolute_url = urljoin(base_url, match)
                if urlparse(absolute_url).netloc == self.domain:
                    svg_urls.add(absolute_url)
                    print(f"   Found by pattern: {absolute_url}")
        
        return list(svg_urls)
    
    def download_svg(self, svg_url):
        """Download SVG file"""
        try:
            print(f"📥 Downloading: {svg_url}")
            
            response = self.session.get(svg_url, timeout=10)
            response.raise_for_status()
            
            # Get filename
            url_path = urlparse(svg_url).path
            filename = Path(url_path).name
            if not filename or not filename.endswith('.svg'):
                filename = f"svg_{len(self.downloaded_svgs) + 1}.svg"
            
            # Handle duplicates
            svg_file = self.svg_dir / filename
            counter = 1
            original_stem = svg_file.stem
            while svg_file.exists():
                svg_file = self.svg_dir / f"{original_stem}_{counter}.svg"
                counter += 1
            
            # Save SVG
            with open(svg_file, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            
            # Save metadata
            metadata = {
                'original_url': svg_url,
                'filename': svg_file.name,
                'size_bytes': file_size,
                'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'content_type': response.headers.get('content-type', '')
            }
            
            with open(svg_file.with_suffix('.json'), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.downloaded_svgs.append(metadata)
            
            print(f"✅ Saved: {svg_file} ({file_size:,} bytes)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {svg_url}: {e}")
            return False
    
    def get_page_links(self, html_content, base_url):
        """Get links to other pages"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if href and not href.startswith(('#', 'javascript:', 'mailto:')):
                absolute_url = urljoin(base_url, href)
                if (urlparse(absolute_url).netloc == self.domain and
                    (absolute_url.endswith('.html') or '.' not in Path(urlparse(absolute_url).path).name)):
                    links.add(absolute_url)
        
        return list(links)
    
    def scan_website(self, max_pages=10):
        """Scan website untuk SVG files"""
        print(f"🚀 Starting SVG scan of {self.base_url}")
        
        to_visit = [self.base_url]
        pages_scanned = 0
        
        while to_visit and pages_scanned < max_pages:
            url = to_visit.pop(0)
            
            if url in self.visited_pages:
                continue
            
            try:
                print(f"\n🌐 Scanning page {pages_scanned + 1}: {url}")
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                self.visited_pages.add(url)
                pages_scanned += 1
                
                # Find SVG references
                svg_refs = self.find_svg_references(response.text, url)
                
                # Download SVGs
                for svg_url in svg_refs:
                    if svg_url not in self.found_svgs:
                        self.found_svgs.add(svg_url)
                        self.download_svg(svg_url)
                
                # Get more page links
                if pages_scanned < max_pages:
                    new_links = self.get_page_links(response.text, url)
                    for link in new_links[:5]:  # Limit new links
                        if link not in self.visited_pages:
                            to_visit.append(link)
                
                print(f"📊 Page summary: {len(svg_refs)} SVGs found on this page")
                
                time.sleep(0.5)  # Be nice to server
                
            except Exception as e:
                print(f"❌ Error scanning {url}: {e}")
        
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print final results"""
        print("\n" + "="*60)
        print("🎨 SVG SCANNING COMPLETED!")
        print("="*60)
        print(f"📄 Pages Scanned: {len(self.visited_pages)}")
        print(f"🎨 SVG Files Found: {len(self.found_svgs)}")
        print(f"📥 SVG Files Downloaded: {len(self.downloaded_svgs)}")
        
        if self.downloaded_svgs:
            total_size = sum(svg['size_bytes'] for svg in self.downloaded_svgs)
            print(f"💾 Total Size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
            print(f"📁 Location: {self.svg_dir.absolute()}")
            
            print(f"\n📋 Downloaded SVG Files:")
            for svg in self.downloaded_svgs:
                print(f"   • {svg['filename']} ({svg['size_bytes']:,} bytes)")
                print(f"     Source: {svg['original_url']}")
        
        # Save report
        report = {
            'scan_completed': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url,
            'pages_scanned': list(self.visited_pages),
            'svg_urls_found': list(self.found_svgs),
            'downloaded_svgs': self.downloaded_svgs,
            'summary': {
                'pages_count': len(self.visited_pages),
                'svgs_found': len(self.found_svgs),
                'svgs_downloaded': len(self.downloaded_svgs),
                'total_size_bytes': sum(svg['size_bytes'] for svg in self.downloaded_svgs) if self.downloaded_svgs else 0
            }
        }
        
        report_file = self.output_dir / 'svg_scan_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Report saved: {report_file}")
        print("="*60)

def main():
    print("🎨 Simple SVG Finder")
    print("="*50)
    
    # You can change these defaults
    target_url = "https://admin.pixelstrap.net/mofi/template/"
    output_dir = "svg_results"
    max_pages = 12
    
    finder = SimpleSVGFinder(target_url, output_dir)
    finder.scan_website(max_pages)

if __name__ == "__main__":
    main()
