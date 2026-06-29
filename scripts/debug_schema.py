"""Investigate and fix schema JSON errors in brand pages"""
import re, json, sys
from pathlib import Path

ROOT = Path("d:/code/seo_deploy")

def check_schema(path):
    content = path.read_text("utf-8")
    blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        content, re.DOTALL | re.IGNORECASE
    )
    errors = []
    for i, b in enumerate(blocks):
        try:
            json.loads(b.strip())
        except json.JSONDecodeError as e:
            errors.append((i+1, str(e), b.strip()))
    return errors

# Check FANUC
for fn in ["brands/FANUC.html", "brands/MAZAK.html", "brands/HAAS.html"]:
    path = ROOT / fn
    if path.exists():
        print(f"\n=== {fn} ===")
        errs = check_schema(path)
        for i, msg, block in errs:
            print(f"  Block #{i}: {msg}")
            lines = block.split('\n')
            for j, line in enumerate(lines):
                print(f"    L{j+1}: {line[:120]}")

# Full dump of en/about.html first broken schema block
print(f"\n=== en/about.html block #1 (full) ===")
content = (ROOT / "en/about.html").read_text("utf-8")
blocks = re.findall(
    r'<script[^>]+type=[\"'"']application/ld\+json[\"'"'][^>]*>(.*?)</script>',
    content, re.DOTALL | re.IGNORECASE
)
if blocks:
    b = blocks[0].strip()
    lines = b.split('\n')
    for j, line in enumerate(lines):
        print(f"    L{j+1}: {repr(line[:150])}")
    m = re.search(r'control character', str(errs[0][1]))
    if m:
        # Find actual control chars
        for j, line in enumerate(lines):
            for col, c in enumerate(line):
                if ord(c) < 32 and c not in '\n\r\t':
                    print(f"  CONTROL CHAR at L{j+1}:{col} U+{ord(c):04X}")
