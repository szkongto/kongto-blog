# -*- coding: utf-8 -*-
"""P1-3 meta description 现状扫描
审计报告: 122页缺 meta description / 103页过长 / 60页过短 / 17页重复
统计当前状态, 按文件列出。
"""
import io, sys, re, glob, os
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SKIP_DIRS = {'en_bak', '_archive', '_archive_audit', '_templates', 'node_modules', '.git',
             '.github', 'backlinks_output', 'backlinks_daily', 'screaming_frog_reports',
             'output', '__pycache__'}

missing = []      # 无 meta description
too_long = []     # >160 chars
too_short = []    # <50 chars
dup_desc = []     # 重复 description
ok = []

desc_counter = Counter()
desc_owner = {}

html_files = [f.replace('\\', '/') for f in glob.glob('**/*.html', recursive=True)]
html_files = [f for f in html_files if not any(
    f.startswith(s + '/') or '/node_modules/' in f for s in SKIP_DIRS)]

for f in html_files:
    h = open(f, encoding='utf-8', errors='ignore').read()
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', h, re.S | re.I)
    if not m:
        missing.append(f)
        continue
    desc = m.group(1).strip()
    n = len(desc)
    if n > 160:
        too_long.append((f, n))
    elif n < 50:
        too_short.append((f, n))
    else:
        ok.append((f, n))
    desc_counter[desc] += 1
    desc_owner[desc] = desc_owner.get(desc, f)

dup_desc = [(f, cnt) for desc, cnt in desc_counter.items() if cnt > 1 for f in [desc_owner[desc]]]

print('== 全站 HTML: %d 页 ==' % len(html_files))
print('缺 meta description: %d' % len(missing))
print('  过长(>160): %d  过短(<50): %d  合格(50-160): %d' % (
    len(too_long), len(too_short), len(ok)))
print('重复 description(>1页共用): %d 组' % len([1 for d, c in desc_counter.items() if c > 1]))
print()
print('== 缺 description 的文件 ==')
for f in sorted(missing):
    print('  %s' % f)
print()
print('== 过短(<50) ==')
for f, n in sorted(too_short, key=lambda x: -x[1])[:20]:
    print('  %3d  %s' % (n, f))
print('== 过长(>160) 前20 ==')
for f, n in sorted(too_long, key=lambda x: -x[1])[:20]:
    print('  %3d  %s' % (n, f))
