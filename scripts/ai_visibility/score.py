# -*- coding: utf-8 -*-
"""AI 可见度监测 — 结果计分器。
输入: LLM 回答文本 (人工从 Bright Data AI insights 粘贴,或自动读 baseline json)
输出: 结构化计分 (referenced / rank / cited_url_type / reason_given)
用法:
  python score.py <result.json>            # 对已有 json 计分
  python score.py --interactive            # 交互式输入回答文本
计分由脚本自动做,不靠人眼 —— 保证 2-4 周后重跑可比。
"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CNC_DOMAINS = [
    "cncdisplay.com", "cncdisplay", "kongto", "江图",
]
URL_PATTERNS = {
    "product_page": r"cncdisplay\.com/products/",
    "home":        r"cncdisplay\.com(?:/index\.html)?(?:\?|/|$)",
    "pdf":         r"cncdisplay\.com/[^)\s]*\.pdf",
    "article":     r"cncdisplay\.com/(?:posts|guides|docs)/",
}


def classify_url_type(text: str) -> str:
    if re.search(URL_PATTERNS["product_page"], text):
        return "product_page"
    if re.search(URL_PATTERNS["pdf"], text):
        return "pdf"
    if re.search(URL_PATTERNS["article"], text):
        return "article"
    if re.search(URL_PATTERNS["home"], text):
        return "home"
    return "none"


def score_answer(model_label: str, llm: str, answer_text: str) -> dict:
    text = (answer_text or "").lower()
    mentioned = any(d.lower() in text for d in CNC_DOMAINS)
    url_type = classify_url_type(answer_text or "")

    # rank: 找推荐列表里的位次。粗判: 是否在首句/前 1/3 出现
    first_third = text[: max(len(text) // 3, 200)]
    early = any(d.lower() in first_third for d in CNC_DOMAINS)

    # reason: 有 cncdisplay 域名 + 上下文有 because/since/offers/uses 等给因词
    has_reason_word = bool(re.search(r"because|since|offers?|provides?|compatible|factory|direct", text))
    reason_given = mentioned and has_reason_word

    return {
        "model": model_label,
        "llm": llm,
        "referenced": mentioned,
        "rank": 1 if (mentioned and early) else (2 if mentioned else 0),
        "cited_url_type": url_type if mentioned else "none",
        "reason_given": reason_given,
        "raw_fragment": (answer_text or "")[:400],
    }


def score_file(path: str) -> list:
    data = json.load(open(path, encoding='utf-8'))
    results = []
    for item in data.get("results", []):
        results.append(score_answer(item["model"], item["llm"], item.get("answer", "")))
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        print("粘贴 LLM 回答文本 (Ctrl+Z 结束):")
        buf = sys.stdin.read()
        print(json.dumps(score_answer("interactive", "unknown", buf), ensure_ascii=False, indent=2))
    elif len(sys.argv) > 1:
        res = score_file(sys.argv[1])
        for r in res:
            print(json.dumps(r, ensure_ascii=False))
        print(f"\n合计 {len(res)} 条 | 被引 {sum(1 for r in res if r['referenced'])} | "
              f"产品页 {sum(1 for r in res if r['cited_url_type']=='product_page')}")
    else:
        print("用法: score.py <result.json>  |  score.py --interactive")
