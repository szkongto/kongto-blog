# -*- coding: utf-8 -*-
"""P1-5 分析: 型号命名连字符/下划线混用扫描
目标: 找出同一型号在不同文件/URL里用不同分隔符的案例
"""
import io, sys, re, glob, os
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SKIP = {'en_bak','_archive','_archive_audit','_templates','node_modules','.git','.github',
        'backlinks_output','backlinks_daily','screaming_frog_reports','output','__pycache__',
        'seo_reports','data','docs','scripts'}

files = [f.replace('\\','/') for f in glob.glob('**/*.html', recursive=True)]
files = [f for f in files if not any(f.startswith(s+'/') or '/node_modules/' in f for s in SKIP)]
print('扫描 HTML 页: %d' % len(files))

hyphen = []
underscore = []
mixed_same = []

for f in files:
    base = os.path.basename(f).replace('.html','').replace('-zh','').replace('_zh','')
    if '-' in base and '_' in base:
        mixed_same.append(f)
    elif '-' in base:
        hyphen.append(f)
    elif '_' in base:
        underscore.append(f)

print('\n=== 文件名同时含连字符+下划线: %d 个 ===' % len(mixed_same))
for f in sorted(mixed_same):
    print('  %s' % f)
print('\n=== 仅连字符: %d  仅下划线: %d ===' % (len(hyphen), len(underscore)))
print('连字符样例:', [os.path.basename(x) for x in hyphen[:10]])
print('下划线样例:', [os.path.basename(x) for x in underscore[:10]])
