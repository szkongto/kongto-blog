# FANUC A61L Part number data
# Pricing provided by seller - do not change without confirmation
MODELS = [
    {'part': 'A61L-0001-{'part': 'A61L-0001-0072', 'sku': '0072', 'size': '9-inch', 'lcd_size': '8', 'price': '255'',
     'crt_type': 'Monochrome',
     'compatible': ['FANUC Series 6M', 'FANUC Series 6T', 'FANUC 6-MA', 'FANUC 6-TA'],
     'resolution': '640x400', 'interface': 'HONDA 20-pin',
     'systems': 'FANUC 6M/6T series', 'guide': ''},
    {'part': 'A61L-0001-0074', 'sku': '0074', 'size': '14-inch', 'lcd_size': '12.1', 'price': '350',
     'crt_type': 'Color',
     'compatible': ['FANUC 15T', 'FANUC 10', 'FANUC 10TE-F'],
     'resolution': '640x480', 'interface': 'HONDA 20-pin',
     'systems': 'FANUC 15T/10/10TE-F series', 'guide': '/en/posts/article_20260503_FANUC_A61L_0001_0074_LCD.html'},
    {'part': 'A61L-0001-0076', 'sku': '0076', 'size': '9-inch', 'lcd_size': '8', 'price': '350',
     'crt_type': 'Monochrome',
     'compatible': ['FANUC Series 6', 'FANUC Series 6B', 'FANUC Series 6BII'],
     'resolution': '640x400', 'interface': 'HONDA 20-pin',
     'systems': 'FANUC 6/6B/6BII series', 'guide': ''},
    {'part': 'A61L-0001-0086', 'sku': '0086', 'size': '8.4-inch', 'lcd_size': '8.4', 'price': '350',
     'crt_type': 'Monochrome',
     'compatible': ['FANUC Series 6', 'FANUC Series 10', 'FANUC Series 11', 'FANUC 0-M', 'FANUC 0-T'],
     'resolution': '640x400', 'interface': 'HONDA 20-pin',
     'systems': 'FANUC 6/10/11/0-M/0-T series', 'guide': '/en/posts/article_20260503_FANUC_A61L_0001_0086_LCD.html'},
    {'part': 'A61L-0001-0090', 'sku': '0090', 'size': '9-inch', 'lcd_size': '8', 'price': '350',
     'crt_type': 'Monochrome',
     'compatible': ['FANUC 0T', 'FANUC 0M', 'FANUC Series 6'],
     'resolution': '640x400', 'interface': 'HONDA 20-pin',
     'systems': 'FANUC 0T/0M/Series 6', 'guide': '/en/posts/article_20260503_FANUC_A61L_0001_0090_LCD.html'},
    {'part': 'A61L-0001-0092', 'sku': '0092', 'size': '9-inch', 'lcd_size': '8', 'price': '350',
     'crt_type': 'Monochrome',
     'compatible': ['FANUC Series 6M', 'FANUC Series 6T', 'FANUC 6-MA/B', 'FANUC 6-TA/B'],
     'resolution': '640x400', 'interface': 'HONDA 20-pin',
     'systems': 'FANUC 6M/6T series', 'guide': '/en/posts/article_20260503_FANUC_A61L_0001_0092_LCD.html'},
    {'part': 'A61L-0001-0094', 'sku': '0094', 'size': '14-inch', 'lcd_size': '12.1', 'price': '350',
     'crt_type': 'Color',
     'compatible': ['FANUC Series 6', 'FANUC Series 10', 'FANUC Series 11', 'FANUC Series 12'],
     'resolution': '640x480', 'interface': 'HONDA 20-pin',
     'systems': 'FANUC Series 6/10/11/12', 'guide': '/en/posts/article_20260503_FANUC_A61L_0001_0094_LCD.html'},
    {'part': 'A61L-0001-0095', 'sku': '0095', 'size': '9-inch', 'lcd_size': '8', 'price': '199',
     'crt_type': 'Monochrome',
     'compatible': ['FANUC 0 / 0-Mate', 'FANUC 0i', 'FANUC 15', 'FANUC 16/18/21'],
     'resolution': '640x400', 'interface': 'HONDA 20-pin',
     'systems': 'FANUC 0/0i/15/16/18/21 series', 'guide': '/en/posts/article_20260503_FANUC_A61L_0001_0095_LCD.html'},
    {'part': 'A61L-0001-0096', 'sku': '0096', 'size': '14-inch', 'lcd_size': '12.1', 'price': '350',
     'crt_type': 'Color',
     'compatible': ['FANUC 15T', 'FANUC 16/18/20/21', 'Toshiba D14CM-01A', 'Tatung CD14JBS'],
     'resolution': '640x480', 'interface': 'HONDA 20-pin',
     'systems': 'FANUC 15T/16/18/20/21 series', 'guide': '/en/posts/FANUC_A61L_0001_0096_LCD_CNC_Upgrade_Replacement.html'},
    {'part': 'A61L-0001-0097', 'sku': '0097', 'size': '14-inch', 'lcd_size': '12.1', 'price': '350',
     'crt_type': 'Color',
     'compatible': ['FANUC 0 / 0-Mate', 'FANUC 0i Mate'],
     'resolution': '640x480', 'interface': 'HONDA 20-pin',
     'systems': 'FANUC 0/0-Mate/0i Mate series', 'guide': '/en/posts/FANUC_A61L_0001_0097_LCD_CNC_CRT_Replacement.html'},
]

