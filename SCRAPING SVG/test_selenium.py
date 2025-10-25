#!/usr/bin/env python3
"""
Test script untuk memastikan Selenium dan ChromeDriver bekerja
"""

import sys
import time

def test_selenium():
    """Test apakah Selenium bisa jalan"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("✅ Selenium import berhasil")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        print("🚗 Mencoba initialize ChromeDriver...")
        
        # Try to create driver
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ ChromeDriver berhasil diinisialisasi")
        
        # Test navigasi
        print("🌐 Testing navigasi ke Google...")
        driver.get("https://www.google.com")
        
        title = driver.title
        print(f"📄 Page title: {title}")
        
        driver.quit()
        print("✅ Test berhasil! Selenium siap digunakan")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error import Selenium: {e}")
        print("💡 Install dengan: pip3 install selenium")
        return False
        
    except Exception as e:
        print(f"❌ Error dengan ChromeDriver: {e}")
        print("💡 Possible solutions:")
        print("   1. Install ChromeDriver: sudo apt install chromium-chromedriver")
        print("   2. Or install Chrome: wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
        print("   3. Download ChromeDriver manually from: https://chromedriver.chromium.org/")
        return False

def check_alternatives():
    """Check alternatif browser lain"""
    print("\n🔍 Checking browser alternatives...")
    
    import subprocess
    
    browsers = [
        ('chromium-browser', 'Chromium'),
        ('google-chrome', 'Google Chrome'),
        ('firefox', 'Firefox'),
    ]
    
    for cmd, name in browsers:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {name} available: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"❌ {name} not found")

if __name__ == "__main__":
    print("🧪 Testing Selenium WebDriver Setup")
    print("=" * 50)
    
    success = test_selenium()
    
    if not success:
        check_alternatives()
        print("\n💡 Jika ChromeDriver tidak tersedia, coba install manual:")
        print("   wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip")
        print("   unzip chromedriver_linux64.zip")
        print("   sudo mv chromedriver /usr/local/bin/")
        print("   sudo chmod +x /usr/local/bin/chromedriver")
    
    sys.exit(0 if success else 1)
