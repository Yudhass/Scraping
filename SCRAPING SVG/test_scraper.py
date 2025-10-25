#!/usr/bin/env python3
"""
Quick test script untuk memverifikasi functionality scraper
"""

import sys
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time

def test_website_accessibility(url):
    """Test apakah website bisa diakses"""
    print(f"Testing accessibility of: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Website accessible! Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot access website: {e}")
        return None

def test_html_parsing(response):
    """Test parsing HTML untuk mencari links dan resources"""
    print("\nTesting HTML parsing...")
    
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Count various elements
        links = soup.find_all('a', href=True)
        css_links = soup.find_all('link', rel='stylesheet')
        js_scripts = soup.find_all('script', src=True)
        images = soup.find_all('img', src=True)
        
        print(f"✅ Found {len(links)} links")
        print(f"✅ Found {len(css_links)} CSS files")
        print(f"✅ Found {len(js_scripts)} JavaScript files")
        print(f"✅ Found {len(images)} images")
        
        # Show sample links
        if links:
            print("\nSample links found:")
            for link in links[:5]:
                href = link.get('href')
                text = link.get_text(strip=True)[:50]
                print(f"  - {href} ({text})")
        
        if css_links:
            print("\nCSS files found:")
            for css in css_links[:3]:
                print(f"  - {css.get('href')}")
        
        if js_scripts:
            print("\nJavaScript files found:")
            for js in js_scripts[:3]:
                print(f"  - {js.get('src')}")
                
        return True
        
    except Exception as e:
        print(f"❌ HTML parsing failed: {e}")
        return False

def test_resource_discovery(url, response):
    """Test penemuan resource dari halaman"""
    print("\nTesting resource discovery...")
    
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        base_url = url
        
        resources = []
        
        # Find all possible resources
        for tag in soup.find_all(['link', 'script', 'img', 'source']):
            src = tag.get('src') or tag.get('href')
            if src:
                absolute_url = urljoin(base_url, src)
                parsed = urlparse(absolute_url)
                
                if parsed.netloc == urlparse(base_url).netloc:  # Same domain
                    resources.append({
                        'url': absolute_url,
                        'type': tag.name,
                        'relative': src
                    })
        
        print(f"✅ Found {len(resources)} same-domain resources")
        
        # Group by type
        resource_types = {}
        for res in resources:
            res_type = res['type']
            if res_type not in resource_types:
                resource_types[res_type] = []
            resource_types[res_type].append(res)
        
        for res_type, items in resource_types.items():
            print(f"  - {res_type}: {len(items)} items")
            for item in items[:2]:  # Show first 2 of each type
                print(f"    {item['relative']}")
        
        return resources
        
    except Exception as e:
        print(f"❌ Resource discovery failed: {e}")
        return []

def test_sample_download(resources):
    """Test download sample resource"""
    if not resources:
        print("\nNo resources to test download")
        return
    
    print("\nTesting sample resource download...")
    
    # Find a small resource to test (CSS or small image)
    test_resource = None
    for res in resources:
        if res['url'].endswith(('.css', '.js', '.ico')):
            test_resource = res
            break
    
    if not test_resource:
        test_resource = resources[0]  # Use first available
    
    try:
        print(f"Testing download of: {test_resource['url']}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        start_time = time.time()
        response = requests.get(test_resource['url'], headers=headers, timeout=10)
        download_time = time.time() - start_time
        
        response.raise_for_status()
        
        print(f"✅ Download successful!")
        print(f"  Size: {len(response.content)} bytes")
        print(f"  Time: {download_time:.2f} seconds")
        print(f"  Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Download test failed: {e}")
        return False

def main():
    """Main test function"""
    print("="*60)
    print("WEB SCRAPER - QUICK TEST")
    print("="*60)
    
    # Default URL untuk test
    test_url = "https://admin.pixelstrap.net/mofi/template/"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    print(f"Testing URL: {test_url}")
    print("="*60)
    
    # Test 1: Website accessibility
    response = test_website_accessibility(test_url)
    if not response:
        print("\n❌ Basic connectivity test failed!")
        return 1
    
    # Test 2: HTML parsing
    if not test_html_parsing(response):
        print("\n❌ HTML parsing test failed!")
        return 1
    
    # Test 3: Resource discovery
    resources = test_resource_discovery(test_url, response)
    if not resources:
        print("\n⚠️ No resources found for download test")
    else:
        # Test 4: Sample download
        test_sample_download(resources)
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETED!")
    print("="*60)
    print("\nScraper should work properly. You can now run:")
    print("  python3 run_scraper.py --verbose")
    print("  python3 web_scraper.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
