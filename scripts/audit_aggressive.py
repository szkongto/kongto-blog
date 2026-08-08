#!/usr/bin/env python3
"""
audit_aggressive.py — 攻击式内容审计门禁
=========================================
catch check_dupes.py (精确标题匹配) 漏掉的"近似重复"内容。

根因 (2026-08-09 自省):
  旧 check_dupes.py 只做 <title> 精确匹配。外部 AI 能发现的问题
  ——不同标题但正文 99% 相同 (EUM-1491A vs JUM-1482)、同文双文件——
  全靠人工/外部工具才能看到。此脚本把"正文相似度"变成门禁。

用法:
  python scripts/audit_aggressive.py [--threshold 0.55] [--hard 0.90] [--dir posts]
  退出码: 0 = 通过; 1 = 发现近似重复 (≥hard 阈值且双方均可索引)

规则:
  - 正文提取: 去标签/去空白, <body> 内文本
  - 跳过 meta-refresh 壳页 (title 是 Redirecting...) 与 noindex 页
  - 同型号判断: 文件名完整型号串 (a61l-0001-0072 ≠ a61l-0001-0076)。
    FANUC 等前缀共享但尾号不同的 = 不同型号, 永不判重复。
    不同型号共享模板 (菜单/页脚/CTA) = 正常 SEO 独立页, 仅计数不拦。
  - 真重复 (FAIL): 同型号 + 正文相似 ≥hard + 双方均可索引
  - 报告只列同型号对; 不同型号对只计数 (避免模板噪声刷屏)
"""
import io
import os
import re
import sys
from difflib import SequenceMatcher

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DEFAULT_REPORT_THRESHOLD = 0.55
DEFAULT_HARD_THRESHOLD = 0.90
DEFAULT_PRODUCT_HARD = 0.99  # products 分享 spec 模板属正常, 仅 0.99 以上才硬拦
COMPARE_CHARS = 1200  # 只比较正文前 N 字符 (SequenceMatcher) — 够判近似, CI 保持秒级
MIN_BODY_LEN = 1500   # 正文过短不算完整文章, 不参与
PREFILTER_THRESHOLD = 0.30  # token-Jaccard 预筛下限, 低于此直接跳过

# 内容文章目录 (posts/knowledge) 近似重复 = 关键词自相蚕食, 硬拦
CONTENT_DIRS = {"posts", "knowledge"}
# products/ 目录: 同品牌产品共享 spec 模板是设计使然, 仅 0.99 近似才拦
PRODUCT_DIRS = {"products"}

import re as _re
WORD_RE = _re.compile(r"[a-z0-9]+", _re.I)


def token_shingles(text, k=3):
    """word n-gram set — 快速 Jaccard 预筛用"""
    words = WORD_RE.findall(text.lower())
    if len(words) < k:
        return set(words) if words else set()
    return {tuple(words[i : i + k]) for i in range(len(words) - k + 1)}


# 型号 token 提取 — 文件名/标题中"含数字的长 token"视为型号标识
# 例: bm09df, mdt962b, ct100, 1491a, 6fc5103, a61l
# 避免把 lcd/crt/upgrade/guide/article 等通用词当型号
_MODEL_STOP = {
    "article", "guide", "lcd", "crt", "display", "replacement", "upgrade",
    "retrofit", "comparison", "repair", "maintenance", "cost", "content",
    "industrial", "series", "custom", "case", "study", "kongto", "zh", "en",
    "posts", "products", "index", "html", "complete", "screen", "module",
    "faq", "press", "release", "technical", "practical", "installation",
    "step", "breathe", "new", "life", "into", "aging", "your", "vs", "and",
    "the", "for", "with", "from", "mitsubishi", "fanuc", "siemens", "haas",
    "okuma", "mazak", "heidenhain", "totoku", "toshiba", "matsushita",
    "nancy", "nanjing", "zhongjing", "display", "monitor", "color",
}

