# -*- coding: utf-8 -*-
"""AI 可见度监测 — 基线对比。
用法: python compare.py <baseline.json> <rerun.json>
输出: 每个 (model × llm) 的进步/退步/持平,加总体趋势。
baseline 是 llms.txt 扩展前的记录,rerun 是 2-4 周后的新抽测。
"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CNC_DOMAINS = ["cncdisplay.com", "cncdisplay", "kongto", "江图"]


def key_of(r):
    return (r["model"], r["llm"])


def score_raw(model, llm, answer):
    text = (answer or "").lower()
    mentioned = any(d.lower() in text for d in CNC_DOMAINS)
    early = mentioned and any(d.lower() in text[: max(len(text) // 3, 200)] for d in CNC_DOMAINS)
    url = "product_page" if re.search(r"cncdisplay\.com/products/", text) else (
        "pdf" if re.search(r"cncdisplay\.com/[^)\s]*\.pdf", text) else (
        "home" if mentioned else "none"))
    return {"model": model, "llm": llm, "referenced": mentioned,
            "rank": 1 if (mentioned and early) else (2 if mentioned else 0),
            "cited_url_type": url}


def load(path):
    data = json.load(open(path, encoding='utf-8'))
    return {key_of(r): r for r in data.get("results", [])}, data.get("date", path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: compare.py <baseline.json> <rerun.json>")
        sys.exit(1)
    base, base_date = load(sys.argv[1])
    new, new_date = load(sys.argv[2])

    print(f"对比 {base_date}  →  {new_date}\n")
    delta_ref = delta_pp = up = down = same = 0
    for k, r in sorted(new.items()):
        b = base.get(k)
        if not b:
            print(f"  [新] {k[0]} / {k[1]}: ref={r['referenced']} url={r['cited_url_type']}")
            continue
        d_ref = int(r["referenced"]) - int(b["referenced"])
        d_url = (r["cited_url_type"] == "product_page") - (b["cited_url_type"] == "product_page")
        delta_ref += d_ref
        delta_pp += d_url
        if d_ref > 0 or d_url > 0:
            up += 1
        elif d_ref < 0 or d_url < 0:
            down += 1
        else:
            same += 1
        flag = {1: "▲进步", -1: "▼退步", 0: "·持平"}[1 if (d_ref or d_url) > 0 else (-1 if (d_ref or d_url) < 0 else 0)]
        print(f"  {flag} {k[0]} / {k[1]}: "
              f"ref {int(b['referenced'])}→{int(r['referenced'])} "
              f"url {b['cited_url_type']}→{r['cited_url_type']}")

    print(f"\n=== 汇总 ===\n被引次数 {delta_ref:+d} | 产品页引用 {delta_pp:+d} | "
          f"进步 {up} 退步 {down} 持平 {same}")
    print("llms.txt 扩展生效判据: ChatGPT 行被引次数上升 + 引用类型从 pdf/home → product_page")
