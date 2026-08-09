# -*- coding: utf-8 -*-
"""P1-2 图片现状审计: 总量/目录/大图/重复对"""
import io, sys, os, glob
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SKIP = {'en_bak','_archive','_archive_audit','node_modules','.git','.github',
        'backlinks_output','backlinks_daily','screaming_frog_reports','output',
        '__pycache__','data','docs','seo_reports'}
IMGS = ['*.jpg','*.jpeg','*.png','*.webp','*.gif','*.avif','*.svg','*.ico']

all_imgs = []
for pat in IMGS:
    for f in glob.glob('**/'+pat, recursive=True):
        fs = f.replace('\\','/')
        if any(fs.startswith(s+'/') for s in SKIP):
            continue
        all_imgs.append(fs)

total = sum(os.path.getsize(f) for f in all_imgs)
print('图片文件总数: %d' % len(all_imgs))
print('总体积: %.1f MB' % (total/1048576))

by_dir = defaultdict(lambda: [0, 0])
for f in all_imgs:
    d = f.rsplit('/',1)[0]
    by_dir[d][0] += 1; by_dir[d][1] += os.path.getsize(f)
print('\n按目录(top15 体积):')
for d,(n,sz) in sorted(by_dir.items(), key=lambda x:-x[1][1])[:15]:
    print('  %-42s %4d个 %6.1fMB' % (d or '.', n, sz/1048576))

print('\n>300KB 的图 (top 30):')
big = sorted([(os.path.getsize(f), f) for f in all_imgs], reverse=True)[:30]
for sz,f in big:
    print('  %7.1fKB  %s' % (sz/1024, f))
