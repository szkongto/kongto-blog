"""Delete redirect stub files (old <meta refresh> pages superseded by _redirects)"""
import os, re
from pathlib import Path

ROOT = Path(__file__).parent.parent

def find_redirect_stubs(directory):
    stubs = []
    for f in Path(directory).glob("**/*.html"):
        if f.name == "index.html":
            continue
        content = f.read_text(encoding="utf-8", errors="ignore")
        if 'http-equiv="refresh"' in content and "Redirecting" in content:
            stubs.append(f)
    return stubs

stubs = find_redirect_stubs(ROOT)
print(f"Found {len(stubs)} redirect stub files to delete:")
for s in stubs:
    rel = s.relative_to(ROOT)
    print(f"  {rel} ({s.stat().st_size} bytes)")
    s.unlink()

print(f"\nDone. Deleted {len(stubs)} stubs.")
