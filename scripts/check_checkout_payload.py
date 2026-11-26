# -*- coding: utf-8 -*-
"""硬门禁: 产品页的 PayPal createOrder 必须带齐订单识别信息。

背景: 订单邮件/后台靠 createOrder 里的字段还原「买了哪个型号、几台、单价、
运费、电话」。页面若从老模板复制或手写, 常漏 items / breakdown / tel=,
结果是订单只有总价、无法发货 (2026-11-19 那单 $507 就是这么丢的)。

每个含 paypal.Buttons 的 products/*.html 必须同时有:
  - id="buyerPhone"                      页面收集电话
  - |tel=                                custom_id 带电话兜底
  - custom_id: '<slug>|<...>'            首段 = 文件名, 否则邮件链接指向别页
  - invoice_id:
  - items: [ { name / quantity / unit_amount } ]
  - amount.breakdown.item_total
  - amount.breakdown.shipping

不含 paypal.Buttons 的页面 (症状页、index 等) 跳过。
全站全量扫描, 不只查本次变更: 57 个结账页规模下开销可忽略, 也不受 CI
fetch-depth 1 影响 (拿不到 HEAD^ 做 diff)。

用法: python scripts/check_checkout_payload.py
exit 0 = 全部合规; exit 1 = 有页面缺字段。
"""
import glob
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

REQUIRED = [
    ('页内电话输入框', re.compile(r'id="buyerPhone"')),
    ('custom_id 带 tel=', re.compile(r'\|tel=')),
    ('invoice_id', re.compile(r'invoice_id:')),
    ('items 数组', re.compile(r'items:\s*\[\s*\{')),
    ('unit_amount', re.compile(r'unit_amount')),
    ('breakdown.item_total', re.compile(r'item_total')),
    ('breakdown.shipping', re.compile(r'shipping:\s*\{')),
]

CUSTOM_ID = re.compile(r"custom_id:\s*'([^']*)'|custom_id:\s*\"([^\"]*)\"")


def check(path):
    src = open(path, encoding='utf-8', errors='replace').read()
    if 'paypal.Buttons' not in src:
        return None
    problems = [label for label, pat in REQUIRED if not pat.search(src)]

    m = CUSTOM_ID.search(src)
    stem = os.path.splitext(os.path.basename(path))[0]
    if not m:
        problems.append('custom_id 缺失')
    else:
        slug = (m.group(1) or m.group(2)).split('|')[0]
        # 模板里用变量拼 slug 时跳过, 只校验字面量首段。
        if slug and not slug.startswith('${') and slug != stem:
            problems.append(f"custom_id 首段是 {slug!r}, 应等于文件名 {stem!r}")
    return problems


def main():
    pages = sorted(glob.glob('products/*.html'))
    failed = []
    checked = 0
    for p in pages:
        problems = check(p)
        if problems is None:
            continue
        checked += 1
        if problems:
            failed.append((p, problems))

    if failed:
        print(f'FAIL: {len(failed)} 个结账页的 createOrder 字段不全')
        for p, problems in failed:
            print(f'  {p}: ' + '; '.join(problems))
        print('修法: 对照 products/mitsubishi-eum-1491a-crt-lcd-upgrade.html 的 createOrder 块补齐;')
        print('      存量页可跑 python scripts/patch_paypal_description.py / patch_checkout_phone.py / patch_checkout_required.py')
        sys.exit(1)
    print(f'OK: {checked} 个结账页 createOrder 字段齐全')


if __name__ == '__main__':
    main()
