"""
Content manager: select articles, extract content, format per platform.

Scans cncdisplay posts/ directories for unpublished articles,
extracts title + body from HTML, and formats for each platform.
"""

import os
import re
import random
from typing import Optional, Tuple, List, Dict
from bs4 import BeautifulSoup

from .config import CN_POSTS_DIR, EN_POSTS_DIR
from .tracker import get_unpublished

# Domain for backlinks
DOMAIN = "https://cncdisplay.com"


def _is_redirect_page(soup: BeautifulSoup) -> bool:
    """Check if page is a meta-refresh redirect (skip those)."""
    meta = soup.find("meta", attrs={"http-equiv": "refresh"})
    return meta is not None


def _extract_article(filepath: str, lang: str = "en") -> Optional[Dict]:
    """
    Extract title and body from an HTML article file.

    Returns:
        dict with title, body_text, body_html, source_url, or None if invalid
    """
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Skip redirect pages
    if _is_redirect_page(soup):
        return None

    # Skip stub pages (< 500 chars real content)
    text = soup.get_text(separator="\n", strip=True)
    if len(text) < 500:
        return None

    # Get title
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # Fallback to <title> tag
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Remove site name suffix
            title = re.sub(r"\s*[||-]\s*Kongto Technology.*$", "", title).strip()

    # Get source filename
    source = os.path.basename(filepath)

    # Construct source URL
    if lang == "en":
        source_url = f"{DOMAIN}/en/posts/{source}"
    else:
        source_url = f"{DOMAIN}/posts/{source}"

    # Extract body content (main article, excluding header/footer/schema)
    body_html = _extract_body_html(soup, lang)

    # Clean text version
    body_text = BeautifulSoup(body_html, "html.parser").get_text(separator="\n", strip=True)

    return {
        "title": title,
        "body_html": body_html,
        "body_text": body_text,
        "source_url": source_url,
        "source": source,
    }


def _extract_body_html(soup: BeautifulSoup, lang: str) -> str:
    """Extract main article content HTML, excluding nav, footer, schema."""
    # Remove unwanted elements
    for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # Try to find main content area
    main = soup.find("main")
    article = soup.find("article")
    content = soup.find(class_=re.compile(r"(post-content|article-content|content)"))

    target = main or article or content or soup.find("body") or soup

    # Get inner HTML
    result = str(target)

    # Clean up: remove JSON-LD, excessive whitespace
    result = re.sub(r'<script[^>]*type="application/ld\+json"[^>]*>.*?</script>', "", result, flags=re.DOTALL)
    result = re.sub(r'\n\s*\n', '\n\n', result)
    result = result.strip()

    return result


def _format_backlink(source_url: str, platform: str) -> str:
    """Generate platform-appropriate backlink text."""
    if platform in ("zhihu", "csdn", "baijiahao"):
        return f"\n\n---\n\n原文链接: [{source_url}]({source_url})\n本文由 Kongto Technology 原创，专注于工业CNC显示器CRT转LCD升级方案。"
    elif platform == "medium":
        return f"\n\n---\n\n*Originally published at [Kongto Technology]({source_url})*"
    elif platform == "linkedin":
        return f"\n\n---\n\nOriginally published on our website: {source_url}\n#KongtoTechnology #CNCDisplay #IndustrialAutomation"
    elif platform == "facebook":
        return f"\n\n---\n\nOriginal article: {source_url}\n#CNC #IndustrialDisplay #Manufacturing"
    return f"\n\n---\n\nSource: {source_url}"


def _format_title(title: str, platform: str) -> str:
    """Format title for platform-specific conventions."""
    if platform in ("zhihu", "csdn", "baijiahao"):
        return title  # Keep original Chinese title
    elif platform == "medium":
        return title  # Medium titles are straightforward
    elif platform == "linkedin":
        # LinkedIn articles benefit from slightly longer titles
        if len(title) < 40 and "CNC" not in title:
            return f"{title} | CNC Display Upgrade Guide"
        return title
    elif platform == "facebook":
        if len(title) > 80:
            return title[:77] + "..."
        return title
    return title


