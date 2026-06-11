"""Fix primary model keyword (BRAND MODEL DISPLAY) across ALL articles — EN and CN.

Every article's H1, title, meta description, and first paragraph MUST contain
the primary keyword: {BRAND} {MODEL} {DISPLAY_TYPE}
e.g. "FANUC A61L-0001-0093 LCD Display" / "FANUC发那科 A61L-0001-0093 LCD液晶显示器"
"""
import json, os, re, sys

ROOT = "d:/code/seo_deploy"
os.chdir(ROOT)

# Master list: (filename_pattern, brand_en, model, display_type_en, display_type_cn)
TARGET_KEYWORDS = [
    # FANUC A61L series
    ("0093", "FANUC", "A61L-0001-0093", "LCD Display Replacement", "LCD液晶显示器替换"),
    ("0074", "FANUC", "A61L-0001-0074", "LCD Display Replacement", "LCD液晶显示器替换"),
    ("0086", "FANUC", "A61L-0001-0086", "LCD Display Replacement", "LCD液晶显示器替换"),
    ("0090", "FANUC", "A61L-0001-0090", "LCD Display Replacement", "LCD液晶显示器替换"),
    ("0092", "FANUC", "A61L-0001-0092", "LCD Display Replacement", "LCD液晶显示器替换"),
    ("0094", "FANUC", "A61L-0001-0094", "LCD Display Replacement", "LCD液晶显示器替换"),
    ("0095", "FANUC", "A61L-0001-0095", "LCD Display Replacement", "LCD液晶显示器替换"),
    ("0096", "FANUC", "A61L-0001-0096", "LCD Display Replacement", "LCD液晶显示器替换"),
    ("0097", "FANUC", "A61L-0001-0097", "LCD Display Replacement", "LCD液晶显示器替换"),
    ("D9MM", "FANUC", "D9MM-11A", "LCD Display", "LCD液晶显示器"),
    # Mitsubishi
    ("MDT962B", "Mitsubishi", "MDT962B", "Industrial LCD Display", "工业液晶显示器"),
    ("BM09DF", "Mitsubishi", "BM09DF", "Industrial Display TFT Replacement", "工业显示器TFT替换"),
    ("FCUA-CT100", "Mitsubishi", "FCUA-CT100", "Industrial Display TFT Replacement", "工业TFT显示器替换"),
    # Mazak
    ("CD1472", "Mazak", "CD1472-D1M", "CNC Display", "数控显示器"),
    ("C5470NS", "Mazak", "C5470NS", "CNC CRT Display", "数控CRT显示器"),
    ("DR5614", "Mazak", "DR5614", "CNC CRT Display", "数控CRT显示器"),
    ("MDT-1283", "Mazak", "MDT-1283", "CNC Display", "数控显示器"),
    # Siemens
    ("6FC3988", "Siemens", "6FC3988-7FA20", "SINUMERIK LCD Display", "SINUMERIK液晶显示器"),
    ("SM0901", "Siemens", "SM0901-579417-TA", "SINUMERIK LCD Display", "SINUMERIK液晶显示器"),
    # Sharp / Mazak
    ("A1QA8DSP40", "Mazak", "A1QA8DSP40", "CNC Display", "数控显示器"),
    # Generic converters
    ("GBS-8219", "Kongto", "GBS-8219", "RGB to VGA Industrial Converter", "RGB转VGA工业转换器"),
    ("KT809", "Kongto", "KT809", "Industrial Video Converter", "工业视频转换器"),
    ("KT819", "Kongto", "KT819", "Industrial Video Converter", "工业视频转换器"),
    # Okuma
    ("OSP 5000", "Okuma", "OSP 5000", "CNC CRT Display", "数控CRT显示器"),
    ("OSP 5020", "Okuma", "OSP 5020", "CNC CRT Display", "数控CRT显示器"),
]