# 型号标识 = 完整部件号串 (分隔符 - 或 _ 均可), 例如:
#   a61l-0001-0072 / bm09df / eum-1491a / fcua-ct100 / 6fc5103 / mdt962b
# 必须整串提取 — 拆碎片会把 a61l-0001-0072 拆成 a61l+0001+0072,
# 让不同型号 (0072 vs 0076) 误判为同型号。
# 规则: 字母开头 → 数字 → 可选字母, 后续段以分隔符接数字开头 (排除 -lcd / -upgrade)。
# 关键 (2026-08-09 用户纠正): FANUC 型号前缀全同只尾号不同 (a61l-0001-0092 vs
# 0095) 是不同型号, 必须整串区分。下划线文件名 (article_20260503_FANUC_A61L_0001_0092_LCD)
# 也必须吃到纯数字尾段, 否则全部塌缩成 a61l。
_MODEL_TOKEN_RE = _re.compile(
    r"[a-z]+(?:[-_]?\d[a-z0-9]*(?:[-_][a-z0-9]*\d[a-z0-9]*)*)"
)


def model_tokens(filepath):
    """从文件名提取完整型号串集合"""
    base = filepath.replace("\\", "/").split("/")[-1].lower()
    toks = set()
    for m in _MODEL_TOKEN_RE.finditer(base):
        tok = m.group(0).replace("_", "-")
        # 剔除纯日期段 (20260503) 与通用词
        if tok in _MODEL_STOP or re.search(r"\d{8}", tok):
            continue
        toks.add(tok)
    return toks


def model_match(toks_a, toks_b):
    """同型号判断: 完整串相等, 或一个串是另一个的段前缀。
    例: a61l-0001-0092 vs a61l-0001-0095 → 尾段不同, 非前缀 → 不同型号 (用户铁律)
        bm09df-e60       vs bm09df        → 前缀 → 同型号 (系列后缀可省略)
    """
    for ta in toks_a:
        for tb in toks_b:
            if ta == tb or ta.startswith(tb + "-") or tb.startswith(ta + "-"):
                return True
    return False

SKIP_DIRS = {"_archive", "en_bak", "_archive_audit", "images", "assets", ".git"}
DEFAULT_DIRS = ["posts", "products", "knowledge", "zh", "brands"]


