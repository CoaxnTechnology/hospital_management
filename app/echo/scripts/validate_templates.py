#!/usr/bin/env python3
"""
Validate Django templates for duplicate block tags.
Run: python scripts/validate_templates.py
"""
import os
import re
import sys

TEMPLATES_DIR = '/home/echo/echo/templates'
DUPLICATE_BLOCKS = []

def check_template(filepath):
    """Check for duplicate block declarations in a template."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    blocks = re.findall(r'\{%\s*block\s+(\w+)\s*%\}', content)
    block_counts = {}
    
    for block in blocks:
        block_counts[block] = block_counts.get(block, 0) + 1
    
    duplicates = {b: c for b, c in block_counts.items() if c > 1}
    if duplicates:
        rel_path = filepath.replace(TEMPLATES_DIR + '/', '')
        DUPLICATE_BLOCKS.append((rel_path, duplicates))

def scan_templates(directory):
    """Scan all template files."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                check_template(filepath)

if __name__ == '__main__':
    print("Validating templates for duplicate block tags...")
    scan_templates(TEMPLATES_DIR)
    
    if DUPLICATE_BLOCKS:
        print("\n❌ FOUND DUPLICATE BLOCKS:")
        for filepath, blocks in DUPLICATE_BLOCKS:
            print(f"\n  {filepath}:")
            for block, count in blocks.items():
                print(f"    - '{block}' appears {count} times")
        sys.exit(1)
    else:
        print("✅ All templates OK - no duplicate blocks found")
        sys.exit(0)