def build_keyword_combos(kw_info, is_en):
    """Build all keyword variants."""
    brand, model, dt_en, dt_cn = kw_info[1], kw_info[2], kw_info[3], kw_info[4]
    if is_en:
        return [
            f"{brand} {model} {dt_en}",          # FANUC A61L-0001-0093 LCD Display Replacement
            f"{brand} {model}",                    # FANUC A61L-0001-0093
            model,                                 # A61L-0001-0093
        ]
    else:
        return [
            f"{brand} {model} {dt_cn}",           # FANUC A61L-0001-0093 LCD液晶显示器替换
            f"{brand} {model}",                    # FANUC A61L-0001-0093
            model,                                 # A61L-0001-0093
        ]

def match_keyword(filepath, html):
    """Find which keyword this page targets."""
    fname = os.path.basename(filepath)
    for pattern, *rest in TARGET_KEYWORDS:
        if pattern in fname:
            return (pattern, *rest)
    # Try content
    for pattern, *rest in TARGET_KEYWORDS:
        if pattern in html:
            return (pattern, *rest)
    return None

def fix_page(filepath, kw_info, is_en):
    """Aggressively ensure primary keyword is in all critical positions."""
    with open(filepath, "rb") as f:
        raw = f.read()
    html = raw.decode("utf-8", errors="replace")
    original = html

    brand, model, dt_en, dt_cn = kw_info[1], kw_info[2], kw_info[3], kw_info[4]
    kw_primary = f"{brand} {model} {dt_en}" if is_en else f"{brand} {model} {dt_cn}"

    changes = []

    # 1. TITLE — must contain brand+model
    m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    if m:
        title_old = m.group(1)
        title_text = re.sub(r'<[^>]+>', '', title_old).strip()
        if model.lower() not in title_text.lower():
            sep = " | " if is_en else " | "
            suffix = title_text.split(sep)[-1] if sep in title_text else title_text
            new_title = f"{kw_primary} - {suffix}"[:120]
            html = html.replace(title_old, new_title, 1)
            changes.append(f"title: {title_text[:60]} → {new_title[:80]}")

    # 2. H1 — must contain brand+model
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE)
    if m:
        h1_old = m.group(1)
        h1_text = re.sub(r'<[^>]+>', '', h1_old).strip()
        if model.lower() not in h1_text.lower():
            new_h1 = f"{kw_primary} — {h1_text}"
            if len(new_h1) > 120:
                new_h1 = kw_primary
            html = html.replace(h1_old, new_h1, 1)
            changes.append(f"H1: +'{model}'")

    # 3. META DESCRIPTION — must contain brand+model
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.IGNORECASE)
    if m:
        desc_old = m.group(1)
        if model.lower() not in desc_old.lower():
            prefix = f"{brand} {model} " if is_en else f"{brand} {model} "
            new_desc = prefix + desc_old
            if len(new_desc) > 158:
                new_desc = prefix + desc_old[:158 - len(prefix)]
            html = html.replace(f'content="{desc_old}"', f'content="{new_desc}"', 1)
            changes.append(f"meta_desc: +'{model}'")

    # 4. META KEYWORDS — must contain brand+model+display
    m = re.search(r'<meta\s+name="keywords"\s+content="([^"]+)"', html, re.IGNORECASE)
    if m:
        kwds_old = m.group(1)
        to_add = []
        if model.lower() not in kwds_old.lower():
            to_add.append(model)
        if brand.lower() not in kwds_old.lower():
            to_add.append(brand)
        to_add.extend([kw_primary, f"{brand} {model} replacement", f"{brand} {model} upgrade"])
        for kw in to_add:
            if kw.lower() not in kwds_old.lower() and kw not in to_add[to_add.index(kw)+1:]:
                kwds_old = kw + ", " + kwds_old
        if kwds_old != m.group(1):
            html = html.replace(f'content="{m.group(1)}"', f'content="{kwds_old}"', 1)
            changes.append(f"keywords: added brand+model")

    # 5. FIRST PARAGRAPH AFTER H1 — bold lead-in with keyword
    h1_pos = html.lower().find("<h1")
    if h1_pos > 0:
        first_p_match = re.search(r"<p\b[^>]*>(.*?)</p>", html[h1_pos:], re.DOTALL)
        if first_p_match:
            fp = first_p_match.group(1)
            fp_text = re.sub(r'<[^>]+>', '', fp).strip()
            if model.lower() not in fp_text.lower()[:200]:
                lead = f"<strong>{kw_primary}</strong> — "
                new_fp = lead + fp.strip()
                html = html.replace(fp, new_fp, 1)
                changes.append(f"first_p: bold lead-in '{kw_primary}'")

    # 6. ENSURE at least 3 occurrences of model in body
    body_start = html.lower().find("<body")
    body_end = html.lower().find("<footer") if "<footer" in html.lower() else html.lower().rfind("</body>")
    body = html[body_start:body_end] if body_start > 0 and body_end > 0 else html
    model_count = body.lower().count(model.lower())
    if model_count < 3:
        # Append a keyword-rich description paragraph before </article>
        if is_en:
            booster = f'<p style="color:#555;margin-top:1.5rem;"><em>{kw_primary} — supplied by Shenzhen Kongto Technology, a China-based manufacturer with 12+ years of industrial display expertise. This {model} upgrade solution is plug-and-play, retains original mounting dimensions, and includes 2-year warranty with free lifetime technical support. Contact szkongto01@foxmail.com for pricing and availability.</em></p>'
        else:
            booster = f'<p style="color:#555;margin-top:1.5rem;"><em>{kw_primary} — 由深圳市江图科技有限公司（Kongto Technology）提供，12年工业显示经验厂家直供。{model}升级方案即插即用，保留原安装尺寸，2年超长质保，终身免费技术支持。联系szkongto01@foxmail.com获取报价。</em></p>'
        if "</article>" in html:
            html = html.replace("</article>", f"{booster}\n</article>", 1)
        elif "</div>" in html[html.lower().rfind("<main"):]:
            html = html.replace("</main>", f"{booster}\n</main>", 1)
        changes.append(f"body: added keyword booster ({model_count} → ~{model_count+2} occurrences)")

    if changes:
        with open(filepath, "wb") as f:
            f.write(html.encode("utf-8"))
        return changes
    return None

