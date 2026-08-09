# -*- coding: utf-8 -*-
"""P1-4 死链量化: 指向301源的软死链 + 真断链
页面直接链接到 _redirects 源(会301跳转) = 软死链, 应更新为最终目标。
"""
import re, glob, os
from collections import Counter, defaultdict

# _redirects 源 → 目标
redir = {}
for line in open('_redirects', encoding='utf-8'):
    m = re.match(r'^(\S+)\s+(\S+)\s+30[12]\s*$', line.strip())
    if m:
        redir[m.group(1)] = m.group(2).replace('https://cncdisplay.com', '')

# 站内真实文件
real_files = set()
for dirpath, dirnames, filenames in os.walk('.'):
    dp = dirpath.replace('\\', '/').rstrip('/').lstrip('./')
    if any(part in ('en_bak','_archive','_archive_audit','node_modules','.git','.github',
                    'backlinks_output','backlinks_daily','screaming_frog_reports','output')
           for part in dp.split('/') if part):
        continue
    for fn in filenames:
        real_files.add((dp + '/' + fn).lstrip('/'))

soft = []   # 指向 301 源的链接
hard = []   # 真断链
target_refs = defaultdict(list)

for f in glob.glob('**/*.html', recursive=True):
    fs = f.replace('\\', '/')
    if fs.startswith(('en_bak', '_archive', 'node_modules')):
        continue
    pagedir = os.path.dirname(fs)
    h = open(f, encoding='utf-8', errors='ignore').read()
    for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>', h):
        url = m.group(1).strip()
        if url.startswith(('#','mailto:','tel:','javascript:','data:','http','//')) or '${' in url or '/cdn-cgi' in url:
            continue
        if "' + " in url:
            continue
        if url.startswith('/'):
            p = url.lstrip('/')
        else:
            p = (pagedir + '/' + url).lstrip('/')
        p = p.split('?')[0].split('#')[0]
        if not p:
            continue
        exists = (p in real_files) or ((p.rstrip('/') + '/index.html') in real_files)
        if not exists:
            if ('/' + p) in redir:
                soft.append((fs, url, redir['/' + p]))
                target_refs[redir['/' + p]].append(fs)
            else:
                hard.append((fs, url))

print('== 指向301重定向源的链接(软死链, 应更新为最终目标) ==')
print('条数:', len(soft))
print()
print('== 真断链(本地+redirect都无) ==')
print('条数:', len(hard))
for fs, u in hard[:30]:
    print('  %s -> %s' % (fs, u))

print()
print('== 按最终目标聚合(高频在前) ==')
agg = Counter()
for fs, u, fin in soft:
    agg[fin] += 1
for fin, n in agg.most_common(40):
    print('%3d  %s' % (n, fin))
