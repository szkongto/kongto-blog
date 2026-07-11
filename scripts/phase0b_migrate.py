"""Phase 0b: Root domain switch to English.
1. Copy /en/ → root (overwrite Chinese)
2. Update hreflang in English files: /en/ → /
3. Update hreflang+canonical in /zh/: / → /zh/
4. Rewrite _redirects: remove /en/ prefix, add CN→/zh/ redirects
5. Backup /en/ → /en_bak/, delete /en/
6. Regenerate sitemap
"""
import os, re, shutil, sys

ROOT = r"d:\code\seo_deploy"
EN_DIR = os.path.join(ROOT, "en")
ZH_DIR = os.path.join(ROOT, "zh")

# ================================================================
# HELPERS
# ================================================================

def walk_html(dir_path):
    """Yield (full_path, rel_path) for .html files under dir_path."""
    for root_dir, dirs, files in os.walk(dir_path):
        for f in files:
            if f.endswith('.html'):
                full = os.path.join(root_dir, f)
                rel = os.path.relpath(full, dir_path)
                yield full, rel

def replace_in_file(fp, old, new, desc=""):
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    if old in c:
        c = c.replace(old, new)
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"  {desc}: {os.path.relpath(fp, ROOT)}")
        return True
    return False

def regex_replace_in_file(fp, pattern, replacement, desc=""):
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    new_c, count = re.subn(pattern, replacement, c)
    if count:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new_c)
        print(f"  {desc} ({count}x): {os.path.relpath(fp, ROOT)}")
    return count

# ================================================================
# STEP 0: Backup /en/ → /en_bak/
# ================================================================
print("=" * 60)
print("STEP 0: Backup /en/ → /en_bak/")
print("=" * 60)
EN_BAK = os.path.join(ROOT, "en_bak")
if os.path.exists(EN_BAK):
    shutil.rmtree(EN_BAK)
shutil.copytree(EN_DIR, EN_BAK)
print(f"Backup saved: {EN_BAK}")

# ================================================================
# STEP 1: Copy /en/ files to root
# ================================================================
print("\n" + "=" * 60)
print("STEP 1: Copy /en/ → root")
print("=" * 60)

# 1a. Copy root-level .html files
count = 0
for fname in os.listdir(EN_DIR):
    fp_en = os.path.join(EN_DIR, fname)
    fp_root = os.path.join(ROOT, fname)
    if os.path.isfile(fp_en) and fname.endswith('.html'):
        shutil.copy2(fp_en, fp_root)
        count += 1
        print(f"  cp: {fname}")
print(f"  Copied {count} root HTML files")

# 1b. Copy subdirectories (merge, overwrite)
for subdir in ['brands', 'products', 'posts', 'docs', 'guides']:
    src = os.path.join(EN_DIR, subdir)
    dst = os.path.join(ROOT, subdir)
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)  # remove old Chinese version entirely
        shutil.copytree(src, dst)
        fcount = len([f for f in os.listdir(dst) if f.endswith('.html')])
        print(f"  cp dir: {subdir}/ ({fcount} files)")

# 1c. Copy llms.txt if exists
if os.path.exists(os.path.join(EN_DIR, "llms.txt")):
    shutil.copy2(os.path.join(EN_DIR, "llms.txt"), os.path.join(ROOT, "llms.txt"))
    print("  cp: llms.txt")

# 1d. Copy .ts (search index) if exists
ts_src = os.path.join(EN_DIR, ".ts")
ts_dst = os.path.join(ROOT, ".ts")
if os.path.isdir(ts_src):
    if os.path.exists(ts_dst):
        shutil.rmtree(ts_dst)
    shutil.copytree(ts_src, ts_dst)
    print("  cp: .ts/ (search index)")

# ================================================================
# STEP 2: Update hreflang + canonical in English root files
# ================================================================
print("\n" + "=" * 60)
print("STEP 2: Update hreflang in English root files (/en/ → /)")
print("=" * 60)

# Directories to scan for English HTML files now at root
EN_SCAN_DIRS = [
    ROOT,                          # root-level EN files
    os.path.join(ROOT, "brands"),
    os.path.join(ROOT, "products"),
    os.path.join(ROOT, "posts"),
    os.path.join(ROOT, "docs"),
    os.path.join(ROOT, "guides"),
]