def main():
    fixed = []
    skipped = 0

    for root, dirs, files in os.walk("."):
        if any(x in root for x in ["seo_fix_package", "output", ".git"]):
            continue
        for fname in sorted(files):
            if not fname.endswith(".html"):
                continue
            filepath = os.path.join(root, fname).replace("\\", "/")
            rel = os.path.relpath(filepath, ".").replace("\\", "/")

            # Only fix article pages (posts/*)
            if "/posts/" not in rel or fname == "index.html":
                continue

            is_en = rel.startswith("en/")

            with open(filepath, "rb") as f:
                raw = f.read()
            html = raw.decode("utf-8", errors="replace")

            # Skip redirect pages
            if 'http-equiv="refresh"' in html.lower()[:1000]:
                skipped += 1
                continue

            kw_info = match_keyword(rel, html)
            if not kw_info:
                continue

            changes = fix_page(filepath, kw_info, is_en)
            if changes:
                fixed.append((rel, kw_info[2], changes))

    print(f"Fixed {len(fixed)} pages ({skipped} skipped as redirects):")
    for rel, model, changes in fixed:
        print(f"  [{model}] {rel}")
        for c in changes:
            print(f"    {c}")

    print(f"\nTotal: {len(fixed)} pages with primary keyword optimized")
    if fixed:
        print(f"Target keyword pattern: {{BRAND}} {{MODEL}} {{DISPLAY TYPE}}")
        print(f"Critical positions fixed: title, H1, meta desc, meta keywords, first paragraph, body density")

if __name__ == "__main__":
    main()
