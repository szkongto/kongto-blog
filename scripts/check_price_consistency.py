# -*- coding: utf-8 -*-
"""产品页价格一致性门禁 — cncdisplay.com

背景：产品页价格过去散在各页 HTML 里手写，没有单一真源，于是漂移出 17 个自相
矛盾的页面：同一个页面上顾客能同时看到两个不同价格，Google 从 og meta 读到的
又是第三个。根因是生成脚本在页面底部注入了一行硬编码价格的 CTA。

本门禁对每个产品页断言一件事：页面上的四处价格声明必须完全一致。

  真值来源 = 可见的价格容器 —— 顾客实际看到并支付的价。
             `<span class="price">`（55 页）或 `<div class="price">`（7 页）。
  必须与之一致 = og `product:price:amount`、JSON-LD `price`、底部 CTA 行
                 `$XXX — In Stock — Ships within 24 hours` 里的价格。

  2026-09-13：此前只认 `<span class="price">`，7 个用 `<div class="price">`
  的产品页（bruce-systems / delem / fagor / heidenhain-bc120 /
  kme-17dm14af03 / num-760 / panasonic-9inch）被整页跳过，门禁报
  「55 页全一致」而实际 62 页。已放开为 span|div。

底部 CTA 重复标价是合理的转化设计（价格出现在购买决策点），保留；门禁负责
保证它不会再次跑偏。

`products/index.html` 是列表页，天然列多个价格，排除。

## 盲区补灯：命中价格模式但抽不出数字 → WARN（2026-09-13 加）

上面的断言全部建立在「抽得出数字」之上。em dash 吃掉数字的形态 B
（`$480 — In Stock` → `$— In Stock`）把数字整个抹掉，正则一条都匹配不上，
页面被 `continue` 静默跳过，门禁照报「全部一致」——数字没了反而没人管。

这条只 WARN 不 FAIL：它是防回归的补灯，而合法的无价容器（例如
"Request a quote"）会撞上同样的形状，做成 HARD 会为低频风险抬高整条门禁的
误伤面。WARN 只亮不拦，人工看一眼即可。

用法：python scripts/check_price_consistency.py
退出码 0 = 无价格冲突（可能带 WARN），1 = 有页面不一致。
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
PRICE_RE = re.compile(r'<(?:span|div) class="price">\s*\$?([\d,]+)')
CTA_PRICE_RE = re.compile(r'\$([\d,]+)\s*—\s*In Stock\s*—\s*Ships within 24 hours')

# —— 盲区补灯用（只 WARN）——
# 价格声明：值可能是空的或被 em dash 顶掉，所以 group 用 [^"]* 而不是 [\d.]+。
DECL_RES = (
    ('og meta product:price:amount', re.compile(r'product:price:amount" content="([^"]*)"')),
    ('JSON-LD price', re.compile(r'"price"\s*:\s*"([^"]*)"')),
    ('底部 CTA 行', re.compile(r'\$([^\s<]*)\s*—\s*In Stock')),
)
# 任何带 price 字样的 class 属性（含 product-price / price 两种写法）。
CONTAINER_RE = re.compile(r'class="[^"]*price[^"]*"', re.I)
# 该容器后面真的跟了数字。
CONTAINER_DIGIT_RE = re.compile(r'<\w+[^>]*class="[^"]*price[^"]*"[^>]*>\s*\$?\s*\d', re.I)


def norm(s):
    return s.replace(',', '').strip()


def main():
    problems = []
    warns = []
    checked = 0

    for p in sorted(PRODUCTS.glob('*.html')):
        if p.name in SKIP:
            continue
        with open(p, encoding='utf-8', newline='') as fh:
            text = fh.read()

        # 盲区补灯：命中价格容器/价格声明，却抽不出数字。必须在下面的
        # `continue` 之前跑，否则这些页面正好是被静默跳过的那一批。
        for label, rex in DECL_RES:
            hit = rex.search(text)
            if hit and not re.search(r'\d', hit.group(1)):
                warns.append(
                    f'{p.name}: {label} 命中但抽不出数字（实际值 {hit.group(1)!r}）'
                    f' — 疑似 em dash 吃掉数字，人工看这一行')
        if CONTAINER_RE.search(text) and not CONTAINER_DIGIT_RE.search(text):
            warns.append(
                f'{p.name}: 有价格容器 class 但整页容器里抽不出数字'
                f' — 疑似 em dash 吃掉数字；若本就是无价容器（"Request a quote"）可忽略')

        meta = META_RE.search(text)
        jsonld = JSONLD_RE.search(text)
        vis = PRICE_RE.search(text)
        if not (meta and jsonld and vis):
            continue  # 非标准产品页（故障排查页等），本门禁不覆盖
        checked += 1

        vals = {'og meta': norm(meta.group(1)),
                'JSON-LD': norm(jsonld.group(1)),
                'visible price': norm(vis.group(1))}
        cta = CTA_PRICE_RE.search(text)
        if cta:
            vals['底部 CTA'] = norm(cta.group(1))

        if len(set(vals.values())) > 1:
            detail = '  '.join(f'{k}={v}' for k, v in vals.items())
            problems.append(f'{p.name}: 页面内价格不一致 — {detail}')

    if warns:
        print(f'价格一致性 WARN — {len(warns)} 条盲区提示（不拦提交，人工确认）')
        for x in warns:
            print(f'  WARN {x}')

    if problems:
        print(f'价格一致性 FAIL — 检查 {checked} 页，{len(problems)} 处问题')
        for x in problems:
            print(f'  {x}')
        return 1

    print(f'价格一致性 OK — {checked} 页价格声明全部一致（og meta / JSON-LD / '
          f'可见价格容器 / 底部 CTA）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
