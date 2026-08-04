# -*- coding: utf-8 -*-
"""全站 301 Link Equity 审计 — 逐条分类 + 输出 Markdown 报告"""
import re
import os
import urllib.parse

SRC = '_redirects'
MODEL_RE = re.compile(
    r'(A61L[- ]0001[- ]\d{4}|A02B[- ]\d{4}|A05B[- ]\d{4}|009\d|008\d|007\d|'
    r'D9MM[- ]11A|MDT[- ]?94\d|TX[- ]\d+|C14C[- ]1472DF|DR5614|6FC3\d{3}|'
    r'BM09DF|CD1472|C5470|MDT1283|KTV\d+)'
)


def dec(p):
    return urllib.parse.unquote(p)


def model_key(m):
    n = m.replace('-', '').replace(' ', '').upper()
    d = re.findall(r'\d{4}', n)
    return d[-1] if d else n


lines = [l for l in open(SRC, encoding='utf-8').read().splitlines()
         if l.strip() and not l.startswith('#')]
cats = {'正确(同主题)': [], '首页(泄漏)': [], '品牌页(兜底)': [], '跨型号错配': [],
        '目标404': [], '自循环': [], '格式异常': []}
for ln in lines:
    m = re.match(r'^(\S+)\s+(\S+)\s+(30[12])\s*$', ln)
    if not m:
        cats['格式异常'].append(ln)
        continue
    src, dst = m.group(1), m.group(2)
    if src == dst or dec(src) == dec(dst):
        cats['自循环'].append(ln)
        continue
    if dst in ('/', '/index.html', 'https://cncdisplay.com/', 'https://cncdisplay.com'):
        cats['首页(泄漏)'].append(ln)
        continue
    if '/brands/' in dst:
        cats['品牌页(兜底)'].append(ln)
        continue
    p = dec(dst).lstrip('/').split('?')[0]
    if p and not p.endswith('/') and not os.path.isfile(p) and not dst.startswith('http'):
        cats['目标404'].append(ln)
        continue
    sm = MODEL_RE.search(src)
    dm = MODEL_RE.search(dst)
    if sm and dm and model_key(sm.group(0)) != model_key(dm.group(0)):
        cats['跨型号错配'].append(ln)
        continue
    cats['正确(同主题)'].append(ln)

total = sum(len(v) for v in cats.values())
print('=== %d 条 301 全量分类 ===' % total)
for k, v in cats.items():
    print('  %s: %d' % (k, len(v)))

with open('redirect_link_equity_audit.md', 'w', encoding='utf-8') as f:
    f.write('# cncdisplay.com 301 迁移审计报告（%d 条）\n\n' % total)
    f.write('生成时间：2026-08-05（基于当前 _redirects 实盘数据）\n\n')
    f.write('## 统计\n\n')
    for k, v in cats.items():
        f.write('- %s: **%d**\n' % (k, len(v)))
    f.write('\n## 异常明细（需人工复核的）\n\n')
    for cat in ['首页(泄漏)', '跨型号错配', '目标404', '自循环', '格式异常']:
        if cats[cat]:
            f.write('### %s（%d）\n\n' % (cat, len(cats[cat])))
            for ln in cats[cat]:
                f.write('- `%s`\n' % ln)
            f.write('\n')
    f.write('## 品牌页(兜底)明细（产品无独立页→品牌页，可接受）\n\n')
    for ln in cats['品牌页(兜底)']:
        f.write('- `%s`\n' % ln)
    f.write('\n')
    # 全量逐条清单
    f.write('## 全量 301 规则清单（%d 条，逐条）\n\n' % total)
    f.write('| # | 分类 | 规则 |\n|---|---|---|\n')
    order = ['正确(同主题)', '首页(泄漏)', '品牌页(兜底)', '跨型号错配', '目标404', '自循环', '格式异常']
    idx = 1
    for cat in order:
        for ln in cats[cat]:
            f.write('| %d | %s | `%s` |\n' % (idx, cat, ln))
            idx += 1
    f.write('\n')
print('written: redirect_link_equity_audit.md')
