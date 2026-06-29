#!/usr/bin/env python3
"""
Cross-poster: auto-publish articles to 6 platforms.

Usage:
    python -m cross_poster.main --dry-run       # Preview next article
    python -m cross_poster.main --all            # Publish to all platforms
    python -m cross_poster.main --platform csdn  # Single platform
    python -m cross_poster.main --first-login zhihu  # First-time login
    python -m cross_poster.main --stats          # Publishing stats
"""

import asyncio
import logging
import sys
import os

# Fix GBK terminal for emoji output on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent dir to path so we can run as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cross_poster.content import pick_article, format_for_platform, dry_run
from cross_poster.tracker import mark_published, get_stats
from cross_poster.session import load_or_login, save_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cross_poster")


PLATFORM_MAP = {
    "zhihu": ("cross_poster.adapters.zhihu", "ZhihuAdapter"),
    "baijiahao": ("cross_poster.adapters.baijiahao", "BaijiahaoAdapter"),
    "csdn": ("cross_poster.adapters.csdn", "CSDNAdapter"),
    "medium": ("cross_poster.adapters.medium", "MediumAdapter"),
    "linkedin": ("cross_poster.adapters.linkedin", "LinkedInAdapter"),
    "facebook": ("cross_poster.adapters.facebook", "FacebookAdapter"),
}

# Platform groups
CN_PLATFORMS = ["zhihu", "csdn", "baijiahao"]
EN_PLATFORMS = ["medium", "linkedin", "facebook"]
ALL_PLATFORMS = CN_PLATFORMS + EN_PLATFORMS


def _load_adapter(platform: str):
    """Dynamically import and instantiate a platform adapter."""
    module_path, class_name = PLATFORM_MAP[platform]
    import importlib
    mod = importlib.import_module(module_path)
    cls = getattr(mod, class_name)
    return cls()


async def run_dry_run():
    """Preview what would be published."""
    results = dry_run()
    if not results:
        print("✅ 所有文章已发布完毕！没有新文章待发。")
        return

    print("\n" + "=" * 60)
    print("  Dry Run: 下一轮发布预览")
    print("=" * 60)

    for r in results:
        plat_names = {
            "zhihu": "知乎", "baijiahao": "百家号", "csdn": "CSDN",
            "medium": "Medium", "linkedin": "LinkedIn", "facebook": "Facebook",
        }
        name = plat_names.get(r["platform"], r["platform"])
        print(f"\n  📌 {name}")
        print(f"    标题: {r['title']}")
        print(f"    标签: {', '.join(r['tags'])}")
        print(f"    内容预览: {r['content_preview'][:150]}")

    cn_article, en_article = pick_article("zh")
    cn_title = cn_article["title"] if cn_article else "（无可选）"
    en_title = en_article["title"] if en_article else "（无可选）"

    print("\n" + "-" * 60)
    print(f"  中文原文: {cn_title}")
    print(f"  英文原文: {en_title}")
    print("=" * 60)


async def run_platform(platform: str):
    """Publish to a single platform."""
    if platform not in ALL_PLATFORMS:
        print(f"❌ 未知平台: {platform}")
        print(f"   可用: {', '.join(ALL_PLATFORMS)}")
        return

    # Pick appropriate language article
    lang = "zh" if platform in CN_PLATFORMS else "en"
    cn_article, en_article = pick_article(lang)

    if lang == "zh" and not cn_article:
        print("❌ 没有未发布的中文文章。运行 --dry-run 查看状态。")
        return
    if lang == "en" and not en_article:
        print("❌ 没有未发布的英文文章。运行 --dry-run 查看状态。")
        return

    article = cn_article if lang == "zh" else en_article
    formatted = format_for_platform(article, platform)

    plat_names = {
        "zhihu": "知乎", "baijiahao": "百家号", "csdn": "CSDN",
        "medium": "Medium", "linkedin": "LinkedIn", "facebook": "Facebook",
    }
    name = plat_names.get(platform, platform)

    print(f"\n{'=' * 60}")
    print(f"  发布到 {name}")
    print(f"  标题: {formatted['title']}")
    print(f"{'=' * 60}\n")

    adapter = _load_adapter(platform)
    url = await adapter.run(
        title=formatted["title"],
        body=formatted["body"],
        tags=formatted["tags"],
    )

    if url:
        mark_published(
            source=formatted["source"],
            title=formatted["title"],
            platform=platform,
            url=url,
            status="published",
        )
        print(f"\n✅ [{name}] 发布成功！")
        print(f"   URL: {url}")
    else:
        print(f"\n❌ [{name}] 发布失败")


