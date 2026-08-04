#!/usr/bin/env python3
"""Full-site _redirects audit."""
import os, re, urllib.parse
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REDIRECTS = os.path.join(ROOT, '_redirects')

existing_files = set()
for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', 'en_bak', '__pycache__', '.git')]
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), ROOT)
        existing_files.add('/' + rel.replace(os.sep, '/'))

MODEL_PATTERNS = [
    (r'A61L[-_]?0001[-_]?(\d{4})', 'FANUC'),
    (r'DR(\d{4})', 'MAZAK-DR'),
    (r'CD(\d{4})', 'MAZAK-CD'),
    (r'MDT[-_]?(\d{4}[A-Z]?)', 'MITSU-MDT'),
    (r'BM(\d{2}[A-Z]{2})', 'MITSU-BM'),
    (r'6FC(\d{4})', 'SIEMENS'),
    (r'6fc(\d{4})', 'SIEMENS'),
    (r'D9MM[-_]?(\d+[A-Z]?)', 'FANUC-D9MM'),
    (r'KT(\d{3})', 'KT'),
    (r'KTV(\d+[A-Z]?)', 'KTV'),
    (r'GBS[-_]?(\d{4})', 'GBS'),
]

def extract_models(url):
    models = set()
    for pat, brand in MODEL_PATTERNS:
        matches = re.findall(pat, url, re.IGNORECASE)
        for m in matches:
            models.add(brand + '-' + m.upper())
    return models

def target_exists(target):
    if target.startswith('http'):
        return True
    path = target.split('?')[0].split('#')[0]
    if path in existing_files:
        return True
    return False

redirects = []
with open(REDIRECTS, 'r', encoding='utf-8') as f:
    for lineno, line in enumerate(f, 1):
        raw = line.strip()
        if not raw or raw.startswith('#'):
            continue
        clean = re.sub(r'\s+30[12]\s*$', '', raw).strip()
        if not clean:
            continue
        parts = clean.split(None, 1)
        if len(parts) < 2:
            continue
        src, dst_raw = parts[0], parts[1]
        src = src.strip('"').strip("'")
        if src.startswith('http'):
            try:
                src = urllib.parse.urlparse(src).path
            except:
                pass
        if not src.startswith('/'):
            src = '/' + src
        dst = dst_raw.strip('"').strip("'").strip()
        dst = re.sub(r'\s+.*$', '', dst)
        if not dst.startswith('http') and not dst.startswith('/'):
            dst = '/' + dst
        src_models = extract_models(src)
        dst_models = extract_models(dst)
        redirects.append({
            'line': lineno, 'src': src, 'dst': dst,
            'src_models': src_models, 'dst_models': dst_models,
            'exists': target_exists(dst),
        })

problems = []
for r in redirects:
    issues = []
    if r['dst'] in ('/index.html', 'https://cncdisplay.com/', 'https://cncdisplay.com'):
        issues.append('WEIGHT_LOSS_HOMEPAGE')
    if '/brands/' in r['dst'] and r['dst'] != '/brands/':
        issues.append('WEIGHT_LOSS_BRAND')
    if r['src_models'] and r['dst_models']:
        missing = r['src_models'] - r['dst_models']
        if missing:
            issues.append('MODEL_MISMATCH: ' + str(missing))
    if not r['exists'] and not r['dst'].startswith('http'):
        issues.append('TARGET_404')
    if issues:
        r['issues'] = issues
        problems.append(r)

print('=== TOTAL REDIRECT RULES: %d ===' % len(redirects))
print('=== PROBLEMS FOUND: %d ===' % len(problems))

by_type = defaultdict(list)
for p in problems:
    for issue in p['issues']:
        main = issue.split(':')[0]
        by_type[main].append(p)

for issue_type, items in sorted(by_type.items()):
    print()
    print('=' * 70)
    print('  %s: %d rules' % (issue_type, len(items)))
    print('=' * 70)
    for item in items:
        print()
        print('  Line %d: %s' % (item['line'], issue_type))
        print('    SRC: %s' % item['src'][:140])
        print('    DST: %s' % item['dst'][:140])
        for iss in item['issues']:
            if 'MODEL_MISMATCH' in iss:
                print('    *** %s' % iss)
        if not item['exists'] and not item['dst'].startswith('http'):
            print('    *** TARGET FILE DOES NOT EXIST ON DISK')
