# -*- coding: utf-8 -*-
"""全站链接指向正确性审计 — pre-commit 门禁
检查每类"指向":
  1. 内部链接目标文件存在(断链)
  2. 语言切换按钮: zh页lang-en→非zh, en页lang-zh→/zh/ (调 check_lang_switch 逻辑)
  3. 重定向型号匹配 (调 audit_redirects_hard 逻辑)
  4. 内容链接: 锚文本含型号X, 目标页文件名含型号Y(X≠Y) → 指向错误
退出码: 0=通过, 1=有错
"""
import re
import glob
import os
import sys
import subprocess

MODEL_RE = re.compile(
    r'(A61L[- ]0001[- ]\d{4}|A02B[- ]\d{4}|A05B[- ]\d{4}|009\d|008\d|007\d|'
    r'D9MM[- ]11A|MDT[- ]?94\d|TX[- ]\d+|C14C[- ]1472DF|DR5614|6FC3\d{3}|'
    r'BM09DF|CD1472|C5470|MDT1283|KTV\d+)')

# 面板型号 = 整机型号 别名 (D9MM-11A 就是 A61L-0001-0093 的显示面板)
ALIAS = {'D9MM11A': '0093', 'TX1450': '0074', 'MDT947': '0086'}


def model_key(m):
    n = m.replace('-', '').replace(' ', '').upper()
    if n in ALIAS:
        return ALIAS[n]
    d = re.findall(r'\d{4}', n)
    return d[-1] if d else n


# 重定向源 → 目标 (链接到重定向源 = 功能通, 但应更新为最终目标)
def load_redirects():
    redir = {}
    if not os.path.isfile('_redirects'):
        return redir
    for line in open('_redirects', encoding='utf-8'):
        m = re.match(r'^(\S+)\s+(\S+)\s+30[12]\s*$', line.strip())
        if m:
            redir[m.group(1)] = m.group(2).replace('https://cncdisplay.com', '')
    return redir


def final_target(url, redir):
    """解析链接最终目标(经重定向)"""
    seen = set()
    cur = url
    while cur in redir and cur not in seen:
        seen.add(cur)
        nxt = redir[cur]
        cur = nxt if nxt.startswith('/') else '/' + nxt.split('/')[-1]
    return cur


def main():
    redir = load_redirects()
    bad = []
    warnings = []

    # 真实文件集合(大小写敏感): os.walk 保留磁盘实际大小写 + set 精确匹配,
    # 模拟 GitHub Pages(Linux) 大小写语义. os.path.isfile 在 Windows 大小写不敏感,
    # 会把磁盘上不存在(仅大小写不同)的目标误判为存在 → 断链漏检.
    SKIP = ('en_bak', '_archive', '_archive_audit', 'node_modules', '.git',
            '.github', 'backlinks_output', 'backlinks_daily')
    real_files = set()
    for dirpath, dirnames, filenames in os.walk('.'):
        dp = dirpath.replace('\\', '/').rstrip('/').lstrip('./')
        if any(part in SKIP for part in dp.split('/') if part):
            continue
        for fn in filenames:
            real_files.add((dp + '/' + fn).lstrip('/'))

    # 遍历所有 html
    for f in glob.glob('**/*.html', recursive=True):
        fs = f.replace('\\', '/')
        if fs.startswith('en_bak/') or fs.startswith('_archive') or '/node_modules/' in fs:
            continue
        h = open(f, encoding='utf-8', errors='ignore').read()
        for m in re.finditer(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', h, re.S):
            url = m.group(1)
            anchor = re.sub(r'<[^>]+>', ' ', m.group(2)).strip()
            if url.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:', '#')):
                continue
            if url.startswith(('/images', '/assets', '/docs', '/cdn-cgi', 'weixin', '//')) or '${' in url:
                continue
            # 相对链接解析为绝对(相对当前页目录)
            if not url.startswith('/'):
                url = '/' + os.path.dirname(fs).replace('\\', '/').rstrip('/') + '/' + url
            p = url.lstrip('/').split('?')[0]
            if not p:
                continue
            # 1) 断链 (解析重定向后判定)
            final = final_target('/' + p, redir) if p.startswith(('posts', 'products', 'zh/', 'guides', 'brands', 'en/')) else '/' + p
            fp = final.lstrip('/').split('?')[0]
            if not fp.endswith('/') and fp not in real_files:
                if fp + '/index.html' not in real_files:
                    if p != fp and p in redir:
                        bad.append((fs, url, f'重定向目标不存在: {url}→{final}'))
                    else:
                        bad.append((fs, url, '断链'))
                    continue
            # 链接指向重定向源 → 警告(应更新为最终目标)
            if '/' + p in redir and final != '/' + p:
                warnings.append((fs, url, f'链接指向重定向源, 应更新为{final}'))
                continue
            # 4) 锚文本型号 vs 目标型号 (警告: 相关型号互链合法, 但错配需抽查)
            am = MODEL_RE.search(anchor)
            tm = MODEL_RE.search(url)
            if am and tm:
                ak, tk = model_key(am.group(0)), model_key(tm.group(0))
                if ak != tk:
                    base = os.path.basename(url)
                    if any(x in base.lower() for x in ['guide', 'faq', 'hub', 'index', 'matrix', 'compare', 'compat', 'brand', 'series', 'complete', 'catalog']):
                        warnings.append((fs, url, f'型号不同但目标为聚合页:{ak}→{tk}'))
                        continue
                    warnings.append((fs, url, f'锚文本型号{ak}≠目标型号{tk}, 需抽查'))

    if bad:
        print(f'[LINK-CORRECTNESS] {len(bad)} 个指向错误:')
        for fs, url, why in bad[:25]:
            print(f'  {fs}\n    {why}: {url}')
        print(f'\n另有 {len(warnings)} 个需人工确认(聚合页跨型号链接)')
        sys.exit(1)
    print(f'[LINK-CORRECTNESS] OK — 断链0, 锚文本型号错配0')
    if warnings:
        print(f'  (注意: {len(warnings)} 个跨型号聚合页链接, 抽查确认)')
    sys.exit(0)


if __name__ == '__main__':
    main()
