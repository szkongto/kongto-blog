# -*- coding: utf-8 -*-
"""P1-2 图片审计2: 备份目录引用 + MD5重复对"""
import io, sys, os, glob, hashlib
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SKIP = {'en_bak','_archive','_archive_audit','node_modules','.git','.github',
        'backlinks_output','backlinks_daily','screaming_frog_reports','output',
        '__pycache__','data','docs','seo_reports','scripts'}

# 1. HTML 是否引用 images_backup
print('== 1. HTML 引用 images_backup? ==')
refs = []
for f in glob.glob('**/*.html', recursive=True):
    fs = f.replace('\\','/')
    if any(fs.startswith(s+'/') for s in SKIP): continue
    h = open(f, encoding='utf-8', errors='ignore').read()
    if 'images_backup' in h:
        refs.append(fs)
print('引用文件数:', len(refs))
for f in refs[:10]: print('  ', f)

# 2. images_backup 是否在 git 里
print('\n== 2. git 追踪 images_backup? ==')
r = os.popen('git ls-files images_backup_20260809_035304/ | wc -l').read().strip()
print('git 追踪文件数:', r)

# 3. 图片引用数 (HTML 里 img src 指向 images/)
print('\n== 3. img src 引用统计 ==')
from collections import Counter
cnt = Counter()
img_refs = 0
for f in glob.glob('**/*.html', recursive=True):
    fs = f.replace('\\','/')
    if any(fs.startswith(s+'/') for s in SKIP): continue
    h = open(f, encoding='utf-8', errors='ignore').read()
    for m in __import__('re').finditer(r'src="([^"]+\.(?:jpg|jpeg|png|webp|gif))"', h, __import__('re').I):
        u = m.group(1)
        img_refs += 1
        base = u.split('/')[-1]
        cnt[base] += 1
print('HTML img 引用总数: %d' % img_refs)
print('被引用不同的图片: %d' % len(cnt))

# 4. MD5 重复对 (全站图片内容级重复)
print('\n== 4. MD5 内容级重复 ==')
by_md5 = defaultdict(list)
imgs = []
for pat in ['*.jpg','*.jpeg','*.png','*.webp']:
    for f in glob.glob('**/'+pat, recursive=True):
        fs = f.replace('\\','/')
        if any(fs.startswith(s+'/') for s in SKIP): continue
        imgs.append(fs)
for f in imgs:
    h = hashlib.md5(open(f,'rb').read()).hexdigest()
    by_md5[h].append(f)
dups = {k:v for k,v in by_md5.items() if len(v)>1}
n_dup_files = sum(len(v) for v in dups.values())
print('重复组: %d, 涉及文件: %d (可省 %.1fMB)' % (
    len(dups), n_dup_files,
    sum(os.path.getsize(v[1:][0]) if len(v)>1 else 0 for v in dups.values())/1048576))
# 展示最大的重复组
big_groups = sorted(dups.values(), key=lambda v: -os.path.getsize(v[0]))[:15]
for v in big_groups:
    print('  %6.1fKB x%d' % (os.path.getsize(v[0])/1024, len(v)))
    for f in v[:4]: print('      %s' % f)
