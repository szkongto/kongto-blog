#!/usr/bin/env python3
"""
Audit and add Schema.org structured data to all HTML pages.
Page type detection:
- index.html → Organization + LocalBusiness
- brands/*.html → Product
- compatibility-matrix.html → Dataset
- posts/*upgrade*.html or *guide*.html → HowTo
- posts/*.html → Article (BlogPosting)
- en/* → Same as above but with @language
"""
import os, re, json
from html.parser import HTMLParser

repo = '.'

# Page type detection
def detect_page_type(filepath):
    rel = filepath.replace(repo + '/', '').replace('\\', '/')
    fname = os.path.basename(filepath)
    
    if fname == 'index.html' and '/en/' not in rel:
        return 'homepage_zh'
    if fname == 'index.html' and '/en/' in rel:
        return 'homepage_en'
    if 'compatibility-matrix.html' in fname:
        return 'compatibility_matrix'
    if '/brands/' in rel:
        return 'product_brand'
    if '/posts/' in rel:
        if 'upgrade' in fname.lower() or 'guide' in fname.lower() or 'install' in fname.lower():
            return 'howto_article'
        return 'article'
    if fname in ('about.html', 'author.html'):
        return 'organization'
    return 'unknown'

# Check if page already has Schema
def has_schema(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    return 'application/ld+json' in content

# Generate Schema JSON-LD based on page type
def generate_schema(filepath):
    rel = filepath.replace(repo + '/', '').replace('\\', '/')
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', content, re.I)
    title = title_match.group(1) if title_match else os.path.basename(filepath)
    
    # Extract description
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', content, re.I)
    description = desc_match.group(1) if desc_match else title
    
    # Extract og:image
    img_match = re.search(r'<meta property="og:image" content="([^"]+)"', content, re.I)
    image = img_match.group(1) if img_match else 'https://cncdisplay.com/images/kongto-logo.png'
    if image.startswith('/'):
        image = 'https://cncdisplay.com' + image
    
    page_type = detect_page_type(filepath)
    schemas = []
    
    if page_type == 'homepage_zh':
        schemas = [
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Kongto Display Technology Co., Ltd.",
                "url": "https://cncdisplay.com/",
                "logo": "https://cncdisplay.com/images/kongto-logo.png",
                "description": description,
                "address": {
                    "@type": "PostalAddress",
                    "addressCountry": "CN"
                },
                "sameAs": [
                    "https://www.linkedin.com/company/kongto-display/"
                ]
            },
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "CNC Display",
                "url": "https://cncdisplay.com/",
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": "https://cncdisplay.com/posts/?q={search_term_string}",
                    "query-input": "required name=search_term_string"
                }
            }
        ]
    
    elif page_type == 'homepage_en':
        schemas = [
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Kongto Display Technology Co., Ltd.",
                "url": "https://cncdisplay.com/en/",
                "logo": "https://cncdisplay.com/images/kongto-logo.png",
                "description": description,
                "sameAs": [
                    "https://www.linkedin.com/company/kongto-display/"
                ]
            },
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "CNC Display",
                "url": "https://cncdisplay.com/en/",
                "inLanguage": "en"
            }
        ]
    
    elif page_type == 'product_brand':
        # Extract brand name from filename or content
        brand_match = re.search(r'/brands/([A-Z]+)\.html', rel)
        brand_name = brand_match.group(1) if brand_match else 'Unknown'
        
        schemas = [
            {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": title,
                "description": description,
                "brand": {
                    "@type": "Brand",
                    "name": brand_name
                },
                "manufacturer": {
                    "@type": "Organization",
                    "name": "Kongto Display Technology Co., Ltd."
                },
                "image": image,
                "offers": {
                    "@type": "Offer",
                    "availability": "https://schema.org/InStock",
                    "seller": {
                        "@type": "Organization",
                        "name": "Kongto Display Technology Co., Ltd."
                    }
                }
            }
        ]
    
    elif page_type == 'compatibility_matrix':
        schemas = [
            {
                "@context": "https://schema.org",
                "@type": "Dataset",
                "name": title,
                "description": description,
                "url": "https://cncdisplay.com/compatibility-matrix.html",
                "inLanguage": ["zh-CN", "en"],
                "creator": {
                    "@type": "Organization",
                    "name": "Kongto Display Technology Co., Ltd."
                }
            }
        ]
    
    elif page_type == 'howto_article':
        schemas = [
            {
                "@context": "https://schema.org",
                "@type": "HowTo",
                "name": title,
                "description": description,
                "image": image,
                "totalTime": "PT30M",
                "supply": [
                    {"@type": "HowToSupply", "name": "Replacement LCD Display"}
                ],
                "step": [
                    {"@type": "HowToStep", "name": "Safety Preparation", "text": "Power off CNC machine and discharge static"},
                    {"@type": "HowToStep", "name": "Remove Old Display", "text": "Carefully remove the original LCD display unit"},
                    {"@type": "HowToStep", "name": "Install New Display", "text": "Connect and mount the replacement LCD"},
                    {"@type": "HowToStep", "name": "Test Functionality", "text": "Power on and verify display operation"}
                ]
            },
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": title,
                "description": description,
                "image": image,
                "publisher": {
                    "@type": "Organization",
                    "name": "Kongto Display Technology Co., Ltd.",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://cncdisplay.com/images/kongto-logo.png"
                    }
                }
            }
        ]
    
    elif page_type == 'article':
        schemas = [
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": title,
                "description": description,
                "image": image,
                "datePublished": "2026-01-01",
                "publisher": {
                    "@type": "Organization",
                    "name": "Kongto Display Technology Co., Ltd.",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://cncdisplay.com/images/kongto-logo.png"
                    }
                }
            }
        ]
    
    return schemas

