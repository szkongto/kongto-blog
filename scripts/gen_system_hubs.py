#!/usr/bin/env python3
"""Generate by-system hub pages: FANUC 0i, 16i/18i/21i, Mitsubishi E60, M64, Siemens 810/820.
Template modeled on existing guides/by-size pages. Rich data for GEO/rich results.
"""

import os, json, html

BASE = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE, 'guides', 'by-system')

with open(os.path.join(BASE, 'data', 'cnc-crt-to-lcd-compatibility.json'), encoding='utf-8') as f:
    COMPAT = json.load(f)

def models_for(pattern):
    """Return list of (crt_model, url, size_type) for systems matching pattern."""
    out = []
    for item in COMPAT:
        if pattern.lower() in item.get('cnc_system', '').lower():
            out.append((item['crt_model'], item['url'], item.get('size_type', '')))
    return out

def table_rows(models):
    """HTML table rows, dedup by product URL, label = CRT model(s) pointing there."""
    by_url = {}
    for crt, url, size in models:
        if url not in by_url:
            by_url[url] = {'models': [], 'size': size}
        by_url[url]['models'].append(crt)
    rows = []
    for url, info in by_url.items():
        label = ' / '.join(info['models'])
        slug = url.replace('/products/', '').replace('.html', '')
        rows.append(f'<tr><td><a href="{url}">{html.escape(label)}</a></td><td>{html.escape(info["size"])}</td></tr>')
    return '\n'.join(rows)

def faq_ld(faqs):
    entries = []
    for q, a in faqs:
        entries.append({
            '@type': 'Question',
            'name': q,
            'acceptedAnswer': {'@type': 'Answer', 'text': a},
        })
    obj = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': entries}
    body = json.dumps(obj, ensure_ascii=False, indent=2)
    # indent nested body so it sits inside the <script> block
    return '    <script type="application/ld+json">\n' + body + '\n    </script>'

def breadcrumb_ld(system_name):
    return ('    <script type="application/ld+json">\n'
            '    {\n      "@context": "https://schema.org",\n'
            '      "@type": "BreadcrumbList",\n      "itemListElement": [\n'
            f'        {{"@type":"ListItem","position":1,"name":"Home","item":"https://cncdisplay.com/"}},\n'
            f'        {{"@type":"ListItem","position":2,"name":"Guides","item":"https://cncdisplay.com/guides/fanuc-crt-to-lcd-guide.html"}},\n'
            f'        {{"@type":"ListItem","position":3,"name":{json.dumps(system_name, ensure_ascii=False)},"item":""}}\n'
            '      ]\n    }\n    </script>')

NAV = """<header><nav>
<a href="/" class="logo">Kongto Technology</a>
<div class="nav-links">
<a href="/">Home</a><a href="/compatibility-matrix.html">Compatibility</a>
<a href="/products/">Products</a><a href="/posts/">Articles</a>
<a href="/case-studies.html">Cases</a><a href="/docs/">Downloads</a>
<a href="/about.html">About</a>
<a href="/quote.html" style="color:#ff9800;font-weight:700;">Get Quote</a>
</div>
</nav></header>"""

CSS = """<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.6;color:#1d1d1f;background:#fff;margin:0}
.guide-page{max-width:1000px;margin:2rem auto;padding:0 1.5rem}
.model-table{width:100%;border-collapse:collapse;margin:1.5rem 0}
.model-table th{background:#1a1a2e;color:#fff;padding:10px 12px;text-align:left}
.model-table td{padding:10px 12px;border:1px solid #e2e8f0}
.model-table tr:nth-child(even){background:#f8fafc}
h1{font-size:1.9rem;margin-bottom:0.75rem}
h2{font-size:1.35rem;margin-top:2rem;color:#1a1a2e}
.answer-first{font-size:1.1rem;color:#555;line-height:1.7}
</style>"""

def build_page(slug, title, meta_desc, h1, intro, system_name, pattern, faqs):
    models = models_for(pattern)
    rows = table_rows(models)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(meta_desc)}">
<link rel="canonical" href="https://cncdisplay.com/guides/by-system/{slug}">
<link rel="alternate" hreflang="en" href="https://cncdisplay.com/guides/by-system/{slug}" />
<link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/" />
<link rel="stylesheet" href="/css/style.css?v=9">
{CSS}
{breadcrumb_ld(system_name)}
{faq_ld(faqs)}
</head>
<body>
{NAV}
<div class="guide-page">
<h1>{html.escape(h1)}</h1>
<p class="answer-first">{html.escape(intro)}</p>

<h2>Compatible Display Models for {html.escape(system_name)}</h2>
<p>Find your CRT model below — every one is a drop-in replacement using the original connector. No CNC parameter changes, no rewiring.</p>
<table class="model-table">
<thead><tr><th>CRT Model</th><th>LCD Size</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>

