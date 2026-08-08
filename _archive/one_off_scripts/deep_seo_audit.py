"""Deep SEO/GEO/BUG audit across all pages — find and report every issue."""
import json, os, re, sys, hashlib
from collections import defaultdict

ROOT = "d:/code/seo_deploy"
os.chdir(ROOT)

# Audit categories
ISSUES = {
    "critical": [],
    "high": [],
    "medium": [],
    "low": [],
    "info": [],
}

def add(cat, filepath, msg):
    ISSUES[cat].append({"file": filepath, "msg": msg})

def check_page(filepath, relpath):
    with open(filepath, "rb") as f:
        raw = f.read()
    size_kb = len(raw) / 1024
    try:
        html = raw.decode("utf-8")
    except UnicodeDecodeError:
        add("critical", relpath, "Not valid UTF-8")
        return

    # Skip redirect pages
    if 'http-equiv="refresh"' in html.lower() and 'window.location.href' not in html:
        add("info", relpath, "Skip: redirect page")
        return

    # ===== CRITICAL CHECKS =====
    if "<title>" not in html:
        add("critical", relpath, "Missing <title>")
    elif "</title>" not in html:
        add("critical", relpath, "Unclosed <title>")

    if "lang=" not in html[:200]:
        add("critical", relpath, "Missing lang attribute on <html>")

    # Check for broken HTML patterns
    if html.count("<html") > 1:
        add("critical", relpath, "Multiple <html> tags")
    if html.count("<body") > 1:
        add("critical", relpath, "Multiple <body> tags")

    # ===== HIGH CHECKS =====
    m = re.search(r"<title>(.*?)</title>", html)
    if m:
        title = m.group(1).strip()
        if len(title) < 20:
            add("high", relpath, f"Title too short ({len(title)} chars): {title[:50]}")
        elif len(title) > 70:
            add("low", relpath, f"Title too long ({len(title)} chars)")

    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
    if not m:
        add("high", relpath, "Missing meta description")
    else:
        desc = m.group(1)
        if len(desc) < 70:
            add("medium", relpath, f"Meta description too short ({len(desc)} chars)")
        elif len(desc) > 160:
            add("low", relpath, f"Meta description too long ({len(desc)} chars)")

    if 'rel="canonical"' not in html.lower():
        add("high", relpath, "Missing canonical link")
    else:
        m = re.search(r'canonical\s+href="([^"]+)"', html, re.IGNORECASE)
        if m:
            canon = m.group(1)
            if "cncdisplay.com" not in canon:
                add("high", relpath, f"Canonical points off-site: {canon}")

    # Check hreflang
    if 'hreflang=' not in html:
        add("medium", relpath, "Missing hreflang tags")
    else:
        hreflangs = re.findall(r'hreflang="([^"]+)"', html)
        if "x-default" not in hreflangs:
            add("low", relpath, "Missing x-default hreflang")

    # Schema
    if 'application/ld+json' not in html:
        add("medium", relpath, "Missing JSON-LD schema markup")
    else:
        schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        for i, schema_str in enumerate(schemas):
            try:
                schema = json.loads(schema_str.strip())
                stype = schema.get("@type", "unknown")
            except json.JSONDecodeError:
                add("medium", relpath, f"Invalid JSON-LD schema block #{i+1}")

    # OG tags
    if 'og:title' not in html:
        add("medium", relpath, "Missing og:title")
    if 'og:description' not in html:
        add("medium", relpath, "Missing og:description")
    if 'og:image' not in html:
        add("low", relpath, "Missing og:image")

    # Twitter cards
    if 'twitter:card' not in html:
        add("low", relpath, "Missing Twitter card meta")

    # ===== SECURITY HEADERS =====
    csp_issues = []
    if 'Content-Security-Policy' not in html:
        csp_issues.append("missing CSP")
    if 'X-Content-Type-Options' not in html:
        csp_issues.append("missing X-Content-Type-Options")
    if 'X-Frame-Options' not in html:
        csp_issues.append("missing X-Frame-Options")
    if 'Referrer-Policy' not in html:
        csp_issues.append("missing Referrer-Policy")
    if csp_issues:
        add("low", relpath, f"Security headers: {', '.join(csp_issues)}")

    # ===== CONTENT CHECKS =====
    words = len(re.findall(r'\w+', html))
    if words < 100:
        add("medium", relpath, f"Very thin content ({words} words)")

    # Check for broken image references
    imgs = re.findall(r'src="([^"]+)"', html)
    for img in imgs:
        if img.startswith("http") and "cncdisplay.com" not in img and "github" not in img:
            add("low", relpath, f"External image reference: {img}")

    # Check for empty alt text on important images
    img_alts = re.findall(r'<img[^>]*alt="([^"]*)"[^>]*>', html)
    empty_alts = [a for a in img_alts if not a.strip()]
    if empty_alts and len(empty_alts) > 5:
        add("low", relpath, f"{len(empty_alts)} images with empty alt text")

    # ===== LINK CHECKS =====
    internal_links = re.findall(r'href="([^"]*(?:cncdisplay\.com|/)[^"]*)"', html)
    if not internal_links and 'posts/' in relpath:
        add("medium", relpath, "No internal links found (orphan page risk)")

    # ===== H1 CHECKS =====
    h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', html)
    if not h1s:
        add("high", relpath, "Missing H1 tag")
    elif len(h1s) > 1:
        add("medium", relpath, f"Multiple H1 tags ({len(h1s)})")

    # ===== IMAGE SIZE CHECK =====
    large_imgs = [img for img in imgs if img.endswith(('.jpg', '.png', '.gif')) and '/images/' in img]
    # Just note image references for optimization later

    return True

