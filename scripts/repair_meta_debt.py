# -*- coding: utf-8 -*-
"""清算 meta 增强债：缺 viewport 加 viewport；缺 hreflang 的单语言页加 x-default。
只处理真页面（跳过 meta-refresh 壳页）。幂等。
用法: python scripts/repair_meta_debt.py --apply
"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SKIP = {'en_bak', '_archive_audit', '_templates', '.git', '__pycache__',
        'backlinks_daily', 'backlinks_output', 'node_modules', 'fonts',
        'images', 'output', 'screaming_frog_reports', 'data', 'schema',
        'css', 'patches', 'docs', 'workers'}
SKIP_PATTERNS = ('audit-verification', 'redirect_audit_report', '-content.html',
                 '_content', 'template-', '-fragment', 'google7478', 'baidu_verify')

VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1">'


def fix_file(rel):
    with open(rel, encoding='utf-8', errors='ignore') as f:
        content = f.read()
    orig = content
    changes = []

    if 'http-equiv="refresh"' in content:
        return None  # 壳页跳过

    # 1. viewport
    if not re.search(r'name=["\']?viewport', content):
        # 插到 <head> 后（charset 之后）
        m = re.search(r'(<head[^>]*>.*?<meta charset=[^>]+>)', content, re.I | re.S)
        if m:
            content = content[:m.end(1)] + '\n' + VIEWPORT + content[m.end(1):]
            changes.append('viewport')

    # 2. x-default hreflang（单语言页，自身即默认）
    if not re.search(r'hreflang=["\']x-default', content):
        url = rel.replace('\\', '/')
        if url.endswith('/index.html'):
            url = url.replace('/index.html', '/')
        if not url.startswith('/'):
            url = '/' + url
        canon = re.search(r'rel=["\']canonical["\'] href=["\']([^"\']+)', content)
        xd_href = canon.group(1) if canon else ('https://cncdisplay.com' + url)
        xd = f'<link rel="alternate" hreflang="x-default" href="{xd_href}">'
        if xd not in content:
            content = content.replace('</head>', '    ' + xd + '\n</head>', 1)
            changes.append('x-default')

    if content != orig:
        return content, changes
    return None


def main():
    apply = '--apply' in sys.argv
    stats = {'viewport': 0, 'x-default': 0}
    done = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in SKIP]
        for f in files:
            if not f.endswith('.html') or any(s in f for s in SKIP_PATTERNS):
                continue
            rel = os.path.relpath(os.path.join(root, f), '.').replace('\\', '/')
            r = fix_file(rel)
            if not r:
                continue
            content, changes = r
            for c in changes:
                stats[c] += 1
            if apply:
                with open(rel, 'w', encoding='utf-8') as fh:
                    fh.write(content)
            done.append((rel, changes))

    print(f'待修 {len(done)} 页: viewport={stats["viewport"]}, x-default={stats["x-default"]}')
    for rel, changes in done[:15]:
        print(f'  {rel}: +{"+".join(changes)}')
    if not apply:
        print('\n加 --apply 实际写入')


if __name__ == '__main__':
    main()
