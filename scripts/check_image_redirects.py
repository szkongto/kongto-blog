"""Check which HTML pages reference images that are being blocked by _redirects."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load image->page redirects
redirects = {}
with open(os.path.join(ROOT, '_redirects'), 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 3 and '/images/' in parts[0]:
            src = parts[0]
            dst = parts[1]
            # Only flag image->page redirects (not image->image)
            if not dst.startswith('/images/') and not dst.startswith('https://'):
                redirects[src] = dst

print(f"Found {len(redirects)} image-to-page redirects in _redirects\n")

# Walk all HTML files
html_files = []
skip_dirs = {'.git', '.github', 'node_modules', '_archive_audit',
             'backlinks_output', 'backlinks_daily', '.claude', '_templates'}
for root, dirs, files in os.walk(ROOT):
    rel = os.path.relpath(root, ROOT).replace(os.sep, '/')
    # Skip dirs
    dirs[:] = [d for d in dirs if d not in skip_dirs and not rel.startswith(tuple(skip_dirs))]
    for f in files:
        if f.endswith('.html'):
            html_files.append(os.path.join(root, f))

print(f"Scanning {len(html_files)} HTML files...\n")

found = 0
problems = []
for src, dst in sorted(redirects.items()):
    img_name = os.path.basename(src)
    for fp in html_files:
        try:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            continue
        if img_name in content:
            rel = os.path.relpath(fp, ROOT).replace(os.sep, '/')
            problems.append((rel, img_name, dst))
            found += 1

if problems:
    print("PAGES WITH BLOCKED IMAGES:")
    for rel, img, dst in problems:
        print(f"  {rel} -> {img} (redirected to {dst})")
    print(f"\nTotal: {found}")
else:
    print("No blocked images found. All remaining image redirects are clean.")

# Also list all remaining image redirects for reference
print("\n=== REMAINING IMAGE REDIRECTS ===")
for src, dst in sorted(redirects.items()):
    print(f"  {src} -> {dst}")
