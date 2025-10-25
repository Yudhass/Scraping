#!/usr/bin/env python3
"""
SVG URLs Cross-Check - Manual check semua kemungkinan lokasi SVG
"""

import requests
from urllib.parse import urljoin
import time

def test_svg_urls():
    """Test all possible SVG URLs"""
    
    base_url = "https://admin.pixelstrap.net/mofi"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    })
    
    print("🔍 TESTING ALL POSSIBLE SVG LOCATIONS")
    print("="*60)
    
    # All possible combinations
    directories = [
        "/assets/svg/",
        "/assets/icons/", 
        "/assets/images/svg/",
        "/assets/images/icons/",
        "/assets/img/svg/",
        "/assets/img/icons/",
        "/svg/",
        "/icons/",
        "/images/svg/",
        "/img/svg/",
        "/static/svg/",
        "/static/icons/",
        "/public/svg/",
        "/public/icons/",
        "/template/assets/svg/",
        "/template/assets/icons/",
        "/template/svg/",
        "/template/icons/"
    ]
    
    filenames = [
        "icon-sprite.svg",
        "icons.svg",
        "sprite.svg",
        "symbols.svg",
        "icon.svg",
        "fontawesome.svg",
        "feather.svg",
        "bootstrap-icons.svg",
        "material-icons.svg",
        "hero-icons.svg",
        "lucide.svg",
        "tabler-icons.svg",
        "phosphor.svg",
        "iconify.svg",
        "eva-icons.svg",
        "ant-design.svg",
        "carbon.svg",
        "logos.svg",
        "brands.svg",
        "social.svg",
        "ui.svg",
        "interface.svg",
        "system.svg",
        "outline.svg",
        "solid.svg",
        "line.svg",
        "fill.svg",
        "duotone.svg",
        "light.svg",
        "regular.svg",
        "bold.svg",
        "thin.svg"
    ]
    
    # Add numbered variants
    for i in range(1, 10):
        filenames.extend([
            f"icon-sprite{i}.svg",
            f"icons{i}.svg", 
            f"sprite{i}.svg",
            f"icon-sprite-{i}.svg",
            f"icons-{i}.svg",
            f"sprite-{i}.svg"
        ])
    
    found_svgs = []
    total_tests = len(directories) * len(filenames)
    current_test = 0
    
    print(f"🎯 Testing {total_tests} URLs...")
    print()
    
    for directory in directories:
        for filename in filenames:
            current_test += 1
            
            svg_url = base_url + directory + filename
            
            try:
                response = session.head(svg_url, timeout=5)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    print(f"✅ FOUND: {svg_url}")
                    print(f"   Content-Type: {content_type}")
                    
                    # Get file size
                    content_length = response.headers.get('content-length', 'Unknown')
                    print(f"   Size: {content_length} bytes")
                    
                    found_svgs.append({
                        'url': svg_url,
                        'content_type': content_type,
                        'size': content_length
                    })
                    print()
                    
                elif current_test % 100 == 0:
                    print(f"📊 Progress: {current_test}/{total_tests} tested...")
                    
            except Exception as e:
                if current_test % 200 == 0:
                    print(f"📊 Progress: {current_test}/{total_tests} tested...")
                continue
            
            # Small delay to be nice to server
            if current_test % 50 == 0:
                time.sleep(0.1)
    
    print(f"\n🎉 RESULTS:")
    print("="*60)
    print(f"📊 Total URLs tested: {total_tests}")
    print(f"✅ SVG files found: {len(found_svgs)}")
    
    if found_svgs:
        print(f"\n📋 FOUND SVG FILES:")
        for i, svg in enumerate(found_svgs, 1):
            print(f"{i}. {svg['url']}")
            print(f"   Type: {svg['content_type']}")
            print(f"   Size: {svg['size']} bytes")
            print()
            
        # Download all found SVGs
        print(f"📥 DOWNLOADING ALL FOUND SVGs...")
        for svg in found_svgs:
            download_svg(session, svg['url'])
    else:
        print("❌ No SVG files found in standard locations")
        print("💡 SVG files might be:")
        print("   • Embedded inline in HTML")
        print("   • Generated dynamically")
        print("   • In non-standard locations")
        print("   • Require authentication")

def download_svg(session, svg_url):
    """Download individual SVG"""
    try:
        response = session.get(svg_url, timeout=10)
        response.raise_for_status()
        
        from pathlib import Path
        from urllib.parse import urlparse
        
        # Create output directory
        output_dir = Path("found_svgs")
        output_dir.mkdir(exist_ok=True)
        
        # Get filename
        filename = Path(urlparse(svg_url).path).name
        svg_file = output_dir / filename
        
        # Handle duplicates
        counter = 1
        original_stem = svg_file.stem
        while svg_file.exists():
            svg_file = output_dir / f"{original_stem}_{counter}.svg"
            counter += 1
        
        # Save file
        with open(svg_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded: {svg_file}")
        
    except Exception as e:
        print(f"❌ Failed to download {svg_url}: {e}")

if __name__ == "__main__":
    test_svg_urls()
