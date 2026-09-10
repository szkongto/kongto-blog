# -*- coding: utf-8 -*-
"""跨型号产品页近重复审计 — cncdisplay.com

背景
----
`scripts/audit_aggressive.py` 是内容站( posts/ )的重复门禁，它的规则里有一条
刻意的豁免：**不同型号共享模板不算重复**（`same_model` 判断不通过就 `continue`，
只计数不报告），并且 products/ 的硬阈值被抬到 0.99。那条豁免在 2026-08-09 是
合理的 —— 当时担心的是"不同型号本来就是独立关键词页，不该互相拦截"。

代价是它看不见另一类问题：**不同型号但正文几乎逐字相同**。同一个 14 寸 Mazak
显示器在 aiqa8dsp40 / c3470 / c5470 / c5470ns / cd1472 五个部件号下各建了一页，
规格表、故障症状、FAQ、客户评价四块内容逐字节一样，Google 看到的是五个几乎相同
的页面。这不是"共享模板"，模板只占导航和页脚；正文本身在重复。

本脚本补上这块视野。它是**报告工具**，默认不改任何东西、永远 exit 0 —— 因为
修复方式（合并 or 逐页差异化）需要真实机型事实，不能由脚本自己拍板。加 --hard
可以让它在超过阈值时 exit 1，用于接进门禁。

度量
----
正文按 `<h2>` 切成块，逐块算 8-gram Jaccard，另外算整页总分。产品页正文短
（中位数 405 词），8-gram 比 3-gram 更能反映"整句照抄"而非"共享术语"。

  Jaccard = |A∩B| / |A∪B|   1.000 = 逐字相同

用法
----
    python scripts/audit_duplicate_products.py                 # 报告，exit 0
    python scripts/audit_duplicate_products.py --threshold 0.5 # 换报告阈值
    python scripts/audit_duplicate_products.py --hard 0.85     # 超阈值 exit 1
"""
import io
import itertools
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / 'products'
SKIP = {'index.html'}

# 报告阈值：整页 8-gram Jaccard 到这个程度就认为读者会觉得"这两页是同一篇"
REPORT = 0.30
# --hard 默认关掉（None）。设了值才当门禁用。
HARD = None

# 按 <h2> 切块用的锚点 —— 这是产品页固定的版式，缺了就当没有该块
BLOCKS = [
    ('specs',      'Specifications'),
    ('compatible', 'Compatible Systems'),
    ('symptoms',   'Common CRT Failure Symptoms'),
    ('faq',        'Frequently Asked Questions'),
    ('reviews',    'What Our Customers Say'),
    ('warranty',   'Warranty &amp; Service'),
]

TAG_RE = re.compile(r'(?s)<[^>]+>')
WS_RE = re.compile(r'\s+')


def strip_text(html):
    t = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', html)
    t = TAG_RE.sub(' ', t)
    t = re.sub(r'&[a-z#0-9]+;', ' ', t)
    return WS_RE.sub(' ', t).strip()


def shingles(text, k=8):
    w = re.findall(r'[a-z0-9]+', text.lower())
    if len(w) < k:
        return set()
    return set(zip(*[w[i:] for i in range(k)]))


def jac(a, b):
    if not a or not b:
        return None
    return len(a & b) / len(a | b)


def split_blocks(html):
    """按 <h2> 标题把正文切块；返回 {块名: html} 与 整页 html"""
    marks = [(m.start(), strip_text(m.group(1)))
             for m in re.finditer(r'(?is)<h2[^>]*>(.*?)</h2>', html)]
    out = {}
    for i, (pos, title) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(html)
        for key, label in BLOCKS:
            if key in out:
                continue
            if strip_text(label) == title:
                out[key] = html[pos:end]
    return out


