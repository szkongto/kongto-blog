#!/usr/bin/env python3
"""Refresh sitemap.xml <lastmod> to each URL's real last git commit date.

Usage:
    python scripts/update_sitemap_lastmod.py

Behaviour:
    - Reads sitemap.xml (preserving exact bytes / line endings).
    - For every <url> block, maps <loc> to a repo-relative file path:
        https://cncdisplay.com/            -> index.html
        https://cncdisplay.com/brands/     -> brands/index.html
        https://cncdisplay.com/posts/x.html -> posts/x.html
    - Fetches the file's last commit date via `git log -1 --format=%cd
      --date=format:%Y-%m-%d -- <relpath>`.
    - Only rewrites the <lastmod> VALUE when the new date is a valid
      YYYY-MM-DD and differs from the current value.  Never touches <loc>,
      <changefreq>, <priority>, indentation, or the URL set.
    - Files that are missing on disk, untracked, or with an unparseable git
      date are left untouched (never fabricated).

The sitemap URL set is maintained by hand (301/noindex/canonical-dup purges),
so this script deliberately edits in place rather than regenerating from the
_archive/ generator.
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(REPO, "sitemap.xml")
DOMAIN = "https://cncdisplay.com"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_BLOCK_RE = re.compile(r"<url>.*?</url>", re.DOTALL)
LOC_RE = re.compile(r"<loc>(.*?)</loc>")
LASTMOD_RE = re.compile(r"<lastmod>(.*?)</lastmod>")


def loc_to_relpath(loc: str):
    """Map a full <loc> URL to a repo-relative file path, or None if foreign."""
    if not loc.startswith(DOMAIN):
        return None
    path = loc[len(DOMAIN):]
    if path in ("", "/"):
        return "index.html"
    rel = path.lstrip("/")
    if rel.endswith("/"):
        return rel + "index.html"
    return rel


def git_last_commit_date(relpath: str):
    """Return YYYY-MM-DD of the last commit touching relpath, or None."""
    proc = subprocess.run(
        ["git", "log", "-1", "--format=%cd", "--date=format:%Y-%m-%d", "--", relpath],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return None
    out = proc.stdout.strip()
    return out if DATE_RE.match(out) else None


def main() -> int:
    with open(SITEMAP, encoding="utf-8", newline="") as fh:
        content = fh.read()

    changed = 0
    kept = 0
    missing = []

    def repl(match):
        nonlocal changed, kept
        block = match.group(0)
        loc_m = LOC_RE.search(block)
        lm_m = LASTMOD_RE.search(block)
        if not loc_m or not lm_m:
            return block

        loc = loc_m.group(1).strip()
        cur = lm_m.group(1).strip()
        rel = loc_to_relpath(loc)
        if rel is None:
            return block

        full = os.path.join(REPO, rel)
        if not os.path.isfile(full):
            missing.append((loc, rel))
            return block

        newdate = git_last_commit_date(rel)
        if not newdate or newdate == cur:
            kept += 1
            return block

        changed += 1
        return block.replace(
            lm_m.group(0),
            "<lastmod>{}</lastmod>".format(newdate),
            1,
        )

    new_content = URL_BLOCK_RE.sub(repl, content)

    if new_content == content:
        print("No <lastmod> changes needed.")
        return 0

    with open(SITEMAP, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_content)

    print("changed={} kept={} missing_files={}".format(changed, kept, len(missing)))
    for loc, rel in missing:
        print("  MISSING: {} -> {}".format(loc, rel))
    return 0


if __name__ == "__main__":
    sys.exit(main())