# Add Schema to page
def add_schema_to_page(filepath, schemas):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Generate JSON-LD script tags
    schema_scripts = []
    for schema in schemas:
        json_str = json.dumps(schema, ensure_ascii=False, indent=2)
        script = f'<script type="application/ld+json">\n{json_str}\n</script>'
        schema_scripts.append(script)
    
    schema_block = '\n'.join(schema_scripts)
    
    # Insert before </head>
    if '</head>' in content:
        content = content.replace('</head>', f'{schema_block}\n</head>', 1)
    else:
        # Insert after <head>
        head_match = re.search(r'(<head[^>]*>)', content, re.I)
        if head_match:
            insert_pos = head_match.end()
            content = content[:insert_pos] + f'\n{schema_block}\n' + content[insert_pos:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

# Main audit
print("=== Schema.org Audit ===")
pages_with_schema = []
pages_without_schema = []

for root, dirs, files in os.walk(repo):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('images', 'css', 'schema', 'docs', 'images_backup_compressed', 'backlinks_output', 'backlinks_daily', 'seo_audit_output')]
    for f in files:
        if not f.endswith('.html'):
            continue
        fpath = os.path.join(root, f)
        if has_schema(fpath):
            pages_with_schema.append(fpath.replace(repo + '/', '').replace('\\', '/'))
        else:
            pages_without_schema.append(fpath.replace(repo + '/', '').replace('\\', '/'))

print(f"Pages WITH Schema: {len(pages_with_schema)}")
print(f"Pages WITHOUT Schema: {len(pages_without_schema)}")
print(f"\nPages missing Schema:")
for p in pages_without_schema[:30]:
    print(f"  - {p}")

# Add Schema to pages that don't have it
if pages_without_schema:
    print(f"\n=== Adding Schema to {len(pages_without_schema)} pages ===")
    added = 0
    for relpath in pages_without_schema:
        fpath = os.path.join(repo, relpath.replace('/', os.sep))
        schemas = generate_schema(fpath)
        if schemas:
            add_schema_to_page(fpath, schemas)
            added += 1
            print(f"  [OK] Added Schema to {relpath} (type: {detect_page_type(fpath)})")
    print(f"\nTotal pages updated: {added}")
else:
    print("\nAll pages already have Schema!")

# Also check existing Schema quality
print("\n=== Schema Quality Check ===")
# Check for common issues: missing @context, missing @type, etc.
issues = []
for root, dirs, files in os.walk(repo):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('images', 'css', 'schema', 'docs', 'images_backup_compressed')]
    for f in files:
        if not f.endswith('.html'):
            continue
        fpath = os.path.join(root, f)
        relpath = fpath.replace(repo + '/', '').replace('\\', '/')
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
        
        # Find all JSON-LD blocks
        json_ld_blocks = re.findall(r'<script type="application/ld+json">(.*?)</script>', content, re.DOTALL)
        for i, block in enumerate(json_ld_blocks):
            try:
                schema = json.loads(block)
                # Check for required fields
                if '@context' not in schema:
                    issues.append(f"{relpath}: JSON-LD block {i+1} missing @context")
                if '@type' not in schema:
                    issues.append(f"{relpath}: JSON-LD block {i+1} missing @type")
            except json.JSONDecodeError as e:
                issues.append(f"{relpath}: JSON-LD block {i+1} invalid JSON: {e}")

if issues:
    print(f"Found {len(issues)} Schema quality issues:")
    for issue in issues[:20]:
        print(f"  - {issue}")
else:
    print("No Schema quality issues found!")

print("\n=== DONE ===")
