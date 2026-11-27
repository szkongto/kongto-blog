"""给产品页结账加「How did you find us?」下拉，并把渠道编码进 PayPal 的 custom_id。

背景：2026-11-19 那单 $507 的买家来自 Bing 自然搜索，但订单里没有任何渠道字段，
只能事后翻 Cloudflare 日志 + Bing 站长工具反推。站内加一个非必填下拉，把渠道
直接写进订单（`|src=bing`），以后每单自带归因，不再靠猜。

用法:
  python scripts/patch_checkout_source.py            # dry run，只报告
  python scripts/patch_checkout_source.py --apply    # 实际写入
"""

import argparse
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

PHONE_INPUT = 'id="buyerPhone"'

SOURCE_ROW = """            <div><label class="th-bold">How did you find us?</label>
              <select id="buyerSource" class="qty-input" style="width:180px">
                <option value="">Select (optional)</option>
                <option value="google">Google search</option>
                <option value="bing">Bing / other search</option>
                <option value="youtube">YouTube</option>
                <option value="ai">AI assistant (ChatGPT etc.)</option>
                <option value="referral">Referral / forum</option>
                <option value="other">Other</option>
              </select></div>
"""

SOURCE_VAR = (
    "var _ppSrc = ((document.getElementById('buyerSource') || {}).value || '')"
    ".replace(/[^a-z]/gi, '').toLowerCase().slice(0, 12);"
)

TEL_ID = "'|tel=' + _ppPhone"
TEL_SRC = "'|tel=' + _ppPhone + '|src=' + _ppSrc"


def patch(html: str, nl: str = "\n"):
    if "actions.order.create" not in html:
        return None, "no paypal"
    if 'id="buyerSource"' in html:
        return None, "already patched"
    if PHONE_INPUT not in html:
        return None, "phone input missing"
    if TEL_ID not in html:
        return None, "custom_id tel segment missing"

    # 1) 下拉插在电话行后面（电话行的 </div> 之后）
    start = html.find(PHONE_INPUT)
    end = html.find("</div>", start)
    if end == -1:
        return None, "phone row end missing"
    end += len("</div>")
    out = html[:end] + nl + SOURCE_ROW.replace("\n", nl).rstrip("\n") + html[end:]

    # 2) 变量声明插在 _ppPhone 那行后面
    line = "var _ppPhone = ((document.getElementById('buyerPhone')"
    pos = out.find(line)
    if pos == -1:
        return None, "_ppPhone var missing"
    eol = out.find("\n", pos)
    indent = out[out.rfind("\n", 0, pos) + 1:pos]
    out = out[:eol + 1] + indent + SOURCE_VAR + nl + out[eol + 1:]

    # 3) custom_id 追加 |src=
    out = out.replace(TEL_ID, TEL_SRC, 1)

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
            open(f, "w", encoding="utf-8", newline="").write(out)

    print(("APPLIED" if args.apply else "DRY RUN") + f": {len(changed)} pages")
    for name in changed[:5]:
        print("  +", name)
    if len(changed) > 5:
        print(f"  ... {len(changed) - 5} more")
    for name, why in skipped:
        print("  SKIP", name, why)
    return 0 if not skipped else 1


if __name__ == "__main__":
    sys.exit(main())
