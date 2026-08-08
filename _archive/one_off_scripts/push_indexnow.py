#!/usr/bin/env python
"""IndexNow auto-push: read sitemap.xml and submit URLs to IndexNow API.
Usage:
  python push_indexnow.py                # push all URLs from sitemap.xml
  python push_indexnow.py --urls url1,url2   # push specific URLs
  python push_indexnow.py --dry-run      # show what would be pushed, no action
"""

import sys
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

KEY = "ddac7c800685a15fa23809dc08c3b6c9"
HOST = "cncdisplay.com"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
INDEXNOW_API = "https://api.indexnow.org/indexnow"
SITEMAP = Path(__file__).parent / "sitemap.xml"


def get_urls_from_sitemap() -> list[str]:
    tree = ET.parse(SITEMAP)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [el.text for el in tree.findall(".//s:loc", ns) if el.text]
    return urls


def push_urls(urls: list[str], dry_run: bool = False) -> bool:
    urls = [u for u in urls if u.strip()]
    if not urls:
        print("No URLs to push.")
        return False

    print(f"Pushing {len(urls)} URLs to IndexNow...")
    for i, url in enumerate(urls[:5]):
        print(f"  {i+1}. {url}")
    if len(urls) > 5:
        print(f"  ... and {len(urls) - 5} more")

    if dry_run:
        print("[DRY RUN] Would push but --dry-run set.")
        return True

    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls
    }).encode("utf-8")

    req = urllib.request.Request(
        INDEXNOW_API,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            body = resp.read().decode()
            print(f"IndexNow response: HTTP {status}")
            if body:
                print(f"  Body: {body}")
            return status == 200
    except urllib.error.HTTPError as e:
        print(f"IndexNow error: HTTP {e.code} - {e.reason}")
        body = e.read().decode() if e.fp else ""
        if body:
            print(f"  Body: {body}")
        return False
    except Exception as e:
        print(f"Request failed: {e}")
        return False


def main():
    dry_run = "--dry-run" in sys.argv

    # Check for --urls flag
    urls = None
    for i, arg in enumerate(sys.argv):
        if arg == "--urls" and i + 1 < len(sys.argv):
            urls = sys.argv[i + 1].split(",")
            break

    if urls is None:
        if not SITEMAP.exists():
            print(f"Sitemap not found: {SITEMAP}")
            sys.exit(1)
        urls = get_urls_from_sitemap()
        print(f"Read {len(urls)} URLs from {SITEMAP}")

    success = push_urls(urls, dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
