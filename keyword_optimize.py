"""Keyword optimization for cncdisplay.com — improve Google keyword rankings.

Strategy: Target long-tail model-specific keywords where competition is low.
Add commercial intent modifiers to titles, FAQ sections for long-tail coverage,
Product schema for model-specific pages, and topic cluster internal links.
"""
import json, os, re, sys, random

ROOT = "d:/code/seo_deploy"
os.chdir(ROOT)

# Commercial intent modifier keywords (English)
EN_BUY_MODIFIERS = [
    "Replacement", "Upgrade", "Supplier", "China Manufacturer",
    "Plug and Play", "Free Shipping", "2 Year Warranty",
    "Factory Price", "Buy Online", "Wholesale"
]

CN_BUY_MODIFIERS = [
    "替换", "升级", "供应商", "厂家直供",
    "即插即用", "包邮", "2年质保",
    "工厂直销", "在线购买", "技术支持"
]

# Long-tail FAQ templates by brand
FAQ_TEMPLATES_EN = {
    "FANUC": [
        ("Q: Is the FANUC {model} LCD replacement truly plug-and-play?",
         "A: Yes. Kongto Technology's FANUC {model} LCD upgrade module uses the original HONDA 20-pin connector and retains factory mounting dimensions. No CNC parameter changes, no soldering, no adapter boards required. Power off, swap the display, power on — done in 10-15 minutes."),
        ("Q: What is the price of FANUC {model} LCD replacement?",
         "A: Contact us at szkongto01@foxmail.com for a quote. Pricing depends on order quantity and shipping destination. We offer factory-direct pricing with 2-year warranty — the longest in the industrial display industry."),
        ("Q: How long does shipping take for FANUC {model} LCD module?",
         "A: Typically 2-5 business days via express courier. We ship worldwide from Shenzhen, China. Bulk orders may require additional processing time. Free express shipping on orders over certain quantities."),
        ("Q: Is the FANUC {model} LCD compatible with my CNC system?",
         "A: The {model} LCD module is compatible with FANUC 0 series, 0i-A/B/C/D, 16i, 18i, 21i, and OM-D CNC systems. It works with any CNC machine originally equipped with the {model} CRT display — machining centers, lathes, mills, grinders, and boring machines."),
    ],
    "Mitsubishi": [
        ("Q: Is the Mitsubishi {model} LCD replacement plug-and-play?",
         "A: Yes. Kongto Technology's Mitsubishi {model} LCD upgrade retains original connectors and mounting dimensions. Compatible with M64, E60, M500, M520 CNC systems. Installation takes approximately 15 minutes with zero CNC parameter modifications."),
        ("Q: Where to buy Mitsubishi {model} industrial LCD replacement in China?",
         "A: Kongto Technology (Shenzhen) is a direct manufacturer and supplier. Contact szkongto01@foxmail.com or call +86-13686889647 for pricing and availability. We offer 2-year warranty and worldwide shipping."),
    ],
    "Mazak": [
        ("Q: Is the Mazak {model} CRT to LCD upgrade plug-and-play?",
         "A: Yes. The Mazak {model} LCD module from Kongto Technology uses the original interface and mounting points. Compatible with Mazatrol CNC systems. No parameter changes, no modifications. Installation: 10-15 minutes."),
        ("Q: How much does Mazak {model} display replacement cost?",
         "A: Contact szkongto01@foxmail.com for a custom quote. We offer factory-direct pricing with 2-year warranty. Substantially more affordable than OEM replacement which can cost thousands of dollars."),
    ],
    "Siemens": [
        ("Q: Is the Siemens {model} LCD upgrade compatible with my Sinumerik system?",
         "A: The {model} LCD upgrade is compatible with Siemens SINUMERIK 840D and 810D Power Line systems. Plug-and-play installation with original connectors — no CNC parameter changes needed."),
    ],
    "Okuma": [
        ("Q: Can I replace my Okuma OSP CRT with an LCD display?",
         "A: Yes. Kongto Technology offers LCD upgrade solutions for Okuma OSP 5000 and 5020 CNC systems. Original connectors retained, plug-and-play installation in 10-15 minutes with 2-year warranty."),
    ],
    "Haas": [
        ("Q: Is there an LCD upgrade for older Haas CNC displays?",
         "A: Yes. Kongto Technology provides CRT-to-LCD upgrade kits for Haas VF, ST, and SL series machining centers. Direct-fit replacement with original mounting dimensions. 2-year warranty, worldwide shipping."),
    ],
}

