#!/usr/bin/env python3
"""
Final Web Scraper - Mofi Template Complete Solution
Combined the best features from all scrapers
"""

import os
import sys
import argparse
import time
from pathlib import Path
import logging

# Import our scraper modules
try:
    from web_scraper import WebScraper
    from simple_scraper import download_page_and_resources
    from analyze_downloads import ScrapingAnalyzer
    from discover_urls import test_url_availability, discover_working_paths
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all scraper modules are in the same directory")
    sys.exit(1)

def setup_logging(verbose=False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('final_scraper.log')
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Main function with comprehensive options"""
    parser = argparse.ArgumentParser(
        description='🚀 Final Web Scraper - Mofi Template Complete Solution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick start - download main page and resources
  python3 final_scraper.py --mode simple
  
  # Full scraping with all pages (advanced)
  python3 final_scraper.py --mode advanced --workers 4
  
  # Test URLs first
  python3 final_scraper.py --mode discover
  
  # Analyze existing downloads
  python3 final_scraper.py --mode analyze --input simple_download
  
  # Custom URL and output
  python3 final_scraper.py --url "https://example.com" --output "my_site"
        """
    )
    
    # Main arguments
    parser.add_argument('--mode', '-m', 
                       choices=['simple', 'advanced', 'discover', 'analyze'],
                       default='simple',
                       help='Scraping mode (default: simple)')
    
    parser.add_argument('--url', '-u',
                       default='https://admin.pixelstrap.net/mofi/template/',
                       help='Target URL (default: Mofi template)')
    
    parser.add_argument('--output', '-o',
                       default='final_download',
                       help='Output directory (default: final_download)')
    
    parser.add_argument('--input', '-i',
                       help='Input directory for analysis mode')
    
    # Advanced options
    parser.add_argument('--workers', '-w',
                       type=int, default=4,
                       help='Number of worker threads (default: 4)')
    
    parser.add_argument('--delay',
                       type=float, default=1.0,
                       help='Delay between requests in seconds (default: 1.0)')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Verbose output')
    
    parser.add_argument('--extensions',
                       nargs='+',
                       help='Filter file extensions (e.g., .html .css .js)')
    
    parser.add_argument('--no-images',
                       action='store_true',
                       help='Skip image downloads')
    
    args = parser.parse_args()
    
    logger = setup_logging(args.verbose)
    
    print("="*70)
    print("🚀 FINAL WEB SCRAPER - MOFI TEMPLATE")
    print("="*70)
    print(f"Mode: {args.mode.upper()}")
    print(f"URL: {args.url}")
    if args.mode != 'analyze':
        print(f"Output: {args.output}")
    if args.input:
        print(f"Input: {args.input}")
    print("="*70)
    
    # Execute based on mode
    try:
        if args.mode == 'discover':
            logger.info("🔍 Running URL discovery...")
            working_paths = discover_working_paths(args.url)
            valid_urls, invalid_urls, all_urls = test_url_availability(args.url, max_test=30)
            
            if valid_urls:
                print(f"\n✅ Found {len(valid_urls)} valid URLs for scraping!")
                print("You can now run the scraper with confidence.")
            else:
                print("\n⚠️  No valid URLs found. The site might have restrictions.")
            
        elif args.mode == 'analyze':
            input_dir = args.input or args.output
            logger.info(f"📊 Analyzing downloads in: {input_dir}")
            
            analyzer = ScrapingAnalyzer(input_dir)
            analyzer.analyze_downloaded_files()
            analyzer.find_broken_links()
            
        elif args.mode == 'simple':
            logger.info("🎯 Running simple scraper (recommended)...")
            
            downloaded = download_page_and_resources(args.url, args.output)
            
            logger.info(f"\n✅ Simple scraping completed!")
            logger.info(f"Downloaded {len(downloaded)} files to: {args.output}")
            
            # Auto-analyze
            logger.info("\n📊 Running automatic analysis...")
            analyzer = ScrapingAnalyzer(args.output)
            analyzer.analyze_downloaded_files()
            
        elif args.mode == 'advanced':
            logger.info("⚡ Running advanced scraper...")
            
            scraper = WebScraper(
                base_url=args.url,
                download_dir=args.output,
                max_workers=args.workers
            )
            
            # Apply filters if specified
            if args.extensions:
                scraper.resource_extensions = set(args.extensions)
                logger.info(f"Filtering extensions: {args.extensions}")
            
            if args.no_images:
                image_exts = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', '.bmp'}
                scraper.resource_extensions -= image_exts
                logger.info("Images disabled")
            
            scraper.start_scraping()
            
            # Auto-analyze
            logger.info("\n📊 Running automatic analysis...")
            analyzer = ScrapingAnalyzer(args.output)
            analyzer.analyze_downloaded_files()
        
        # Final summary
        print("\n" + "="*70)
        print("🎉 SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        if args.mode in ['simple', 'advanced']:
            output_path = Path(args.output)
            if output_path.exists():
                file_count = len(list(output_path.rglob("*"))) - len(list(output_path.rglob("*/")))
                total_size = sum(f.stat().st_size for f in output_path.rglob("*") if f.is_file())
                
                print(f"📁 Output Directory: {output_path.absolute()}")
                print(f"📊 Files Downloaded: {file_count}")
                print(f"💾 Total Size: {total_size / (1024*1024):.2f} MB")
                
                # Quick recommendations
                print(f"\n💡 NEXT STEPS:")
                print(f"   • Open {args.output}/index.html in your browser")
                print(f"   • Check {args.output}/scraping_report.json for details")
                print(f"   • Run analysis: python3 final_scraper.py --mode analyze --input {args.output}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Scraping interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