IMG = 'A6100010093_install_effect_2.jpg'

def make_en(m):
    part = m['part']; slug = f"fanuc-{part.lower().replace(' ', '-')}-lcd-upgrade"
    url = f"https://cncdisplay.com/en/products/{slug}.html"
    cn_url = f"https://cncdisplay.com/products/{slug}.html"
    compat_list = '\n'.join([f'                    <li>{c}</li>' for c in m['compatible']])
    guide_btn = f'<a href="{m["guide"]}" class="btn btn-secondary" style="padding:14px 32px;">Installation Guide</a>' if m['guide'] else ''
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FANUC {part} LCD Replacement | {m['size']} CRT to LCD ${m['price']} | Kongto Technology</title>
    <meta name="description" content="FANUC {part} {m['size']} CRT to LCD replacement. ${m['price']} plug-and-play, 800x600 resolution, 350-450cd/m2 brightness, 50,000+ hour lifespan. Compatible with {m['systems']}.">
    <link rel="canonical" href="{url}">
    <link rel="alternate" hreflang="en" href="{url}">
    <link rel="alternate" hreflang="zh-CN" href="{cn_url}">
    <link rel="alternate" hreflang="x-default" href="{url}">
    <link rel="stylesheet" href="/css/style.css?v=7">
    <meta property="og:type" content="product">
    <meta property="og:title" content="FANUC {part} LCD Replacement | {m['size']} CRT to LCD">
    <meta property="og:description" content="${m['price']} plug-and-play LCD replacement for FANUC {part}. {m['systems']} compatible">
    <meta property="og:image" content="https://cncdisplay.com/images/{IMG}">
    <meta property="product:price:amount" content="{m['price']}">
    <meta property="product:price:currency" content="USD">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="FANUC {part} LCD Replacement">
    <meta name="twitter:image" content="https://cncdisplay.com/images/{IMG}">    <meta http-equiv="X-Content-Type-Options" content="nosniff"><meta http-equiv="X-Frame-Options" content="SAMEORIGIN"><meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
    <script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "FANUC {part} LCD Replacement Display",
  "description": "FANUC {part} {m['size']} CRT to TFT-LCD replacement. Plug-and-play, 800x600, 350-450cd/m2, 50,000+ hour lifespan.",
  "sku": "KONGTO-A61L-{m['sku']}",
  "brand": {{ "@type": "Brand", "name": "KONGTO" }},
  "image": "https://cncdisplay.com/images/{IMG}",
  "offers": {{
    "@type": "Offer", "price": "{m['price']}.00", "priceCurrency": "USD",
    "hasMerchantReturnPolicy": {{"@type":"MerchantReturnPolicy","applicableCountry":"CN","returnPolicyCategory":"https://schema.org/MerchantReturnFiniteReturnWindow","merchantReturnDays":7,"returnMethod":"https://schema.org/ReturnByMail","returnFees":"https://schema.org/FreeReturn"}},
    "availability": "https://schema.org/InStock",
    "url": "{url}"
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
    <script>(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i+"?ref=bwt";y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window, document, "clarity", "script", "wx8gkt3utu");</script>
    <script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Kongto Technology (Shenzhen) Co., Ltd.",
  "url": "https://cncdisplay.com",
  "description": "Manufacturer of industrial CNC display CRT-to-LCD retrofit solutions",
  "address": {{ "@type": "PostalAddress", "addressLocality": "Shenzhen", "addressRegion": "Guangdong", "addressCountry": "CN" }},
  "contactPoint": {{ "@type": "ContactPoint", "telephone": "+86-13686889647", "email": "szkongto01@foxmail.com", "contactType": "sales", "availableLanguage": ["Chinese", "English"] }}
}}</script>
    <script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "FANUC {part} CRT to LCD Installation Guide",
  "step": [
    {{"@type":"HowToStep","position":1,"name":"Power off","text":"Turn off CNC system power. Remove the CRT display housing. Disconnect the HONDA 20-pin signal cable and power cable."}},
    {{"@type":"HowToStep","position":2,"name":"Install LCD","text":"Place the LCD module into the original mounting position. Align holes and secure with original screws."}},
    {{"@type":"HowToStep","position":3,"name":"Connect cables","text":"Insert the signal cable into the LCD module port. Connect DC 24V power."}},
    {{"@type":"HowToStep","position":4,"name":"Power on","text":"Restore power. The LCD displays automatically. Use OSD buttons to adjust."}}
  ],
  "totalTime": "PT30M"
}}</script>
    </head>
