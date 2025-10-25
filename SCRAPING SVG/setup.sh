#!/bin/bash

echo "=================================="
echo "Web Scraper Setup & Installation"
echo "=================================="

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python3 not found! Please install Python 3.6 or higher."
    exit 1
fi

echo "✅ Python3 found!"

# Create virtual environment (optional)
read -p "Do you want to create a virtual environment? (y/N): " create_venv

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "✅ Virtual environment created and activated!"
    echo "To activate later, run: source venv/bin/activate"
fi

# Install dependencies
echo "Installing required packages..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies!"
    exit 1
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x web_scraper.py
chmod +x run_scraper.py
chmod +x analyze_downloads.py

echo "✅ Scripts are now executable!"

# Test basic functionality
echo "Testing basic functionality..."
python3 -c "
import requests
import bs4
import urllib.parse
print('✅ All modules imported successfully!')
"

if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Module import test failed!"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Quick start:"
echo "  python3 run_scraper.py --help"
echo "  python3 run_scraper.py --verbose"
echo ""
echo "Advanced usage:"
echo "  python3 run_scraper.py --url 'https://example.com' --output 'my_download'"
echo "  python3 run_scraper.py --workers 12 --extensions .html .css .js"
echo ""