FAQ_TEMPLATES_CN = {
    "FANUC": [
        ("问：FANUC {model} LCD替换真的是即插即用吗？",
         "答：是的。江图科技的FANUC {model} LCD升级模块采用原装HONDA 20针接口，保留原安装尺寸和固定孔位。不需要改数控参数、不需要焊接、不需要转接板。断电-更换-上电，10-15分钟完成。"),
        ("问：FANUC {model} LCD替换模块多少钱？",
         "答：请联系szkongto01@foxmail.com获取报价。价格取决于采购数量和发货地址。我们提供厂家直供价格，行业最长2年质保，终身免费技术支持。"),
        ("问：FANUC {model} LCD模块发货需要多久？",
         "答：一般2-5个工作日快递发货。我们从深圳直发全球。批量订单可能需要额外备货时间。达到一定采购量可享免运费。"),
        ("问：FANUC {model} LCD模块兼容哪些数控系统？",
         "答：{model} LCD模块兼容FANUC 0系列、0i-A/B/C/D、16i、18i、21i、OM-D等数控系统。适用于任何原配{model} CRT显示器的加工中心、数控车床、铣床、磨床、镗床。"),
    ],
    "Mitsubishi": [
        ("问：三菱{model} LCD替换是即插即用吗？",
         "答：是的。江图科技的三菱{model} LCD升级模块保留原装接口和安装尺寸，兼容M64、E60、M500、M520数控系统。安装约15分钟，不需修改任何CNC参数。"),
        ("问：三菱{model}工业液晶替代方案哪里购买？",
         "答：深圳市江图科技有限公司是直接生产厂家和供应商。联系szkongto01@foxmail.com或致电13686889647获取报价，2年质保，全球发货。"),
    ],
    "Mazak": [
        ("问：马扎克{model} CRT转LCD是即插即用吗？",
         "答：是的。江图科技的马扎克{model} LCD模块使用原装接口和安装位置，兼容Mazatrol数控系统。无需修改参数，安装只需10-15分钟。"),
        ("问：马扎克{model}显示器替换多少钱？",
         "答：联系szkongto01@foxmail.com获取报价。厂家直销价格，2年质保，比原厂替换便宜很多。"),
    ],
    "Siemens": [
        ("问：西门子{model} LCD升级兼容我的SINUMERIK系统吗？",
         "答：{model} LCD升级兼容西门子SINUMERIK 840D和810D Power Line系统。即插即用安装，原装接口，不需要改CNC参数。"),
    ],
    "Okuma": [
        ("问：大隈OSP CRT能换LCD吗？",
         "答：可以。江图科技提供大隈OSP 5000和5020数控系统的CRT转LCD升级方案。原装接口即插即用，安装10-15分钟，2年质保。"),
    ],
    "Haas": [
        ("问：老款哈斯CNC显示器能升级LCD吗？",
         "答：可以。江图科技提供哈斯Haas VF、ST、SL系列加工中心的CRT转LCD升级套件。原安装尺寸直接替换，2年质保，全球发货。"),
    ],
}

def extract_model(content, filepath):
    """Extract the primary model number from an article."""
    rel = filepath.replace("\\", "/")
    # Try from filename first
    fname = os.path.basename(filepath)
    # Common model patterns
    patterns = [
        r'A61L[-_]0001[-_]00\d+', r'D9MM[-_]11A', r'MDT962B', r'MDT[-_]1283',
        r'BM09DF', r'FCUA[-_]CT100', r'CD1472[-_]D1M', r'C5470NS', r'DR5614',
        r'6FC3988[-_]7FA20', r'SM0901[-_]579417[-_]TA',
        r'A1QA8DSP40', r'KTV\d+', r'GBS[-_]8219', r'KT809', r'KT819',
        r'A61L[-_]0001[-_]0074', r'A61L[-_]0001[-_]0086', r'A61L[-_]0001[-_]0090',
        r'A61L[-_]0001[-_]0092', r'A61L[-_]0001[-_]0094', r'A61L[-_]0001[-_]0095',
        r'A61L[-_]0001[-_]0096', r'A61L[-_]0001[-_]0097',
        r'OSP\s*5000', r'OSP\s*5020',
    ]
    for p in patterns:
        m = re.search(p, fname, re.IGNORECASE)
        if m:
            return m.group(0)
    return None

def detect_brand(content, filepath):
    """Detect which brand this article is about."""
    fname = os.path.basename(filepath)
    text = fname + " " + content[:2000].lower()
    brands = ["FANUC", "Mitsubishi", "Mazak", "Siemens", "Okuma", "Haas"]
    for b in brands:
        if b in text:
            return b
    if "fanuc" in text.lower() or "发那科" in text:
        return "FANUC"
    if "mitsubishi" in text.lower() or "三菱" in text:
        return "Mitsubishi"
    if "mazak" in text.lower() or "马扎克" in text:
        return "Mazak"
    if "siemens" in text.lower() or "西门子" in text:
        return "Siemens"
    if "okuma" in text.lower() or "大隈" in text:
        return "Okuma"
    if "haas" in text.lower() or "哈斯" in text:
        return "Haas"
    return None

