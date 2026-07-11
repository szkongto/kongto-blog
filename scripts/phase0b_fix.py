"""Fix Phase 0b issues:
1. _redirects: missing leading / on sources (211 entries)
2. Root EN files: hreflang zh → /zh/
3. /zh/ files: hreflang en → / (remove /en/)
4. _redirects: 2 remaining /en/ targets
"""
import os, re

ROOT = r"d:\code\seo_deploy"

# ================================================================
# FIX 1: _redirects - add back leading /
# ================================================================
print("FIX 1: _redirects leading /")
redirects_fp = os.path.join(ROOT, "_redirects")
with open(redirects_fp, 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed = 0
new_lines = []
for line in lines:
    stripped = line.strip()
    if not stripped or stripped.startswith('#'):
        new_lines.append(line)
        continue

    parts = stripped.split()
    if len(parts) < 2:
        new_lines.append(line)
        continue

    source = parts[0]
    target = parts[1]
    code = parts[2] if len(parts) > 2 else '301'
    changed = False

    # Fix source missing leading /
    if not source.startswith('/') and not source.startswith('http'):
        source = '/' + source
        changed = True

    # Fix target missing leading /
    if not target.startswith('/') and not target.startswith('http'):
        target = '/' + target
        changed = True

    # Fix remaining /en/ in target
    if '/en/' in target:
        target = target.replace('/en/', '/')
        changed = True

    if changed:
        line = f"{source} {target} {code}\n"
        fixed += 1

    new_lines.append(line)

with open(redirects_fp, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print(f"  Fixed {fixed} redirect entries")

# ================================================================
# FIX 2: Root EN files - hreflang zh → /zh/
# ================================================================
print("\nFIX 2: Root EN hreflang zh → /zh/")
fix_en_zh = 0
for root_dir, dirs, files in os.walk(ROOT):
    # Skip /zh/, /en_bak/, /scripts/, . directories
    rel = os.path.relpath(root_dir, ROOT)
    if rel.startswith('zh') or rel.startswith('en_bak') or rel.startswith('scripts') or rel.startswith('.'):
        continue
    for f in files:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(root_dir, f)
        with open(fp, 'r', encoding='utf-8') as fh:
            c = fh.read()

        changes = 0
        # hreflang="zh" href="https://cncdisplay.com/" → /zh/
        c, n = re.subn(
            r'(hreflang="zh"[^>]*href="https://cncdisplay\.com/)(?!(en|zh))',
            r'\1zh/',
            c
        )
        changes += n

        # hreflang="zh-CN" href="/" → /zh/
        c, n = re.subn(
            r'(hreflang="zh-CN"[^>]*href="/(?!(en|zh)))',
            r'\1zh/',
            c
        )
        changes += n

        if changes:
            with open(fp, 'w', encoding='utf-8') as fh:
                fh.write(c)
            print(f"  FIXED: {os.path.relpath(fp, ROOT)}")
            fix_en_zh += 1

print(f"  Total EN files fixed: {fix_en_zh}")

# ================================================================
# FIX 3: /zh/ files - hreflang en → / (remove /en/)
# ================================================================
print("\nFIX 3: /zh/ files hreflang en → /")
fix_zh_en = 0
for root_dir, dirs, files in os.walk(os.path.join(ROOT, "zh")):
    for f in files:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(root_dir, f)
        with open(fp, 'r', encoding='utf-8') as fh:
            c = fh.read()

        changes = 0
        # hreflang="en" href="https://cncdisplay.com/en/" → https://cncdisplay.com/
        c, n = re.subn(
            r'(hreflang="en"[^>]*href="https://cncdisplay\.com)/en/',
            r'\1/',
            c
        )
        changes += n

        # Also fix relative: hreflang="en" href="/en/" → /
        c, n = re.subn(
            r'(hreflang="en"[^>]*href=")/en/',
            r'\1/',
            c
        )
        changes += n

        if changes:
            with open(fp, 'w', encoding='utf-8') as fh:
                fh.write(c)
            print(f"  FIXED: {os.path.relpath(fp, ROOT)[len(ROOT)+1:]}")
            fix_zh_en += 1

print(f"  Total /zh/ files fixed: {fix_zh_en}")

print("\nAll fixes applied.")
