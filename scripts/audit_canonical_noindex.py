# -*- coding: utf-8 -*-
"""GSC分类解读实证:
A) canonical 非自引用页(=「备用网页」候选26)
B) noindex 页分布(=「被noindex排除」候选90)
用法: PYTHONIOENCODING=utf-8 python scripts/audit_canonical_noindex.py
"""
import re, glob, collections, os

files = [f.replace('\\', '/').lstrip('./') for f in glob.glob('**/*.html', recursive=True)
         if not f.replace('\\', '/').lstrip('./').startswith(
             ('en_bak/', 'node_modules/', '_archive_audit/', '_templates/'))]

base = 'https://cncdisplay.com/'

def url_of(f):
    return base + f

non_self = []          # canonical != 自身URL
self_ok = 0
noindex = []           # noindex 页
noindex_re = re.compile(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\'][^>]*noindex', re.I)
canon_re = re.compile(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', re.I)

for fs in files:
    try:
        h = open(fs, encoding='utf-8', errors='ignore').read()
    except Exception:
        continue
    u = url_of(fs)
    m = canon_re.search(h)
    if m:
        can = m.group(1)
        if can.rstrip('/') != u.rstrip('/'):
            non_self.append((fs, can))
        else:
            self_ok += 1
    if noindex_re.search(h):
        noindex.append(fs)

print(f'总文件: {len(files)}')
print(f'canonical 自引用: {self_ok}')
print(f'=== canonical 非自引用: {len(non_self)} ===')
for fs, can in sorted(non_self):
    print(f'  {fs}')
    print(f'      -> {can}')

print(f'\n=== noindex 页: {len(noindex)} ===')
cats = collections.Counter()
for fs in noindex:
    if fs.startswith('zh/'):
        root = fs[3:]
    else:
        root = fs
    if '/stubs/' in root or root.startswith('stubs/'):
        cats['stub/'] += 1
    elif root.startswith('tags/') or root.startswith('zh/tags/'):
        cats['tags/'] += 1
    elif root.startswith('search') or root.startswith('zh/search'):
        cats['search'] += 1
    elif root.startswith('thank') or 'thank-you' in root:
        cats['thankyou'] += 1
    elif root.startswith('docs/') or '/docs/' in root:
        cats['docs/'] += 1
    elif root.startswith('posts/') or '/posts/' in root:
        cats['posts/'] += 1
    elif root.startswith('products/') or '/products/' in root:
        cats['products/'] += 1
    else:
        cats['other'] += 1
for c, n in cats.most_common():
    print(f'  {c}: {n}')
print('--- noindex 明细(前40) ---')
for fs in sorted(noindex)[:40]:
    print(f'  {fs}')