def format_for_platform(article: Dict, platform: str) -> Dict:
    """
    Format article content for a specific platform.

    Returns dict with platform_title, platform_body, tags
    """
    title = _format_title(article["title"], platform)
    backlink = _format_backlink(article["source_url"], platform)

    # Platform-specific formatting
    if platform in ("csdn",):
        # CSDN supports Markdown
        body = article["body_text"]
        body += backlink
    elif platform in ("zhihu", "baijiahao"):
        # Rich text editor - use plain text (no HTML tags)
        body = article["body_text"]
        body += f"\n\n{backlink}"
    elif platform == "medium":
        # Medium uses their own editor - use text
        body = article["body_text"]
        body += backlink
    elif platform == "linkedin":
        body = article["body_text"]
        body += backlink
    elif platform == "facebook":
        # Facebook posts are shorter
        body = article["body_text"][:3000]
        body += f"\n\nFull article: {article['source_url']}"
    else:
        body = article["body_text"]
        body += backlink

    # Tags
    tags = _suggest_tags(article, platform)

    return {
        "title": title,
        "body": body,
        "tags": tags,
        "source": article["source"],
        "source_url": article["source_url"],
    }


def _suggest_tags(article: Dict, platform: str) -> list:
    """Suggest tags based on article content."""
    tags_base = ["CNC", "LCD升级", "工业显示器", "CRT转LCD"]

    # Content-based tag extraction
    text = article.get("title", "") + " " + article.get("body_text", "")[:500]
    content_tags = []
    brand_keywords = {
        "FANUC": "FANUC",
        "三菱|Mitsubishi": "Mitsubishi",
        "西门子|Siemens": "Siemens",
        "Mazak|马扎克": "Mazak",
        "OKUMA|大隈": "OKUMA",
        "HAAS|哈斯": "HAAS",
    }
    for pattern, tag in brand_keywords.items():
        if re.search(pattern, text, re.I):
            content_tags.append(tag)

    if platform in ("medium", "linkedin", "facebook"):
        tags_base = ["CNC", "Industrial Display", "Manufacturing", "CRT to LCD"]

    # Medium allows max 5 tags
    if platform == "medium":
        return (content_tags + tags_base)[:5]

    # Dev.to supports max 4 tags
    return (content_tags + tags_base)[:4]


def pick_article(lang: str = "zh") -> Optional[Tuple[Dict, Dict]]:
    """
    Pick next unpublished article.

    Returns: (cn_article, en_article) dicts, or None if all published
    """
    # Scan directories
    cn_files = sorted([f for f in os.listdir(CN_POSTS_DIR) if f.endswith(".html")])
    en_files = sorted([f for f in os.listdir(EN_POSTS_DIR) if f.endswith(".html")])

    # Get unpublished articles for Chinese platforms
    if lang == "zh":
        cn_unpublished = get_unpublished(cn_files, "zhihu")

        for fname in cn_unpublished:
            cn_article = _extract_article(os.path.join(CN_POSTS_DIR, fname), lang="zh")
            if cn_article is None:
                continue

            # Try to find matching English version
            en_path = os.path.join(EN_POSTS_DIR, fname)
            en_article = _extract_article(en_path, lang="en") if os.path.exists(en_path) else None

            return cn_article, en_article

    # English platforms
    en_unpublished = get_unpublished(en_files, "medium")
    for fname in en_unpublished:
        en_article = _extract_article(os.path.join(EN_POSTS_DIR, fname), lang="en")
        if en_article is None:
            continue

        # Try to find matching Chinese version
        cn_path = os.path.join(CN_POSTS_DIR, fname)
        cn_article = _extract_article(cn_path, lang="zh") if os.path.exists(cn_path) else None

        return cn_article, en_article

    return None, None


def dry_run() -> List[Dict]:
    """Preview what would be published (dry-run mode)."""
    cn_article, en_article = pick_article("zh")

    if not cn_article and not en_article:
        return []

    results = []
    platforms_zh = ["zhihu", "csdn", "baijiahao"]
    platforms_en = ["medium", "linkedin", "facebook"]

    if cn_article:
        for p in platforms_zh:
            formatted = format_for_platform(cn_article, p)
            results.append({
                "platform": p,
                "title": formatted["title"],
                "content_preview": formatted["body"][:200] + "...",
                "tags": formatted["tags"],
            })

    if en_article:
        for p in platforms_en:
            formatted = format_for_platform(en_article, p)
            results.append({
                "platform": p,
                "title": formatted["title"],
                "content_preview": formatted["body"][:200] + "...",
                "tags": formatted["tags"],
            })

    return results
