# -*- coding: utf-8 -*-
"""重定向硬错审计 — 提交门禁（pre-commit hook 调用）
硬错(阻止提交): 自循环 / 目标文件不存在 / 跨型号错配
警告(不阻止): 目标=首页 / 源含型号→品牌页（上下文相关，需人工判断）
退出码: 0=通过, 1=有硬错
"""
import re
import os
import sys
import urllib.parse

SRC = '_redirects'
MODEL_RE = re.compile(
    r'(A61L[- ]0001[- ]\d{4}|A02B[- ]\d{4}[- ][A-Z]\d{3}|A05B[- ]\d{4}[- ][A-Z]\d{3}|'
    r'\d{4}-\d{5}|009\d|008\d|007\d|006\d|D9MM[- ]11A|MDT[- ]?94\d|TX[- ]\d+|'
    r'C14C[- ]1472DF|DR5614|6FC3\d{3}|BM09DF|A20B[- ]\d{4})')


def dec(s):
    return urllib.parse.unquote(s)


def target_exists(urlpath):
    p = dec(urlpath).lstrip('/').split('?')[0]
    if not p or p.endswith('/'):
        return True  # 目录路径不判错
    return os.path.isfile(p)


def model_key(m):
    """型号身份键：取尾部 4 位数字（0093 vs A61L-0001-0093 视为同型号）；
    无 4 位数字则用全归一化串（如 BM09DF）。"""
    n = m.replace('-', '').replace(' ', '').upper()
    import re as _re
    digits = _re.findall(r'\d{4}', n)
    return digits[-1] if digits else n


lines = [l for l in open(SRC, encoding='utf-8').read().splitlines()
         if l.strip() and not l.startswith('#')]
hard = []
for ln in lines:
    m = re.match(r'^(\S+)\s+(\S+)\s+(30[12])\s*$', ln)
    if not m:
        continue  # 格式错由 worker 生成步骤报
    src, dst = m.group(1), m.group(2)
    # 自循环
    if src == dst or dec(src) == dec(dst):
        hard.append((ln, '自循环'))
        continue
    # 目标文件不存在（非 http / 非目录）
    if not dst.startswith('http') and not target_exists(dst):
        hard.append((ln, f'目标不存在: {dec(dst)[:50]}'))
        continue
    # 跨型号错配
    sm = MODEL_RE.search(src)
    dm = MODEL_RE.search(dst)
    if sm and dm and model_key(sm.group(0)) != model_key(dm.group(0)):
        # 已知纠错白名单: 错误型号 → 正确型号(刻意修正, 非错配)
        if (model_key(sm.group(0)), model_key(dm.group(0))) in (('3998', '3988'),):
            continue
        hard.append((ln, f'跨型号错配: {sm.group(0)} → {dm.group(0)}'))

if hard:
    print(f'\n[REDIRECT-AUDIT] 发现 {len(hard)} 条硬错，阻止提交:')
    for ln, why in hard:
        print(f'  [{why}] {ln}')
    print('\n修复 _redirects 后重试。参考: python scripts/audit_redirects.py')
    sys.exit(1)
print('[REDIRECT-AUDIT] OK — 无自循环/目标404/跨型号错配')
sys.exit(0)
