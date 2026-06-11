"""Audit and fix primary model keyword (brand+model+display) across all articles.

The most critical keyword strategy: every article MUST prominently feature
its primary keyword in: title, H1, meta description, first paragraph, URL.
Pattern: {BRAND} {MODEL} {TYPE}  e.g. "FANUC A61L-0001-0093 LCD显示器"

This script:
1. Auto-detects the primary model keyword for each article
2. Checks keyword presence in all critical positions
3. Fixes missing/weak keyword placements
"""
import json, os, re, sys

ROOT = "d:/code/seo_deploy"
os.chdir(ROOT)

# Brand display name mapping
BRAND_NAMES = {
    "FANUC": {"cn": "FANUC发那科", "en": "FANUC"},
    "Mitsubishi": {"cn": "三菱Mitsubishi", "en": "Mitsubishi"},
    "Mazak": {"cn": "马扎克Mazak", "en": "Mazak"},
    "Siemens": {"cn": "西门子Siemens", "en": "Siemens"},
    "Okuma": {"cn": "大隈Okuma", "en": "Okuma"},
    "Haas": {"cn": "哈斯Haas", "en": "Haas"},
}

# Model regex patterns — exact model numbers
MODEL_PATTERNS = [
    (r'A61L[- ]0001[- ]0093', 'FANUC', 'A61L-0001-0093'),
    (r'A61L[- ]0001[- ]0074', 'FANUC', 'A61L-0001-0074'),
    (r'A61L[- ]0001[- ]0086', 'FANUC', 'A61L-0001-0086'),
    (r'A61L[- ]0001[- ]0090', 'FANUC', 'A61L-0001-0090'),
    (r'A61L[- ]0001[- ]0092', 'FANUC', 'A61L-0001-0092'),
    (r'A61L[- ]0001[- ]0094', 'FANUC', 'A61L-0001-0094'),
    (r'A61L[- ]0001[- ]0095', 'FANUC', 'A61L-0001-0095'),
    (r'A61L[- ]0001[- ]0096', 'FANUC', 'A61L-0001-0096'),
    (r'A61L[- ]0001[- ]0097', 'FANUC', 'A61L-0001-0097'),
    (r'D9MM[- ]11A', 'FANUC', 'D9MM-11A'),
    (r'MDT962B', 'Mitsubishi', 'MDT962B'),
    (r'MDT[- ]1283', 'Mazak', 'MDT-1283'),
    (r'BM09DF', 'Mitsubishi', 'BM09DF'),
    (r'FCUA[- ]CT100', 'Mitsubishi', 'FCUA-CT100'),
    (r'CD1472[- ]D1M', 'Mazak', 'CD1472-D1M'),
    (r'C5470NS', 'Mazak', 'C5470NS'),
    (r'DR5614', 'Mazak', 'DR5614'),
    (r'6FC3988[- ]7FA20', 'Siemens', '6FC3988-7FA20'),
    (r'SM0901[- ]579417[- ]TA', 'Siemens', 'SM0901-579417-TA'),
    (r'A1QA8DSP40', 'Sharp/Mazak', 'A1QA8DSP40'),
    (r'KTV\d+', 'Kongto', None),  # Product series, skip
    (r'GBS[- ]8219', 'Generic', 'GBS-8219'),
    (r'KT809', 'Kongto', 'KT809'),
    (r'KT819', 'Kongto', 'KT819'),
    (r'OSP\s*5000', 'Okuma', 'OSP 5000'),
    (r'OSP\s*5020', 'Okuma', 'OSP 5020'),
]

def detect_model_info(html, filepath):
    """Detect the primary brand + model from a page."""
    fname = os.path.basename(filepath)
    rel = filepath.replace("\\", "/")

    # Try filename first
    for pattern, brand, model in MODEL_PATTERNS:
        m = re.search(pattern, fname, re.IGNORECASE)
        if m and model:
            return brand, model

    # Try first 5000 chars of body
    body_start = html.find("<body")
    body = html[body_start:body_start+5000] if body_start > 0 else html[:5000]
    for pattern, brand, model in MODEL_PATTERNS:
        m = re.search(pattern, body, re.IGNORECASE)
        if m and model:
            return brand, model

    return None, None

