#!/usr/bin/env python3
"""
SVG Icon Analyzer - Analyze the downloaded SVG sprite file
"""

import re
import json
from pathlib import Path

def analyze_svg_sprite(svg_file_path):
    """Analyze SVG sprite file dan extract semua icon info"""
    try:
        with open(svg_file_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        print(f"🎨 Analyzing SVG sprite: {svg_file_path}")
        print("="*60)
        
        # Extract all symbols/icons
        symbol_pattern = r'<symbol\s+id="([^"]+)"[^>]*>'
        symbols = re.findall(symbol_pattern, svg_content)
        
        print(f"📊 Total icons found: {len(symbols)}")
        print(f"💾 File size: {len(svg_content):,} characters")
        
        # Categorize icons
        categories = {
            'header': [],
            'navigation': [],
            'ui': [],
            'social': [],
            'arrows': [],
            'forms': [],
            'other': []
        }
        
        for symbol in symbols:
            symbol_lower = symbol.lower()
            if 'header' in symbol_lower:
                categories['header'].append(symbol)
            elif any(nav in symbol_lower for nav in ['nav', 'menu', 'home', 'dashboard']):
                categories['navigation'].append(symbol)
            elif any(ui in symbol_lower for ui in ['button', 'close', 'search', 'settings', 'user']):
                categories['ui'].append(symbol)
            elif any(social in symbol_lower for social in ['facebook', 'twitter', 'instagram', 'linkedin']):
                categories['social'].append(symbol)
            elif any(arrow in symbol_lower for arrow in ['arrow', 'chevron', 'up', 'down', 'left', 'right']):
                categories['arrows'].append(symbol)
            elif any(form in symbol_lower for form in ['input', 'form', 'check', 'radio', 'select']):
                categories['forms'].append(symbol)
            else:
                categories['other'].append(symbol)
        
        # Print categorized results
        print(f"\n📋 Icon Categories:")
        for category, icons in categories.items():
            if icons:
                print(f"\n{category.upper()} ({len(icons)} icons):")
                for icon in sorted(icons)[:10]:  # Show first 10
                    print(f"  • {icon}")
                if len(icons) > 10:
                    print(f"  ... and {len(icons) - 10} more")
        
        # Show all icons
        print(f"\n📜 Complete Icon List:")
        print("-" * 60)
        for i, symbol in enumerate(sorted(symbols), 1):
            print(f"{i:3d}. {symbol}")
        
        # Save icon list
        output_dir = Path(svg_file_path).parent
        icon_list_file = output_dir / 'icon_list.txt'
        
        with open(icon_list_file, 'w', encoding='utf-8') as f:
            f.write(f"SVG Icon Sprite Analysis\n")
            f.write(f"File: {svg_file_path}\n")
            f.write(f"Total Icons: {len(symbols)}\n")
            f.write(f"Analyzed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("CATEGORIZED ICONS:\n")
            f.write("="*50 + "\n")
            for category, icons in categories.items():
                if icons:
                    f.write(f"\n{category.upper()} ({len(icons)} icons):\n")
                    for icon in sorted(icons):
                        f.write(f"  • {icon}\n")
            
            f.write(f"\nCOMPLETE ALPHABETICAL LIST:\n")
            f.write("="*50 + "\n")
            for i, symbol in enumerate(sorted(symbols), 1):
                f.write(f"{i:3d}. {symbol}\n")
        
        print(f"\n📋 Icon list saved: {icon_list_file}")
        
        # Generate HTML preview
        html_preview = generate_html_preview(symbols, svg_file_path)
        html_file = output_dir / 'icon_preview.html'
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_preview)
        
        print(f"🌐 HTML preview: {html_file}")
        
        return {
            'total_icons': len(symbols),
            'categories': categories,
            'all_icons': sorted(symbols)
        }
        
    except Exception as e:
        print(f"❌ Error analyzing SVG: {e}")
        return None

def generate_html_preview(symbols, svg_file_path):
    """Generate HTML preview of all icons"""
    svg_filename = Path(svg_file_path).name
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SVG Icon Preview - {svg_filename}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: #333;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .icon-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .icon-item {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            transition: box-shadow 0.3s;
        }}
        .icon-item:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .icon-svg {{
            width: 32px;
            height: 32px;
            margin-bottom: 10px;
        }}
        .icon-name {{
            font-size: 12px;
            color: #666;
            word-break: break-all;
        }}
        .stats {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #007bff;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 SVG Icon Sprite Preview</h1>
        <p>File: {svg_filename}</p>
        <p>Total Icons: {len(symbols)}</p>
    </div>
    
    <div class="stats">
        <h3>📊 Quick Stats</h3>
        <p><strong>Total Icons:</strong> {len(symbols)}</p>
        <p><strong>Usage:</strong> Use these icons with &lt;use xlink:href="#{svg_filename}#icon-name"&gt;&lt;/use&gt;</p>
    </div>
    
    <div class="icon-grid">
"""
    
    for symbol in sorted(symbols):
        html += f"""
        <div class="icon-item">
            <svg class="icon-svg" viewBox="0 0 24 24">
                <use href="#{symbol}"></use>
            </svg>
            <div class="icon-name">{symbol}</div>
        </div>
"""
    
    html += f"""
    </div>
    
    <script>
        // Load SVG sprite
        fetch('{svg_filename}')
            .then(response => response.text())
            .then(svgContent => {{
                const div = document.createElement('div');
                div.style.display = 'none';
                div.innerHTML = svgContent;
                document.body.insertBefore(div, document.body.firstChild);
            }});
    </script>
</body>
</html>"""
    
    return html

def main():
    import time
    
    # Analyze the downloaded SVG
    svg_files = [
        "svg_complete/icon-sprite.svg",
        "test.svg"
    ]
    
    for svg_file in svg_files:
        svg_path = Path(svg_file)
        if svg_path.exists():
            print(f"\n" + "="*70)
            result = analyze_svg_sprite(svg_path)
            
            if result:
                print(f"\n✅ Analysis completed!")
                print(f"🎯 Found {result['total_icons']} icons")
                
                # Show some example usage
                print(f"\n💡 Usage Examples:")
                print(f"HTML: <svg><use href=\"#icon-sprite.svg#header-home\"></use></svg>")
                print(f"CSS:  background-image: url('icon-sprite.svg#header-home');")
                
                return result
    
    print("❌ No SVG files found to analyze")
    return None

if __name__ == "__main__":
    main()
