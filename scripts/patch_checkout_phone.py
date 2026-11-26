"""给产品页结账加电话输入框，并把号码编码进 PayPal 的 custom_id。

PayPal 的 order 对象不返回收件人电话，DHL 出口必须有电话，所以在站内收：
  - 在 Buy Now 面板的国家选择后面插入一个 Phone 输入框（id=buyerPhone）
  - createOrder 里读该值，清洗成数字+号，追加到 custom_id: `...|tel=+12485550100`

用法：
  python scripts/patch_checkout_phone.py            # dry run，只报告
  python scripts/patch_checkout_phone.py --apply    # 实际写入
"""

import argparse
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ANCHOR = '          <div id="paypal-button-container"'

PHONE_ROW = """            <div><label class="th-bold">Phone:</label>

              <input id="buyerPhone" class="qty-input" type="tel" inputmode="tel" autocomplete="tel" maxlength="32" placeholder="For DHL delivery" style="width:180px">

            </div>

"""

DEST_A = "'|dest=' + window._selectedCountry,"
DEST_B = "'|dest=' + country,"

PHONE_VAR = (
    "var _ppPhone = ((document.getElementById('buyerPhone') || {}).value || '')"
    ".replace(/[^0-9+]/g, '').slice(0, 20);"
)


def patch(html: str, nl: str = "\n"):
    if "actions.order.create" not in html:
        return None, "no paypal"
    if "buyerPhone" in html:
        return None, "already patched"
    if ANCHOR not in html:
        return None, "anchor missing"

    row = PHONE_ROW.replace("\n", nl)
    out = html.replace(ANCHOR, row + ANCHOR, 1)

    m = re.search(r"^([ \t]*)var _ppDestName = .*$", out, re.MULTILINE)
    if not m:
        return None, "_ppDestName missing"
    indent = m.group(1)
    out = out[: m.end()] + nl + indent + PHONE_VAR + out[m.end():]

    if DEST_A in out:
        out = out.replace(DEST_A, "'|dest=' + window._selectedCountry + '|tel=' + _ppPhone,", 1)
    elif DEST_B in out:
        out = out.replace(DEST_B, "'|dest=' + country + '|tel=' + _ppPhone,", 1)
    else:
        return None, "custom_id line missing"

    return out, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = sorted(glob.glob(os.path.join(root, "products", "*.html")))

    changed, skipped = [], []
    for f in files:
        html = open(f, encoding="utf-8", newline="").read()
        nl = "\r\n" if "\r\n" in html else "\n"
        out, status = patch(html, nl)
        if out is None:
            if status not in ("no paypal",):
                skipped.append((os.path.basename(f), status))
            continue
        changed.append(os.path.basename(f))
        if args.apply:
            # 仓库里的 blob 是 LF；统一写 LF，避免整文件行尾 diff
            open(f, "w", encoding="utf-8", newline="").write(out.replace("\r\n", "\n"))

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
