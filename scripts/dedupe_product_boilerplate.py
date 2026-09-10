# -*- coding: utf-8 -*-
"""产品页通用块抽离 — cncdisplay.com

背景
----
54 个产品页正文里嵌着三块逐字相同的样板文字：

    Common CRT Failure Symptoms   54 词
    What Our Customers Say        58 词
    Warranty & Service            31 词
                                 ----
                                 143 词

单页正文中位数 393 词，这三块占 36%。`scripts/audit_duplicate_products.py`
测出 54 个产品页两两 8-gram Jaccard ≥ 0.30，聚成两个大连通簇 —— 主因就是这三块。

这三块在站内都已有更完整的归宿，产品页里的是压缩副本：

    症状   → /crt-dead-symptoms.html            （1064 词，5 症状逐条 + 修复vs替换成本）
    评价   → /case-studies.html                 + brands/*.html 九个品牌页
    质保   → /quality-testing.html /about.html

所以本脚本不是"把三块搬到新页面"（那会造出第四个副本），而是：
删掉产品页里的症状块与评价块，把质保块压成短版并挂上三个链接。

质保短版保留在页面上，因为顾客付款前需要看到质保承诺，抽走会掉转化。

保真约束
--------
1. CRLF —— products/*.html 全部是 CRLF。读写都用 newline=''，否则整文件 diff。
2. 块边界按 <h2> 切，不靠硬编码字符串匹配。症状块有 4 种变体、评价块有 21 种、
   质保块有 4 种，硬编码一个字符串会漏掉大半目录。
3. 块不存在就跳过，不改。

用法
----
    python scripts/dedupe_product_boilerplate.py            # 干跑，只报告
    python scripts/dedupe_product_boilerplate.py --apply    # 写入
"""
import io
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / 'products'
SKIP = {'index.html'}

SYMPTOMS = 'Common CRT Failure Symptoms'
REVIEWS = 'What Our Customers Say'
WARRANTY = 'Warranty & Service'

# 单块最多允许多少字符，超了说明 h2 切分没找到下一个标题（会吞掉整页），拒绝执行
MAX_BLOCK = 6000

WARRANTY_BODY = [
    '<strong>2-Year Warranty</strong> — Lifetime Technical Support — Worldwide Shipping<br>',
    'Email: info@cncdisplay.com | WhatsApp: +86-13686889647<br>',
    '<strong>No CNC parameter changes needed</strong> — plug and play, '
    'your machine programs and settings stay intact.<br>',
    '<a href="/crt-dead-symptoms.html">CRT failure symptoms &amp; repair cost</a> ·',
    '<a href="/case-studies.html">Customer results</a> ·',
    '<a href="/quality-testing.html">Quality testing process</a>',
]

TAG_RE = re.compile(r'(?s)<[^>]+>')
AMP_RE = re.compile(r'&amp;', re.I)


def h2_marks(html):
    """返回 [(起始偏移, 标题纯文本)]，标题里 &amp; 解码成 &"""
    out = []
    for m in re.finditer(r'(?is)<h2[^>]*>(.*?)</h2>', html):
        txt = re.sub(r'\s+', ' ', TAG_RE.sub('', m.group(1))).strip()
        out.append((m.start(), AMP_RE.sub('&', txt)))
    return out


def slice_of(html, marks, title):
    """返回 (start, end) —— 该标题的 <h2> 到下一个 <h2> 之前。找不到返回 None。"""
    for i, (pos, txt) in enumerate(marks):
        if txt != title:
            continue
        end = marks[i + 1][0] if i + 1 < len(marks) else len(html)
        return pos, end
    return None


def spaced(body_lines, blank):
    sep = '\r\n\r\n' if blank else '\r\n'
    out = '<h2>Warranty &amp; Service</h2>' + sep + '<div class="info-box-lg">' + sep
    out += sep.join(body_lines) + sep
    return out + '</div>' + sep


def div_balance(html):
    return len(re.findall(r'(?i)<div\b', html)) - len(re.findall(r'(?i)</div>', html))


def infobox_end(html, start):
    """从 start 起找 <div class="info-box-lg"> 及其配对 </div>，返回收尾偏移。

    质保块后面紧跟 CTA 的包裹层 <div class="ctr-pad">，它的开标签落在
    「质保 h2 到下一个 h2」区间内。整段替换会连带吃掉那个开标签，留下孤立
    </div>。所以只换到 info-box-lg 自己闭合为止，后面原样保留。
    """
    m = re.search(r'(?is)<div[^>]*class="[^"]*info-box-lg[^"]*"[^>]*>', html[start:])
    if not m:
        return None
    i = start + m.end()
    depth = 1
    for t in re.finditer(r'(?i)<div\b|</div>', html[i:]):
        depth += 1 if t.group(0).lower().startswith('<div') else -1
        if depth == 0:
            return i + t.end()
    return None


def main():
    apply = '--apply' in sys.argv
    counts = {'symptoms': 0, 'reviews': 0, 'warranty': 0, 'skipped': 0}
    saved_words = 0
    problems = []

    for p in sorted(PRODUCTS.glob('*.html')):
        if p.name in SKIP:
            continue
        with open(p, encoding='utf-8', newline='') as fh:
            raw = fh.read()

        marks = h2_marks(raw)
        acts = []

        cuts = []
        for title, key in ((SYMPTOMS, 'symptoms'), (REVIEWS, 'reviews')):
            s = slice_of(raw, marks, title)
            if not s:
                continue
            if s[1] - s[0] > MAX_BLOCK:
                problems.append(f'{p.name}: {key} 块 {s[1]-s[0]} 字符超上限，跳过')
                continue
            if div_balance(raw[s[0]:s[1]]) != 0:
                problems.append(f'{p.name}: {key} 块 div 不配对，跳过')
                continue
            cuts.append((s[0], s[1], key, ''))
            acts.append(key)

        w = slice_of(raw, marks, WARRANTY)
        if w:
            end = infobox_end(raw, w[0])
            if end is None or end - w[0] > MAX_BLOCK:
                problems.append(f'{p.name}: warranty 块定位失败，跳过')
            else:
                blank = raw[max(0, w[0] - 4):w[0]] == '\r\n\r\n'
                cuts.append((w[0], end, 'warranty', spaced(WARRANTY_BODY, blank)))
                acts.append('warranty')

        if not cuts:
            counts['skipped'] += 1
            continue

        new = raw
        for start, end, key, repl in sorted(cuts, reverse=True):
            before = len(re.findall(r'[A-Za-z0-9]+', TAG_RE.sub(' ', new[start:end])))
            after = len(re.findall(r'[A-Za-z0-9]+', TAG_RE.sub(' ', repl)))
            saved_words += before - after
            new = new[:start] + repl + new[end:]
            counts[key] += 1

        if new != raw:
            if apply:
                with open(p, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(new)
            print(f'  {p.stem:44s} {"+".join(acts)}')

    print()
    for k in ('symptoms', 'reviews', 'warranty'):
        print(f'  {k:10s} 处理 {counts[k]} 页')
    print(f'  {"未处理":10s} {counts["skipped"]} 页（无这三块，另一套模板）')
    print(f'  净减正文约 {saved_words} 词')

    if problems:
        print()
        for x in problems:
            print(f'  警告: {x}')

    if not apply:
        print('\n这是干跑。确认无误后加 --apply 写入。')
    else:
        print('\n已写入。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
