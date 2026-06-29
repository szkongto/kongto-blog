"""Restore Chinese text corrupted by Phase 0a encoding bug
Phase 0a commit (7001d17c) read UTF-8 files as GBK, corrupting all Chinese text.
This script restores correct Chinese from the pre-corruption git version.
"""
import subprocess, re
from pathlib import Path

ROOT = Path("d:/code/seo_deploy")
SINCE = "64f6e321"  # Last uncorrupted commit

def get_correct(rel_path):
    try:
        r = subprocess.run(["git", "show", f"{SINCE}:{rel_path}"],
            capture_output=True, encoding='utf-8', cwd=ROOT)
        if r.returncode == 0:
            return r.stdout
    except: pass
    return None

def is_corrupted(text):
    markers = ['鍙', '戦', '偅', '绉', '鏄', '剧', 'ず', '鍣', '崌', '绾', '柟', '妗']
    return sum(1 for m in markers if m in text[:500]) >= 3

def restore(rel_path):
    f = ROOT / rel_path
    if not f.exists():
        return False
    current = f.read_text('utf-8', errors='ignore')
    if not is_corrupted(current):
        return False
    correct = get_correct(rel_path)
    if correct is None:
        return False
    f.write_text(correct, 'utf-8')
    return True

# Core pages to restore
pages = ["index.html", "about.html", "contact.html", "quote.html",
         "case-studies.html", "compatibility-matrix.html",
         "comparison-kongto-vs-competitors.html", "resources.html",
         "pricing.html", "privacy.html", "terms.html", "glossary.html",
         "search.html", "sitemap.html", "zh/index.html", "zh/sitemap.html"]

for brand in ["FANUC", "HAAS", "MAZAK", "Mitsubishi", "OKUMA", "Siemens"]:
    pages.append(f"brands/{brand}.html")
    pages.append(f"en/brands/{brand}.html")
pages.append("brands/index.html")
pages.append("en/brands/index.html")
for d in ["", "zh/", "en/"]:
    pages.append(f"{d}posts/index.html")
    pages.append(f"{d}docs/index.html")

print(f"Restoring {len(pages)} pages...")
fixed = 0
for rel in pages:
    if restore(rel):
        print(f"  RESTORED: {rel}")
        fixed += 1

print(f"\nFixed: {fixed} pages")
