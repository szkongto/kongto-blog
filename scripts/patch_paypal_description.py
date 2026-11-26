"""把产品页 PayPal createOrder 传入的商品信息补全（型号 / 数量 / 目的地 / 发票号）。

改前：actions.order.create({ purchase_units: [{ amount: { value: total } }] })
改后：带 description / custom_id / invoice_id / items / breakdown

目的：PayPal 交易详情和收据邮件里直接显示型号，不再出现"只收到钱不知道卖了什么"。

用法：
  python scripts/patch_paypal_description.py            # dry run，只报告
  python scripts/patch_paypal_description.py --apply    # 实际写入
"""

import argparse
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

OLD = "{ purchase_units: [{ amount: { value: total } }] }"

NEW_TEMPLATE = """{ purchase_units: [{
        description: (_ppTitle + ' | qty ' + window._qty + ' | DHL ' + _ppDestName).slice(0, 127),
        custom_id: '__SLUG__|qty=' + window._qty + '|dest=' + window._selectedCountry,
        invoice_id: 'CNCD-' + Date.now(),
        items: [{
          name: _ppTitle.slice(0, 127),
          quantity: '' + window._qty,
          unit_amount: { currency_code: 'USD', value: price.toFixed(2) }
        }],
        amount: {
          currency_code: 'USD',
          value: total,
          breakdown: {
            item_total: { currency_code: 'USD', value: (price * window._qty).toFixed(2) },
            shipping: { currency_code: 'USD', value: ship.toFixed(2) }
          }
        }
      }] }"""

# 在 createOrder 内、创建订单前插入标题与目的地变量
PREP_OLD = "      var total = (price * window._qty + ship).toFixed(2);"
PREP_NEW = """      var total = (price * window._qty + ship).toFixed(2);

      var _ppH1 = document.querySelector('h1');
      var _ppTitle = _ppH1 ? _ppH1.textContent.split('|')[0].trim() : 'CNC LCD Upgrade Kit';
      var _ppDestName = (window._DHL[window._selectedCountry] || {}).name || window._selectedCountry;"""


# 新模板（EUM-1491A / JUM-1482）：局部作用域变量 qty / country + 辅助函数
PREP_OLD_B = "        var total = (unitPrice() * qty + shipping(country, qty)).toFixed(2);"
PREP_NEW_B = """        var total = (unitPrice() * qty + shipping(country, qty)).toFixed(2);
        var _ppH1 = document.querySelector('h1');
        var _ppTitle = _ppH1 ? _ppH1.textContent.split('|')[0].trim() : 'CNC LCD Upgrade Kit';
        var _ppDestName = (DHL[country] || {}).name || country;"""

NEW_TEMPLATE_B = """{ purchase_units: [{
          description: (_ppTitle + ' | qty ' + qty + ' | DHL ' + _ppDestName).slice(0, 127),
          custom_id: '__SLUG__|qty=' + qty + '|dest=' + country,
          invoice_id: 'CNCD-' + Date.now(),
          items: [{
            name: _ppTitle.slice(0, 127),
            quantity: '' + qty,
            unit_amount: { currency_code: 'USD', value: unitPrice().toFixed(2) }
          }],
          amount: {
            currency_code: 'USD',
            value: total,
            breakdown: {
              item_total: { currency_code: 'USD', value: (unitPrice() * qty).toFixed(2) },
              shipping: { currency_code: 'USD', value: shipping(country, qty).toFixed(2) }
            }
          }
        }] }"""


def patch(html: str, slug: str):
    if OLD not in html:
        return None, "createOrder 目标行不存在"
    if "_ppTitle" in html:
        return None, "已打过补丁"

    if PREP_OLD in html:
        out = html.replace(PREP_OLD, PREP_NEW, 1)
        out = out.replace(OLD, NEW_TEMPLATE.replace("__SLUG__", slug), 1)
        return out, "ok"

    if PREP_OLD_B in html:
        out = html.replace(PREP_OLD_B, PREP_NEW_B, 1)
        out = out.replace(OLD, NEW_TEMPLATE_B.replace("__SLUG__", slug), 1)
        return out, "ok"

    return None, "total 计算行不存在"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sorted(glob.glob(os.path.join(root, "products", "*.html")))

    changed, skipped = [], []
    for f in files:
        html = open(f, encoding="utf-8").read()
        if "actions.order.create" not in html:
            continue
        slug = os.path.splitext(os.path.basename(f))[0]
        out, status = patch(html, slug)
        if out is None:
            skipped.append((os.path.basename(f), status))
            continue
        changed.append(os.path.basename(f))
        if args.apply:
            open(f, "w", encoding="utf-8", newline="").write(out)

    print("patched:", len(changed), "| skipped:", len(skipped))
    for name, why in skipped:
        print("  SKIP", name, "-", why)
    if changed and not args.apply:
        print("\n前三个将修改的文件：")
        for n in changed[:3]:
            print("  ", n)
    if not args.apply:
        print("\n(dry run，未写入。加 --apply 生效)")


if __name__ == "__main__":
    main()
