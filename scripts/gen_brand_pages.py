import os

TPL = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="https://cncdisplay.com/en/products/{slug}.html">
    <link rel="alternate" hreflang="en" href="https://cncdisplay.com/en/products/{slug}.html">
    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/en/products/{slug}.html">
    <meta property="og:type" content="product">
    <meta property="og:title" content="{h1_stripped}">
    <meta property="product:price:amount" content="{price}">
    <meta property="product:price:currency" content="USD">
    <meta property="og:site_name" content="Kongto Technology">
    <script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{h1_stripped}",
  "description": "{meta_desc}",
  "brand": {{ "@type": "Brand", "name": "KONGTO" }},
  "offers": {{
    "@type": "Offer", "price": "{price}.00", "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  }}
}}</script>
    <style>
        .product-hero{{display:flex;gap:2rem;flex-wrap:wrap;align-items:flex-start;margin:2rem 0;}}
        .product-hero img{{max-width:450px;width:100%;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.1);}}
        .product-info{{flex:1;min-width:280px;}}.product-price{{font-size:2.5rem;font-weight:800;color:#FF6600;}}
        .spec-table{{width:100%;border-collapse:collapse;margin:1.5rem 0;}}
        .spec-table th,.spec-table td{{padding:10px 14px;border:1px solid #e0e0e0;text-align:left;}}
        .spec-table th{{background:#1a1a2e;color:#fff;width:35%;}}
        .spec-table tr:nth-child(even){{background:#f8f9fa;}}
        .cta-buttons{{display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0;}}
        @media(max-width:768px){{.product-hero{{flex-direction:column;}}}}
    </style>
</head>
<body>    <header>
        <nav>
            <a href="/en/" class="logo">Kongto Technology</a>
            <div class="nav-links">
                <a href="/en/">Home</a><a href="/en/compatibility-matrix.html">Compatibility</a>
                <a href="/en/posts/">Articles</a>
                <a href="/en/case-studies.html">Cases</a>
                <a href="/en/docs/">Downloads</a>
                <a href="/en/about.html">About</a>
                <a href="/en/quote.html" style="color:#ff9800;font-weight:700;">Get Quote</a>
            </div>
            <a href="/en/search.html" class="nav-search">🔍 Search</a>
            <div class="lang-switch">
                <span class="divider"></span>
                <a href="/en/products/{slug}.html" lang="en" class="lang-en">English</a>
            </div>
        </nav>
    </header>
<main style="max-width:1100px;margin:0 auto;padding:20px;">
<nav style="font-size:0.9rem;color:#666;margin-bottom:1rem;"><a href="/en/">Home</a> / <strong>{h1_stripped}</strong></nav>
<section class="product-hero">
<img src="{img}" alt="{h1_stripped}" loading="lazy">
<div class="product-info">
<h1>{h1}</h1>
<p>{size_crt} CRT to TFT-LCD plug-and-play replacement. No modifications needed. 15-30 minute installation.</p>
<div class="product-price">${price} <span style="font-size:1rem;color:#666;">USD</span></div>
<p style="color:#28a745;font-weight:600;">In Stock - Free Shipping - 18-Month Warranty</p>
<div class="cta-buttons"><a href="/en/quote.html" class="btn btn-primary" style="padding:14px 32px;">Get a Quote</a>{guide_btn}</div>
</div>
</section>
<section>
<h2>Specifications: Original CRT vs Kongto LCD</h2>
<table class="spec-table">
<tr><th>Spec</th><th>Original CRT</th><th>Kongto LCD</th></tr>
<tr><td>Technology</td><td>{size_crt} {crt_type} CRT</td><td>TFT-LCD Industrial Panel</td></tr>
<tr><td>Screen Size</td><td>{size_crt}</td><td>{lcd_size}" LED-backlit LCD</td></tr>
<tr><td>Resolution</td><td>640x400 / 640x480</td><td><strong>800x600</strong></td></tr>
<tr><td>Brightness</td><td>~200 cd/m2</td><td><strong>350-450 cd/m2</strong></td></tr>
<tr><td>Lifespan</td><td>~15,000 hrs</td><td><strong>50,000+ hrs</strong></td></tr>
<tr><td>Power</td><td>{power}</td><td>{power} (original)</td></tr>
<tr><td>Interface</td><td>{interface}</td><td>{interface} (direct compatible)</td></tr>
<tr><td>Safety</td><td>High voltage (10-15kV)</td><td><strong>Low voltage DC</strong></td></tr>
</table>
</section>
<section><h2>Compatible Systems</h2><ul>
{systems}
</ul></section>
<section style="background:#f0f7ff;padding:24px;border-radius:12px;margin:2rem 0;"><h2>Warranty & Service</h2><p><strong>18-Month Warranty</strong> - Lifetime Tech Support - Free Shipping Worldwide</p></section>
<section style="text-align:center;padding:3rem 1rem;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border-radius:12px;margin:2rem 0;">
<h2 style="color:#fff;">Ready to replace your CRT?</h2>
<p>${price} - In Stock - Ships within 24 hours</p>
<a href="/en/quote.html" style="display:inline-block;padding:14px 36px;background:#fff;color:#667eea;border-radius:8px;text-decoration:none;font-weight:700;">Request Quote &rarr;</a>
</section>
</main>
<footer><div class="footer-content"><span class="footer-logo">Kongto Technology</span></div></footer>
</body>
</html>'''

PAGES = [
    {
        'slug': 'mazak-14-inch-crt-lcd-upgrade',
        'title': 'Mazak 14-inch CRT LCD Replacement | DR5614 C-5470NS AIQA8DSP40 HM-12PDB | Kongto',
        'meta_desc': 'Mazak 14-inch color CRT to LCD replacement. Covers DR5614, C-5470, C-5470NS, AIQA8DSP40, 26S-14O19L, HM-12PDB, MDT1216, D72MA001840. For Mazatrol T-Plus controls. Plug-and-play, $355.',
        'h1': 'Mazak 14-Inch Color CRT<br>LCD Replacement Display',
        'h1_stripped': 'Mazak 14-Inch Color CRT LCD Replacement',
        'size_crt': '14-inch',
        'lcd_size': '12.1',
        'crt_type': 'Color',
        'price': '355',
        'interface': '26-pin / MC714',
        'power': 'DC 24V',
        'systems': '<li>Mazak DR5614 (14" color CRT)</li><li>Mazak C-5470 / C-5470NS (14" color CRT)</li><li>Mazak AIQA8DSP40 (Sharp 14" CRT)</li><li>Mazak 26S-14O19L (14" CRT)</li><li>Mazak HM-12PDB / MDT1216</li><li>OEM Part D72MA001840</li><li>Compatible Mazatrol T-Plus / T2 / T3</li>',
        'guide_btn': '<a href="/en/posts/mazak-mazatrol-crt-to-lcd-upgrade-guide.html" class="btn btn-secondary">Installation Guide</a>',
        'img': '/images/mazak/mazak-mazak.jpg',
    },

    {
        'slug': 'okuma-osp-crt-lcd-upgrade',
        'title': 'Okuma OSP CRT LCD Replacement | OSP500L-G 5000 5020 7000 MDT-1005 | Kongto',
        'meta_desc': 'Okuma OSP CRT to LCD replacement. Covers OSP500L-G MDT-1005 mono monitor, Okuma 5000 5020 mono monitor, Okuma 7000 colour monitor. Plug-and-play, $430.',
        'h1': 'Okuma OSP CRT<br>LCD Replacement Display',
        'h1_stripped': 'Okuma OSP CRT LCD Replacement',
        'size_crt': '12-inch',
        'lcd_size': '12.1',
        'crt_type': 'Monochrome / Color',
        'price': '430',
        'interface': '14-pin / 20-pin',
        'power': 'DC 24V',
        'systems': '<li>Okuma OSP500L-G (MDT-1005 12" mono)</li><li>Okuma OSP5000 / OSP5020 (12" mono)</li><li>Okuma OSP7000 (14" colour CRT)</li>',
        'guide_btn': '<a href="/en/posts/okuma-osp-crt-to-lcd-upgrade-guide.html" class="btn btn-secondary">Installation Guide</a>',
        'img': '/images/okuma/okuma-machine-panel.jpg',
    },

    {
        'slug': 'haas-28hm-nm4-lcd-upgrade',
        'title': 'HAAS 28HM-NM4 LCD Replacement | 12-inch CRT to LCD for VF Series | Kongto',
        'meta_desc': 'HAAS 28HM-NM4 12-inch monochrome CRT to LCD replacement. Compatible with 93-5220C, 93-5220. For VF-1 through VF-6. 9-pin D-Sub, plug-and-play, $399.',
        'h1': 'HAAS 28HM-NM4<br>LCD Replacement Display',
        'h1_stripped': 'HAAS 28HM-NM4 LCD Replacement',
        'size_crt': '12-inch',
        'lcd_size': '12.1',
        'crt_type': 'Monochrome',
        'price': '399',
        'interface': '9-pin D-Sub',
        'power': 'DC 12V',
        'systems': '<li>HAAS VF-1 / VF-2 / VF-3 (Classic Control)</li><li>HAAS VF-4 / VF-6 (pre-2008)</li><li>OEM Part 28HM-NM4 / 93-5220C / 93-5220</li>',
        'guide_btn': '<a href="/en/posts/haas-vf-series-crt-monitor-troubleshooting-lcd-upgrade-guide.html" class="btn btn-secondary">Installation Guide</a>',
        'img': '/images/haas/haas-haas-v2.5-1904-01.jpg',
    },
    {
        'slug': 'mazak-mdt1283b-lcd-upgrade',
        'title': 'Mazak MDT1283B-1A LCD Replacement | CRT for Mazatrol M32 | Kongto',
        'meta_desc': 'Mazak MDT1283B-1A 12-inch CRT to LCD replacement. Also compatible with CD1472-D1M 14-inch color CRT. Mazatrol M32/M35 controls. Plug-and-play, $355.',
        'h1': 'Mazak MDT1283B-1A<br>LCD Replacement Display',
        'h1_stripped': 'Mazak MDT1283B-1A LCD Replacement',
        'size_crt': '12-inch',
        'lcd_size': '12.1',
        'crt_type': 'Monochrome',
        'price': '355',
        'interface': 'Multi-pin (MC712/MC714)',
        'power': 'DC 24V',
        'systems': '<li>Mazak Mazatrol M32 / M35</li><li>Mazatrol T/M-32 / T-Plus</li><li>Also fits CD1472-D1M (14" color CRT)</li>',
        'guide_btn': '<a href="/en/posts/mazak-mazatrol-crt-to-lcd-upgrade-guide.html" class="btn btn-secondary">Installation Guide</a>',
        'img': '/images/mazak/mazak-mazatrol-m-32.jpg',
    },
]

for p in PAGES:
    slug = p['slug']
    page = TPL.format(**p)
    path = f'd:/code/seo_deploy/en/products/{slug}.html'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(page)
    print(f'  {slug}.html')

print(f'\nDone: {len(PAGES)} pages')
