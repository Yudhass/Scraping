#!/usr/bin/env python3
"""
Final SVG Analysis - Analyze all downloaded SVG files
"""

import re
import json
from pathlib import Path
import time

def analyze_all_svgs():
    """Analyze all downloaded SVG files"""
    
    print("🎨 FINAL SVG ANALYSIS - ALL DOWNLOADED FILES")
    print("="*70)
    
    # Find all SVG files
    svg_files = []
    for svg_file in Path(".").rglob("*.svg"):
        if svg_file.is_file():
            svg_files.append(svg_file)
    
    print(f"📁 Found {len(svg_files)} SVG files total")
    print()
    
    # Group by unique content (same file downloaded multiple times)
    unique_svgs = {}
    
    for svg_file in svg_files:
        try:
            file_size = svg_file.stat().st_size
            
            # Read content to check if it's unique
            with open(svg_file, 'r', encoding='utf-8') as f:
                content = f.read()[:1000]  # First 1000 chars for comparison
            
            # Create key based on size and content start
            key = f"{file_size}_{hash(content)}"
            
            if key not in unique_svgs:
                unique_svgs[key] = {
                    'files': [],
                    'size': file_size,
                    'content_preview': content[:200]
                }
            
            unique_svgs[key]['files'].append(str(svg_file))
            
        except Exception as e:
            print(f"❌ Error reading {svg_file}: {e}")
    
    print(f"🎯 Unique SVG files: {len(unique_svgs)}")
    print()
    
    # Analyze each unique SVG
    total_icons = 0
    svg_analysis = []
    
    for i, (key, info) in enumerate(unique_svgs.items(), 1):
        main_file = info['files'][0]
        file_size = info['size']
        
        print(f"{i}. ANALYZING: {Path(main_file).name}")
        print(f"   📁 Locations: {len(info['files'])} copies")
        print(f"   📏 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Analyze content
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = analyze_svg_content(content, main_file)
            svg_analysis.append(analysis)
            total_icons += analysis.get('total_icons', 0)
            
            print(f"   🎯 Icons/Symbols: {analysis.get('total_icons', 0)}")
            print(f"   📄 Type: {analysis.get('svg_type', 'Unknown')}")
            print(f"   📝 Description: {analysis.get('description', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
        
        print()
    
    # Final summary
    print("="*70)
    print("🎉 FINAL SVG DOWNLOAD SUMMARY")
    print("="*70)
    print(f"📊 STATISTICS:")
    print(f"   📁 Total SVG files found: {len(svg_files)}")
    print(f"   🎯 Unique SVG files: {len(unique_svgs)}")
    print(f"   🎨 Total icons available: {total_icons:,}")
    
    total_size = sum(info['size'] for info in unique_svgs.values())
    print(f"   💾 Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    print(f"\n📋 UNIQUE SVG FILES:")
    for analysis in svg_analysis:
        print(f"   • {analysis['filename']}")
        print(f"     Icons: {analysis.get('total_icons', 0):,}")
        print(f"     Type: {analysis.get('svg_type', 'Unknown')}")
        if analysis.get('sample_icons'):
            sample = analysis['sample_icons'][:5]
            print(f"     Sample: {', '.join(sample)}")
        print()
    
    # Save final report
    final_report = {
        'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'summary': {
            'total_svg_files': len(svg_files),
            'unique_svg_files': len(unique_svgs),
            'total_icons': total_icons,
            'total_size_bytes': total_size,
            'total_size_kb': round(total_size/1024, 1)
        },
        'svg_files': svg_analysis
    }
    
    with open('FINAL_SVG_ANALYSIS.json', 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Complete analysis saved: FINAL_SVG_ANALYSIS.json")
    print("="*70)
    
    return svg_analysis

def analyze_svg_content(content, filepath):
    """Analyze individual SVG content"""
    
    filename = Path(filepath).name
    analysis = {
        'filename': filename,
        'filepath': str(filepath)
    }
    
    # Detect SVG type
    if '<font' in content and 'glyph' in content:
        # Font SVG
        analysis['svg_type'] = 'Font SVG'
        analysis['description'] = 'SVG font file with glyph definitions'
        
        # Count glyphs
        glyph_count = len(re.findall(r'<glyph', content, re.IGNORECASE))
        analysis['total_icons'] = glyph_count
        
        # Extract glyph names
        glyph_names = re.findall(r'glyph-name="([^"]+)"', content)
        analysis['sample_icons'] = glyph_names[:10]
        
        # Check if it's FontAwesome
        if 'fontawesome' in filename.lower() or 'FontAwesome' in content:
            analysis['description'] = 'FontAwesome SVG font file'
            analysis['library'] = 'FontAwesome'
    
    elif '<symbol' in content:
        # Symbol sprite
        analysis['svg_type'] = 'Symbol Sprite'
        analysis['description'] = 'SVG sprite with symbol definitions'
        
        # Count symbols
        symbol_count = len(re.findall(r'<symbol', content, re.IGNORECASE))
        analysis['total_icons'] = symbol_count
        
        # Extract symbol IDs
        symbol_ids = re.findall(r'<symbol\s+id="([^"]+)"', content, re.IGNORECASE)
        analysis['sample_icons'] = symbol_ids[:10]
        
        # Check if it's icon sprite
        if 'icon' in filename.lower() or 'sprite' in filename.lower():
            analysis['description'] = 'Custom icon sprite'
            analysis['library'] = 'Custom Icons'
    
    elif '<path' in content or '<circle' in content or '<rect' in content:
        # Single icon or simple SVG
        analysis['svg_type'] = 'Single Icon/Graphic'
        analysis['description'] = 'Individual SVG graphic or icon'
        analysis['total_icons'] = 1
        
        # Count graphic elements
        paths = len(re.findall(r'<path', content, re.IGNORECASE))
        circles = len(re.findall(r'<circle', content, re.IGNORECASE))
        rects = len(re.findall(r'<rect', content, re.IGNORECASE))
        
        analysis['elements'] = {
            'paths': paths,
            'circles': circles,
            'rectangles': rects
        }
    
    else:
        analysis['svg_type'] = 'Unknown'
        analysis['description'] = 'Unknown SVG format'
        analysis['total_icons'] = 0
    
    return analysis

if __name__ == "__main__":
    analyze_all_svgs()
