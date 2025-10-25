#!/bin/bash

echo "🚀 Setting up Enhanced Web Scraper dengan Selenium"
echo "=================================================="

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install Chrome/Chromium browser
echo "🌐 Installing Chromium browser..."
sudo apt install -y chromium-browser

# Install ChromeDriver
echo "🚗 Installing ChromeDriver..."
sudo apt install -y chromium-chromedriver

# Alternative: Download latest ChromeDriver manually
# echo "📥 Downloading latest ChromeDriver..."
# CHROME_VERSION=$(chromium-browser --version | grep -oP "\d+\.\d+\.\d+")
# wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}/chromedriver_linux64.zip"
# sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
# sudo chmod +x /usr/local/bin/chromedriver

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r enhanced_requirements.txt

# Test ChromeDriver installation
echo "🧪 Testing ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver installed successfully!"
    chromedriver --version
else
    echo "❌ ChromeDriver not found. Please install manually:"
    echo "   sudo apt install chromium-chromedriver"
fi

# Test Chromium installation
echo "🧪 Testing Chromium..."
if command -v chromium-browser &> /dev/null; then
    echo "✅ Chromium installed successfully!"
    chromium-browser --version
else
    echo "❌ Chromium not found. Please install manually:"
    echo "   sudo apt install chromium-browser"
fi

echo ""
echo "🎉 Setup completed!"
echo "💡 Usage examples:"
echo "   python3 enhanced_scraper.py"
echo "   python3 enhanced_scraper.py --max-pages 50"
echo "   python3 enhanced_scraper.py --no-headless  # Show browser"
echo ""
