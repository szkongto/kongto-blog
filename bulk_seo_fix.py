"""Bulk fix all SEO issues: OG tags, JSON-LD schema, hreflang, meta descriptions."""
import json, os, re, sys

ROOT = "d:/code/seo_deploy"
os.chdir(ROOT)

def fix_page(filepath, relpath):
    with open(filepath, "rb") as f:
        raw = f.read()
    html = raw.decode("utf-8", errors="replace")
    original = html

    # Determine page type and language
    is_en = relpath.startswith("en/")
    is_brand = "/brands/" in relpath
    is_article = "/posts/" in relpath and relpath.endswith(".html")
    is_search = relpath in ("search.html", "en/search.html")
    is_sitemap = relpath == "sitemap.html"
    is_author = relpath == "author.html"
    is_docs = relpath in ("docs/index.html", "en/docs/index.html")

    # Extract title
    m = re.search(r"<title>(.*?)</title>", html)
    title = m.group(1).strip() if m else ""
    title_clean = re.sub(r"\s*[|｜]\s*(?:深圳市江图科技有限公司|Kongto Technology).*$", "", title).strip()

    # Extract existing description
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
    desc = m.group(1) if m else ""

    lang_str = "en" if is_en else "zh-CN"
    site_name = "Kongto Technology" if is_en else "深圳市江图科技有限公司"
    base_path = "/en/" if is_en else "/"

    changes = []

    # ===== 1. Add OG tags if missing =====
    if "og:title" not in html:
        og_tags = f'\n    <meta property="og:type" content="website">\n    <meta property="og:title" content="{title_clean}">\n    <meta property="og:description" content="{desc[:150] if desc else title_clean}">\n    <meta property="og:url" content="https://cncdisplay.com/{relpath}">\n    <meta property="og:site_name" content="{site_name}">'
        # Insert after the existing meta description or charset
        if "link rel=\"canonical\"" in html:
            html = re.sub(r'(<link rel="canonical"[^>]*>)', rf'\1{og_tags}', html, count=1)
        else:
            html = re.sub(r'(<meta charset="[^"]+">)', rf'\1{og_tags}', html, count=1)
        changes.append("Added OG tags")

    # ===== 2. Add JSON-LD BreadcrumbList if missing =====
    if 'application/ld+json' not in html:
        url_path = "/" + relpath if not relpath.startswith("/") else relpath
        base_url = "https://cncdisplay.com"
        if is_en:
            home_name = "Home"
            page_name = title_clean
        else:
            home_name = "首页"
            page_name = title_clean

        breadcrumb = f'''
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [{{
        "@type": "ListItem",
        "position": 1,
        "name": "{home_name}",
        "item": "{base_url}{base_path}"
      }},{{
        "@type": "ListItem",
        "position": 2,
        "name": "{page_name}",
        "item": "{base_url}/{relpath}"
      }}]
    }}
    </script>'''

        # Insert before </head>
        html = html.replace("</head>", f"{breadcrumb}\n</head>", 1)
        changes.append("Added JSON-LD BreadcrumbList")

    # ===== 3. Add hreflang if missing for articles =====
    if is_article and "hreflang=" not in html:
        # Determine counterpart URL
        cn_url = "#"
        en_url = "#"
        src_fname = os.path.basename(filepath)
        if is_en:
            base_fname = src_fname
            cn_fname = None
            # Try to find matching CN file
            for fn in os.listdir("posts"):
                if "202605" in fn and os.path.splitext(fn)[0].replace("-", "_")[:20] == os.path.splitext(base_fname)[0].replace("-", "_")[:20]:
                    cn_fname = fn
                    break
            if cn_fname:
                cn_url = f"https://cncdisplay.com/posts/{cn_fname}"
            en_url = f"https://cncdisplay.com/{relpath}"
        else:
            cn_url = f"https://cncdisplay.com/{relpath}"
            base_fname = src_fname
            en_fname = None
            for fn in os.listdir("en/posts"):
                if os.path.splitext(fn)[0].replace("-", "_")[:20] == os.path.splitext(base_fname)[0].replace("-", "_")[:20]:
                    en_fname = fn
                    break
            if en_fname:
                en_url = f"https://cncdisplay.com/en/posts/{en_fname}"

        hreflang = f'\n    <link rel="alternate" hreflang="zh" href="{cn_url}" />\n    <link rel="alternate" hreflang="en" href="{en_url}" />\n    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/" />'
        # Insert after canonical
        if '<link rel="canonical"' in html:
            html = re.sub(r'(<link rel="canonical"[^>]*>)', rf'\1{hreflang}', html, count=1)
        else:
            html = html.replace("<head>", f"<head>{hreflang}", 1)
        changes.append("Added hreflang tags")

    # ===== 4. Fix invalid JSON-LD schema block #3 =====
    # These are articles that have a 3rd JSON-LD block with errors
    schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    fixed_schemas = []
    for s in schemas:
        try:
            json.loads(s.strip())
            fixed_schemas.append(s)
        except json.JSONDecodeError:
            # Try to fix common issues
            fixed = s.strip()
            # Remove trailing commas
            fixed = re.sub(r',\s*}', '}', fixed)
            fixed = re.sub(r',\s*]', ']', fixed)
            try:
                json.loads(fixed)
                html = html.replace(s, fixed, 1)
                fixed_schemas.append(fixed)
                changes.append(f"Fixed invalid JSON-LD block")
            except:
                # Remove the bad block entirely
                html = html.replace(f'<script type="application/ld+json">{s}</script>', '', 1)
                changes.append("Removed invalid JSON-LD block")

    if changes:
        with open(filepath, "wb") as f:
            f.write(html.encode("utf-8"))
        return changes
    return []

def main():
    fix_count = 0
    total_changes = 0
    for root, dirs, files in os.walk("."):
        if any(x in root for x in ["seo_fix_package", "output", ".git"]):
            continue
        for fname in files:
            if not fname.endswith(".html"):
                continue
            filepath = os.path.join(root, fname).replace("\\", "/")
            relpath = os.path.relpath(filepath, ".").replace("\\", "/")

            changes = fix_page(filepath, relpath)
            if changes:
                fix_count += 1
                total_changes += len(changes)
                print(f"  {relpath}: {', '.join(changes)}")

    print(f"\nFixed {fix_count} pages with {total_changes} total changes")

if __name__ == "__main__":
    main()
