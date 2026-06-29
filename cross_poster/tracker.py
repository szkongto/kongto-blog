"""
Tracker: record and query published articles.

Uses a JSON file to track which articles have been published where.
Prevents duplicate publishing across platforms.
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List

from .config import TRACKER_FILE


def _load() -> list:
    if not os.path.exists(TRACKER_FILE):
        return []
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(records: list):
    os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def is_published(source_file: str, platform: str) -> bool:
    """Check if an article source was already published on a given platform."""
    records = _load()
    for r in records:
        if r["source"] == source_file:
            if platform in r.get("platforms", {}):
                return True
    return False


def get_unpublished(source_files: List[str], platform: str) -> List[str]:
    """Filter out already-published source files for a platform."""
    records = _load()
    published_sources = set()
    for r in records:
        if platform in r.get("platforms", {}):
            published_sources.add(r["source"])
    return [f for f in source_files if f not in published_sources]


def mark_published(
    source: str,
    title: str,
    platform: str,
    url: str,
    status: str = "published",
):
    """Mark an article as published on a platform."""
    records = _load()
    existing = None
    for r in records:
        if r["source"] == source:
            existing = r
            break

    today = datetime.now().strftime("%Y-%m-%d")

    if existing:
        existing.setdefault("platforms", {})[platform] = {
            "url": url,
            "date": today,
            "status": status,
        }
        # Update language-specific titles
        if "title_cn" not in existing:
            existing["title_cn"] = title if any(
                p in platform for p in ["zhihu", "baijiahao", "csdn"]
            ) else ""
        if "title_en" not in existing:
            existing["title_en"] = title if any(
                p in platform for p in ["medium", "linkedin", "facebook"]
            ) else ""
    else:
        is_cn = any(p in platform for p in ["zhihu", "baijiahao", "csdn"])
        records.append({
            "source": source,
            "title_cn": title if is_cn else "",
            "title_en": title if not is_cn else "",
            "platforms": {
                platform: {"url": url, "date": today, "status": status}
            },
            "published_date": today,
        })

    _save(records)


def get_all_records() -> list:
    """Return all publication records."""
    return _load()


def get_stats() -> Dict:
    """Get publishing statistics."""
    records = _load()
    stats = {
        "total_articles": len(records),
        "by_platform": {},
        "total_publishes": 0,
    }
    for r in records:
        for plat, info in r.get("platforms", {}).items():
            stats["by_platform"][plat] = stats["by_platform"].get(plat, 0) + 1
            stats["total_publishes"] += 1
    return stats