def build_primary_keyword(brand, model, is_en):
    """Build the primary keyword: BRAND MODEL TYPE"""
    if is_en:
        display_type = "LCD Display" if "LCD" in model else "CNC Display"
        return f"{brand} {model} {display_type}"
    else:
        brand_cn = BRAND_NAMES.get(brand, {}).get("cn", brand)
        display_type = "LCD液晶显示器" if "LCD" in model else "数控显示器"
        return f"{brand_cn} {model} {display_type}"

def check_keyword_positions(html, keyword):
    """Check where the keyword appears and return positions."""
    results = {}
    kw_lower = keyword.lower()
    html_lower = html.lower()

    # Title
    m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    title = m.group(1) if m else ""
    results["title"] = kw_lower in title.lower()

    # H1
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE)
    h1 = m.group(1) if m else ""
    results["h1"] = kw_lower in h1.lower()

    # Meta description
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.IGNORECASE)
    desc = m.group(1) if m else ""
    results["meta_desc"] = kw_lower in desc.lower()

    # Meta keywords
    m = re.search(r'<meta\s+name="keywords"\s+content="([^"]+)"', html, re.IGNORECASE)
    kwds = m.group(1) if m else ""
    results["meta_keywords"] = kw_lower in kwds.lower()

    # First <p> after H1
    h1_pos = html_lower.find("<h1")
    first_p = ""
    if h1_pos > 0:
        m = re.search(r"<p[^>]*>(.*?)</p>", html[h1_pos:], re.IGNORECASE | re.DOTALL)
        if m:
            first_p = m.group(1)
    results["first_para"] = kw_lower in first_p.lower()

    # Count total occurrences in body
    body_start = html_lower.find("<body")
    body_end = html_lower.find("<footer") if "<footer" in html_lower else html_lower.find("</body>")
    body = html_lower[body_start:body_end] if body_start > 0 and body_end > 0 else html_lower
    # Count the brand+model part (not full keyword, just model number)
    model_part = keyword.split()[-1] if " " in keyword else keyword
    results["body_count"] = body.count(model_part.lower())

    return results, title, h1, desc, kwds, first_p

def fix_keyword(html, keyword, brand, model, is_en):
    """Fix keyword placement issues."""
    original = html
    changes = []

    kw_brand_model = f"{brand} {model}"  # Just brand+model
    kw_full = keyword  # brand+model+display type

    # 1. Fix H1 — MUST contain brand+model at minimum
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE)
    if m:
        h1 = m.group(1)
        h1_clean = re.sub(r'<[^>]+>', '', h1).strip()
        if kw_brand_model.lower() not in h1_clean.lower() and model.lower() not in h1_clean.lower():
            # H1 is missing the model number — prepend it
            # Different H1 patterns:
            if is_en:
                new_h1 = f"{kw_full} — {h1_clean}"
            else:
                new_h1 = f"{kw_full} — {h1_clean}"
            # Don't make it too long
            if len(new_h1) > 120:
                new_h1 = f"{kw_full}"
            html = html.replace(h1, new_h1, 1)
            changes.append(f"H1: added '{model}'")
    else:
        changes.append("WARN: No H1 tag found")

    # 2. Fix meta description — MUST contain brand+model
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.IGNORECASE)
    if m:
        desc = m.group(1)
        if kw_brand_model.lower() not in desc.lower() and model.lower() not in desc.lower():
            # Prepend model info to description
            prefix = f"{brand} {model} " if is_en else f"{BRAND_NAMES.get(brand, {}).get('cn', brand)} {model} "
            new_desc = prefix + desc
            if len(new_desc) > 160:
                # Truncate the old desc to fit
                new_desc = prefix + desc[:160 - len(prefix)]
            html = html.replace(f'content="{desc}"', f'content="{new_desc}"', 1)
            changes.append(f"Meta desc: added '{model}'")
    else:
        changes.append("WARN: No meta description")

    # 3. Fix meta keywords — MUST contain brand+model+display variants
    m = re.search(r'<meta\s+name="keywords"\s+content="([^"]+)"', html, re.IGNORECASE)
    if m:
        kwds = m.group(1)
        needed = [model]
        if brand.lower() not in kwds.lower():
            needed.insert(0, brand)
        missing = [k for k in needed if k.lower() not in kwds.lower()]
        if missing:
            new_kwds = ", ".join(missing) + ", " + kwds
            html = html.replace(f'content="{kwds}"', f'content="{new_kwds}"', 1)
            changes.append(f"Keywords: added {missing}")

    # 4. Ensure first paragraph after H1 contains the model
    h1_pos = html.lower().find("<h1")
    if h1_pos > 0:
        first_p_match = re.search(r"<p[^>]*>(.*?)</p>", html[h1_pos:], re.IGNORECASE | re.DOTALL)
        if first_p_match:
            first_p = first_p_match.group(1)
            if model.lower() not in first_p.lower().replace('<strong>', '').replace('</strong>', ''):
                # Add model mention at start of first paragraph
                if is_en:
                    insert = f"<strong>{kw_full}</strong> "
                else:
                    insert = f"<strong>{kw_full}</strong> "
                new_p = insert + first_p.strip()
                html = html.replace(first_p, new_p, 1)
                changes.append(f"First para: added '{model}' bold lead-in")

    return html if html != original else original, changes