# Patterns to fix in English files
# Canonical: href="https://cncdisplay.com/en/... → href="https://cncdisplay.com/...
# Canonical relative: href="/en/... → href="/...
# hreflang en: /en/ in URLs
# hreflang zh: https://cncdisplay.com/ → https://cncdisplay.com/zh/
# x-default: keep as /

fixes_en = 0
for scan_dir in EN_SCAN_DIRS:
    if not os.path.isdir(scan_dir):
        continue
    for fname in os.listdir(scan_dir):
        if not fname.endswith('.html'):
            continue
        fp = os.path.join(scan_dir, fname)

        with open(fp, 'r', encoding='utf-8') as f:
            c = f.read()

        changes = 0

        # 1. canonical: https://cncdisplay.com/en/ → https://cncdisplay.com/
        c, n = re.subn(r'(https://cncdisplay\.com)/en/', r'\1/', c)
        changes += n

        # 2. canonical: href="/en/... → href="/... (for relative canonical paths)
        c, n = re.subn(r'href="/(en/[^"]*)"', lambda m: f'href="/{m.group(1)[3:]}"' if m.group(1).startswith('en/') else m.group(0), c)
        changes += n

        # 3. hreflang zh-CN URLs: change from https://cncdisplay.com/ → https://cncdisplay.com/zh/
        # Only for zh-CN links that point to root
        # Pattern: hreflang="zh-CN" href="https://cncdisplay.com/ (NOT followed by en/ or zh/)
        c, n = re.subn(
            r'(hreflang="zh-CN"[^>]*href="https://cncdisplay\.com/)(?!((en|zh)/|$))',
            r'\1zh/',
            c
        )
        changes += n

        # 4. hreflang en href: https://cncdisplay.com/en/ → https://cncdisplay.com/ (already covered by #1)
        # But also handle hreflang="en" pointing to /en/...
        c, n = re.subn(
            r'(hreflang="en"[^>]*href="/)en/',
            r'\1',
            c
        )
        changes += n

        # 5. hreflang x-default pointing to /en/ → fix to /
        c, n = re.subn(
            r'(hreflang="x-default"[^>]*href="/)en/',
            r'\1',
            c
        )
        changes += n

        # 6. Internal English URLs in body (e.g., /en/posts/... → /posts/)
        c, n = re.subn(r'href="/en/', 'href="/', c)
        changes += n

        # 7. src="/en/ → src="/" (unlikely but safe)
        c, n = re.subn(r'src="/en/', 'src="/', c)
        changes += n

        if changes:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(c)
            fixes_en += 1
            print(f"  FIXED ({changes} changes): {os.path.relpath(fp, ROOT)}")

print(f"  Total English files updated: {fixes_en}")

# ================================================================
# STEP 3: Update hreflang + canonical in /zh/ files
# ================================================================
print("\n" + "=" * 60)
print("STEP 3: Update /zh/ hreflang + canonical (/ → /zh/)")
print("=" * 60)

