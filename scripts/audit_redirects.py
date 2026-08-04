# -*- coding: utf-8 -*-
"""全量审计 _redirects — 逐条核对源/目标，输出 UTF-8 报告 + 候选目标"""
import re, os, urllib.parse, glob

SRC = '_redirects'
MODEL_RE = re.compile(r'(A61L[- ]0001[- ]\d{4}|A02B[- ]\d{4}[- ][A-Z]\d{3}|A05B[- ]\d{4}[- ][A-Z]\d{3}|\d{4}-\d{5}|009\d|008\d|007\d|006\d|D9MM[- ]11A|MDT[- ]?94\d|TX[- ]\d+|C14C[- ]1472DF|DR5614|6FC3\d{3}|BM09DF|A20B[- ]\d{4})')

def dec(s): return urllib.parse.unquote(s)
def exists(urlpath):
    p = dec(urlpath).lstrip('/').split('?')[0]
    if not p or p.endswith('/'): return False
    return os.path.isfile(p)

# 建候选池
all_files = set()
for d in ['posts','zh/posts','products','guides','brands','docs','en/posts']:
    all_files.update(f'{d}/{os.path.basename(f)}' for f in glob.glob(f'{d}/*.html'))
    all_files.update(f'{d}/{os.path.basename(f)}' for f in glob.glob(f'{d}/*.pdf'))

def find_candidates(src):
    """按型号/关键词从活文件池找候选"""
    s = dec(src)
    mod = MODEL_RE.search(s)
    cands = []
    if mod:
        m = mod.group(0)
        for f in all_files:
            if m.replace(' ','').replace('-','') in f.replace(' ','').replace('-','') and ('LCD' in f or 'CRT' in f or 'display' in f.lower()):
                cands.append('/'+f)
    return cands[:4]

lines = [l for l in open(SRC, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')]
flags = []
for ln in lines:
    m = re.match(r'^(\S+)\s+(\S+)\s+(30[12])\s*$', ln)
    if not m:
        flags.append((ln, '格式异常', '', [])); continue
    src, dst, code = m.group(1), m.group(2), m.group(3)
    issues = []
    if src == dst or dec(src) == dec(dst): issues.append('自循环')
    if dst in ('/', '/index.html', 'https://cncdisplay.com/', 'https://cncdisplay.com'):
        issues.append('目标=首页')
    if not dst.startswith('http') and not exists(dst):
        issues.append(f'目标不存在:{dec(dst)[:40]}')
    sm, dm = MODEL_RE.search(src), MODEL_RE.search(dst)
    if sm and dm and sm.group(0).replace('-','').replace(' ','')[:6] != dm.group(0).replace('-','').replace(' ','')[:6]:
        issues.append(f'型号错配:{sm.group(0)}→{dm.group(0)}')
    if sm and '/brands/' in dst: issues.append('源含型号→品牌页')
    if issues:
        flags.append((ln, '; '.join(issues), dec(src), find_candidates(src)))

with open('audit_report_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(f"共 {len(lines)} 条，疑似异常 {len(flags)} 条\n\n")
    for ln, why, src, cands in flags:
        f.write(f"[{why}]\n  {ln}\n  候选落地页: {cands[:3]}\n\n")
print("written audit_report_utf8.txt, flags:", len(flags))
