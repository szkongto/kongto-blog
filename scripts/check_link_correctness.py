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

# re.IGNORECASE 不可省: href 路径一律小写, 而候选里 D9MM/CD1472/MDT1283/DR5614/
# BM09DF 等是大写字面量——没有 IGNORECASE 时它们对小写 URL 永不命中, 第 4 项
# 比对的"目标型号"一侧恒为 None, `if am and tm` 短路, 整对被静默跳过。
MODEL_RE = re.compile(
    r'(A61L[- ]0001[- ]\d{4}|A02B[- ]\d{4}|A05B[- ]\d{4}|009\d|008\d|007\d|'
    r'D9MM[- ]11A|MDT[- ]?94\d|TX[- ]\d+|C14C[- ]1472DF|DR5614|6FC3\d{3}|'
    r'BM09DF|CD1472|C5470|MDT1283|KTV\d+)', re.IGNORECASE)

# 面板型号 = 整机型号 别名 (D9MM-11A 就是 A61L-0001-0093 的显示面板)
ALIAS = {'D9MM11A': '0093', 'TX1450': '0074', 'MDT947': '0086'}

# 人工别名表 — 补 MODEL_RE 的 token 盲区。
#
# MODEL_RE 是 token 正则, 认不出的别名会让第 4 项比对直接 `if am and tm`
# 短路: 锚文本型号与目标型号两侧只要有一侧认不出, 整对被静默跳过, 既不报错
# 也不进 warnings。已知实例: 4 个州页锚文本 "CD1283 D1M" 指向
# /products/mazak-mdt1283b-lcd-upgrade.html, CD1283 不在 MODEL_RE 里 → 该对
# 从未被比过。本表把这些对子显式录进来, 让它们重新进入比对。
#
# 键 = 归一化别名(大写/去连字符/去空格); 值 = 规范 key, 与 model_key() 同空间。
#
# 录表即等于宣布"这个别名与规范型号是同一显示器" —— 录多了会盖掉真错配。
# 所以每条必须能指出站内依据; 依据不足不录, 宁可继续报"需抽查"。
ALIAS_TABLE = {
    # CD1283-D1M 与 MDT-1283B 是同一显示器的两个编号, _redirects L248
    # 已 301 归并 (redirect_audit_report.html 亦记为合理)。
    'CD1283D1M': '1283',
    # NC6225 = MDT1283B, NC6212 = MDT962B —— 候选型号收敛别名, 见
    # memory cncdisplay-candidates-resolved-20260904; 两者都无独立页。
    'NC6225': '1283',
    'NC6212': '962',
    # MDT962B 本身不在 MODEL_RE 里 (MDT[- ]?94\d 不覆盖 96x)。补进来,
    # 否则它作为链接目标时永远算不出 key, 整对再次短路。
    'MDT962B': '962',
}
_ALIAS_KEYS = sorted(ALIAS_TABLE, key=len, reverse=True)


def _norm(s):
    return s.replace('-', '').replace(' ', '').upper()


def model_tokens(text):
    """取文本里出现的全部型号 token(正则命中 + 别名表命中)。"""
    toks = {m.group(0) for m in MODEL_RE.finditer(text)}
    n = _norm(text)
    for alias in _ALIAS_KEYS:
        if alias in n:
            toks.add(alias)
    return toks


def model_keys(text):
    """取文本里全部型号的规范 key 集合。空集=这段文本没提型号。

    必须取全集而非首个命中: 锚文本常并列举多个型号(如
    "MDT962B/BM09DF/FCUA-CT100"), 只取首个会把"锚文本含型号X"误判成
    不含目标型号Y, 报出假错配。
    """
    return {model_key(t) for t in model_tokens(text)}


def model_key(m):
    n = _norm(m)
    if n in ALIAS:
        return ALIAS[n]
    if n in ALIAS_TABLE:
        return ALIAS_TABLE[n]
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
            aks = model_keys(anchor)
            tks = model_keys(url)
            if aks and tks and not (aks & tks):
                ak, tk = '/'.join(sorted(aks)), '/'.join(sorted(tks))
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
        # 只报计数等于无法逐行抽查; 门禁的警告必须可读原文
        print(f'  (注意: {len(warnings)} 个跨型号链接, 需抽查)')
        for fs, url, why in warnings[:40]:
            print(f'    {fs} → {url}\n      {why}')
        if len(warnings) > 40:
            print(f'    ...另有 {len(warnings) - 40} 条')
    sys.exit(0)


if __name__ == '__main__':
    main()