fixes_zh = 0
for fp, rel in walk_html(ZH_DIR):
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()

    changes = 0

    # 1. canonical: https://cncdisplay.com/... (not /en/ or /zh/) → /zh/...
    # This catches the root-level canonical and changes to /zh/ equivalent
    # But be careful not to change https://cncdisplay.com/en/ or already /zh/
    c, n = re.subn(
        r'<link[^>]*rel="canonical"[^>]*href="https://cncdisplay\.com/(?!(en|zh)/)[^"]*"[^>]*>',
        # Replace the matched URL with /zh/ version
        lambda m: m.group(0).replace(
            m.group(0)[m.group(0).find('href="')+6:m.group(0).rfind('"')],
            'https://cncdisplay.com/zh/' +
            m.group(0)[m.group(0).find('https://cncdisplay.com/')+22:m.group(0).rfind('"')].lstrip('/')
        ) if 'href="https://cncdisplay.com/' in m.group(0) else m.group(0),
        c
    )
    changes += n

    # More reliable: just replace all canonical href from https://cncdisplay.com/ to /zh/
    # But skip ones that already have /en/ or /zh/
    c, n = re.subn(
        r'(<link[^>]*rel="canonical"[^>]*href="https://cncdisplay\.com/)(?!(en|zh))',
        r'\1zh/',
        c
    )
    changes += n

    # 2. hreflang en: https://cncdisplay.com/en/ → https://cncdisplay.com/
    # Already correct in most cases

    # 3. hreflang zh-CN: should point to /zh/...
    # Currently may point to /zh/ or / — fix any that point to root
    # hreflang="zh-CN" href="https://cncdisplay.com/something" → add /zh/
    c, n = re.subn(
        r'(hreflang="zh-CN"[^>]*href="https://cncdisplay\.com/)(?!(en|zh))',
        r'\1zh/',
        c
    )
    changes += n

    # Also fix zh-CN relative href="/... → /zh/...
    c, n = re.subn(
        r'(hreflang="zh-CN"[^>]*href="/)(?!(en|zh))',
        r'\1zh/',
        c
    )
    changes += n

    # 4. hreflang x-default should point to root (English now)
    # Already correct if pointing to https://cncdisplay.com/
    # But if pointing to /en/... fix to /...
    c, n = re.subn(
        r'(hreflang="x-default"[^>]*href="/)en/',
        r'\1',
        c
    )
    changes += n

    # 5. Body internal links in /zh/ files: fix /zh/ linking to root Chinese files
    # Links like href="/posts/xxx" should become href="/zh/posts/xxx" (relative to zh)
    # But NOT links to external sites, NOT links already starting with /zh/, /en/, http, #
    # This is tricky - let's just fix the lang switch links

    # 6. Lang switch: <link rel="alternate" hreflang="en"... > usually fine

    # 7. Og:url
    c, n = re.subn(
        r'(<meta[^>]*property="og:url"[^>]*content="https://cncdisplay\.com/)(?!(en|zh))',
        r'\1zh/',
        c
    )
    changes += n

    if changes:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)
        fixes_zh += 1
        print(f"  FIXED ({changes} changes): {rel}")

print(f"  Total /zh/ files updated: {fixes_zh}")

# ================================================================
# STEP 4: Rewrite _redirects
# ================================================================
print("\n" + "=" * 60)
print("STEP 4: Rewrite _redirects")
print("=" * 60)

