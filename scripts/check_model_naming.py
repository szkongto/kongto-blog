# -*- coding: utf-8 -*-
"""P1-5 门禁: 页面可见文本中的型号分隔符校验
规则: 型号数字文本统一连字符写法 (SM0901-579417-TA), 禁止下划线 (SM0901_579417_TA)。
命中仅限可见文本 (正文/h1/h3/p), 不算 URL/href/canonical/hreflang (文件名下划线是合法约定)。
stub 页 (Redirecting/跳转中) 与工具/报告页跳过。exit 1 = 有下划线型号文本。
"""
import io, sys, re, glob, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SKIP = {'en_bak','_archive','_archive_audit','_templates','node_modules','.git','.github',
        'backlinks_output','backlinks_daily','screaming_frog_reports','output','__pycache__',
        'seo_reports','data','docs','scripts'}
TOOL_PAGES = {'redirect_audit_report.html','sitemap.html','404.html','robots.txt',
              'baidu_verify_codeva-MOcuLxbSCp.html','google7478b8e743977291.html'}

# 下划线型号: 大写字母开头含数字, 至少2组下划线分隔数字组
UNDER_MODEL = re.compile(r'(?<![A-Za-z0-9])([A-Z]{1,6}[A-Z0-9]*\d_[A-Z0-9]+_[A-Z0-9]+)(?![A-Za-z0-9])')

files = [f.replace('\\','/') for f in glob.glob('**/*.html', recursive=True)]
files = [f for f in files if not any(f.startswith(s+'/') or '/node_modules/' in f for s in SKIP)]

hits = []
for f in sorted(files):
    if os.path.basename(f) in TOOL_PAGES:
        continue
    h = open(f, encoding='utf-8', errors='ignore').read()
    t = re.search(r'<title>(.*?)</title>', h, re.S | re.I)
    if t and ('Redirecting' in t.group(1) or '跳转中' in t.group(1)):
        continue  # stub, 301 处理中
    body = re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>', ' ', h, flags=re.S|re.I)
    body = re.sub(r'<head.*?</head>', ' ', body, flags=re.S|re.I)
    body = re.sub(r'\s+', ' ', body)
    for m in UNDER_MODEL.finditer(body):
        hits.append((f, m.group(1), body[max(0,m.start()-35):m.end()+35].strip()))

if hits:
    print(f'FAIL: 发现 {len(hits)} 处下划线型号文本（应统一连字符）')
    for f, tok, ctx in hits:
        print(f'  {f}')
        print(f'    {tok}  ...{ctx}')
    sys.exit(1)
print(f'OK: 可见文本型号分隔符规范 (扫描 {len(files)} 文件, 0 处下划线)')
