"""Find which deleted stubs are still referenced by other pages and add redirects"""
from pathlib import Path
import re, os

ROOT = Path(__file__).parent.parent

# Get all current HTML files
all_files = set()
for f in ROOT.rglob("*.html"):
    rel = f.relative_to(ROOT)
    all_files.add(str(rel).replace("\\", "/"))

# Read existing _redirects
redirects_path = ROOT / "_redirects"
redirects_content = redirects_path.read_text(encoding="utf-8")

# Find all internal href links
stub_refs = {}  # stub_path -> set of referencing files

# Get all deleted stubs from git
result = os.popen("cd /d/code/seo_deploy && git diff --name-only --diff-filter=D HEAD").read()
deleted = [l.strip() for l in result.split("\n") if l.strip() and l.strip().endswith(".html")]
print(f"Deleted files: {len(deleted)}")

# Check which deleted files are referenced by other pages
for f in ROOT.rglob("*.html"):
    if ".git" in str(f):
        continue
    rel = str(f.relative_to(ROOT)).replace("\\", "/")
    if rel in deleted:
        continue
    content = f.read_text(encoding="utf-8", errors="ignore")
    for stub in deleted:
        stub_name = stub.split("/")[-1]
        if stub_name in content:
            if stub not in stub_refs:
                stub_refs[stub] = set()
            stub_refs[stub].add(rel)

# For stubs that are referenced, find target (from meta refresh URL) and add redirect
added = 0
with open(redirects_path, "a", encoding="utf-8") as rfile:
    for stub in sorted(stub_refs.keys()):
        # Try to find the redirect target from git stash or the _redirects rule
        stub_name = stub.split("/")[-1]

        # Check if already in _redirects
        if stub_name in redirects_content:
            continue

        # Try to extract target from stub file (from git)
        result = os.popen(f"cd /d/code/seo_deploy && git show HEAD:{stub} 2>/dev/null | grep -oP 'url=[\"'"']?[^\"'"' >]+' 2>/dev/null || git stash show -p -- {stub} 2>/dev/null | grep -oP 'url=[\"'"']?[^\"'"' >]+'").read()

        # Count referrers
        ref_count = len(stub_refs[stub])
        refs = ", ".join(list(stub_refs[stub])[:3])
        print(f"  {stub} -> {ref_count} referrers (e.g. {refs})")

print(f"\nTotal stubs still referenced: {len(stub_refs)}")
