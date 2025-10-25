#!/usr/bin/env python3
"""
Compare Results dari semua scraper yang telah dibuat
"""

import os
import json
from pathlib import Path

def analyze_download_folder(folder_path):
    """Analyze isi download folder"""
    folder = Path(folder_path)
    if not folder.exists():
        return None
    
    stats = {
        'total_size': 0,
        'html_files': 0,
        'css_files': 0,
        'js_files': 0,
        'image_files': 0,
        'other_files': 0,
        'total_files': 0
    }
    
    # Count files
    for file_path in folder.rglob('*'):
        if file_path.is_file():
            stats['total_files'] += 1
            stats['total_size'] += file_path.stat().st_size
            
            suffix = file_path.suffix.lower()
            if suffix == '.html':
                stats['html_files'] += 1
            elif suffix == '.css':
                stats['css_files'] += 1
            elif suffix == '.js':
                stats['js_files'] += 1
            elif suffix in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']:
                stats['image_files'] += 1
            else:
                stats['other_files'] += 1
    
    return stats

def load_report(report_path):
    """Load JSON report jika ada"""
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def format_size(size_bytes):
    """Format size dalam MB"""
    return f"{size_bytes / (1024*1024):.2f} MB"

def main():
    """Compare semua hasil scraping"""
    print("="*80)
    print("📊 COMPARISON OF ALL SCRAPING RESULTS")
    print("="*80)
    
    scrapers = [
        {
            'name': 'Simple Scraper',
            'folder': 'simple_download',
            'report': 'simple_download/scraping_report.json'
        },
        {
            'name': 'Demo Final (Advanced)',
            'folder': 'demo_final',
            'report': 'demo_final/scraping_report.json'
        },
        {
            'name': 'Final Download',
            'folder': 'final_download',
            'report': 'final_download/scraping_report.json'
        },
        {
            'name': 'Hybrid Scraper (Selenium)',
            'folder': 'hybrid_download',
            'report': 'hybrid_download/hybrid_crawling_report.json'
        }
    ]
    
    results = []
    
    for scraper in scrapers:
        print(f"\n🔍 Analyzing {scraper['name']}...")
        
        # Analyze folder
        stats = analyze_download_folder(scraper['folder'])
        
        if stats is None:
            print(f"   ❌ Folder {scraper['folder']} not found")
            continue
        
        # Load report
        report = load_report(scraper['report'])
        
        result = {
            'name': scraper['name'],
            'stats': stats,
            'report': report
        }
        results.append(result)
        
        # Print stats
        print(f"   📁 Total Files: {stats['total_files']}")
        print(f"   📄 HTML Files: {stats['html_files']}")
        print(f"   🎨 CSS Files: {stats['css_files']}")
        print(f"   ⚡ JS Files: {stats['js_files']}")
        print(f"   🖼️  Images: {stats['image_files']}")
        print(f"   📦 Total Size: {format_size(stats['total_size'])}")
        
        if report and 'statistics' in report:
            rep_stats = report['statistics']
            if 'pages_visited' in rep_stats:
                print(f"   🌐 Pages Visited: {rep_stats['pages_visited']}")
            if 'assets_downloaded' in rep_stats:
                print(f"   📥 Assets Downloaded: {rep_stats['assets_downloaded']}")
    
    # Summary comparison
    print("\n" + "="*80)
    print("📋 SUMMARY COMPARISON")
    print("="*80)
    
    print(f"{'Scraper':<25} {'Files':<8} {'Size':<10} {'HTML':<6} {'Assets':<8} {'Method'}")
    print("-" * 80)
    
    for result in results:
        stats = result['stats']
        report = result['report']
        
        method = "Unknown"
        if report and 'method_used' in report:
            method = report['method_used']
        elif report and 'statistics' in report and 'method_used' in report['statistics']:
            method = report['statistics']['method_used']
        elif 'Simple' in result['name']:
            method = "Requests"
        elif 'Hybrid' in result['name']:
            method = "Selenium + Requests"
        
        assets = stats['total_files'] - stats['html_files']
        
        print(f"{result['name']:<25} {stats['total_files']:<8} {format_size(stats['total_size']):<10} "
              f"{stats['html_files']:<6} {assets:<8} {method}")
    
    # Best result
    if results:
        best_coverage = max(results, key=lambda x: x['stats']['html_files'])
        best_assets = max(results, key=lambda x: x['stats']['total_files'] - x['stats']['html_files'])
        largest = max(results, key=lambda x: x['stats']['total_size'])
        
        print(f"\n🏆 BEST RESULTS:")
        print(f"   📄 Most HTML Pages: {best_coverage['name']} ({best_coverage['stats']['html_files']} pages)")
        print(f"   📦 Most Assets: {best_assets['name']} ({best_assets['stats']['total_files'] - best_assets['stats']['html_files']} assets)")
        print(f"   💾 Largest Download: {largest['name']} ({format_size(largest['stats']['total_size'])})")
    
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS:")
    print("="*80)
    print("🌟 For COMPREHENSIVE scraping (multiple pages): Use Hybrid Scraper")
    print("🎯 For SINGLE PAGE + assets: Use Simple Scraper")  
    print("⚡ For SPEED: Use Simple Scraper")
    print("🧠 For JAVASCRIPT-heavy sites: Use Hybrid Scraper (Selenium)")
    print("🔒 For AUTHENTICATED content: Use Hybrid Scraper")
    print("="*80)

if __name__ == "__main__":
    main()
