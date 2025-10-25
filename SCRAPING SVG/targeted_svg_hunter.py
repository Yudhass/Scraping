#!/usr/bin/env python3
"""
Targeted SVG Hunter - Langsung cek URL SVG yang diketahui dan scan lebih dalam
"""

import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import json

class TargetedSVGHunter:
    def __init__(self, output_dir="targeted_svg"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
        self.found_svgs = []
        
    def test_svg_url(self, svg_url):
        """Test apakah URL SVG bisa diakses"""
        try:
            print(f"🔍 Testing: {svg_url}")
            response = self.session.head(svg_url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"✅ Found SVG: {svg_url}")
                print(f"   Content-Type: {content_type}")
                return True
            else:
                print(f"❌ Not found ({response.status_code}): {svg_url}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing {svg_url}: {e}")
            return False
    
    def download_svg(self, svg_url):
        """Download SVG file"""
        try:
            print(f"📥 Downloading: {svg_url}")
            
            response = self.session.get(svg_url, timeout=15)
            response.raise_for_status()
            
            # Get filename
            filename = Path(urlparse(svg_url).path).name
            if not filename.endswith('.svg'):
                filename += '.svg'
            
            svg_file = self.output_dir / filename
            
            # Save SVG
            with open(svg_file, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            
            svg_info = {
                'url': svg_url,
                'filename': filename,
                'size_bytes': file_size,
                'content_type': response.headers.get('content-type', ''),
                'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.found_svgs.append(svg_info)
            
            print(f"✅ Saved: {svg_file} ({file_size:,} bytes)")
            
            # Also save a preview of content
            try:
                content_preview = response.text[:500] + "..." if len(response.text) > 500 else response.text
                print(f"📄 Content preview:\n{content_preview}")
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {svg_url}: {e}")
            return False
    
    def scan_page_for_svg_refs(self, page_url):
        """Scan halaman untuk referensi SVG"""
        try:
            print(f"\n🌐 Scanning page: {page_url}")
            
            response = self.session.get(page_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for any mention of SVG
            page_text = str(soup).lower()
            svg_mentions = []
            
            # Find any .svg mentions
            import re
            svg_patterns = [
                r'["\']([^"\']*\.svg[^"\']*)["\']',  # Quoted SVG paths
                r'src=["\']([^"\']*\.svg[^"\']*)["\']',  # src attributes
                r'href=["\']([^"\']*\.svg[^"\']*)["\']',  # href attributes
                r'url\(["\']?([^"\']*\.svg[^"\']*)["\']?\)',  # CSS url()
            ]
            
            for pattern in svg_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    if match and not match.startswith('#'):
                        absolute_url = urljoin(page_url, match)
                        svg_mentions.append(absolute_url)
            
            # Remove duplicates
            unique_svgs = list(set(svg_mentions))
            
            print(f"📄 Found {len(unique_svgs)} potential SVG references:")
            for svg_url in unique_svgs:
                print(f"   • {svg_url}")
            
            return unique_svgs
            
        except Exception as e:
            print(f"❌ Error scanning {page_url}: {e}")
            return []
    
    def hunt_known_svgs(self):
        """Hunt for known SVG locations"""
        print("🎯 TARGETED SVG HUNTING")
        print("="*50)
        
        base_url = "https://admin.pixelstrap.net/mofi"
        
        # Known SVG patterns and locations
        known_svg_urls = [
            f"{base_url}/assets/svg/icon-sprite.svg",
            f"{base_url}/assets/svg/icons.svg",
            f"{base_url}/assets/svg/sprite.svg",
            f"{base_url}/assets/images/icons.svg",
            f"{base_url}/assets/images/icon-sprite.svg",
            f"{base_url}/assets/icons/icon-sprite.svg",
            f"{base_url}/assets/icons/icons.svg",
        ]
        
        # Test each known URL
        print(f"\n1️⃣ Testing known SVG locations...")
        for svg_url in known_svg_urls:
            if self.test_svg_url(svg_url):
                self.download_svg(svg_url)
        
        # Scan specific pages
        print(f"\n2️⃣ Scanning pages for SVG references...")
        pages_to_scan = [
            "https://admin.pixelstrap.net/mofi/template/",
            "https://admin.pixelstrap.net/mofi/template/index.html",
            "https://admin.pixelstrap.net/mofi/template/general-widget.html",
            "https://admin.pixelstrap.net/mofi/template/form-wizard.html",
        ]
        
        all_found_svgs = set()
        
        for page_url in pages_to_scan:
            try:
                svg_refs = self.scan_page_for_svg_refs(page_url)
                all_found_svgs.update(svg_refs)
                time.sleep(0.5)
            except Exception as e:
                print(f"❌ Error scanning {page_url}: {e}")
        
        # Test and download found SVGs
        print(f"\n3️⃣ Testing discovered SVG references...")
        for svg_url in all_found_svgs:
            if svg_url not in [svg['url'] for svg in self.found_svgs]:
                if self.test_svg_url(svg_url):
                    self.download_svg(svg_url)
        
        # Try directory listing approach
        print(f"\n4️⃣ Trying common SVG directories...")
        svg_directories = [
            f"{base_url}/assets/svg/",
            f"{base_url}/assets/icons/",
            f"{base_url}/assets/images/svg/",
        ]
        
        for dir_url in svg_directories:
            try:
                print(f"🔍 Checking directory: {dir_url}")
                response = self.session.get(dir_url, timeout=10)
                if response.status_code == 200:
                    # Try to parse directory listing
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        if href.endswith('.svg'):
                            svg_url = urljoin(dir_url, href)
                            if self.test_svg_url(svg_url):
                                self.download_svg(svg_url)
            except Exception as e:
                print(f"❌ Error checking directory {dir_url}: {e}")
        
        self.print_results()
    
    def print_results(self):
        """Print final results"""
        print("\n" + "="*60)
        print("🎨 SVG HUNTING RESULTS")
        print("="*60)
        
        if self.found_svgs:
            print(f"✅ Found {len(self.found_svgs)} SVG files!")
            total_size = sum(svg['size_bytes'] for svg in self.found_svgs)
            print(f"💾 Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
            print(f"📁 Location: {self.output_dir.absolute()}")
            
            print(f"\n📋 Downloaded SVG files:")
            for i, svg in enumerate(self.found_svgs, 1):
                print(f"{i}. {svg['filename']}")
                print(f"   Source: {svg['url']}")
                print(f"   Size: {svg['size_bytes']:,} bytes")
                print(f"   Type: {svg['content_type']}")
                print()
        else:
            print("❌ No SVG files found")
            print("💡 The website might not have SVG files, or they might be:")
            print("   • Embedded inline in HTML")
            print("   • Generated dynamically by JavaScript")
            print("   • Protected by authentication")
            print("   • Located in non-standard directories")
        
        # Save report
        report = {
            'hunt_completed': time.strftime('%Y-%m-%d %H:%M:%S'),
            'svgs_found': len(self.found_svgs),
            'total_size_bytes': sum(svg['size_bytes'] for svg in self.found_svgs) if self.found_svgs else 0,
            'svg_files': self.found_svgs
        }
        
        report_file = self.output_dir / 'svg_hunt_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Report saved: {report_file}")
        print("="*60)

def main():
    hunter = TargetedSVGHunter()
    hunter.hunt_known_svgs()

if __name__ == "__main__":
    main()
