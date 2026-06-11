"""Precise model keyword optimization — only target pages where the model IS the primary topic.

Rule: Only optimize pages whose ORIGINAL H1 or title already contains the model number.
This ensures we don't inject model keywords into general-topic pages.
"""
import os, re, sys

ROOT = "d:/code/seo_deploy"
os.chdir(ROOT)

# Model → (brand_en, brand_cn, display_en, display_cn)
MODEL_MAP = {
    "A61L-0001-0093": ("FANUC", "FANUC发那科", "LCD Display Replacement", "LCD液晶显示器替换"),
    "A61L-0001-0074": ("FANUC", "FANUC发那科", "LCD Display Replacement", "LCD液晶显示器替换"),
    "A61L-0001-0086": ("FANUC", "FANUC发那科", "LCD Display Replacement", "LCD液晶显示器替换"),
    "A61L-0001-0090": ("FANUC", "FANUC发那科", "LCD Display Replacement", "LCD液晶显示器替换"),
    "A61L-0001-0092": ("FANUC", "FANUC发那科", "LCD Display Replacement", "LCD液晶显示器替换"),
    "A61L-0001-0094": ("FANUC", "FANUC发那科", "LCD Display Replacement", "LCD液晶显示器替换"),
    "A61L-0001-0095": ("FANUC", "FANUC发那科", "LCD Display Replacement", "LCD液晶显示器替换"),
    "A61L-0001-0096": ("FANUC", "FANUC发那科", "LCD Display Replacement", "LCD液晶显示器替换"),
    "A61L-0001-0097": ("FANUC", "FANUC发那科", "LCD Display Replacement", "LCD液晶显示器替换"),
    "D9MM-11A": ("FANUC", "FANUC发那科", "LCD Display", "LCD液晶显示器"),
    "MDT962B": ("Mitsubishi", "三菱Mitsubishi", "Industrial LCD Display", "工业液晶显示器"),
    "BM09DF": ("Mitsubishi", "三菱Mitsubishi", "Industrial Display TFT Replacement", "工业显示器TFT替换"),
    "FCUA-CT100": ("Mitsubishi", "三菱Mitsubishi", "Industrial Display TFT Replacement", "工业TFT显示器替换"),
    "CD1472-D1M": ("Mazak", "马扎克Mazak", "CNC Display Replacement", "数控显示器替换"),
    "C5470NS": ("Mazak", "马扎克Mazak", "CNC CRT Display", "数控CRT显示器"),
    "DR5614": ("Mazak", "马扎克Mazak", "CNC CRT Display Replacement", "数控CRT显示器替换"),
    "MDT-1283": ("Mazak", "马扎克Mazak", "CNC Display Replacement", "数控显示器替换"),
    "6FC3988-7FA20": ("Siemens", "西门子Siemens", "SINUMERIK LCD Display", "SINUMERIK液晶显示器"),
    "SM0901-579417-TA": ("Siemens", "西门子Siemens", "SINUMERIK LCD Display", "SINUMERIK液晶显示器"),
    "A1QA8DSP40": ("Mazak", "马扎克Mazak", "CNC Display Replacement", "数控显示器替换"),
    "OSP 5000": ("Okuma", "大隈Okuma", "CNC CRT Display", "数控CRT显示器"),
    "GBS-8219": ("Kongto", "江图科技", "RGB to VGA Industrial Converter", "RGB转VGA工业信号转换器"),
    "KT809": ("Kongto", "江图科技", "Industrial Video Converter", "工业视频转换器"),
    "KT819": ("Kongto", "江图科技", "Industrial Video Converter", "工业视频转换器"),
}

def get_model_from_h1(html):
    """Check if the original H1 contains any model from our map."""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE)
    if not m:
        return None
    h1 = m.group(1)
    for model in MODEL_MAP:
        if model.lower() in h1.lower():
            return model
    return None

