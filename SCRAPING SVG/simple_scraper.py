#!/usr/bin/env python3
"""
Simple Web Scraper yang lebih konservatif dan targeted
"""

import os
import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pathlib import Path
import logging

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('simple_scraper.log')
        ]
    )
    return logging.getLogger(__name__)

def download_page_and_resources(url, download_dir):
    """Download halaman dan resource yang ada di dalamnya"""
    logger = setup_logging()
    download_path = Path(download_dir)
    download_path.mkdir(exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    downloaded_files = []
    
    try:
        # Download halaman utama
        logger.info(f"Downloading main page: {url}")
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Simpan halaman utama
        main_file = download_path / "index.html"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        downloaded_files.append(str(main_file))
        logger.info(f"✅ Saved: {main_file}")
        
        # Parse HTML untuk mencari resource
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari CSS files
        css_links = soup.find_all('link', rel='stylesheet')
        logger.info(f"Found {len(css_links)} CSS files")
        
        for link in css_links:
            href = link.get('href')
            if href:
                css_url = urljoin(url, href)
                if download_resource(session, css_url, download_path, 'css'):
                    downloaded_files.append(css_url)
        
        # Mencari JavaScript files
        js_scripts = soup.find_all('script', src=True)
        logger.info(f"Found {len(js_scripts)} JavaScript files")
        
        for script in js_scripts:
            src = script.get('src')
            if src:
                js_url = urljoin(url, src)
                if download_resource(session, js_url, download_path, 'js'):
                    downloaded_files.append(js_url)
        
        # Mencari images
        images = soup.find_all('img', src=True)
        logger.info(f"Found {len(images)} images")
        
        for img in images:
            src = img.get('src')
            if src:
                img_url = urljoin(url, src)
                if download_resource(session, img_url, download_path, 'images'):
                    downloaded_files.append(img_url)
        
        # Mencari favicon dan icons
        favicons = soup.find_all('link', rel=['icon', 'shortcut icon', 'apple-touch-icon'])
        logger.info(f"Found {len(favicons)} favicon/icon files")
        
        for favicon in favicons:
            href = favicon.get('href')
            if href:
                icon_url = urljoin(url, href)
                if download_resource(session, icon_url, download_path, 'icons'):
                    downloaded_files.append(icon_url)
        
        logger.info(f"\n✅ Download completed! Total files: {len(downloaded_files)}")
        logger.info(f"Files saved to: {download_path.absolute()}")
        
        return downloaded_files
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return downloaded_files

def download_resource(session, url, base_path, resource_type):
    """Download single resource"""
    logger = logging.getLogger(__name__)
    
    try:
        # Skip external domains (Google Fonts, CDNs, etc.)
        if not is_same_domain(url, "admin.pixelstrap.net"):
            logger.info(f"⏭️  Skipping external: {url}")
            return False
        
        logger.info(f"📥 Downloading {resource_type}: {url}")
        
        response = session.get(url, timeout=15, stream=True)
        
        if response.status_code == 404:
            logger.warning(f"⚠️  Not found (404): {url}")
            return False
        
        response.raise_for_status()
        
        # Tentukan path file
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        # Buat struktur directory
        file_dir = base_path
        for part in path_parts[:-1]:
            if part:
                file_dir = file_dir / part
        
        file_dir.mkdir(parents=True, exist_ok=True)
        
        # Nama file
        filename = path_parts[-1] if path_parts[-1] else 'index.html'
        file_path = file_dir / filename
        
        # Download file
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"✅ Saved: {file_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"⚠️  Failed to download {url}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error downloading {url}: {e}")
        return False

def is_same_domain(url, target_domain):
    """Check if URL is from the same domain"""
    parsed = urlparse(url)
    return target_domain in parsed.netloc

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://admin.pixelstrap.net/mofi/template/"
    
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = "simple_download"
    
    print("="*60)
    print("🚀 SIMPLE WEB SCRAPER")
    print("="*60)
    print(f"URL: {url}")
    print(f"Output: {output_dir}")
    print("="*60)
    
    downloaded = download_page_and_resources(url, output_dir)
    
    print(f"\n🎉 Scraping completed!")
    print(f"📁 Check the '{output_dir}' directory")
    print(f"📊 Total downloads: {len(downloaded)}")

if __name__ == "__main__":
    main()