def load():
    pages = {}
    for p in sorted(PRODUCTS.glob('*.html')):
        if p.name in SKIP:
            continue
        with open(p, encoding='utf-8', newline='') as fh:
            raw = fh.read()
        body = re.search(r'(?is)<body[^>]*>(.*)</body>', raw)
        if not body:
            continue
        html = body.group(1)
        html = re.sub(r'(?is)<(script|style|nav|footer)[^>]*>.*?</\1>', ' ', html)
        text = strip_text(html)
        if not text:
            continue
        noindex = bool(re.search(r'name=["\']robots["\'][^>]*noindex', raw, re.I))
        blk_html = split_blocks(html)
        pages[p.stem] = {
            'text': text,
            'whole': shingles(text),
            'blocks': {k: shingles(strip_text(v)) for k, v in blk_html.items()},
            'words': len(re.findall(r'[A-Za-z0-9]+', text)),
            'indexable': not noindex,
        }
    return pages


def main():
    global REPORT, HARD
    if '--threshold' in sys.argv:
        REPORT = float(sys.argv[sys.argv.index('--threshold') + 1])
    if '--hard' in sys.argv:
        HARD = float(sys.argv[sys.argv.index('--hard') + 1])

    pages = load()
    names = sorted(pages)

    pairs = []
    for a, b in itertools.combinations(names, 2):
        s = jac(pages[a]['whole'], pages[b]['whole'])
        if s is None or s < REPORT:
            continue
        per = {k: jac(pages[a]['blocks'].get(k, set()), pages[b]['blocks'].get(k, set()))
               for k, _ in BLOCKS}
        pairs.append((s, a, b, per))
    pairs.sort(reverse=True)

    print('=' * 78)
    print(f'跨型号产品页近重复审计 — 扫描 {len(names)} 个产品页，'
          f'整页 8-gram Jaccard ≥ {REPORT:.2f} 的对')
    print('=' * 78)

    if not pairs:
        print('无近重复对。')
        return 0

    both = [p for p in pairs if pages[p[1]]['indexable'] and pages[p[2]]['indexable']]
    print(f'近重复对 {len(pairs)} 对，其中双方均可索引 {len(both)} 对\n')
    hdr = '  '.join(f'{k:>9s}' for k, _ in BLOCKS)
    print(f'{"整页":>6s}  {"词数":>13s}  页面对')
    print(f'{"":>6s}  {hdr}')

    for s, a, b, per in pairs:
        cells = []
        for k, _ in BLOCKS:
            v = per[k]
            cells.append('        -' if v is None else f'{v:9.3f}')
        wa, wb = pages[a]['words'], pages[b]['words']
        flag = '' if (pages[a]['indexable'] and pages[b]['indexable']) else '  [含noindex]'
        print(f'{s:6.3f}  {wa:6d}/{wb:<6d}  {a}  ×  {b}{flag}')
        print(f'{"":>6s}  ' + '  '.join(cells))

    # 连通分量：把"互相都像"的页面归成一群，方便看成簇而不是一堆对
    parent = {n: n for n in names}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for s, a, b, _ in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    groups = {}
    for n in names:
        r = find(n)
        if any(r == find(p[1]) or r == find(p[2]) for p in pairs):
            groups.setdefault(r, []).append(n)

    print('\n' + '=' * 78)
    print(f'聚类 — {len(groups)} 个近重复簇')
    print('=' * 78)
    for i, (_, members) in enumerate(sorted(groups.items(),
                                            key=lambda kv: -len(kv[1])), 1):
        idx = sum(1 for m in members if pages[m]['indexable'])
        print(f'\n簇 {i}（{len(members)} 页，{idx} 页可索引）')
        for m in sorted(members):
            print(f'    {"索引" if pages[m]["indexable"] else "noindex"}  '
                  f'{pages[m]["words"]:5d} 词  {m}')

    if HARD is not None:
        bad = [p for p in both if p[0] >= HARD]
        if bad:
            print(f'\nFAIL — {len(bad)} 对双方可索引且整页相似 ≥ {HARD:.2f}')
            return 1
        print(f'\nOK — 无双方可索引且 ≥ {HARD:.2f} 的对')
    return 0


if __name__ == '__main__':
    sys.exit(main())
