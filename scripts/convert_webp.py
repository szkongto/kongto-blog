"""Convert all JPG/PNG images to WebP + update HTML references."""
import os, re
from PIL import Image

ROOT = r"d:\code\seo_deploy"
IMG_DIR = os.path.join(ROOT, "images")
QUALITY = 80

# Phase 1: Convert images
converted = 0
skipped = 0
errors = 0

for dirpath, dirs, files in os.walk(IMG_DIR):
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png'):
            continue

        src = os.path.join(dirpath, f)
        webp_name = os.path.splitext(f)[0] + '.webp'
        dst = os.path.join(dirpath, webp_name)

        # Skip if WebP already exists and is newer
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            skipped += 1
            continue

        try:
            img = Image.open(src)
            # Convert RGBA/PA to RGB for WebP
            if img.mode in ('RGBA', 'PA', 'P'):
                img = img.convert('RGBA')
            img.save(dst, 'WEBP', quality=QUALITY)
            converted += 1
            print(f"  WEBP: {os.path.relpath(dst, ROOT)} ({os.path.getsize(src)//1024}KB -> {os.path.getsize(dst)//1024}KB)")
        except Exception as e:
            print(f"  ERROR: {f}: {e}")
            errors += 1

print(f"\nConverted: {converted}, Skipped: {skipped}, Errors: {errors}")

# Phase 2: Update HTML references
print("\n--- Updating HTML .jpg references to .webp ---")
html_updated = 0

# Skip dirs
SKIP_DIRS = {'.git', '.github', '.claude', '__pycache__', 'en_bak', '_archive_audit', '_templates',
             'backlinks_daily', 'backlinks_output', 'schema', 'scripts', 'patches', '.ts', '.vscode',
             '.well-known', 'cross_poster', 'screaming_frog_reports', 'seo_reports'}

for dirpath, dirs, files in os.walk(ROOT):
    # Skip unwanted dirs
    rel = os.path.relpath(dirpath, ROOT).replace('\\', '/')
    if any(rel.startswith(s) or f'/{s}/' in f'/{rel}/' for s in SKIP_DIRS):
        continue
    for f in files:
        if not f.endswith('.html'):
            continue
        fp = os.path.join(dirpath, f)

        with open(fp, 'r', encoding='utf-8') as fh:
            c = fh.read()
        orig = c

        # Replace src="/images/xxx.jpg" → src="/images/xxx.webp"
        c = re.sub(r'(src=["\']/images/[^"\']+)\.(jpg|jpeg|png)(["\'])',
                   r'\1.webp\3', c, flags=re.IGNORECASE)

        # Replace src="images/xxx.jpg" (relative)
        c = re.sub(r'(src=["\']images/[^"\']+)\.(jpg|jpeg|png)(["\'])',
                   r'\1.webp\3', c, flags=re.IGNORECASE)

        # Replace content="/images/xxx.jpg" (OG images)
        c = re.sub(r'(content=["\']/images/[^"\']+)\.(jpg|jpeg|png)(["\'])',
                   r'\1.webp\3', c, flags=re.IGNORECASE)

        # Also handle loading="lazy" for any missing images
        # (separate step)

        if c != orig:
            with open(fp, 'w', encoding='utf-8') as fh:
                fh.write(c)
            html_updated += 1
            print(f"  HTML: {os.path.relpath(fp, ROOT)}")

print(f"\nHTML files updated: {html_updated}")
print("Done.")
