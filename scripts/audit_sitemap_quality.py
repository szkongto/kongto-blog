# -*- coding: utf-8 -*-
"""
audit_sitemap_quality.py —— sitemap 门禁用例

核心设计：两个键分离
  301 源判定  -> URL 路径键（保留目录尾斜杠，不补 index.html）
  文件/内容检查 -> relpath 键（目录补 index.html）
若复用同一函数，/、/products/ 等 10 个目录 loc 会被 _redirects 的
/index.html 规则误判为 301 源（假阳性）。

用法：
    python scripts/audit_sitemap_quality.py            # 静态检查 sitemap.xml + zh/sitemap.xml
    python scripts/audit_sitemap_quality.py --online   # 追加逐条线上 GET（约 2 分钟）

退出码：0 = 通过；1 = 有 fail。
"""
import os
import re
import sys
import argparse
import xml.etree.ElementTree

REPO = os.environ.get("SITEMAP_REPO") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://cncdisplay.com"
SITEMAPS = ["sitemap.xml", "zh/sitemap.xml"]
REDIRECT_FILES = ["_redirects"]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_BLOCK_RE = re.compile(r"<url>.*?</url>", re.DOTALL)
LOC_RE = re.compile(r"<loc>(.*?)</loc>")
LASTMOD_RE = re.compile(r"<lastmod>(.*?)</lastmod>")
REDIRECT_LINE_RE = re.compile(r"^(\S+)\s+(\S+)\s+(301|302|307|308)\s*$")
# noindex 判定：不依赖 name= 与 content= 的书写顺序
META_TAG_RE = re.compile(r"<meta\b[^>]*>", re.I)


def has_noindex(html):
    """两个独立正则取交集：meta 标签内同时出现 robots 与 noindex。"""
    for tag in META_TAG_RE.findall(html):
        low = tag.lower()
        if "robots" in low and "noindex" in low:
            return True
    return False


def loc_to_relpath(loc):
    """<loc> -> 仓库相对文件路径（目录补 index.html）。仅用于文件/内容检查。"""
    if not loc.startswith(DOMAIN):
        return None
    path = loc[len(DOMAIN):]
    if path in ("", "/"):
        return "index.html"
    rel = path.lstrip("/")
    if rel.endswith("/"):
        return rel + "index.html"
    return rel


def loc_to_urlkey(loc):
    """<loc> -> _redirects 源路径键（保留前导 / 与目录尾斜杠，绝不补 index.html）。

    仅用于 301 源比对：
        https://cncdisplay.com/          -> "/"
        https://cncdisplay.com/products/ -> "/products/"
        https://cncdisplay.com/a/b.html  -> "/a/b.html"
    """
    if not loc.startswith(DOMAIN):
        return None
    path = loc[len(DOMAIN):]
    return path if path else "/"


def redirect_source_keys():
    srcs = set()
    for name in REDIRECT_FILES:
        p = os.path.join(REPO, name)
        if not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = REDIRECT_LINE_RE.match(line.strip())
                if m:
                    srcs.add(m.group(1))
    return srcs


def parse_sitemap(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    entries = []
    for block in URL_BLOCK_RE.findall(content):
        loc_m = LOC_RE.search(block)
        if not loc_m:
            continue
        lm_m = LASTMOD_RE.search(block)
        entries.append((loc_m.group(1).strip(), lm_m.group(1).strip() if lm_m else ""))
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--online", action="store_true", help="追加线上逐条 GET")
    args = ap.parse_args()

    fails, warns = [], []
    srcs = redirect_source_keys()
    print("loaded {} redirect source keys from {}".format(len(srcs), ",".join(REDIRECT_FILES)))

    for sm_rel in SITEMAPS:
        sm_path = os.path.join(REPO, sm_rel)
        if not os.path.isfile(sm_path):
            warns.append("{}: 文件不存在，跳过".format(sm_rel))
            continue
        # XML 结构完整性：正则解析看不出缺 </urlset> 这类错误，必须走真解析器
        try:
            xml.etree.ElementTree.parse(sm_path)
        except xml.etree.ElementTree.ParseError as exc:
            fails.append("{}: XML 不合法 {}".format(sm_rel, exc))

        entries = parse_sitemap(sm_path)
        locs = [e[0] for e in entries]
        print("\n[{}] {} 条".format(sm_rel, len(entries)))

        for loc, _ in entries:
            if not loc.startswith(DOMAIN):
                fails.append("{}: 非本站 loc {}".format(sm_rel, loc))

        seen = set()
        for loc in locs:
            if loc in seen:
                fails.append("{}: 重复 loc {}".format(sm_rel, loc))
            seen.add(loc)

        for loc, lm in entries:
            if not lm:
                fails.append("{}: 缺 lastmod {}".format(sm_rel, loc))
            elif not DATE_RE.match(lm):
                fails.append("{}: lastmod 非法 '{}' {}".format(sm_rel, lm, loc))

        for loc, _ in entries:
            rel = loc_to_relpath(loc)
            if rel and not os.path.isfile(os.path.join(REPO, rel)):
                fails.append("{}: 本地文件不存在 {} (rel={})".format(sm_rel, loc, rel))

        # 关键：URL 键，不是 relpath 键
        for loc, _ in entries:
            key = loc_to_urlkey(loc)
            if key and key in srcs:
                fails.append("{}: 301 源不得入 sitemap {}".format(sm_rel, loc))

        for loc, _ in entries:
            rel = loc_to_relpath(loc)
            if not rel:
                continue
            fp = os.path.join(REPO, rel)
            if not os.path.isfile(fp):
                continue
            try:
                html = open(fp, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if has_noindex(html):
                fails.append("{}: noindex 页不得入 sitemap {}".format(sm_rel, loc))

        if args.online:
            import ssl, http.client
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            for loc in locs:
                path = loc[len(DOMAIN):] or "/"
                try:
                    conn = http.client.HTTPSConnection("cncdisplay.com", 443, timeout=25, context=ctx)
                    conn.request("GET", path, headers={"User-Agent": "Mozilla/5.0 sitemap-audit"})
                    resp = conn.getresponse()
                    body = resp.read()
                    code, loc_hdr = resp.status, resp.getheader("Location", "")
                    conn.close()
                except Exception as exc:
                    fails.append("{}: 线上探测失败 {} ({})".format(sm_rel, loc, exc))
                    continue
                if code != 200:
                    fails.append("{}: 线上非 200 {} -> {} {}".format(sm_rel, loc, code, loc_hdr))
                    continue
                low = body.lower()
                if b'http-equiv="refresh"' in low or b"http-equiv='refresh'" in low:
                    fails.append("{}: 线上是 meta-refresh 壳 {}".format(sm_rel, loc))

    print("\n" + "=" * 60)
    for f in fails:
        print("FAIL " + f)
    for w in warns:
        print("WARN " + w)
    print("=" * 60)
    print("RESULT: {} fail, {} warn".format(len(fails), len(warns)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
