"""把产品页结账的电话改成必填，并在 PayPal 弹窗前拦截。

用户要求（2026-11-27）：下单时电话与收货信息必须齐全，否则无法发货。
PayPal 的 order 对象不返回收件人电话，所以电话由站内收，站内必须先挡住空号码：
  - Phone 标签加红色 *，输入框加 required / aria-required
  - 号码必须在 7-15 位数字之间（E.164 上限 15）
  - 校验放在 paypal.Buttons 的 onClick 里：不合格就不打开 PayPal 窗口，
    错误文案写到 #ppFormError，不弹 alert
  - 收货地址由 PayPal 结账页必填收集，页面补一句提示

用法：
  python scripts/patch_checkout_required.py            # dry run，只报告
  python scripts/patch_checkout_required.py --apply    # 实际写入
"""

import argparse
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

PHONE_RE = re.compile(
    r'<div><label class="th-bold">Phone:</label>\s*<input id="buyerPhone"[^>]*>\s*</div>'
)

PHONE_NEW = (
    '<div><label class="th-bold">Phone <span style="color:#c00">*</span>:</label>\n'
    '              <input id="buyerPhone" class="qty-input" type="tel" inputmode="tel" '
    'autocomplete="tel" required aria-required="true" maxlength="32" '
    'placeholder="Required - DHL needs it" style="width:180px" '
    'oninput="var e=document.getElementById(\'ppFormError\');if(e){e.style.display=\'none\'}">\n'
    '            </div>\n'
    '            <div id="ppFormError" role="alert" '
    'style="display:none;color:#c00;font-size:13px;margin:6px 0"></div>'
)

ONCLICK_RE = re.compile(r'^([ \t]*)paypal\.Buttons\(\{', re.MULTILINE)

ONCLICK = """{i}onClick: function(data, actions) {{
{i}  var _perr = document.getElementById('ppFormError');
{i}  var _pcountry = document.getElementById('shippingCountry');
{i}  var _pinput = document.getElementById('buyerPhone');
{i}  var _pdigits = _pinput ? String(_pinput.value || '').replace(/\\D/g, '') : '';
{i}  var _pmsg = '';
{i}  if (!_pcountry || !_pcountry.value) {{
{i}    _pmsg = 'Please select a shipping country.';
{i}  }} else if (_pdigits.length < 7 || _pdigits.length > 15) {{
{i}    _pmsg = 'Please enter your phone number with country code (7-15 digits). DHL needs a phone number to deliver.';
{i}  }}
{i}  if (_pmsg) {{
{i}    if (_perr) {{ _perr.textContent = _pmsg; _perr.style.display = 'block'; }}
{i}    if (_pdigits.length < 7 && _pinput) {{ _pinput.focus(); }}
{i}    if (actions && actions.reject) {{ return actions.reject(); }}
{i}    return false;
{i}  }}
{i}  if (_perr) {{ _perr.style.display = 'none'; _perr.textContent = ''; }}
{i}  return actions && actions.resolve ? actions.resolve() : true;
{i}}},
"""

HINT_OLD = '<p class="hint-sm">🔒 Secure checkout via PayPal. Credit/debit cards accepted.</p>'
HINT_NEW = (
    HINT_OLD + '\n'
    '          <p class="hint-sm">📦 Your full ship-to address (street, city, postal code) '
    'is entered on the PayPal page. Incomplete address or missing phone delays shipment.</p>'
)


def patch(html: str):
    if "actions.order.create" not in html:
        return None, "no paypal"
    if "ppFormError" in html:
        return None, "already patched"

    out, n = PHONE_RE.subn(PHONE_NEW, html)
    if n != 1:
        return None, f"phone block matched {n}"

    m = ONCLICK_RE.search(out)
    if not m:
        return None, "paypal.Buttons line missing"
    ind = m.group(1) + "  "
    out = out[: m.end()] + "\n" + ONCLICK.format(i=ind) + out[m.end():]
    if HINT_OLD not in out:
        return None, "checkout hint missing"
    out = out.replace(HINT_OLD, HINT_NEW, 1)
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
        out, status = patch(html)
        if out is None:
            if status not in ("no paypal",):
                skipped.append((os.path.basename(f), status))
            continue
        changed.append(os.path.basename(f))
        if args.apply:
            open(f, "w", encoding="utf-8", newline="").write(out.replace("\r\n", "\n"))

    print("patched:", len(changed), "| skipped:", len(skipped))
    for name, why in skipped:
        print("  SKIP", name, "-", why)
    if not args.apply:
        print("\n(dry run，未写入。加 --apply 生效)")


if __name__ == "__main__":
    main()
