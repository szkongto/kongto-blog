# -*- coding: utf-8 -*-
"""P1-5 内容级扫描: 页面文本里型号用下划线写法的案例
模式: [A-Z]+[0-9]+-[_][0-9]+ 系 型号(大写开头含数字, 下划线分隔数字组)
统一目标: 连字符写法
"""
import io, sys, re, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SKIP = {'en_bak','_archive','_archive_audit','_templates','node_modules','.git','.github',
        'backlinks_output','backlinks_daily','screaming_frog_reports','output','__pycache__',
        'seo_reports','data','docs','scripts'}

files = [f.replace('\\','/') for f in glob.glob('**/*.html', recursive=True)]
files = [f for f in files if not any(f.startswith(s+'/') or '/node_modules/' in f for s in SKIP)]

# 下划线型号: 形如 A61L_0001_0093 / MDT962B_系列 等
# 模式: 字母数字开头(含大写字母+数字), 至少2个 _数字 组
UNDER_MODEL = re.compile(r'(?<![A-Za-z0-9])([A-Z]{1,6}[A-Z0-9]*\d(?:[_][A-Z0-9]+){2,})(?![A-Za-z0-9])')
# 也抓 字母_数字_数字 但字母可能小写(如 kt800_m)? 先看大类

hits = defaultdict(list)  # file -> [(match, context)]
for f in files:
    h = open(f, encoding='utf-8', errors='ignore').read()
    # 只看 body 文本, 去掉 script/style
    body = re.sub(r'<script.*?</script>', ' ', h, flags=re.S|re.I)
    body = re.sub(r'<style.*?</style>', ' ', body, flags=re.S|re.I)
    body = re.sub(r'<[^>]+>', ' ', body)
    body = re.sub(r'\s+', ' ', body)
    for m in UNDER_MODEL.finditer(body):
        ctx = body[max(0,m.start()-30):m.end()+30]
        hits[f].append((m.group(0), ctx.strip()))

nfiles = len(hits)
total = sum(len(v) for v in hits.values())
print('== 内容含下划线型号文本: %d 文件 / %d 处 ==' % (nfiles, total))
print()
# 统计出现最多的下划线型号词
from collections import Counter
cnt = Counter(m for fl in hits.values() for m,_ in fl)
print('== 下划线型号 TOP20 ==')
for tok, c in cnt.most_common(20):
    print('  %4d  %s' % (c, tok))
print()
print('== 受影响文件 ==')
for f in sorted(hits, key=lambda x: -len(hits[x])):
    print('  %-80s %d处' % (f, len(hits[f])))
