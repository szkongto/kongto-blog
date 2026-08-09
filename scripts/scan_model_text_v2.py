# -*- coding: utf-8 -*-
"""P1-5 终判: 全站文本中 型号token 分隔符用法分布
模式 [A-Z]+[0-9]+[-_][0-9]+[-_][0-9]+ (连字符或下划线),
规范化后分组, 统计每个型号族在文本中 连字符/下划线 各自出现次数与文件数。
"""
import io, sys, re, glob, os
from collections import defaultdict, Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SKIP = {'en_bak','_archive','_archive_audit','_templates','node_modules','.git','.github',
        'backlinks_output','backlinks_daily','screaming_frog_reports','output','__pycache__',
        'seo_reports','data','docs','scripts'}
# 工具页/报告: 不计入 GEO 正文
TOOL = {'redirect_audit_report.html','sitemap.html','404.html','robots.txt'}

files = [f.replace('\\','/') for f in glob.glob('**/*.html', recursive=True)]
files = [f for f in files if not any(f.startswith(s+'/') or '/node_modules/' in f for s in SKIP)]

MODEL = re.compile(r'(?<![A-Za-z0-9])([A-Z]{1,5}[A-Z0-9]*\d[-_][A-Z0-9]+[-_][A-Z0-9]+)(?![A-Za-z0-9])')

# canon -> {sep: {file_set}}
by_canon = defaultdict(lambda: {'-':set(), '_':set(), '-n':0, '_n':0})
for f in files:
    h = open(f, encoding='utf-8', errors='ignore').read()
    body = re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>', ' ', h, flags=re.S|re.I)
    body = re.sub(r'\s+', ' ', body)
    for m in MODEL.finditer(body):
        tok = m.group(1)
        canon = re.sub(r'[-_]','',tok).upper()
        if re.fullmatch(r'\d+', canon):
            continue
        sep = '_' if '_' in tok else '-'
        by_canon[canon][sep].add(f)
        by_canon[canon][sep+'n'] += 1

print('== 文本中含型号数字模式的文件总数: %d ==' % len({f for c in by_canon.values() for s in ('-','_') for f in c[s]}))
print()
print('%-16s %-8s %-8s %-8s %-8s' % ('canon','-文件','_文件','-次数','_次数'))
for canon in sorted(by_canon, key=lambda c: -(by_canon[c]['-n']+by_canon[c]['_n'])):
    d = by_canon[canon]
    flag = ' <== 下划线' if d['_'] else ''
    print('%-16s %-8d %-8d %-8d %-8d%s' % (canon, len(d['-']), len(d['_']), d['-n'], d['_n'], flag))

print()
print('== 含下划线型号文本的文件(需统一为连字符) ==')
under_files = set()
for canon, d in by_canon.items():
    under_files |= d['_']
for f in sorted(under_files):
    print('  %s' % f)
print('共 %d 文件' % len(under_files))
