"""Create 8 hub + guide pages from keyword map."""
import os

SITE = r'd:\code\seo_deploy'

HUBS = [
    {'slug': 'buy-cnc-monitor-replacement', 'dir': 'hub',
     'title': 'Buy CNC Monitor Replacement | CRT to LCD Upgrade | Kongto',
     'desc': 'Buy CNC monitor replacement — CRT to LCD upgrade kits for FANUC, Mitsubishi, Siemens, Mazak, Okuma, Haas. Factory direct pricing, 2-year warranty. Ships worldwide.',
     'h1': 'Buy CNC Monitor Replacement — CRT to LCD Upgrade',
     'content': '<p>Browse our complete range of CNC CRT-to-LCD replacement monitors. Every module is a direct plug-and-play replacement for the original CRT — no wiring changes, no parameter modifications, no special tools required.</p>\n<p>All modules are manufactured and tested at our Shenzhen facility. We stock 500+ units across 30+ models. Most orders ship within 24 hours.</p>',
     'brands': ['FANUC', 'Mitsubishi', 'Siemens', 'MAZAK', 'OKUMA', 'HAAS']},

    {'slug': 'wholesale-industrial-lcd-monitors', 'dir': 'hub',
     'title': 'Wholesale Industrial LCD Monitors | CNC Display OEM | Kongto',
     'desc': 'Wholesale industrial LCD monitors for CNC retrofit. OEM/ODM available. CRT-to-LCD modules for FANUC, Mitsubishi, Siemens. Factory direct pricing, MOQ negotiable.',
     'h1': 'Wholesale Industrial LCD Monitors — CRT to LCD OEM',
     'content': '<p>Kongto Technology offers wholesale pricing on industrial LCD monitor replacements for CNC machine tools. As a manufacturer with 12 years of experience, we supply CRT-to-LCD retrofit modules to distributors, machine tool rebuilders, and OEM integrators worldwide.</p>\n<p>All modules use industrial-grade TFT-LCD panels rated for 50,000+ hours continuous operation in shop-floor conditions.</p>',
     'brands': ['FANUC', 'Mitsubishi', 'Siemens', 'MAZAK', 'OKUMA']},

    {'slug': 'cnc-monitor-suppliers', 'dir': 'hub',
     'title': 'CNC Monitor Suppliers USA | Industrial LCD Replacement | Kongto',
     'desc': 'CNC monitor suppliers for USA customers — industrial LCD replacements for legacy CRT displays. FANUC, Mitsubishi, Siemens. Fast shipping from China. Duty & tax handled.',
     'h1': 'CNC Monitor Suppliers — USA & International Shipping',
     'content': '<p>Kongto Technology supplies CNC monitor replacements to customers in the United States and worldwide. Our CRT-to-LCD modules are trusted by machine shops, aerospace suppliers, and automotive manufacturers across North America.</p>\n<p>Shipping to USA via DHL Express takes 3-5 business days. Duties and taxes are clearly shown at checkout. Free shipping on all orders.</p>',
     'brands': ['FANUC', 'Mitsubishi', 'Siemens', 'MAZAK', 'OKUMA', 'HAAS', 'Heidenhain']},

    {'slug': 'aftermarket-cnc-display-manufacturer', 'dir': 'hub',
     'title': 'Aftermarket CNC Display Manufacturer | CRT to LCD | Kongto',
     'desc': 'Aftermarket CNC display manufacturer — CRT-to-LCD replacements for FANUC, Mitsubishi, Siemens. 12 years manufacturing experience. Custom solutions available.',
     'h1': 'Aftermarket CNC Display Manufacturer — CRT to LCD Specialist',
     'content': '<p>Kongto Technology is an aftermarket CNC display manufacturer specializing in CRT-to-LCD replacement modules. Founded in 2013, we have designed and manufactured over 40 different LCD modules covering the most popular CNC CRT models from FANUC, Mitsubishi, Siemens, Mazak, Okuma, and Haas.</p>\n<p>Unlike generic LCD monitors, our modules are engineered to match the exact electrical, mechanical, and timing specifications of the original CRT displays they replace.</p>',
     'brands': ['FANUC', 'Mitsubishi', 'Siemens', 'MAZAK', 'OKUMA', 'HAAS']},

    {'slug': 'fanuc-crt-to-lcd-guide', 'dir': 'guides',
     'title': 'FANUC CRT to LCD Upgrade Guide | Complete Replacement | Kongto',
     'desc': 'Complete FANUC CRT to LCD upgrade guide. Covers A61L-0001 series, D9MM-11A, OM-D. Includes model identification, installation steps, wiring diagram, FAQ.',
     'h1': 'FANUC CRT to LCD Upgrade — Complete Guide',
     'content': '<p>FANUC is the world\'s most widely used CNC control brand. Their CRT displays (A61L-0001 series) are found on virtually every FANUC-controlled machine tool from the 1980s through early 2000s. This guide covers model identification, compatible LCD replacements, installation, and troubleshooting.</p><h3>Model Identification</h3><p>FANUC CRT models are marked with a part number beginning with A61L-0001-xxxx. The most common models are 0093 (9-inch, FANUC 0/0i), 0094 (12.1-inch, FANUC Series 6/10/11/12), 0092/MDT-947, and 0090/0076 (8-inch).</p>',
     'brands': ['FANUC']},

    {'slug': 'mitsubishi-crt-to-lcd-guide', 'dir': 'guides',
     'title': 'Mitsubishi CRT to LCD Upgrade Guide | MELDAS Display | Kongto',
     'desc': 'Mitsubishi CRT to LCD upgrade guide for MELDAS M60/M64/M500 CNC. MDT962B, BM09DF, FCUA-CT100 replacement. Installation steps, wiring, FAQ.',
     'h1': 'Mitsubishi CRT to LCD Upgrade Guide',
     'content': '<p>Mitsubishi MELDAS CNC controls use CRT displays (MDT962B, BM09DF, FCUA-CT100) that are now discontinued. Our LCD replacement modules are drop-in compatible — same connectors, same mounting, same power supply.</p><h3>Common Models</h3><p>The MDT962B (8-inch, MELDAS M60/M64) is the most common replacement. The BM09DF (9-inch, E60/E68) and FCUA-CT100 (M500/M520 series) are also widely available.</p>',
     'brands': ['Mitsubishi']},

    {'slug': 'mazak-crt-to-lcd-guide', 'dir': 'guides',
     'title': 'Mazak CRT to LCD Upgrade Guide | Mazatrol Display | Kongto',
     'desc': 'Mazak CRT to LCD upgrade guide for Mazatrol T-32/M-32 CNC. CD1472, C5470NS, MDT1283B replacement. Model lookup, installation, wiring.',
     'h1': 'Mazak CRT to LCD Upgrade Guide',
     'content': '<p>Mazak Mazatrol CNC controls (T-32, M-32, Fusion 640) use several CRT display models. The most common are the CD1472-D1M (14-inch, 26-pin), C5470NS, MDT1283B (12-inch, 20-pin), and DR5614.</p><h3>Compatibility</h3><p>All Kongto LCD modules for Mazak use the original connector type (26-pin D-Sub or 20-pin Honda). Installation takes 15-30 minutes. No Mazatrol parameter changes required.</p>',
     'brands': ['MAZAK']},

    {'slug': 'siemens-crt-to-lcd-guide', 'dir': 'guides',
     'title': 'Siemens CRT to LCD Upgrade Guide | SINUMERIK Display | Kongto',
     'desc': 'Siemens CRT to LCD upgrade guide for SINUMERIK 810/820/840D. 6FC5103, 6FC3988, SM0901 replacement. Installation steps, DB-25 wiring, FAQ.',
     'h1': 'Siemens CRT to LCD Upgrade Guide',
     'content': '<p>Siemens SINUMERIK controls (810, 820, 840D, 850, 880) use various CRT display modules. The 6FC5103-0AB01 (DB-25, 840D), 6FC3988-7FA20 (850/880), and SM0901 (810M) are the most common models we replace.</p><h3>Signal Compatibility</h3><p>Siemens CRTs use TTL-level RGB signals through DB-25 or 15-pin D-Sub connectors. Our LCD modules accept these signals natively — no signal converter needed.</p>',
     'brands': ['Siemens']},
]

