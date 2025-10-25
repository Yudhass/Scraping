#!/usr/bin/env python3
"""
Script runner untuk Web Scraper dengan berbagai opsi
"""

import argparse
import sys
from pathlib import Path
from web_scraper import WebScraper
from analyze_downloads import ScrapingAnalyzer

def main():
    parser = argparse.ArgumentParser(description='Web Scraper untuk Mofi Template')
    
    # Basic arguments
    parser.add_argument('--url', '-u', 
                       default='https://admin.pixelstrap.net/mofi/template/',
                       help='Base URL untuk scraping (default: Mofi template)')
    
    parser.add_argument('--output', '-o',
                       default='mofi_template_downloaded',
                       help='Directory output untuk menyimpan file (default: mofi_template_downloaded)')
    
    parser.add_argument('--workers', '-w',
                       type=int, default=8,
                       help='Jumlah worker threads (default: 8)')
    
    parser.add_argument('--analyze', '-a',
                       action='store_true',
                       help='Hanya analisis hasil download tanpa scraping')
    
    parser.add_argument('--depth', '-d',
                       type=int, default=None,
                       help='Kedalaman maksimum scraping (default: unlimited)')
    
    parser.add_argument('--delay', 
                       type=float, default=0.5,
                       help='Delay antar request dalam detik (default: 0.5)')
    
    parser.add_argument('--extensions',
                       nargs='+',
                       default=None,
                       help='Filter ekstensi file yang akan didownload (contoh: .html .css .js)')
    
    parser.add_argument('--exclude-extensions',
                       nargs='+',
                       default=[],
                       help='Ekstensi file yang akan diabaikan')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Output verbose')
    
    args = parser.parse_args()
    
    # Setup output directory
    output_path = Path(args.output)
    
    print("="*70)
    print("WEB SCRAPER - ADVANCED MODE")
    print("="*70)
    print(f"Target URL: {args.url}")
    print(f"Output Directory: {output_path.absolute()}")
    print(f"Workers: {args.workers}")
    if args.depth:
        print(f"Max Depth: {args.depth}")
    print(f"Request Delay: {args.delay}s")
    if args.extensions:
        print(f"Include Extensions: {', '.join(args.extensions)}")
    if args.exclude_extensions:
        print(f"Exclude Extensions: {', '.join(args.exclude_extensions)}")
    print("="*70)
    
    if args.analyze:
        # Hanya analisis
        print("Running analysis only...")
        analyzer = ScrapingAnalyzer(args.output)
        analyzer.analyze_downloaded_files()
        analyzer.find_broken_links()
        return 0
    
    # Konfirmasi sebelum mulai
    if not args.verbose:
        response = input("\nProceed with scraping? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Scraping cancelled.")
            return 1
    
    # Start scraping
    try:
        scraper = WebScraper(
            base_url=args.url,
            download_dir=str(output_path),
            max_workers=args.workers
        )
        
        # Apply custom settings if provided
        if args.extensions:
            # Filter untuk hanya extension tertentu
            scraper.resource_extensions = set(args.extensions)
            scraper.html_extensions = set(ext for ext in args.extensions if ext in {'.html', '.htm', '.php'})
        
        if args.exclude_extensions:
            # Hapus extension yang dikecualikan
            for ext in args.exclude_extensions:
                scraper.resource_extensions.discard(ext)
                scraper.html_extensions.discard(ext)
        
        scraper.start_scraping()
        
        print("\n" + "="*50)
        print("✓ SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*50)
        
        # Auto-analyze hasil
        print("\nRunning automatic analysis...")
        analyzer = ScrapingAnalyzer(args.output)
        analyzer.analyze_downloaded_files()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n✗ Error during scraping: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
