#!/usr/bin/env python3
"""
URL Discovery Script - Mencari URL yang valid sebelum scraping
"""

import requests
import sys
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from collections import defaultdict

def test_url_availability(base_url, max_test=50):
    """Test availability beberapa URL untuk menemukan pattern yang benar"""
    print(f"🔍 Testing URL availability from: {base_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    # Dapatkan halaman utama
    try:
        response = session.get(base_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ambil semua link dari halaman utama
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href and not href.startswith(('#', 'javascript:', 'mailto:')):
                absolute_url = urljoin(base_url, href)
                if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                    links.append(absolute_url)
        
        # Remove duplicates
        unique_links = list(set(links))
        print(f"Found {len(unique_links)} unique same-domain links")
        
        # Test beberapa URL untuk melihat mana yang valid
        valid_urls = []
        invalid_urls = []
        
        test_count = min(max_test, len(unique_links))
        print(f"\n📡 Testing {test_count} URLs for availability...")
        
        for i, url in enumerate(unique_links[:test_count]):
            try:
                print(f"  [{i+1}/{test_count}] Testing: {url}")
                test_response = session.head(url, timeout=5)
                
                if test_response.status_code == 200:
                    valid_urls.append(url)
                    print(f"    ✅ VALID (200)")
                elif test_response.status_code == 404:
                    invalid_urls.append(url)
                    print(f"    ❌ NOT FOUND (404)")
                else:
                    print(f"    ⚠️  OTHER ({test_response.status_code})")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                invalid_urls.append(url)
                print(f"    ❌ ERROR: {str(e)[:50]}")
        
        # Analisis hasil
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"✅ Valid URLs: {len(valid_urls)}")
        print(f"❌ Invalid URLs: {len(invalid_urls)}")
        
        if valid_urls:
            print(f"\n✅ VALID URLs (first 10):")
            for url in valid_urls[:10]:
                print(f"  - {url}")
        
        if invalid_urls:
            print(f"\n❌ INVALID URLs (first 10):")
            for url in invalid_urls[:10]:
                print(f"  - {url}")
        
        # Analisis pattern
        print(f"\n🔍 URL PATTERN ANALYSIS:")
        pattern_analysis = defaultdict(list)
        
        for url in valid_urls:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) > 0:
                pattern_analysis[path_parts[0]].append(url)
        
        for pattern, urls in pattern_analysis.items():
            print(f"  Pattern '/{pattern}/': {len(urls)} valid URLs")
        
        return valid_urls, invalid_urls, unique_links
        
    except Exception as e:
        print(f"❌ Error accessing {base_url}: {e}")
        return [], [], []

def discover_working_paths(base_url):
    """Mencoba beberapa path umum untuk menemukan yang bekerja"""
    common_paths = [
        '',           # root
        'index.html',
        'dashboard.html',
        'template/',
        'demo/',
        'html/',
        'dist/',
        'assets/',
        'css/',
        'js/',
        'images/',
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    working_paths = []
    
    print(f"\n🔍 Discovering working paths from: {base_url}")
    
    for path in common_paths:
        try:
            test_url = urljoin(base_url, path)
            response = requests.head(test_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                working_paths.append(test_url)
                print(f"  ✅ {test_url}")
            else:
                print(f"  ❌ {test_url} ({response.status_code})")
                
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  ❌ {test_url} (ERROR: {str(e)[:30]})")
    
    return working_paths

def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "https://admin.pixelstrap.net/mofi/template/"
    
    print("="*70)
    print("🔍 URL DISCOVERY & VALIDATION TOOL")
    print("="*70)
    print(f"Target: {base_url}")
    print("="*70)
    
    # Step 1: Discover working paths
    working_paths = discover_working_paths(base_url)
    
    # Step 2: Test URL availability from main page
    valid_urls, invalid_urls, all_urls = test_url_availability(base_url, max_test=30)
    
    # Step 3: Recommendations
    print("\n" + "="*70)
    print("📋 RECOMMENDATIONS")
    print("="*70)
    
    if working_paths:
        print("✅ Working base paths found:")
        for path in working_paths:
            print(f"  - {path}")
        print("\nYou can try scraping from these working paths.")
    else:
        print("❌ No working base paths found.")
    
    if valid_urls:
        print(f"\n✅ Found {len(valid_urls)} valid URLs to scrape.")
        print("You can modify the scraper to only target these valid URLs.")
    else:
        print("\n❌ No valid URLs found from the main page.")
        print("The website might be using dynamic content or have access restrictions.")
    
    # Generate focused scraper command
    if valid_urls:
        print(f"\n💡 SUGGESTED SCRAPER COMMANDS:")
        print(f"   # Conservative approach (fewer workers, more delay)")
        print(f"   python3 run_scraper.py --url '{base_url}' --workers 2 --delay 2")
        print(f"   ")
        print(f"   # HTML only")
        print(f"   python3 run_scraper.py --url '{base_url}' --extensions .html")
    
    return 0 if valid_urls else 1

if __name__ == "__main__":
    sys.exit(main())