<body>    <header><!-- nav same as all EN pages -->
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
            <a href="/en/search.html" class="nav-search">&#x1f50d; Search</a>
            <div class="lang-switch">
                <a href="/products/{slug}.html" lang="zh" class="lang-zh">&#x4e2d;&#x6587;</a>
                <span class="divider">|</span>
                <a href="/en/products/{slug}.html" lang="en" class="lang-en">English</a>
            </div>
        </nav>
    </header>
    <main style="max-width:1100px;margin:0 auto;padding:20px;">
        <nav style="font-size:0.9rem;color:#666;margin-bottom:1rem;"><a href="/en/">Home</a> / <strong>FANUC {part} LCD Replacement</strong></nav>
        <section class="product-hero">
            <img src="/images/{IMG}" alt="FANUC {part} LCD replacement" loading="lazy">
            <div class="product-info">
                <h1>FANUC {part}<br>LCD Replacement Display</h1>
                <p>{m['size']} CRT to TFT-LCD plug-and-play replacement. No CNC parameter changes needed. 30-minute installation.</p>
                <div class="product-price">${m['price']} <span style="font-size:1rem;color:#666;">USD</span></div>
                <p style="color:#28a745;font-weight:600;">In Stock - Free Shipping - 18-Month Warranty</p>
                <div class="cta-buttons"><a href="/en/quote.html" class="btn btn-primary" style="padding:14px 32px;">Get a Quote</a>{guide_btn}</div>
            </div>
        </section>
        <section>
            <h2>Specifications: Original CRT vs Kongto LCD</h2>
            <table class="spec-table">
                <tr><th>Spec</th><th>Original CRT</th><th>Kongto LCD</th></tr>
                <tr><td>Technology</td><td>{m['size']} {m['crt_type']} CRT</td><td>TFT-LCD Industrial Panel</td></tr>
                <tr><td>Screen Size</td><td>{m['size']}</td><td>{m['lcd_size']}" LED-backlit LCD</td></tr>
                <tr><td>Resolution</td><td>{m['resolution']}</td><td><strong>800x600</strong></td></tr>
                <tr><td>Brightness</td><td>~200 cd/m2</td><td><strong>350-450 cd/m2</strong></td></tr>
                <tr><td>Lifespan</td><td>~15,000 hrs</td><td><strong>50,000+ hrs</strong></td></tr>
                <tr><td>Power</td><td>25-30W</td><td><strong>8-12W</strong></td></tr>
                <tr><td>Temperature</td><td>0~40C</td><td><strong>-10~+60C</strong></td></tr>
                <tr><td>Interface</td><td>{m['interface']}</td><td>{m['interface']} (direct compatible)</td></tr>
            </table>
        </section>
        <section><h2>Compatible Systems</h2><ul>
{compat_list}
                </ul></section>
        <section style="background:#f0f7ff;padding:24px;border-radius:12px;margin:2rem 0;"><h2>Warranty & Service</h2><p><strong>18-Month Warranty</strong> - Lifetime Tech Support - Free Shipping Worldwide</p><p>Outright sale - no core exchange required</p></section>
        <section class="cta" style="text-align:center;padding:3rem 1rem;"><h2>Ready to replace your CRT?</h2><p>szkongto01@foxmail.com | +86-13686889647 | <a href="https://wa.me/8613686899647">WhatsApp</a></p><a href="/en/quote.html" class="btn btn-primary btn-large">Request Quote</a></section>
    </main>
        <div class="related-products" style="background:#f8fafc;padding:1.5rem;border-radius:8px;margin:2rem 0;border:1px solid #e2e8f0;">
            <p style="font-weight:bold;color:#1e40af;margin:0 0 0.75rem 0;">&#x1F4DA; Related Resources</p>
            <ul style="margin:0;padding-left:1.2rem;">
                <li><a href="/en/compatibility-matrix.html">CNC CRT Model Compatibility Matrix</a></li>
                <li><a href="/en/brands/FANUC.html">All FANUC Display Solutions</a></li>
                <li><a href="/en/quote.html">Get a Quote</a> &mdash; Reply within 24 hours</li>
            </ul>
        </div>
    <footer>
        <div class="footer-content">
            <div class="footer-brand">
                <span class="footer-logo">Kongto Technology</span>
                <p>Industrial Video Display Solutions &mdash; CNC CRT-to-LCD Retrofit</p>
            </div>
            <div class="footer-links">
                <a href="/en/posts/">Articles</a>
                <a href="/en/brands/FANUC.html">FANUC</a>
                <a href="/en/brands/Mitsubishi.html">Mitsubishi</a>
                <a href="/en/brands/Siemens.html">Siemens</a>
                <a href="/en/docs/">Downloads</a>
                <a href="/en/about.html">About Us</a>
            </div>
            <p class="footer-copy">&copy; 2013-2026 Kongto Technology | +86-13686889647</p>
        </div>
    </footer>
</body>
</html>'''

for m in MODELS:
    slug = f"fanuc-{m['part'].lower().replace(' ', '-')}-lcd-upgrade"
    with open(f"d:/code/seo_deploy/en/products/{slug}.html", 'w', encoding='utf-8') as f:
        f.write(make_en(m))
    print(f"  EN: {slug}.html")

print(f"\nDone: {len(MODELS)} EN pages regenerated")