REDIRECTS_FILE = os.path.join(ROOT, "_redirects")
with open(REDIRECTS_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
mod_count = 0
zh_redirect_added = set()

for line in lines:
    stripped = line.strip()

    # Skip comments and blank lines
    if not stripped or stripped.startswith('#'):
        new_lines.append(line)
        continue

    # Parse: source target [code]
    parts = stripped.split()
    if len(parts) < 2:
        new_lines.append(line)
        continue

    source = parts[0]
    target = parts[1]
    code = parts[2] if len(parts) > 2 else '301'
    changed = False

    # 1. Source starts with /en/ → remove /en/
    if source.startswith('/en/'):
        new_source = source[4:]  # /en/XXX → /XXX
        if new_source == '':
            new_source = '/'
        source = new_source
        changed = True

    # 2. Target starts with /en/ → remove /en/
    if target.startswith('/en/'):
        target = target[4:]  # /en/XXX → /XXX
        if target == '':
            target = '/'
        changed = True

    # 3. Target is https://cncdisplay.com/en/ → https://cncdisplay.com/
    if 'https://cncdisplay.com/en/' in target:
        target = target.replace('https://cncdisplay.com/en/', 'https://cncdisplay.com/')
        changed = True

    # 4. Chinese source URLs → redirect to /zh/ if target was / or /index.html or cncdisplay.com/
    # Detect Chinese-named source files (containing Chinese chars or known CN patterns)
    is_chinese_source = bool(re.search(r'[一-鿿]', source))
    is_chinese_target = target in ['/', '/index.html', 'https://cncdisplay.com/']

    if is_chinese_source and is_chinese_target:
        # Try to redirect to /zh/ equivalent
        # Extract filename from source
        src_path = source.lstrip('/')
        zh_path = os.path.join(ZH_DIR, src_path)
        if os.path.exists(zh_path):
            target = f'/zh/{src_path}'
            changed = True
            zh_redirect_added.add(f'/zh/{src_path}')
            print(f"  CN→/zh/: {source} → /zh/{src_path}")

    # Reconstruct line
    if changed:
        line = f"{source} {target} {code}\n"
        mod_count += 1

    new_lines.append(line)

# Write updated _redirects
with open(REDIRECTS_FILE, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"  Rewrote {mod_count} redirect entries")

# Add catch-all Chinese→/zh/ redirects for root-level Chinese files that got overwritten
# Scan for any Chinese pages we moved and add redirects
print("\n  Adding Chinese→/zh/ redirects for overwritten root pages...")
cn_redirects_added = 0

# Check root-level Chinese pages (now overwritten by EN)
# Add redirects for the old root Chinese pages to /zh/ equivalents
for fname in os.listdir(ZH_DIR):
    if not fname.endswith('.html'):
        continue
    # These existed at root, now overwritten by EN
    # Add 301 from /filename.html → /zh/filename.html
    new_redirect = f"/{fname} /zh/{fname} 301\n"
    # Check if already in _redirects
    already = False
    for l in new_lines:
        if l.strip().startswith(f"/{fname} ") or l.strip().startswith(f"/{fname}\t"):
            already = True
            break
    if not already:
        new_lines.append(new_redirect)
        cn_redirects_added += 1

# Also add for subdirectories that had Chinese content
# Only add for files that exist in /zh/ but the root now has EN
# These are already handled if the EN version is at root

with open(REDIRECTS_FILE, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"  Added {cn_redirects_added} Chinese→/zh/ redirects")

# ================================================================
# STEP 5: Backup /en/ → /en_bak/ (already done), remove /en/
# ================================================================
print("\n" + "=" * 60)
print("STEP 5: Remove /en/ directory")
print("=" * 60)

if os.path.exists(EN_DIR):
    shutil.rmtree(EN_DIR)
    print(f"  Removed: {EN_DIR}")

# ================================================================
# SUMMARY
# ================================================================
print("\n" + "=" * 60)
print("MIGRATION COMPLETE")
print("=" * 60)
print(f"  /en/ → /en_bak/ (rollback if needed)")
print(f"  English files copied to root: {count}")
print(f"  English hreflang updated: {fixes_en}")
print(f"  /zh/ hreflang updated: {fixes_zh}")
print(f"  _redirects entries rewritten: {mod_count}")
print(f"  Chinese→/zh/ redirects added: {cn_redirects_added}")
print(f"  /en/ directory removed")
print("\nNext: regenerate sitemap, commit, push")

# Save a rollback script
ROLLBACK = os.path.join(ROOT, "scripts", "phase0b_rollback.py")
with open(ROLLBACK, 'w', encoding='utf-8') as f:
    f.write(f'''"""Rollback Phase 0b: restore /en/ + Chinese root."""
import os, shutil
ROOT = r"{ROOT}"
EN_DIR = os.path.join(ROOT, "en")
EN_BAK = os.path.join(ROOT, "en_bak")
ZH_DIR = os.path.join(ROOT, "zh")

# 1. Restore /en/
if os.path.exists(EN_BAK):
    if os.path.exists(EN_DIR):
        shutil.rmtree(EN_DIR)
    shutil.copytree(EN_BAK, EN_DIR)
    print("Restored /en/")

# 2. Restore Chinese root from /zh/
for fname in os.listdir(ZH_DIR):
    if fname.endswith('.html'):
        shutil.copy2(os.path.join(ZH_DIR, fname), os.path.join(ROOT, fname))
print("Restored root Chinese files")

# 3. Restore Chinese subdirectories
for subdir in ['brands', 'products', 'posts']:
    src = os.path.join(ZH_DIR, subdir)
    dst = os.path.join(ROOT, subdir)
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"Restored root {subdir}/")

print("Rollback complete. Restore _redirects from git: git checkout _redirects")
''')
print(f"\nRollback script saved: {ROLLBACK}")
