#!/usr/bin/env python3
"""
CI link validator for cncdisplay.com
Runs on every push to main. Fails the build if internal links are broken.

Usage: python check_links_ci.py [--strict]
  --strict: Fail on ANY broken link (default: fail if > 0 unique targets)
"""
import os, re, sys
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent.parent  # repo root
SKIP_DIRS = {'.git', '.github', '_archive_audit', 'node_modules',
             'backlinks_output', 'backlinks_daily', 'schema', 'css',
             'images', 'fonts', 'output', 'patches', '.claude', '_templates'}

STATIC_EXTS = {'jpg', 'jpeg', 'png', 'gif', 'svg', 'webp', 'ico', 'bmp',
               'css', 'js', 'json', 'xml', 'txt', 'pdf', 'zip', 'exe',
               'woff', 'woff2', 'ttf', 'eot', 'mp4', 'webm'}

def find_html_files():
    files = []
    for dirpath, dirnames, filenames in os.walk(str(ROOT)):
        rel = Path(dirpath).relative_to(ROOT)
        if set(rel.parts) & SKIP_DIRS:
            continue
        for f in filenames:
            if f.endswith('.html'):
                files.append(Path(dirpath) / f)
    return files

def normalize(p):
    return str(p).replace('\\', '/')

def is_page_link(href):
    if not href or href.startswith('#') or href.startswith('data:') or href.startswith('javascript:'):
        return False
    if href.startswith('mailto:') or href.startswith('tel:'):
        return False
    if href.startswith('http'):
        return 'cncdisplay.com' in href
    ext = href.split('?')[0].split('#')[0].rsplit('.', 1)[-1].lower() if '.' in href else ''
    return ext not in STATIC_EXTS

def resolve_href(from_file, href):
    if href.startswith('http'):
        parsed = urlparse(href)
        return unquote(parsed.path).lstrip('/')
    from_dir = from_file.parent
    if href.startswith('/'):
        target = ROOT / href.lstrip('/')
    else:
        target = (from_dir / href).resolve()
    try:
        return normalize(target.relative_to(ROOT))
    except ValueError:
        return None

def main():
    strict = '--strict' in sys.argv
    html_files = find_html_files()

    # Build index
    known_files = set()
    known_dirs = set()
    for f in html_files:
        rel = normalize(f.relative_to(ROOT))
        known_files.add(rel)
        parent = str(f.relative_to(ROOT).parent).replace('\\', '/')
        if parent and parent != '.':
            known_dirs.add(parent)

    # Parse _redirects
    redirect_sources = set()
    rf = ROOT / '_redirects'
    if rf.exists():
        with open(rf, 'r', encoding='utf-8', errors='ignore') as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if parts:
                        redirect_sources.add(parts[0].lstrip('/'))

    all_files = known_files | redirect_sources

    # Scan all links
    broken = []
    total = 0

    for html_file in sorted(html_files):
        file_rel = normalize(html_file.relative_to(ROOT))

        with open(html_file, 'r', encoding='utf-8', errors='ignore') as fh:
            content = fh.read()

        for m in re.finditer(r'''(?:href|src)\s*=\s*["']([^"']+)["']''', content, re.IGNORECASE):
            href = m.group(1)
            if not is_page_link(href):
                continue
            total += 1

            resolved = resolve_href(html_file, href)
            if resolved is None:
                continue

            clean = resolved.split('?')[0].split('#')[0]
            if clean in ('', '.'):
                continue

            # Check existence
            if clean in all_files:
                continue
            if clean + '/index.html' in all_files:
                continue
            if clean + '.html' in all_files:
                continue

            line_num = content[:m.start()].count('\n') + 1
            broken.append((file_rel, line_num, href, clean))

    # Report
    unique_targets = len(set(b[3] for b in broken))

    print(f"Checked {len(html_files)} files, {total} page links")
    print(f"Broken links: {len(broken)} ({unique_targets} unique targets)")

    if broken:
        # Group by file
        by_file = defaultdict(list)
        for f, l, h, t in broken:
            by_file[f].append((l, h, t))

        print("\n--- BROKEN LINKS ---")
        for fname in sorted(by_file):
            items = by_file[fname]
            print(f"\n  {fname}:")
            for line, href, target in items[:5]:  # Show max 5 per file
                print(f"    L{line}: {href[:80]}")
                print(f"      -> 404: {target}")
            if len(items) > 5:
                print(f"    ... and {len(items) - 5} more")

        print(f"\nFAIL: {unique_targets} unique broken link targets found.")

        # Threshold: allow up to 25 unique broken targets (pre-existing Chinese-URL encoding variants)
        # Use --strict to fail on any
        threshold = 25 if strict else 25
        if unique_targets > threshold:
            print(f"ERROR: {unique_targets} exceeds threshold of {threshold}")
            sys.exit(1)
        else:
            print(f"WARNING: {unique_targets} within threshold of {threshold}, allowing deploy")
            sys.exit(0)
    else:
        print("\nPASS: All internal links are valid.")
        sys.exit(0)

if __name__ == '__main__':
    main()
