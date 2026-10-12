#!/usr/bin/env python3
"""Build the GitHub Pages deploy artifact.

背景（历史遗留缺陷）：deploy.yml 曾上传 `path: '.'`，即**仓库根 = 站点根**，
于是 scripts/ 、CLAUDE.md 、seo_reports/ 、backlinks_output/ 、tmp_*.txt 等
内部资料全部变成公网 URL（实测 https://cncdisplay.com/CLAUDE.md -> 200）。

本脚本按白名单把站点文件复制到 _site/ ，部署只上传 _site/ 。
构建后自检：被 HTML/JS 引用但产物里不存在的路径会被报出并让构建以非 0 退出，
以免出现"部署成功但站点 404"。

用法: python scripts/build_site_artifact.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"

# 站点内容目录（白名单：只有这些目录进产物）
INCLUDE_DIRS = [
    "zh", "products", "posts", "images", "brands", "css",
    "docs", "guides", "knowledge", "hub", ".well-known",
]

# 根目录必须随产物发布的文件
INCLUDE_ROOT_FILES = [
    "favicon.ico", "CNAME", ".nojekyll",
    "robots.txt", "sitemap.xml", "sitemap-images.xml",
    "llms.txt", "llms-full.txt", "feed.xml", "rsl.txt",
    "search-index.js", "search-index.json",
    "BingSiteAuth.xml", "indexnow-key.txt",
    "ddac7c800685a15fa23809dc08c3b6c9.txt",
    "fbd20d57-8f2e-4234-9ad0-b82a54444ba7.txt",
    "google7478b8e743977291.html",
    "baidu_verify_codeva-MOcuLxbSCp.html",
    "6FC3988-7FA20-CRT.jpg",
    "6FC3988-7FA20-PCB.jpg",
]

# 由 Cloudflare 边缘处理，不进产物
IGNORE_PREFIXES = ("/cdn-cgi/",)

REF_RE = re.compile(r"""["\x27](/(?!/)[A-Za-z0-9_\-./%]{1,200})["\x27]""")

# 明显的假路径：URL 编码片段、轮播页码（"/9"）
REJECT_RE = re.compile(r"^/\d+$")

# 静态资源扩展名：缺失只警告不阻断部署；页面缺失才阻断
ASSET_EXTS = (
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".css", ".js",
    ".pdf", ".docx", ".pptx", ".xlsx", ".ico", ".xml", ".txt", ".csv",
    ".woff", ".woff2", ".mp4", ".zip",
)


def load_redirect_sources() -> set[str]:
    """_redirects 里的源路径会被 301 掉，产物里不存在也算正常。"""
    srcs: set[str] = set()
    f = ROOT / "_redirects"
    if not f.exists():
        return srcs
    for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            srcs.add(parts[0])
            if not parts[0].endswith("/"):
                srcs.add(parts[0] + "/")
    return srcs


def tracked_files() -> set[str] | None:
    """仓库已跟踪文件（POSIX 相对路径）；失败返回 None（回退全量拷贝）。

    只发布 git 跟踪的文件 —— 本地草稿（tmp_*.html、未提交的临时页）不会被误发上线。
    历史缺陷：此前按文件系统 glob 取根目录 *.html，实测把未跟踪的 tmp_orig_crt.html
    一起发到了 cncdisplay.com。
    """
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            capture_output=True, check=True,
        )
    except Exception:
        return None
    return {p.decode("utf-8", "replace") for p in r.stdout.split(b"\0") if p}


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    tracked = tracked_files()
    if tracked is None:
        print("  [warn] 取不到 git 跟踪列表，回退为按目录全量拷贝")

    copied = 0
    skipped: list[str] = []

    def emit(src: Path, rel: str) -> None:
        nonlocal copied
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1

    for name in INCLUDE_DIRS:
        src = ROOT / name
        if not src.exists():
            print(f"  [warn] 目录不存在，跳过: {name}")
            continue
        if tracked is None:
            shutil.copytree(src, OUT / name, symlinks=False)
            copied += sum(1 for _ in (OUT / name).rglob("*") if _.is_file())
            continue
        for f in sorted(src.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(ROOT).as_posix()
            if rel in tracked:
                emit(f, rel)
            else:
                skipped.append(rel)

    for p in sorted(ROOT.glob("*.html")):
        if tracked is not None and p.name not in tracked:
            skipped.append(p.name)
            continue
        emit(p, p.name)

    for name in INCLUDE_ROOT_FILES:
        src = ROOT / name
        if not src.exists():
            print(f"  [warn] 根文件不存在，跳过: {name}")
            continue
        if tracked is not None and name not in tracked:
            skipped.append(name)
            continue
        emit(src, name)

    if skipped:
        print(f"  未进产物（未被 git 跟踪的本地文件，共 {len(skipped)} 个，前 20）:")
        for rel in skipped[:20]:
            print(f"    - {rel}")

    size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"产物: {OUT}  文件 {copied} 个 / {size / 1048576:.1f} MB")


def verify() -> int:
    """产物内自检：被引用的路径是否都真实存在。"""
    redirects = load_redirect_sources()
    missing_pages: dict[str, str] = {}
    missing_assets: dict[str, str] = {}
    checked = 0

    for page in OUT.rglob("*.html"):
        rel = page.relative_to(OUT).as_posix()
        try:
            text = page.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in REF_RE.finditer(text):
            path = m.group(1).split("#")[0].split("?")[0]
            if not path or path in redirects:
                continue
            if path.startswith(IGNORE_PREFIXES):
                continue
            if "%" in path or REJECT_RE.match(path):
                continue
            checked += 1
            target = OUT / path.lstrip("/")
            if (
                target.is_file()
                or target.with_suffix(".html").is_file()
                or (target.is_dir() and (target / "index.html").is_file())
            ):
                continue
            bucket = missing_assets if path.endswith(ASSET_EXTS) else missing_pages
            bucket.setdefault(path, rel)

    print(
        f"自检: 检查引用 {checked} 条 | 缺失页面 {len(missing_pages)} |"
        f" 缺失静态资源 {len(missing_assets)}"
    )
    for path, where in list(missing_pages.items())[:25]:
        print(f"  [missing-page] {path}   (首个引用页: {where})")
    for path, where in list(missing_assets.items())[:25]:
        print(f"  [missing-asset] {path}   (首个引用页: {where})")
    if missing_pages:
        print("产物缺失被引用的页面，已阻止部署。")
        return 1
    if missing_assets:
        print("提示: 存在缺失的静态资源（不阻断本次部署，但需尽快修）。")
    print("自检通过。")
    return 0


def main() -> int:
    build()
    return verify()


if __name__ == "__main__":
    sys.exit(main())
