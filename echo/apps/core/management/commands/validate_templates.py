"""
Management command to validate Django templates for duplicate block tags.
"""
import re
import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Validate templates for duplicate block declarations'

    def handle(self, *args, **options):
        templates_dir = os.path.join(settings.BASE_DIR, 'templates')
        duplicates = []
        
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    blocks = re.findall(r'\{%\s*block\s+(\w+)\s*%\}', content)
                    block_counts = {}
                    for block in blocks:
                        block_counts[block] = block_counts.get(block, 0) + 1
                    
                    dups = {b: c for b, c in block_counts.items() if c > 1}
                    if dups:
                        rel_path = filepath.replace(templates_dir + '/', '')
                        duplicates.append((rel_path, dups))
        
        if duplicates:
            self.stderr.write(self.style.ERROR('❌ Found duplicate blocks:'))
            for filepath, blocks in duplicates:
                self.stderr.write(f'\n  {filepath}:')
                for block, count in blocks.items():
                    self.stderr.write(f"    - '{block}' appears {count} times")
            raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS('✅ All templates OK'))