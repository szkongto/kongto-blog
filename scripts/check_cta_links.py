# -*- coding: utf-8 -*-
"""门禁: 每篇真实文章的购买入口是否符合全站统一标准。

标准（2026-11-26 用户定）:
  1. 标题下方恰好一个购买按钮, 文案 Buy Now →, 指向 data 映射里的目标页
  2. 全文只有一个 btn-orange 购买入口（文章末尾不再保留第二个）
  3. 页头 Get Quote: 型号文章 -> 该型号产品价格页; 非型号 -> /quote.html
  4. 目标页必须真实存在
  5. 旧按钮（btn-pill-orange / View Product Details / View Product & Specs）清零
  6. posts/ 下非文章页（列表页等）不得出现购买按钮

映射来自 scripts/build_article_product_map.py 的 build()（现算, 不读
data/ CSV, 因为 data/ 被 .gitignore 排除）。

用法: python scripts/check_cta_links.py
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)

import build_article_product_map as apm  # noqa: E402

CTA_RE = re.compile(r'<p class="cluster-cta mt-11">\s*<a href="([^"]+)" class="btn-orange">'
                    r'Buy Now &rarr;</a>\s*</p>')
BLOCK_RE = re.compile(r'<p class="cluster-cta mt-11">.*?</p>', re.DOTALL)
H1_END_RE = re.compile(r'</h1>', re.I)
HEADER_RE = re.compile(r'<header>.*?</header>', re.DOTALL)
QUOTE_RE = re.compile(r'<a href="([^"]*)" class="text-accent">Get Quote</a>')
OLD_BTN_RE = re.compile(r'btn-pill-orange|View Product Details|View Product &amp; Specs')


def target_exists(url):
    p = url.lstrip('/')
    if url.endswith('/'):
        return os.path.exists(p + 'index.html')
    return os.path.exists(p)


def main():
    rows = apm.build()
    problems = []
    mapped = set()
    for rel, url, match_type, _note in rows:
        mapped.add(rel)
        if not os.path.exists(rel):
            problems.append('%s: 文件不存在' % rel)
            continue
        if not target_exists(url):
            problems.append('%s: 目标页不存在 %s' % (rel, url))
        text = open(rel, encoding='utf-8').read()

        blocks = BLOCK_RE.findall(text)
        if len(blocks) != 1:
            problems.append('%s: cluster-cta mt-11 块 %d 个（应为 1）' % (rel, len(blocks)))
        else:
            m = CTA_RE.fullmatch(blocks[0].strip())
            if not m:
                problems.append('%s: 按钮形态不符标准: %s' % (rel, blocks[0][:120]))
            elif m.group(1) != url:
                problems.append('%s: 按钮 href=%s 应为 %s' % (rel, m.group(1), url))
            h1 = H1_END_RE.search(text)
            if h1 and text.find(blocks[0]) < h1.end():
                problems.append('%s: 按钮不在标题下方' % rel)

        n_orange = text.count('class="btn-orange"')
        if n_orange != 1:
            problems.append('%s: btn-orange %d 个（应为 1）' % (rel, n_orange))

        if OLD_BTN_RE.search(text):
            problems.append('%s: 残留旧按钮文案/类名' % rel)

        hdr = HEADER_RE.search(text)
        if not hdr:
            problems.append('%s: 缺 <header>' % rel)
        else:
            quotes = QUOTE_RE.findall(hdr.group(0))
            want = url if match_type == 'model' else '/quote.html'
            if not quotes:
                # 老短导航常整条缺 Get Quote, 静默放过就等于标准形同虚设
                problems.append('%s: 页头缺 Get Quote（应为 %s）' % (rel, want))
            elif len(quotes) != 1:
                problems.append('%s: 页头 Get Quote %d 个（应为 1）' % (rel, len(quotes)))
            elif quotes[0] != want:
                problems.append('%s: 页头 Get Quote=%s 应为 %s' % (rel, quotes[0], want))

    # posts/ 下真实页（非跳转桩）必须都在映射里, 且非文章页不得带购买按钮
    for f in sorted(os.listdir('posts')):
        if not f.endswith('.html') or 'audit-verification' in f:
            continue
        rel = 'posts/' + f
        text = open(rel, encoding='utf-8').read()
        if 'http-equiv="refresh"' in text:
            continue
        if rel in mapped:
            continue
        if BLOCK_RE.search(text) or 'class="btn-orange"' in text:
            problems.append('%s: 不在映射内却带购买按钮（非文章页应无按钮）' % rel)

    if problems:
        for p in problems[:40]:
            print('[CTA] ' + p)
        print('[CTA] FAIL %d 项' % len(problems))
        sys.exit(1)
    print('[CTA] OK %d 篇文章, 按钮/页头 Get Quote 全部一致' % len(rows))


if __name__ == '__main__':
    main()