TEMPLATE_START = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="https://cncdisplay.com/{dir}/{slug}.html">
    <link rel="alternate" hreflang="en" href="https://cncdisplay.com/{dir}/{slug}.html">
    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/{dir}/{slug}.html">
    <link rel="stylesheet" href="/css/style.css?v=7">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="https://cncdisplay.com/images/logo_256.png">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
</head>
<body>
    <header>
        <nav>
            <a href="/" class="logo">Kongto Technology</a>
            <div class="nav-links">
                <a href="/">Home</a><a href="/compatibility-matrix.html">Compatibility</a>
                <a href="/products/">Products</a>
                <a href="/posts/">Articles</a>
                <a href="/case-studies.html">Cases</a>
                <a href="/docs/">Downloads</a>
                <a href="/about.html">About</a>
                <a href="/quote.html" style="color:#ff9800;font-weight:700;">Get Quote</a>
            </div>
            <a href="/search.html" class="nav-search">&#x1F50D; Search</a>
            <div class="lang-switch">
                <span class="divider"></span>
                <a href="" lang="en" class="lang-en">English</a>
            </div>
        </nav>
    </header>
    <main style="max-width:980px;margin:0 auto;padding:20px;">
    <h1>{h1}</h1>
    {content}
'''

TEMPLATE_END = '''
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;margin:2rem 0;">
        {brand_cards}
    </div>
    <div style="background:#f8fafc;padding:1.5rem;border-radius:8px;margin:2rem 0;border:1px solid #e2e8f0;">
        <p style="font-weight:bold;color:#1e40af;margin:0 0 0.75rem 0;">&#x1F4D8; Related Resources</p>
        <ul style="margin:0;padding-left:1.2rem;">
            <li><a href="/compatibility-matrix.html">Compatibility Matrix</a> &#x2014; 95+ models</li>
            <li><a href="/crt-dead-symptoms.html">CRT Failure Symptoms</a> &#x2014; Diagnosis guide</li>
            <li><a href="/quote.html">Get a Quote</a> &#x2014; Reply within 24 hours</li>
        </ul>
    </div>
    <section style="background:#f0f7ff;padding:24px;border-radius:12px;margin:2rem 0;">
        <h2>Warranty &amp; Service</h2>
        <p><strong>2-Year Warranty</strong> &#x2014; Lifetime Technical Support &#x2014; Free Worldwide Shipping</p>
        <p>info@cncdisplay.com | +86-13686889647</p>
    </section>
    </main>
    <footer>
        <div class="footer-content">
            <div class="footer-brand">
                <span class="footer-logo">Kongto Technology &#x6C5F;&#x56FE;&#x79D1;&#x6280;</span>
                <p>Industrial Video Display Solutions &#x2014; CNC CRT-to-LCD Retrofit, Video Signal Converters, Custom Industrial Displays</p>
            </div>
            <div class="footer-links">
                <a href="/posts/">&#x1f4c4; Articles</a>
                <a href="/brands/FANUC.html">FANUC</a>
                <a href="/brands/Mitsubishi.html">Mitsubishi</a>
                <a href="/brands/Siemens.html">Siemens</a>
                <a href="/brands/MAZAK.html">Mazak</a>
                <a href="/brands/OKUMA.html">Okuma</a>
                <a href="/brands/HAAS.html">Haas</a>
                <a href="/docs/">Downloads</a>
                <a href="/about.html">About Us</a>
            </div>
            <p class="footer-copy">&copy; 2013-2026 Kongto Technology | Shenzhen, Guangdong, China | +86-13686889647 | sales@cncdisplay.com</p>
        </div>
    </footer>
</body>
</html>'''

BRAND_CARD = '''<a href="/brands/{page}" style="display:block;padding:1rem;background:#f0f7ff;border:1px solid #bfdbfe;border-radius:8px;text-decoration:none;color:#333;text-align:center;">
    <strong>{name}</strong><br><small style="color:#666;">View {name} Solutions</small></a>'''

for hub in HUBS:
    slug = hub['slug']
    dirname = hub['dir']
    title = hub['title']
    desc = hub['desc']
    h1_text = hub['h1']
    content = hub['content']
    brands = hub['brands']

    brand_cards = ''
    for b in brands:
        brand_cards += BRAND_CARD.format(page=f'{b}.html', name=b)

    html = TEMPLATE_START.format(title=title, desc=desc, slug=slug, dir=dirname, h1=h1_text, content=content)
    html += TEMPLATE_END.format(brand_cards=brand_cards)

    out_dir = os.path.join(SITE, dirname)
    os.makedirs(out_dir, exist_ok=True)
    fp = os.path.join(out_dir, f'{slug}.html')
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'CREATED: {dirname}/{slug}.html')

print('\nDone. 8 hub/guide pages created.')
