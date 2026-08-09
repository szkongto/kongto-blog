# -*- coding: utf-8 -*-
"""P1-3 meta description 补全规划
排除非内容工具页, 识别 en/zh 孪生, 输出真实待补/待修清单。
"""
import io, sys, re, glob, os
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SKIP_DIRS = {'en_bak', '_archive', '_archive_audit', '_templates', 'node_modules', '.git',
             '.github', 'backlinks_output', 'backlinks_daily', 'screaming_frog_reports',
             'output', '__pycache__'}
# 非内容工具页/验证页: 不补 description
TOOL_PAGES = {
    'baidu_verify_codeva-MOcuLxbSCp.html', 'google7478b8e743977291.html',
    'sitemap.html', 'robots.txt', '404.html',
}
TOOL_PREFIX = ('seo_reports/', 'redirect_audit_report', 'audit-verification', 'backlinks_')

html_files = [f.replace('\\', '/') for f in glob.glob('**/*.html', recursive=True)]
html_files = [f for f in html_files if not any(
    f.startswith(s + '/') or '/node_modules/' in f for s in SKIP_DIRS)]

missing = []
too_long = []
too_short = []
dup_groups = []
have = {}

desc_counter = Counter()
desc_owner = {}

for f in html_files:
    base = os.path.basename(f)
    if base in TOOL_PAGES or f.startswith(TOOL_PREFIX):
        continue
    h = open(f, encoding='utf-8', errors='ignore').read()
    title = re.search(r'<title>(.*?)</title>', h, re.S | re.I)
    title = title.group(1).strip() if title else ''
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', h, re.S | re.I)
    if not m:
        missing.append((f, title[:60]))
        continue
    desc = m.group(1).strip()
    n = len(desc)
    have[f] = (n, title[:60])
    if n > 160:
        too_long.append((f, n))
    elif n < 50:
        too_short.append((f, n))
    desc_counter[desc] += 1
    desc_owner[desc] = f

dup_groups = [(desc_owner[d], cnt) for d, cnt in desc_counter.items() if cnt > 1]

# en/zh 孪生匹配: 去 -zh 后缀找 en 对应
def twin(f):
    if '/zh/' in f or f.endswith('-zh.html'):
        return None
    base = os.path.basename(f).replace('.html', '')
    zh_candidates = [
        'zh/' + f,
        f.replace('.html', '-zh.html'),
        re.sub(r'\.html$', '-zh.html', f),
    ]
    for c in zh_candidates:
        if c in have or c in [x for x, _ in missing]:
            return c
    return None

print('== 内容页统计(排除工具页) ==')
print('缺 description: %d' % len(missing))
print('过长(>160): %d  过短(<50): %d' % (len(too_long), len(too_short)))
print('重复 description: %d 组' % len(dup_groups))
print()
print('== 缺 description 的内容页 (en版可翻译复用?) ==')
for f, t in sorted(missing):
    print('  %-90s %s' % (f, ('  <' + t + '>') if t else ''))

print()
print('== 过短(<50) ==')
for f, n in sorted(too_short, key=lambda x: -x[1]):
    print('  %3d  %s' % (n, f))
print('== 过长(>160) ==')
for f, n in sorted(too_long, key=lambda x: -x[1]):
    print('  %3d  %s' % (n, f))
print('== 重复 ==')
for f, cnt in dup_groups:
    print('  %dx  %s' % (cnt, f))
