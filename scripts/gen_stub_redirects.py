# -*- coding: utf-8 -*-
"""P1-3 stub 治理: 生成 93 条 _redirects 301 规则清单
扫描无规则的 stub 页, 解析链式目标, 输出 源->目标 规则到 stdout 和 /tmp/p1-3_rules.txt
不直接改 _redirects — 规则由强模型子代理审查后应用。
"""
import io, sys, re, glob, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = 'p1-3_rules.txt'

redir = {}
for line in open('_redirects', encoding='utf-8'):
    m = re.match(r'^(\S+)\s+(\S+)\s+30[12]\s*$', line.strip())
    if m:
        redir[m.group(1)] = m.group(2).replace('https://cncdisplay.com', '')

SKIP = {'en_bak','_archive','_archive_audit','_templates','node_modules','.git','.github',
        'backlinks_output','backlinks_daily','screaming_frog_reports','output','__pycache__'}
# 验证页: 非内容, 不做 301
VERIFY_PAGES = {'baidu_verify_codeva-MOcuLxbSCp.html', 'google7478b8e743977291.html'}

files = [f.replace('\\', '/') for f in glob.glob('**/*.html', recursive=True)]
files = [f for f in files if not any(f.startswith(s + '/') or '/node_modules/' in f for s in SKIP)]

real = set()
for dp, dn, fn in os.walk('.'):
    d = dp.replace('\\', '/').lstrip('./')
    if any(x in SKIP for x in d.split('/') if x):
        continue
    for f in fn:
        real.add((d + '/' + f).lstrip('/'))

_stub_cache = {}
def is_stub(p):
    fp = p.lstrip('/')
    if fp not in real:
        return False
    if fp in _stub_cache:
        return _stub_cache[fp]
    h = open(fp, encoding='utf-8', errors='ignore').read()
    t = re.search(r'<title>(.*?)</title>', h, re.S | re.I)
    r = bool(t) and ('Redirecting' in t.group(1) or '跳转中' in t.group(1))
    _stub_cache[fp] = r
    return r

def meta_target(fp):
    try:
        h = open(fp, encoding='utf-8', errors='ignore').read()
    except:
        return None
    mr = re.search(r'http-equiv=["\']refresh["\']\s+content=["\']0;url=([^"\']+)["\']', h, re.I)
    if not mr:
        return None
    return mr.group(1).replace('https://cncdisplay.com', '').split('?')[0].split('#')[0]

def exists(p):
    p = p.lstrip('/')
    return p in real or (p.rstrip('/') + '/index.html') in real

# 5 个 meta-refresh 指向 / 的 stub 手动映射
MANUAL = {
    '/zh/posts/gbs-8219-rgb-to-vga-converter.html':
        '/zh/posts/article_20260509_GBS-8219_RGB_to_VGA_converter.html',
    '/zh/posts/kt809-industrial-converter.html':
        '/zh/posts/article_20260509_KT809_industrial_converter.html',
    '/zh/posts/kt819-industrial-converter.html':
        '/zh/posts/article_20260509_KT819_industrial_converter.html',
    '/zh/posts/custom-industrial-display-series-zh.html':
        '/zh/posts/custom_industrial_display_series.html',
    '/zh/posts/used-display-recycling-faq-top10-zh.html':
        '/posts/Used_Industrial_Display_Recycling_FAQ_TOP10.html',
}

rules = []
skipped_verify = []
need_review = []

for f in files:
    base = os.path.basename(f)
    if base in VERIFY_PAGES:
        skipped_verify.append(f)
        continue
    h = open(f, encoding='utf-8', errors='ignore').read()
    t = re.search(r'<title>(.*?)</title>', h, re.S | re.I)
    title = t.group(1).strip() if t else ''
    if 'Redirecting' not in title and '跳转中' not in title:
        continue
    src = '/' + f
    if src in redir:
        continue
    # 手动映射优先
    if src in MANUAL:
        target = MANUAL[src]
    else:
        mrt = meta_target(f)
        if not mrt or mrt == '/':
            need_review.append((f, mrt or '(无meta-refresh)'))
            continue
        # 解析链式到最终非 stub 目标
        cur = mrt
        hops = 0
        while is_stub(cur) and hops < 4:
            nxt = meta_target(cur.lstrip('/'))
            if not nxt or nxt == cur:
                break
            cur = nxt
            hops += 1
        target = cur
    if not exists(target):
        need_review.append((f, target))
        continue
    rules.append((src, target))

# 去重 + 排序
seen = set()
uniq = []
for src, target in rules:
    if src not in seen:
        seen.add(src)
        uniq.append((src, target))
uniq.sort(key=lambda x: x[0])

with open(OUT, 'w', encoding='utf-8') as fo:
    for src, target in uniq:
        fo.write('%s %s 301\n' % (src, target))

print('== 生成规则: %d 条 ==' % len(uniq))
print('跳过验证页: %d (%s)' % (len(skipped_verify), ', '.join(skipped_verify)))
print('需人工复核(目标无效/无refresh): %d' % len(need_review))
for f, t in need_review:
    print('  %s -> %s' % (f, t))
print()
print('== 规则前 20 条 (完整见 %s) ==' % OUT)
for src, target in uniq[:20]:
    print('  %s -> %s' % (src, target))