async def run_all():
    """Publish to all platforms sequentially with delays."""
    cn_article, en_article = pick_article("zh")

    if not cn_article and not en_article:
        print("✅ 所有文章已发布完毕！")
        return

    if cn_article:
        print(f"\n📝 中文文章: {cn_article['title']}")
    if en_article:
        print(f"📝 英文文章: {en_article['title']}")

    for platform in ALL_PLATFORMS:
        lang = "zh" if platform in CN_PLATFORMS else "en"
        article = cn_article if lang == "zh" else en_article

        if not article:
            print(f"  ⏭️  {platform}: 跳过（无相应语言文章）")
            continue

        formatted = format_for_platform(article, platform)
        plat_names = {
            "zhihu": "知乎", "baijiahao": "百家号", "csdn": "CSDN",
            "medium": "Medium", "linkedin": "LinkedIn", "facebook": "Facebook",
        }

        print(f"\n{'─' * 50}")
        print(f"  发布到 {plat_names.get(platform, platform)}")
        print(f"{'─' * 50}")

        adapter = _load_adapter(platform)
        url = await adapter.run(
            title=formatted["title"],
            body=formatted["body"],
            tags=formatted["tags"],
        )

        if url:
            mark_published(
                source=formatted["source"],
                title=formatted["title"],
                platform=platform,
                url=url,
            )
            print(f"  ✅ 成功: {url}")
        else:
            print(f"  ❌ 失败")

        # Delay between platforms (2-4 hours for real runs, 10s for test)
        if platform != ALL_PLATFORMS[-1]:
            from cross_poster.config import BETWEEN_PLATFORMS
            delay = 10  # Short delay for testing
            print(f"\n  ⏳ 等待 {delay} 秒后继续...")
            await asyncio.sleep(delay)

    print(f"\n{'=' * 60}")
    print("  全平台发布完成！")
    print(f"{'=' * 60}")


async def first_login(platform: str):
    """Guide through first-time login for a platform."""
    if platform not in ALL_PLATFORMS:
        print(f"❌ 未知平台: {platform}")
        return

    from cross_poster.config import PLATFORMS as CFG
    info = CFG[platform]

    print(f"\n{'=' * 60}")
    print(f"  首次登录: {info['name']} ({platform})")
    print(f"{'=' * 60}")
    print(f"  浏览器已打开，请手动登录你的 {info['name']} 账号")
    print(f"  登录完成后按 Enter 继续保存 Cookie...")
    print()

    context, pw = await load_or_login(platform, info["login_url"], headless=False)

    # Check if login succeeded
    page = await context.new_page()
    await page.goto(info["editor_url"], wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(3)

    print(f"\n  当前页面: {page.url}")
    loop = asyncio.get_event_loop()
    save = (await loop.run_in_executor(None, lambda: input("  ✅ 登录成功了吗？(y/n): "))).strip().lower()

    if save == "y":
        await save_session(context, platform)
        print(f"\n  ✅ {info['name']} 登录信息已保存！")
    else:
        print(f"\n  ⚠️  未保存。下次运行 --first-login {platform} 重试。")

    await page.close()
    await context.close()
    await pw.stop()


async def show_stats():
    """Show publishing statistics."""
    stats = get_stats()
    plat_names = {
        "zhihu": "知乎", "baijiahao": "百家号", "csdn": "CSDN",
        "medium": "Medium", "linkedin": "LinkedIn", "facebook": "Facebook",
    }

    print(f"\n{'=' * 60}")
    print(f"  发布统计")
    print(f"{'=' * 60}")
    print(f"  总文章数: {stats['total_articles']}")
    print(f"  总发布次数: {stats['total_publishes']}")
    print()
    for plat, count in sorted(stats["by_platform"].items()):
        name = plat_names.get(plat, plat)
        print(f"  {name}: {count} 篇")
    print(f"{'=' * 60}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cross-poster: 全平台自动发文章")
    parser.add_argument("--dry-run", action="store_true", help="预览发布内容")
    parser.add_argument("--platform", type=str, help="发布到指定平台")
    parser.add_argument("--all", action="store_true", help="全平台发布")
    parser.add_argument("--first-login", type=str, metavar="PLATFORM", help="首次登录")
    parser.add_argument("--stats", action="store_true", help="发布统计")

    args = parser.parse_args()

    if args.stats:
        asyncio.run(show_stats())
    elif args.dry_run:
        asyncio.run(run_dry_run())
    elif args.first_login:
        asyncio.run(first_login(args.first_login))
    elif args.platform:
        asyncio.run(run_platform(args.platform))
    elif args.all:
        asyncio.run(run_all())
    else:
        # Default: dry-run
        asyncio.run(run_dry_run())


if __name__ == "__main__":
    main()