def optimize_page(filepath):
    with open(filepath, "rb") as f:
        raw = f.read()
    html = raw.decode("utf-8", errors="replace")
    original = html

    relpath = os.path.relpath(filepath, ".").replace("\\", "/")
    is_en = relpath.startswith("en/")
    is_article = "/posts/" in relpath and not relpath.endswith("index.html")
    is_brand = "/brands/" in relpath

    if not is_article and not is_brand:
        return None  # Skip non-content pages

    model = extract_model(html, filepath)
    brand = detect_brand(html, filepath)

    if not brand:
        return None

    changes = []

    # ===== 1. Optimize title tag with commercial modifiers =====
    m = re.search(r"<title>(.*?)</title>", html)
    if m:
        title = m.group(1).strip()
        if is_en:
            modifiers = ["Replacement", "Upgrade Solution", "Buy Online", "Supplier", "China"]
            for mod in modifiers:
                if mod.lower() not in title.lower():
                    # Add a modifier near the end of the title
                    title_new = title.replace(" | Kongto Technology", f" | {mod} | Kongto Technology", 1)
                    if title_new != title:
                        html = html.replace(m.group(1), title_new, 1)
                        changes.append(f"Title +'{mod}'")
                        break
        else:
            modifiers = ["替换方案", "升级方案", "厂家直销", "供应商", "即插即用"]
            for mod in modifiers:
                if mod not in title:
                    title_new = title.replace(" | 深圳市江图科技有限公司", f" | {mod} | 深圳市江图科技有限公司", 1)
                    if title_new != title:
                        html = html.replace(m.group(1), title_new, 1)
                        changes.append(f"Title +'{mod}'")
                        break

    # ===== 2. Add keyword-rich FAQ section before related articles or footer =====
    # Only add FAQ if page has enough content and doesn't already have one
    if 'itemprop="FAQPage"' not in html and is_article:
        faq_data = FAQ_TEMPLATES_EN.get(brand, []) if is_en else FAQ_TEMPLATES_CN.get(brand, [])
        if faq_data and model:
            # Pick 2-3 random FAQs
            selected = faq_data[:min(3, len(faq_data))]
            faq_html = f'\n\n<section class="faq-section" style="margin:2rem 0;padding:1.5rem;background:#f8fafc;border-radius:8px;border:1px solid #e2e8f0;">\n<h2 style="margin-top:0;">{"Frequently Asked Questions" if is_en else "常见问题 FAQ"}</h2>\n'
            for q, a in selected:
                q_filled = q.replace("{model}", model) if "{model}" in q else q
                a_filled = a.replace("{model}", model) if "{model}" in a else a
                faq_html += f'<div style="margin-bottom:1.2rem;padding-bottom:1rem;border-bottom:1px solid #e2e8f0;">\n<h3 style="font-size:1.05rem;color:#1e40af;">{q_filled}</h3>\n<p style="color:#475569;margin:0.3rem 0 0 0;">{a_filled}</p>\n</div>\n'
            faq_html += '</section>'

            # Insert before related articles or before footer
            if '<section class="related-articles"' in html:
                html = html.replace('<section class="related-articles"', f'{faq_html}\n<section class="related-articles"', 1)
            elif '<section class="author-bio"' in html:
                html = html.replace('<section class="author-bio"', f'{faq_html}\n<section class="author-bio"', 1)
            elif '</article>' in html:
                html = html.replace('</article>', f'</article>\n{faq_html}', 1)
            changes.append(f"Added FAQ section ({len(selected)} Q&A)")

    # ===== 3. Add FAQPage schema if FAQ section was added =====
    if "常见问题 FAQ" in html or "Frequently Asked Questions" in html:
        if 'FAQPage' not in html:
            faqs = re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>', html, re.DOTALL)
            if faqs:
                faq_schema_items = []
                for q, a in faqs[:5]:
                    q_clean = re.sub(r'<[^>]+>', '', q).strip()
                    a_clean = re.sub(r'<[^>]+>', '', a).strip()
                    faq_schema_items.append({
                        "@type": "Question",
                        "name": q_clean,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": a_clean[:300]
                        }
                    })

                faq_schema = json.dumps({
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "mainEntity": faq_schema_items
                }, ensure_ascii=False, indent=2)

                faq_script = f'\n<script type="application/ld+json">\n{faq_schema}\n</script>'
                html = html.replace("</head>", f"{faq_script}\n</head>", 1)
                changes.append("Added FAQPage schema")

    if changes:
        with open(filepath, "wb") as f:
            f.write(html.encode("utf-8"))
        rel = os.path.relpath(filepath, ".").replace("\\", "/")
        return (rel, changes)
    return None

def main():
    results = []
    for root, dirs, files in os.walk("."):
        if any(x in root for x in ["seo_fix_package", "output", ".git"]):
            continue
        for fname in files:
            if not fname.endswith(".html"):
                continue
            filepath = os.path.join(root, fname).replace("\\", "/")
            result = optimize_page(filepath)
            if result:
                results.append(result)

    print(f"Optimized {len(results)} pages:")
    for rel, changes in results:
        print(f"  {rel}")
        for c in changes:
            print(f"    + {c}")

    # Summary
    total_changes = sum(len(c) for _, c in results)
    print(f"\nTotal: {len(results)} pages, {total_changes} keyword optimizations applied")

if __name__ == "__main__":
    main()