def fix_page(filepath, model, is_en):
    """Precise keyword fix for a page that IS about this model."""
    with open(filepath, "rb") as f:
        raw = f.read()
    html = raw.decode("utf-8", errors="replace")
    original = html

    brand_en, brand_cn, disp_en, disp_cn = MODEL_MAP[model]
    brand = brand_en if is_en else brand_cn
    display = disp_en if is_en else disp_cn
    kw = f"{brand} {model} {display}"

    changes = []

    # 1. TITLE — ensure model present
    m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    if m:
        title_old = m.group(1)
        title_text = re.sub(r'<[^>]+>', '', title_old).strip()
        if model.lower() not in title_text.lower():
            # Extract suffix (company name)
            suffix = "Kongto Technology" if is_en else "深圳市江图科技有限公司"
            new_title = f"{kw} | {suffix}"
            html = html.replace(title_old, new_title, 1)
            changes.append(f"title: +{model}")

    # 2. H1 — ensure brand+model present
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE)
    if m:
        h1_old = m.group(1)
        h1_text = re.sub(r'<[^>]+>', '', h1_old).strip()
        if brand.lower() not in h1_text.lower() or model.lower() not in h1_text.lower():
            new_h1 = f"{kw} — {h1_text}" if len(f"{kw} — {h1_text}") < 120 else kw
            html = html.replace(h1_old, new_h1, 1)
            changes.append(f"H1: +{brand} {model}")

    # 3. META DESC — must contain model
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.IGNORECASE)
    if m:
        desc_old = m.group(1)
        if model.lower() not in desc_old.lower():
            new_desc = f"{brand} {model} {display}. " + desc_old
            if len(new_desc) > 158:
                new_desc = f"{brand} {model} {display}. " + desc_old[:158 - len(f"{brand} {model} {display}. ")]
            html = html.replace(f'content="{desc_old}"', f'content="{new_desc}"', 1)
            changes.append(f"meta_desc: +{model}")

    # 4. META KEYWORDS — add model variants
    m = re.search(r'<meta\s+name="keywords"\s+content="([^"]+)"', html, re.IGNORECASE)
    if m:
        kwds = m.group(1)
        to_add = [model, f"{brand} {model}", f"{model} replacement", f"{model} upgrade",
                  f"{brand} {model} {display}"]
        for kw_add in to_add:
            if kw_add.lower() not in kwds.lower():
                kwds = kw_add + ", " + kwds
        html = html.replace(f'content="{m.group(1)}"', f'content="{kwds}"', 1)
        changes.append(f"keywords: added model variants")

    # 5. FIRST PARAGRAPH — bold lead-in
    h1_pos = html.lower().find("<h1")
    if h1_pos > 0:
        m = re.search(r"<p\b[^>]*>(.*?)</p>", html[h1_pos:], re.DOTALL)
        if m:
            fp = m.group(1)
            fp_text = re.sub(r'<[^>]+>', '', fp).strip()
            if model.lower() not in fp_text.lower()[:200]:
                new_fp = f"<strong>{kw}</strong> — " + fp.strip()
                html = html.replace(fp, new_fp, 1)
                changes.append(f"first_p: bold {model}")

    # 6. BODY DENSITY — ensure 3+ occurrences
    body = html.lower()
    model_count = body.count(model.lower())
    if model_count < 3:
        booster = f"<p style=\"color:#555;margin-top:1.5rem;\"><em>{kw} — supplied by Shenzhen Kongto Technology Co.,LTD, a China-based manufacturer with 12+ years of industrial display expertise. This {model} upgrade solution is plug-and-play, retains original mounting dimensions, and includes 2-year warranty with free lifetime technical support. Contact szkongto01@foxmail.com for pricing.</em></p>"
        if is_en:
            pass  # use EN booster above
        else:
            booster = f"<p style=\"color:#555;margin-top:1.5rem;\"><em>{kw} — 由深圳市江图科技有限公司提供，12年工业显示经验厂家直供。{model}升级方案即插即用，保留原安装尺寸，2年超长质保，终身免费技术支持。联系szkongto01@foxmail.com获取报价。</em></p>"
        if "</article>" in html:
            html = html.replace("</article>", f"{booster}\n</article>", 1)
            changes.append(f"body: booster paragraph ({model_count}→{model_count+2}+)")

    if changes:
        with open(filepath, "wb") as f:
            f.write(html.encode("utf-8"))
    return changes

def main():
    fixed = []
    for root, dirs, files in os.walk("."):
        if any(x in root for x in ["seo_fix_package", "output", ".git"]):
            continue
        for fname in sorted(files):
            if not fname.endswith(".html"):
                continue
            filepath = os.path.join(root, fname).replace("\\", "/")
            rel = os.path.relpath(filepath, ".").replace("\\", "/")

            if "/posts/" not in rel or fname == "index.html":
                continue
            is_en = rel.startswith("en/")
            if not is_en:
                continue  # Currently only fixing EN pages — add CN later

            with open(filepath, "rb") as f:
                raw = f.read()
            html = raw.decode("utf-8", errors="replace")

            # Skip redirect pages
            if 'http-equiv="refresh"' in html.lower()[:1000]:
                continue

            model = get_model_from_h1(html)
            if not model:
                continue

            changes = fix_page(filepath, model, is_en)
            if changes:
                fixed.append((rel, model, changes))

    print(f"Precise model keyword fix — {len(fixed)} pages:")
    for rel, model, changes in fixed:
        print(f"  [{model}] {rel}")
        for c in changes:
            print(f"    {c}")

if __name__ == "__main__":
    main()