<h2>Why Upgrade Your {html.escape(system_name)} CRT to LCD?</h2>
<p>CRT displays on {html.escape(system_name)} controls fail progressively: dimming screen, flickering, image retention, and eventual blank output. An LCD replacement module removes every CRT-specific failure point — no flyback transformer, no high-voltage tube, no deflection board. Expect 800x600 resolution, 350+ cd/m² brightness, and 50,000+ hour lifespan versus ~15,000 hours for a CRT.</p>

<h2>Installation Is Plug-and-Play</h2>
<p>Each module uses the same connector as the original CRT (20-pin Honda MR-20M on most models). Power off the machine, unplug the old CRT, plug in the LCD, power on. Typical install: 10-15 minutes. Every module ships with a 2-year warranty and lifetime technical support.</p>

<h2>Frequently Asked Questions</h2>
"""
    for q, a in faqs:
        page += f'<h3>{html.escape(q)}</h3>\n<p>{html.escape(a)}</p>\n'

    page += f"""
<div style="margin-top:2rem;padding:1.5rem;background:#f8fafc;border-radius:8px;">
<p style="margin:0;font-size:0.95rem;">Looking for another brand or control? Browse the <a href="/compatibility-matrix.html">full compatibility matrix</a> (52+ models, 12 brands) or check <a href="/guides/by-size/8-inch.html">8-inch LCD replacements</a> for the most common size.</p>
</div>
</div>
</body>
</html>
"""
    return page

PAGES = [
    {
        'slug': 'fanuc-0i.html',
        'title': 'FANUC 0i LCD Upgrade — CRT to LCD Replacement Guide | Kongto',
        'meta_desc': 'FANUC 0i/0 series CNC display CRT-to-LCD upgrade. A61L-0001-0093, 0092, 0094, 0095, 0097 and more. Plug-and-play 8-inch and 14-inch LCD modules, 2-year warranty.',
        'h1': 'FANUC 0i LCD Upgrade — CRT to LCD Replacement Guide',
        'intro': 'FANUC 0i and 0 series controls use 9-inch monochrome and 14-inch color CRT displays. Our LCD replacement modules are drop-in — same 20-pin Honda connector, no parameter changes. Compatible models: A61L-0001-0093, 0092, 0094, 0095, 0097 and the D9MM-11A equivalent.',
        'system_name': 'FANUC 0i',
        'pattern': '0i',
        'faqs': [
            ('How do I upgrade my FANUC 0i display from CRT to LCD?', 'Power off the machine, unplug the existing CRT (20-pin Honda MR-20M connector on most models), plug in the LCD module, and power on. No parameter changes or rewiring. Typical install is 10-15 minutes.'),
            ('Which FANUC 0i CRT models are covered?', 'A61L-0001-0093, A61L-0001-0092, A61L-0001-0094, A61L-0001-0095, A61L-0001-0097, MDT947B-1A, and the Toshiba D9MM-11A (an OEM equivalent of the 0093).'),
            ('Does the LCD module work on FANUC 0i-C or 0i-D?', 'Yes. The 0093 and 0092 modules are used across FANUC 0, 0i-C, 0i-D, 16i, 18i, and 21i controls. Confirm your CRT model and connector type for full compatibility.'),
        ],
    },
    {
        'slug': 'fanuc-16i-18i-21i.html',
        'title': 'FANUC 16i/18i/21i LCD Upgrade — CRT Replacement Guide | Kongto',
        'meta_desc': 'FANUC 16i/18i/21i CNC display CRT-to-LCD upgrade. A61L-0001-0094, 0095, 0097 14-inch color LCD modules. Plug-and-play, 2-year warranty.',
        'h1': 'FANUC 16i/18i/21i LCD Upgrade — CRT Replacement Guide',
        'intro': 'FANUC 16i, 18i, and 21i controls use 14-inch color CRT displays. Our replacement LCD modules fit the original frame and connector — no parameter changes, no rewiring. Compatible models: A61L-0001-0094, 0095, 0097.',
        'system_name': 'FANUC 16i/18i/21i',
        'pattern': '16i',
        'faqs': [
            ('How do I upgrade a FANUC 16i/18i/21i CRT display?', 'Power off, unplug the color CRT, connect the LCD module using the existing connector, power on. Installation takes 10-15 minutes with no parameter changes.'),
            ('Which CRT models fit FANUC 16i/18i/21i?', 'A61L-0001-0094 (14-inch color), A61L-0001-0095 (9-inch color), and A61L-0001-0097 (14-inch color). The 0094 is the most common 14-inch color module for 16i/18i controls.'),
            ('Will image quality improve over my old color CRT?', 'Yes. LCD modules deliver higher resolution, no flicker, no image retention, and 50,000+ hour lifespan. They also eliminate high-voltage hazards from the flyback transformer.'),
        ],
    },
    {
        'slug': 'mitsubishi-e60.html',
        'title': 'Mitsubishi E60 LCD Upgrade — CRT to LCD Replacement | Kongto',
        'meta_desc': 'Mitsubishi E60/E68 CNC display CRT-to-LCD upgrade. MDT962B and BM09DF 9-inch monochrome LCD modules. Plug-and-play, 2-year warranty.',
        'h1': 'Mitsubishi E60 LCD Upgrade — CRT to LCD Replacement Guide',
        'intro': 'Mitsubishi E60/E68 controls use 9-inch monochrome CRT displays. Our LCD modules are drop-in replacements using the original connector. Compatible models: MDT962B and BM09DF.',
        'system_name': 'Mitsubishi E60',
        'pattern': 'E60',
        'faqs': [
            ('How do I upgrade a Mitsubishi E60 display to LCD?', 'Power off the machine, unplug the MDT962B or BM09DF CRT, connect the LCD module with the original connector, and power on. No parameter changes required.'),
            ('Which Mitsubishi E60 CRT models are covered?', 'MDT962B (including -1A and -4A variants) and BM09DF. Both are 9-inch monochrome displays used on E60/E68 controls.'),
            ('Do you ship internationally for Mitsubishi E60 upgrades?', 'Yes. We ship worldwide via DHL/FedEx — USA 5-7 days, Europe 5-10 days, Asia 3-5 days. Every module includes a 2-year warranty and lifetime support.'),
        ],
    },
    {
        'slug': 'mitsubishi-m64.html',
        'title': 'Mitsubishi M64 LCD Upgrade — CRT to LCD Replacement | Kongto',
        'meta_desc': 'Mitsubishi M64 CNC display CRT-to-LCD upgrade. MDT962B and MDT1283B modules. Plug-and-play, 2-year warranty.',
        'h1': 'Mitsubishi M64 LCD Upgrade — CRT to LCD Replacement Guide',
        'intro': 'Mitsubishi M64 controls use 9-inch and 12-inch monochrome CRT displays. Our LCD modules are drop-in replacements using the original connector. Compatible models: MDT962B (9-inch) and MDT1283B (12-inch).',
        'system_name': 'Mitsubishi M64',
        'pattern': 'M64',
        'faqs': [
            ('How do I upgrade a Mitsubishi M64 display to LCD?', 'Power off, unplug the CRT, connect the LCD module with the original connector, power on. Typical install is 10-15 minutes with no parameter changes.'),
            ('Which Mitsubishi M64 CRT models are covered?', 'MDT962B (9-inch monochrome, also used on M3/M300) and MDT1283B (12-inch monochrome, shared with Mazak controls).'),
            ('Is the MDT1283B module the same as the Mazak one?', 'Yes. The MDT1283B is shared between Mitsubishi M64 and Mazak Mazatrol controls. One module covers both.'),
        ],
    },
    {
        'slug': 'siemens-810-820.html',
        'title': 'Siemens SINUMERIK 810/820 LCD Upgrade — CRT Replacement | Kongto',
        'meta_desc': 'Siemens SINUMERIK 810/820/810M CNC display CRT-to-LCD upgrade. 6FC3988-7FA20 and SM0901 modules. Plug-and-play, 2-year warranty.',
        'h1': 'Siemens SINUMERIK 810/820 LCD Upgrade — CRT Replacement Guide',
        'intro': 'Siemens SINUMERIK 810/820 controls use 9-inch monochrome CRT displays. Our LCD modules are drop-in replacements using the original connector. Compatible models: 6FC3988-7FA20 and SM0901/579417TA.',
        'system_name': 'Siemens SINUMERIK 810/820',
        'pattern': 'SINUMERIK 810',
        'faqs': [
            ('How do I upgrade a Siemens 810/820 display to LCD?', 'Power off the control, unplug the 6FC3988-7FA20 CRT, connect the LCD module, power on. No parameter changes or rewiring needed.'),
            ('Which Siemens SINUMERIK models are covered?', '6FC3988-7FA20 (SINUMERIK 810/820) and SM0901/579417TA (SINUMERIK 810M). Both are 9-inch monochrome displays.'),
            ('Does the LCD module work with Siemens 840C or 840D?', 'No — 840C and 840D use different display sizes and connectors. Contact us with your exact model for a compatible solution.'),
        ],
    },
]

os.makedirs(OUT_DIR, exist_ok=True)
for p in PAGES:
    page_html = build_page(**p)
    fp = os.path.join(OUT_DIR, p['slug'])
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f'GENERATED: guides/by-system/{p["slug"]}')

print(f'\nDone. {len(PAGES)} system hub pages.')