def extract_body(filepath):
    try:
        with open(filepath, encoding="utf-8") as fh:
            txt = fh.read()
    except (OSError, UnicodeDecodeError):
        return None
    # 壳页 (meta-refresh) 跳过
    if re.search(r"<meta\s+http-equiv=[\"']?refresh", txt, re.I):
        return None
    m = re.search(r"<body>(.*?)</body>", txt, re.S)
    if not m:
        return None
    body = re.sub(r"<script.*?</script>", " ", m.group(1), flags=re.S)
    body = re.sub(r"<style.*?</style>", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    return body


def is_indexable(filepath):
    try:
        with open(filepath, encoding="utf-8") as fh:
            txt = fh.read()
    except (OSError, UnicodeDecodeError):
        return False
    if re.search(r"name=[\"']robots[\"'][^>]*content=[\"'][^\"']*noindex", txt, re.I):
        return False
    if re.search(r"content=[\"'][^\"']*noindex[\"'][^>]*name=[\"']robots", txt, re.I):
        return False
    return True


def get_title(filepath):
    try:
        with open(filepath, encoding="utf-8") as fh:
            txt = fh.read()
    except (OSError, UnicodeDecodeError):
        return "?"
    m = re.search(r"<title>(.*?)</title>", txt, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else "?"


def collect_html_files():
    files = []
    for d in DEFAULT_DIRS:
        if not os.path.isdir(d):
            continue
        for root, dirs, fs in os.walk(d):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for f in fs:
                if f.endswith(".html"):
                    files.append(os.path.join(root, f))
    return sorted(files)


def main():
    report_threshold = DEFAULT_REPORT_THRESHOLD
    hard_threshold = DEFAULT_HARD_THRESHOLD
    if "--threshold" in sys.argv:
        i = sys.argv.index("--threshold")
        report_threshold = float(sys.argv[i + 1])
    if "--hard" in sys.argv:
        i = sys.argv.index("--hard")
        hard_threshold = float(sys.argv[i + 1])

    files = collect_html_files()
    bodies, indexable, shingles = {}, {}, {}
    for f in files:
        b = extract_body(f)
        if b and len(b) >= MIN_BODY_LEN:
            bodies[f] = b
            indexable[f] = is_indexable(f)
            shingles[f] = token_shingles(b)

    def _norm(p):
        return p.replace("\\", "/")

    def _is_content(p):
        p = _norm(p)
        return any("/" + d + "/" in p or p.startswith(d + "/") for d in CONTENT_DIRS)

    def _is_product(p):
        p = _norm(p)
        return any("/" + d + "/" in p or p.startswith(d + "/") for d in PRODUCT_DIRS)

    def _stem(p):
        """文件名 stem (去扩展名) — 兜底判断同文双文件 (posts/ vs knowledge/ 同 slug)"""
        return re.sub(r"\.html$", "", p.replace("\\", "/").split("/")[-1])

    names = list(bodies)
    model_toks = {f: model_tokens(f) for f in names}
    same_pairs, failures = [], []
    diff_model_count = 0
    for i in range(len(names)):
        s_i = shingles[names[i]]
        mt_i = model_toks[names[i]]
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            s_j = shingles[b]
            # 预筛: token-Jaccard 太低, 正文不可能近似 (秒级)
            inter = len(s_i & s_j)
            if not s_i or not s_j or inter / min(len(s_i), len(s_j)) < PREFILTER_THRESHOLD:
                continue
            r = SequenceMatcher(None, bodies[a][:COMPARE_CHARS], bodies[b][:COMPARE_CHARS]).ratio()
            if r < report_threshold:
                continue
            both_indexable = indexable[a] and indexable[b]
            toks_b = model_toks[b]
            # 同型号判断:
            #   1) 完整型号串相等/段前缀 (a61l-0001-0092 vs 0095 尾段不同 → 不同型号)
            #   2) 双方都无型号 token 且文件名 stem 相同 → 同文双文件
            # 不同型号共享模板 (BM09DF vs MDT962B vs FCUA-CT100) = SEO 独立关键词页,
            # 即使正文 99% 相同也不判重复 — 只计数。
            same_model = model_match(mt_i, toks_b) or (not mt_i and not toks_b and _stem(a) == _stem(b))
            if not same_model:
                diff_model_count += 1
                continue
            # products/ 目录: 同品牌产品共享 spec 模板属设计使然, 且不同型号串
            # (mdt1283b vs mdt1283b-1a) = 独立 SEO 页, 仅 0.99 近似才硬拦。
            threshold = DEFAULT_PRODUCT_HARD if _is_product(a) else hard_threshold
            hard = both_indexable and r >= threshold
            same_pairs.append((r, a, b, both_indexable, hard))
            if hard:
                failures.append((r, a, b))

    print("=" * 80)
    print(f"攻击式审计: 扫描 {len(files)} 个 HTML, {len(names)} 篇完整正文文章")
    print(f"规则: 同型号(完整型号串) + 相似≥{hard_threshold} + 双方可索引 = 真重复(拦)")
    print(f"      不同型号共享模板(菜单/页脚/CTA) = 正常, 只计数不拦")
    print("=" * 80)
    print(f"同型号近重复对: {len(same_pairs)}   |   不同型号共享模板对: {diff_model_count} (正常, 不计重复)")

    if not same_pairs:
        print("✅ 无同型号重复")
        return 0

    same_pairs.sort(reverse=True)
    for r, a, b, both, hard in same_pairs:
        if hard:
            flag = "🛑 真重复"
        elif both:
            flag = "⚠️ 同型号可索引(内容需差异化)"
        else:
            flag = "ℹ️ 同型号(一方noindex)"
        print(f"{flag} {r:.2f}  [{('索引' if both else '一方noindex')}]")
        print(f"    {a}  |  {get_title(a)[:60]}")
        print(f"    {b}  |  {get_title(b)[:60]}")

    if failures:
        print("\n" + "=" * 80)
        print(f"🛑 FAIL: {len(failures)} 对真重复 (同型号 + 双方可索引 + ≥{hard_threshold})")
        for r, a, b in failures:
            print(f"    {r:.2f}  {a}  <->  {b}")
        return 1

    print("\n✅ 无 hard 级同型号重复 (未同时 indexable 的同型号对已由 noindex 收敛)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
