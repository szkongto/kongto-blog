#!/usr/bin/env python3
"""
Audit and optimize image alt attributes for SEO.
- Find images missing alt text
- Generate descriptive alt text with keywords
- Update images with optimized alt text
"""
import os, re

repo = '.'

# Extract keywords from page title/content
def extract_keywords(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Get title
    title_match = re.search(r'<title>(.*?)</title>', content, re.I)
    title = title_match.group(1) if title_match else ''
    
    # Get H1
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.I | re.DOTALL)
    h1 = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip() if h1_match else ''
    
    # Extract brand/CNC keywords
    keywords = []
    brands = re.findall(r'FANUC|Mitsubishi|Mazak|Siemens|Okuma|Haas', content, re.I)
    keywords.extend(list(set([b.upper() for b in brands])))
    
    if 'LCD' in content or 'lcd' in content:
        keywords.append('LCD display')
    if 'CNC' in content or 'cnc' in content:
        keywords.append('CNC')
    if 'replacement' in content.lower() or 'upgrade' in content.lower():
        keywords.append('replacement')
    
    return title, h1, ' '.join(keywords[:5])

# Generate alt text for an image
def generate_alt_text(img_tag, page_title, page_keywords):
    # Get image filename
    src_match = re.search(r'src="([^"]+)"', img_tag, re.I)
    if not src_match:
        return None
    src = src_match.group(1)
    fname = os.path.basename(src)
    
    # If image is decorative (icon, logo, separator), return empty alt
    decorative_patterns = r'(logo|icon|arrow|separator|divider|spacer|pixel|blank)'
    if re.search(decorative_patterns, fname, re.I):
        return ''
    
    # Generate alt from filename + page keywords
    # Remove extension and replace -/_ with spaces
    name_part = os.path.splitext(fname)[0]
    name_part = re.sub(r'[-_]', ' ', name_part)
    name_part = re.sub(r'\d+', '', name_part).strip()  # Remove numbers
    
    if name_part and len(name_part) > 3:
        alt = f"{name_part}, {page_keywords}".strip(', ')
        return alt[:150]  # Limit to 150 chars
    
    # Fallback: use page title keywords
    if page_keywords:
        return f"{page_keywords} - product image"
    
    return None

# Audit images
print("=== Image Alt Attribute Audit ===")
images_total = 0
images_with_alt = 0
images_without_alt = 0
images_decorative = 0
pages_to_fix = {}

for root, dirs, files in os.walk(repo):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('images', 'css', 'schema', 'docs', 'images_backup_compressed', 'backlinks_output', 'backlinks_daily', 'seo_audit_output')]
    for f in files:
        if not f.endswith('.html'):
            continue
        fpath = os.path.join(root, f)
        relpath = fpath.replace(repo + '/', '').replace('\\', '/')
        
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
        
        # Find all images
        imgs = re.findall(r'<img[^>]+>', content, re.I)
        if not imgs:
            continue
        
        missing_alt = []
        for img in imgs:
            images_total += 1
            if 'alt=' in img.lower():
                alt_match = re.search(r'alt="([^"]*)"', img, re.I)
                if alt_match:
                    alt_val = alt_match.group(1)
                    if alt_val == '':
                        images_decorative += 1
                    else:
                        images_with_alt += 1
            else:
                images_without_alt += 1
                missing_alt.append(img)
        
        if missing_alt:
            pages_to_fix[relpath] = missing_alt

print(f"Total images: {images_total}")
print(f"Images with alt text: {images_with_alt}")
print(f"Images without alt text: {images_without_alt}")
print(f"Decorative images (alt=''): {images_decorative}")
print(f"\nPages needing alt text: {len(pages_to_fix)}")

if pages_to_fix:
    print("\nSample pages with missing alt:")
    for i, (page, imgs) in enumerate(list(pages_to_fix.items())[:10]):
        print(f"  {i+1}. {page}: {len(imgs)} images missing alt")

# Fix missing alt attributes
if pages_to_fix:
    print(f"\n=== Adding alt text to {sum(len(imgs) for imgs in pages_to_fix.values())} images ===")
    fixed_total = 0
    for relpath, imgs in pages_to_fix.items():
        fpath = os.path.join(repo, relpath.replace('/', os.sep))
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
        
        title, h1, keywords = extract_keywords(fpath)
        page_keywords = f"{title} {h1}".strip()
        
        fixed = 0
        for img in imgs:
            alt_text = generate_alt_text(img, title, page_keywords)
            if alt_text is not None:
                # Add alt attribute
                new_img = img.replace('>', f' alt="{alt_text}">', 1)
                content = content.replace(img, new_img, 1)
                fixed += 1
        
        if fixed > 0:
            with open(fpath, 'w', encoding='utf-8') as fp:
                fp.write(content)
            fixed_total += fixed
            print(f"  [OK] {relpath}: added alt to {fixed} images")
    
    print(f"\nTotal images fixed: {fixed_total}")
else:
    print("\nAll images already have alt text!")

# Also check for empty alt text that should be descriptive
print("\n=== Checking for non-descriptive alt text ===")
non_descriptive = 0
for root, dirs, files in os.walk(repo):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('images', 'css', 'schema', 'docs')]
    for f in files:
        if not f.endswith('.html'):
            continue
        fpath = os.path.join(root, f)
        relpath = fpath.replace(repo + '/', '').replace('\\', '/')
        
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
        
        # Find images with very short alt text (not decorative)
        imgs = re.findall(r'<img[^>]+alt="([^"]*)"[^>]*>', content, re.I)
        for alt in imgs:
            if 0 < len(alt) < 5:  # Very short, probably not descriptive
                non_descriptive += 1

if non_descriptive > 0:
    print(f"Found {non_descriptive} images with very short alt text (might need improvement)")
else:
    print("All alt text appears descriptive!")

print("\n=== DONE ===")
