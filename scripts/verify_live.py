#!/usr/bin/env python
"""部署后活站核验：本次 push 改动的页面必须真的能在 cncdisplay.com 上打开。

背景（2026-11-28 用户要求）：CI 报 success 只代表 artifact 上传成功，不代表
Pages 已经把这份产物切到线上。部署切换窗口内会有瞬态 404（GSC 那次 16:17:06Z
抓取就撞在 16:15:56Z 完成部署的切换窗口里）。所以部署完要自己 curl 一遍。

判定：
  1. 跟随重定向，最终状态必须是 200（`_redirects` 死源页 301 到落点页，落点活
     就通过，落点死就报错，比只看首跳更严）。
  2. 最终 URL 必须仍在 cncdisplay.com（301 跳外站算失败）。
  3. 响应体要像页面：含 `<title`，且长度 > 500 字节（挡住空壳/软 404）。

Pages 传播有延迟，默认重试 12 轮 × 15 秒（约 3 分钟），全部失败才 exit 1。

用法:
  python scripts/verify_live.py --base HEAD~1     # CI 与本地通用
  python scripts/verify_live.py --urls /a.html,/zh/b.html
"""

import argparse
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
HOST = "cncdisplay.com"
UA = "Mozilla/5.0 (compatible; kongto-live-check/1.0)"

# 与 scripts/build_site_artifact.py 的 INCLUDE_DIRS 保持一致：
# 只有这些目录下的 html 会进部署产物，别的改了也不用核。
SITE_DIRS = (
    "zh", "products", "posts", "images", "brands", "css",
    "docs", "guides", "knowledge", "hub", ".well-known",
)


def changed_pages(base: str) -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AM", base, "HEAD"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if out.returncode != 0:
        sys.exit(f"git diff failed: {out.stderr.strip()[:300]}")
    pages = []
    for line in out.stdout.splitlines():
        rel = line.strip().replace("\\", "/")
        if not rel.endswith(".html"):
            continue
        top = rel.split("/")[0]
        if "/" in rel and top not in SITE_DIRS:
            continue
        pages.append(rel)
    return pages


def to_url(rel: str) -> str:
    if rel == "index.html":
        return f"https://{HOST}/"
    if rel.endswith("/index.html"):
        return f"https://{HOST}/{rel[: -len('index.html')]}"
    return f"https://{HOST}/{rel}"


def check(url: str) -> tuple[bool, str]:
    """返回 (是否通过, 说明)。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            status = resp.status
            final = resp.geturl()
            body = resp.read(65536)
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, f"ERR {type(e).__name__}: {str(e)[:80]}"

    if status != 200:
        return False, f"HTTP {status}"
    if urlparse(final).netloc != HOST:
        return False, f"redirected off-site: {final}"
    if b"<title" not in body.lower():
        return False, "no <title in body"
    if len(body) < 500:
        return False, f"body too short ({len(body)}B)"
    return True, "200"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="git ref，比较 base..HEAD 的改动页")
    ap.add_argument("--urls", help="逗号分隔的站内路径，如 /products/x.html")
    ap.add_argument("--retries", type=int, default=12)
    ap.add_argument("--delay", type=float, default=15.0)
    args = ap.parse_args()

    if args.urls:
        pages = [u.strip() for u in args.urls.split(",") if u.strip()]
        urls = {p if p.startswith("http") else f"https://{HOST}/{p.lstrip('/')}" for p in pages}
    elif args.base:
        pages = changed_pages(args.base)
        urls = {to_url(p) for p in pages}
    else:
        sys.exit("need --base or --urls")

    urls = sorted(urls)
    if not urls:
        print("没有改动的页面，跳过活站核验")
        return 0

    print(f"待核验 {len(urls)} 个页面")
    pending = urls
    for attempt in range(1, args.retries + 1):
        failed = []
        for u in pending:
            ok, why = check(u)
            if not ok:
                failed.append((u, why))
                print(f"[{attempt}/{args.retries}] FAIL {why}  {u}")
        if not failed:
            print(f"全部 {len(urls)} 页活站 200")
            return 0
        pending = [u for u, _ in failed]
        if attempt < args.retries:
            time.sleep(args.delay)

    print(f"仍有 {len(pending)} 页非 200:")
    for u in pending:
        print(f"  {u}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
