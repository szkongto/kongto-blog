# -*- coding: utf-8 -*-
"""产品页价格一致性门禁 — cncdisplay.com

背景：产品页价格过去散在各页 HTML 里手写，没有单一真源，于是漂移出 17 个自相
矛盾的页面：同一个页面上顾客能同时看到两个不同价格，Google 从 og meta 读到的
又是第三个。根因是生成脚本在页面底部注入了一行硬编码价格的 CTA。

本门禁对每个产品页断言一件事：页面上的四处价格声明必须完全一致。

  真值来源 = 可见的 `<span class="price">` —— 顾客实际看到并支付的价。
  必须与之一致 = og `product:price:amount`、JSON-LD `price`、底部 CTA 行
                 `$XXX — In Stock — Ships within 24 hours` 里的价格。

底部 CTA 重复标价是合理的转化设计（价格出现在购买决策点），保留；门禁负责
保证它不会再次跑偏。

`products/index.html` 是列表页，天然列多个价格，排除。

用法：python scripts/check_price_consistency.py
退出码 0 = 全过，1 = 有页面不一致。
"""
import io
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / 'products'
SKIP = {'index.html'}

META_RE = re.compile(r'product:price:amount" content="([\d.]+)"')
JSONLD_RE = re.compile(r'"price"\s*:\s*"([\d.]+)"')
SPAN_RE = re.compile(r'<span class="price">\s*\$?([\d,]+)')
CTA_PRICE_RE = re.compile(r'\$([\d,]+)\s*—\s*In Stock\s*—\s*Ships within 24 hours')


def norm(s):
    return s.replace(',', '').strip()


def main():
    problems = []
    checked = 0

    for p in sorted(PRODUCTS.glob('*.html')):
        if p.name in SKIP:
            continue
        with open(p, encoding='utf-8', newline='') as fh:
            text = fh.read()

        meta = META_RE.search(text)
        jsonld = JSONLD_RE.search(text)
        span = SPAN_RE.search(text)
        if not (meta and jsonld and span):
            continue  # 非标准产品页（故障排查页等），本门禁不覆盖
        checked += 1

        vals = {'og meta': norm(meta.group(1)),
                'JSON-LD': norm(jsonld.group(1)),
                'span.price': norm(span.group(1))}
        cta = CTA_PRICE_RE.search(text)
        if cta:
            vals['底部 CTA'] = norm(cta.group(1))

        if len(set(vals.values())) > 1:
            detail = '  '.join(f'{k}={v}' for k, v in vals.items())
            problems.append(f'{p.name}: 页面内价格不一致 — {detail}')

    if problems:
        print(f'价格一致性 FAIL — 检查 {checked} 页，{len(problems)} 处问题')
        for x in problems:
            print(f'  {x}')
        return 1

    print(f'价格一致性 OK — {checked} 页价格声明全部一致（og meta / JSON-LD / '
          f'span.price / 底部 CTA）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
