#!/usr/bin/env python3
"""
Utilitas tambahan untuk analisis hasil scraping
"""

import os
import json
from pathlib import Path
from collections import defaultdict, Counter
import mimetypes

class ScrapingAnalyzer:
    def __init__(self, download_dir):
        self.download_dir = Path(download_dir)
        
    def analyze_downloaded_files(self):
        """Analisis file yang telah didownload"""
        if not self.download_dir.exists():
            print(f"Directory {self.download_dir} tidak ditemukan!")
            return
        
        file_stats = defaultdict(list)
        extension_counter = Counter()
        total_size = 0
        
        print("Menganalisis file yang didownload...")
        
        for file_path in self.download_dir.rglob("*"):
            if file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    extension = file_path.suffix.lower()
                    mime_type, _ = mimetypes.guess_type(str(file_path))
                    
                    file_stats[extension].append({
                        'path': str(file_path.relative_to(self.download_dir)),
                        'size': file_size,
                        'mime_type': mime_type
                    })
                    
                    extension_counter[extension] += 1
                    total_size += file_size
                    
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
        
        # Print summary
        print("\n" + "="*60)
        print("ANALISIS HASIL SCRAPING")
        print("="*60)
        print(f"Total files: {sum(extension_counter.values())}")
        print(f"Total size: {self.format_size(total_size)}")
        print(f"Directory: {self.download_dir.absolute()}")
        
        print("\nFile types:")
        for ext, count in extension_counter.most_common():
            ext_name = ext if ext else "(no extension)"
            total_ext_size = sum(f['size'] for f in file_stats[ext])
            print(f"  {ext_name}: {count} files ({self.format_size(total_ext_size)})")
        
        # Save detailed report
        self.save_detailed_report(file_stats, extension_counter, total_size)
        
        return file_stats, extension_counter, total_size
    
    def format_size(self, size_bytes):
        """Format ukuran file dalam format yang mudah dibaca"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def save_detailed_report(self, file_stats, extension_counter, total_size):
        """Simpan laporan detail ke file JSON"""
        report = {
            'summary': {
                'total_files': sum(extension_counter.values()),
                'total_size_bytes': total_size,
                'total_size_formatted': self.format_size(total_size),
                'file_types': dict(extension_counter)
            },
            'detailed_files': dict(file_stats)
        }
        
        report_file = self.download_dir / 'scraping_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed report saved to: {report_file}")
    
    def find_broken_links(self):
        """Cari file HTML dan cek link yang mungkin rusak"""
        broken_links = []
        
        for html_file in self.download_dir.rglob("*.html"):
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Check all links
                for tag in soup.find_all(['a', 'link', 'script', 'img']):
                    href = tag.get('href') or tag.get('src')
                    if href and not href.startswith(('http', 'https', 'mailto', 'javascript', '#')):
                        # This is a relative link
                        target_file = (html_file.parent / href).resolve()
                        if not target_file.exists():
                            broken_links.append({
                                'html_file': str(html_file.relative_to(self.download_dir)),
                                'broken_link': href,
                                'expected_path': str(target_file.relative_to(self.download_dir))
                            })
                            
            except Exception as e:
                print(f"Error checking {html_file}: {e}")
        
        if broken_links:
            print(f"\nFound {len(broken_links)} potentially broken links:")
            for link in broken_links[:10]:  # Show first 10
                print(f"  {link['html_file']} -> {link['broken_link']}")
            
            if len(broken_links) > 10:
                print(f"  ... and {len(broken_links) - 10} more")
        else:
            print("\n✓ No broken links found!")
        
        return broken_links

def main():
    """Main function untuk analisis"""
    import sys
    
    if len(sys.argv) > 1:
        download_dir = sys.argv[1]
    else:
        download_dir = "mofi_template_downloaded"
    
    analyzer = ScrapingAnalyzer(download_dir)
    
    print("Starting analysis...")
    file_stats, extension_counter, total_size = analyzer.analyze_downloaded_files()
    
    print("\nChecking for broken links...")
    broken_links = analyzer.find_broken_links()
    
    print("\n✓ Analysis completed!")

if __name__ == "__main__":
    main()
