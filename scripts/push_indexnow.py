#!/usr/bin/env python
"""Push changed page URLs to IndexNow (Bing / Yandex / Seznam).

只在部署完成后调用：先把本次 push 改动的页面映射成公网 URL，验证线上返回
200，再提交给 IndexNow。IndexNow 失败不阻断部署（workflow 里 continue-on-error）。

用法:
  python scripts/push_indexnow.py --base HEAD~1        # 按 git diff 取改动页
  python scripts/push_indexnow.py --urls /a.html,/b/   # 指定 URL
  python scripts/push_indexnow.py --base HEAD~1 --dry-run
"""

import argparse
import concurrent.futures as futures
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
HOST = "cncdisplay.com"
KEY_FILE = ROOT / "indexnow-key.txt"
KEY_LOCATION = f"https://{HOST}/{KEY_FILE.name}"
API = "https://api.indexnow.org/indexnow"
MAX_PER_REQUEST = 10000


def load_key() -> str:
    if not KEY_FILE.exists():
        sys.exit(f"key file missing: {KEY_FILE}")
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not 8 <= len(key) <= 128:
        sys.exit(f"key length invalid ({len(key)}): {KEY_FILE}")
    return key


def changed_files(base: str) -> list[str]:
    """本次 push 新增/修改的文件（删除的不算，删除不该推给 IndexNow）。"""
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AM", base, "HEAD"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if out.returncode != 0:
        sys.exit(f"git diff failed: {out.stderr.strip()[:300]}")
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def to_url(rel: str) -> str | None:
    """仓库相对路径 -> 公网 URL。只处理进入产物的 .html 页面。"""
    if not rel.endswith(".html"):
        return None
    if not (SITE / rel).is_file():
        return None  # 未进部署产物（脚本/文档/未跟踪文件）
    if rel == "index.html":
        return f"https://{HOST}/"
    if rel.endswith("/index.html"):
        return f"https://{HOST}/{rel[: -len('index.html')]}"
    return f"https://{HOST}/{rel}"


def live_ok(url: str) -> bool:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "indexnow-push"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status == 200
    except Exception:
        return False


def push(urls: list[str], key: str) -> bool:
    payload = json.dumps({
        "host": HOST,
        "key": key,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(
        API, data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"IndexNow HTTP {resp.status}  urls={len(urls)}")
            return resp.status in (200, 202)
    except urllib.error.HTTPError as e:
        print(f"IndexNow HTTP {e.code} {e.reason}  urls={len(urls)}")
        return False
    except Exception as e:
        print(f"IndexNow request failed: {e}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="git ref，比较 base..HEAD 的改动")
    ap.add_argument("--urls", help="逗号分隔的绝对路径 URL")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-live-check", action="store_true")
    args = ap.parse_args()

    key = load_key()

    if args.urls:
        urls = [f"https://{HOST}{u.strip()}" for u in args.urls.split(",") if u.strip()]
    elif args.base:
        rels = changed_files(args.base)
        print(f"改动文件 {len(rels)} 个")
        urls = [u for u in (to_url(r) for r in rels) if u]
    else:
        sys.exit("need --base or --urls")

    urls = sorted(set(urls))
    if not urls:
        print("没有需要推送的页面，跳过")
        return 0

    if not args.skip_live_check:
        with futures.ThreadPoolExecutor(8) as ex:
            ok = list(ex.map(live_ok, urls))
        dead = [u for u, good in zip(urls, ok) if not good]
        if dead:
            print(f"线上非 200，剔除 {len(dead)} 条:")
            for u in dead[:10]:
                print(f"  {u}")
        urls = [u for u, good in zip(urls, ok) if good]

    if not urls:
        print("全部非 200，不推送")
        return 0

    for u in urls[:10]:
        print(f"  {u}")
    if len(urls) > 10:
        print(f"  ... 共 {len(urls)}")

    if args.dry_run:
        print("[dry-run] 不发送")
        return 0

    ok = True
    for i in range(0, len(urls), MAX_PER_REQUEST):
        ok = push(urls[i:i + MAX_PER_REQUEST], key) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
