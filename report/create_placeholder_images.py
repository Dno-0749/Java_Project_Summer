#!/usr/bin/env python3
"""
Placeholder Image Generator for LaTeX Report
Scans .tex files for \includegraphics calls and creates placeholder PNG files
for any missing images to prevent build failures.
"""

import os
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def find_referenced_images(tex_dir):
    """Scan .tex files for \\includegraphics{} calls."""
    referenced = {}
    pattern = re.compile(r'\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}')
    
    for tex_file in Path(tex_dir).rglob('*.tex'):
        with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            matches = pattern.findall(content)
            for img_path in matches:
                referenced[img_path] = str(tex_file)
    
    return referenced

def create_placeholder(filepath, width=400, height=200):
    """Create a placeholder PNG with text."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    if filepath.exists():
        print(f"  ✓ Skipping (exists): {filepath}")
        return False
    
    # Create gray placeholder image
    img = Image.new('RGB', (width, height), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    
    # Add text
    text = f"Placeholder\n{filepath.name}"
    bbox = draw.textbbox((0, 0), text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill=(50, 50, 50))
    
    img.save(filepath, 'PNG')
    print(f"  ✓ Created: {filepath}")
    return True

def main():
    """Main function."""
    report_dir = Path(__file__).parent
    tex_dir = report_dir / 'chapters'
    images_dir = report_dir / 'images'
    
    print("📋 Scanning for \\includegraphics references...")
    referenced = find_referenced_images(tex_dir)
    
    if not referenced:
        print("  No \\includegraphics calls found.")
        return
    
    print(f"  Found {len(referenced)} image references:")
    
    missing_count = 0
    for img_ref, tex_file in sorted(referenced.items()):
        # Resolve path relative to report directory
        img_path = images_dir / img_ref if not Path(img_ref).is_absolute() else Path(img_ref)
        
        if not img_path.exists():
            print(f"  ✗ Missing: {img_ref} (referenced in {Path(tex_file).name})")
            missing_count += 1
    
    if missing_count == 0:
        print("  All referenced images exist! ✓")
        return
    
    print(f"\n🎨 Creating {missing_count} placeholder image(s)...")
    created = 0
    for img_ref, tex_file in sorted(referenced.items()):
        img_path = images_dir / img_ref if not Path(img_ref).is_absolute() else Path(img_ref)
        if not img_path.exists():
            if create_placeholder(img_path):
                created += 1
    
    print(f"\n✅ Placeholder generation complete: {created} new image(s) created")
    print("   Replace these with actual images when available.")

if __name__ == '__main__':
    main()
