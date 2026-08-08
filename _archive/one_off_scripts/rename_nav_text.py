#!/usr/bin/env python3
"""Rename 型号对照 to 兼容查询 in all HTML pages (navigation links)."""
import os

repo = '.'
count = 0
files_changed = 0

for root, dirs, files in os.walk(repo):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('images','css','schema','docs','images_backup_compressed')]
    for f in files:
        if not f.endswith('.html'):
            continue
        fpath = os.path.join(root, f)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
        if '型号对照' in content:
            new_content = content.replace('型号对照', '兼容查询')
            with open(fpath, 'w', encoding='utf-8') as fp:
                fp.write(new_content)
            count += content.count('型号对照')
            files_changed += 1
            print(f"  [OK] {fpath.replace(repo+'/', '').replace(chr(92), '/')}: renamed {content.count('型号对照')} occurrences")

print(f"\nTotal: {count} replacements across {files_changed} files")