def main():
    pages = 0
    lang_cn = 0
    lang_en = 0

    for root, dirs, files in os.walk("."):
        if any(x in root for x in ["seo_fix_package", "output", ".git"]):
            continue
        for fname in files:
            if not fname.endswith(".html"):
                continue
            filepath = os.path.join(root, fname).replace("\\", "/")
            relpath = os.path.relpath(filepath, ".").replace("\\", "/")

            # Skip utility/temp pages
            if fname in ("baidu_verify_codeva-MOcuLxbSCp.html",):
                continue

            check_page(filepath, relpath)
            pages += 1
            if relpath.startswith("en/") or "/en/" in relpath:
                lang_en += 1
            else:
                lang_cn += 1

    # Print report
    print("=" * 70)
    print(f"DEEP SEO/GEO AUDIT REPORT — {pages} pages ({lang_cn} CN + {lang_en} EN)")
    print("=" * 70)

    for level in ["critical", "high", "medium", "low", "info"]:
        items = ISSUES[level]
        if not items:
            continue
        emoji = {"critical": "[CRIT]", "high": "[HIGH]", "medium": "[MED ]", "low": "[LOW ]", "info": "[INFO]"}
        print(f"\n{emoji[level]} {level.upper()} — {len(items)} issues")
        print("-" * 40)
        for item in items:
            print(f"  {item['file']}")
            print(f"    → {item['msg']}")

    # Summary stats
    total = sum(len(v) for v in ISSUES.values())
    print(f"\n{'='*70}")
    print(f"SUMMARY: {total} total issues across {pages} pages")
    for lvl in ["critical", "high", "medium", "low"]:
        print(f"  {lvl}: {len(ISSUES[lvl])}")
    print("=" * 70)

    # Write JSON report
    report = {
        "date": "2026-06-10",
        "pages": pages,
        "pages_cn": lang_cn,
        "pages_en": lang_en,
        "issues": {k: v for k, v in ISSUES.items()},
    }
    with open("seo_audit_report.json", "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("\nReport saved to seo_audit_report.json")

if __name__ == "__main__":
    main()