def main():
    issues = []
    fixed = []

    for root, dirs, files in os.walk("."):
        if any(x in root for x in ["seo_fix_package", "output", ".git"]):
            continue
        for fname in sorted(files):
            if not fname.endswith(".html"):
                continue
            filepath = os.path.join(root, fname).replace("\\", "/")
            rel = os.path.relpath(filepath, ".").replace("\\", "/")
            if "/en/" in rel:
                continue  # Skip EN for now, they use different patterns
            is_en = False

            if "/posts/" not in rel or rel.endswith("index.html"):
                continue

            with open(filepath, "rb") as f:
                raw = f.read()
            html = raw.decode("utf-8", errors="replace")

            brand, model = detect_model_info(html, filepath)
            if not brand or not model:
                continue

            keyword = build_primary_keyword(brand, model, is_en)
            pos, title, h1, desc, kwds, first_p = check_keyword_positions(html, keyword)

            # Score: how many of 6 critical positions have the keyword?
            score = sum(1 for v in pos.values() if v)
            body_count = pos.get("body_count", 0)

            if score < 6 or body_count < 3:
                # Needs fixing
                new_html, changes = fix_keyword(html, keyword, brand, model, is_en)
                if changes and new_html != html:
                    with open(filepath, "wb") as f:
                        f.write(new_html.encode("utf-8"))
                    fixed.append((rel, keyword, score, changes))
                else:
                    issues.append((rel, keyword, score, pos, "No auto-fix applied"))
            else:
                issues.append((rel, keyword, score, None, "OK"))

    # Report
    print(f"{'='*70}")
    print(f"MODEL KEYWORD AUDIT — Brand+Model+Display Keyword Check")
    print(f"{'='*70}")
    print(f"\n✅ FIXED ({len(fixed)} pages):")
    for rel, kw, score, changes in fixed:
        print(f"  [{score}/6] {rel}")
        print(f"    Keyword: {kw}")
        for c in changes:
            print(f"    → {c}")

    print(f"\n⚠️  ISSUES (no auto-fix) ({len([i for i in issues if i[2] < 6])} pages):")
    for rel, kw, score, extra, note in issues:
        if score < 6:
            print(f"  [{score}/6] {rel} — {note}")
            if extra:
                missing = [k for k, v in extra.items() if not v]
                print(f"    Missing from: {', '.join(missing)}")

    # Summary
    total = len(fixed) + len(issues)
    good = len([i for i in issues if i[2] >= 5])
    print(f"\n{'='*70}")
    print(f"SUMMARY: {total} articles, {len(fixed)} fixed, {good} already OK")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
