# -*- coding: utf-8 -*-
"""列出所有指向 301 源的链接受影响页面明细"""
import io, sys, re, glob, os
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

redir = {}
for line in open('_redirects', encoding='utf-8'):
    m = re.match(r'^(\S+)\s+(\S+)\s+30[12]\s*$', line.strip())
    if m:
        redir[m.group(1)] = m.group(2).replace('https://cncdisplay.com', '')

real = set()
for dp, dn, fn in os.walk('.'):
    d = dp.replace('\\', '/').lstrip('./')
    if any(x in ('en_bak', '_archive', '_archive_audit', 'node_modules', '.git',
                 '.github', 'backlinks_output', 'backlinks_daily', 'screaming_frog_reports', 'output')
           for x in d.split('/')):
        continue
    for f in fn:
        real.add((d + '/' + f).lstrip('/'))

srcfiles = defaultdict(list)
for f in glob.glob('**/*.html', recursive=True):
    fs = f.replace('\\', '/')
    if fs.startswith(('en_bak', '_archive', 'node_modules')):
        continue
    pd = os.path.dirname(fs)
    h = open(f, encoding='utf-8', errors='ignore').read()
    for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>', h):
        url = m.group(1).strip()
        if url.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:', 'http', '//')) or '${' in url or '/cdn-cgi' in url:
            continue
        if "' + " in url:
            continue
        p = (url.lstrip('/') if url.startswith('/') else (pd + '/' + url)).lstrip('/').split('?')[0].split('#')[0]
        if not p:
            continue
        if (p in real) or ((p.rstrip('/') + '/index.html') in real):
            continue
        if ('/' + p) in redir:
            srcfiles[fs].append((url, redir['/' + p]))

print('受影响页面数: %d' % len(srcfiles))
print()
for fs, items in sorted(srcfiles.items(), key=lambda x: -len(x[1])):
    print('%2d  %s' % (len(items), fs))
    for u, fin in items[:5]:
        print('      %s  ->  %s' % (u, fin))
    if len(items) > 5:
        print('      ... 共 %d 处' % len(items))
