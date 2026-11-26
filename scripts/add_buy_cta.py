# -*- coding: utf-8 -*-
"""给每篇真实文章在标题下方插入统一购买按钮。

标准块（全站唯一形态）:
  <p class="cluster-cta mt-11"><a href="{target}" class="btn-orange">Buy Now &rarr;</a></p>

- 目标取自 data/article_product_map.csv（build_article_product_map.py 生成）
- 位置: </h1> 之后; 若在 .article-hero 内, 放在 hero 容器结束之后（hero 的 ::before 会吃掉点击）
- 幂等: 先删除已有的 cluster-cta mt-11 块, 再按标准位置重插
- 不动 cluster-cta note-left-navy 纯文字 CTA
- 跳过 meta-refresh 跳转桩

用法: python scripts/add_buy_cta.py [--apply]
"""
import io
import os
import re
import sys

# reconfigure 而非重包 TextIOWrapper: build_article_product_map 导入时也重包
# stdout, 两次重包会关掉底层 buffer。
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)

import build_article_product_map as apm  # noqa: E402

BLOCK = '<p class="cluster-cta mt-11"><a href="{url}" class="btn-orange">Buy Now &rarr;</a></p>'
CTA_RE = re.compile(r'\s*<p class="cluster-cta mt-11">.*?</p>', re.DOTALL)
# 文章末尾旧的 "🔧 Ready to upgrade? ... → View Product Details" 卡片：
# 按钮搬到标题下之后整卡删除，避免同一页两个购买入口。
# 锚文本限定 [^<]* —— 用 .*? 会跨过缺失的 </div> 一路吃到后面的
# </main>/<footer>（0093 与 D9MM 两页的卡未闭合，实测删掉了 121 行结构）。
CARD_HEAD = (
    r'<div class="card-mist-c">\s*'
    r'<p class="fs-lg-mb"><strong>🔧 Ready to upgrade\?[^<]*</strong></p>\s*'
    r'<a href="[^"]+"[^>]*btn-pill-orange[^>]*>[^<]*</a>\s*')
# 卡内锚点后可能还有一行 "This module also fits ..." 说明, 一并收掉。
CARD_TAIL = (
    r'(?:<p class="fs-sm-mt075">[^<]*(?:<a href="[^"]+"[^>]*>[^<]*</a>[^<]*)*</p>\s*)?'
    r'</div>\s*')
CARD_RE = re.compile(CARD_HEAD + CARD_TAIL)
# 未闭合卡：只在整个主内容末尾（下一结构元素是 </main>）时才整卡删除，
# 避免跨段落误删。
CARD_OPEN_RE = re.compile(CARD_HEAD + r'(?=</main>)')
H1_RE = re.compile(r'</h1>', re.I)


def load_map():
    """映射现算, 不读 data/ CSV —— data/ 被 .gitignore 排除, 且 CSV 会过期。"""
    return {r[0]: {'target_url': r[1]} for r in apm.build()}


def hero_ranges(text):
    """返回所有 .article-hero 容器的 (起, 止) 字符区间（与 check_cta_links 同算法）。"""
    out, stack = [], []
    for m in re.finditer(r'<div\b[^>]*>|</div>', text, re.I):
        if m.group(0).lower().startswith('</'):
            if stack:
                start, is_hero = stack.pop()
                if is_hero:
                    out.append((start, m.end()))
        else:
            stack.append((m.start(), 'article-hero' in m.group(0)))
    return out


def anchor_end(text):
    """返回插入位置（标题区末尾的字符下标）。"""
    h1 = H1_RE.search(text)
    if not h1:
        return None
    end = h1.end()
    # .article-hero 模板: 按钮必须放在 hero 容器之外。
    # hero 的 ::before 是 inset:0 的装饰层, 按钮放进 hero 会点不动。
    for start, stop in hero_ranges(text):
        if start <= h1.start() < stop:
            return stop
    return end


def build_new(text, url):
    text = CARD_OPEN_RE.sub('', text)
    text = CARD_RE.sub('', text)
    text = CTA_RE.sub('', text)
    pos = anchor_end(text)
    if pos is None:
        return None
    return text[:pos] + '\n    ' + BLOCK.format(url=url) + text[pos:]


def main():
    apply = '--apply' in sys.argv
    mapping = load_map()
    changed = same = skipped = 0
    problems = []
    for rel, row in sorted(mapping.items()):
        text = open(rel, encoding='utf-8').read()
        if 'http-equiv="refresh"' in text:
            skipped += 1
            continue
        new = build_new(text, row['target_url'])
        if new is None:
            problems.append(f'{rel}: 找不到 </h1>')
            continue
        if new == text:
            same += 1
            continue
        changed += 1
        if apply:
            with open(rel, 'w', encoding='utf-8', newline='') as f:
                f.write(new)
    print(f"{'APPLIED' if apply else 'DRY-RUN'}: changed={changed} already-ok={same} "
          f"skipped-stub={skipped} problems={len(problems)}")
    for p in problems:
        print('  ! ' + p)
    if problems:
        sys.exit(1)


if __name__ == '__main__':
    main()
