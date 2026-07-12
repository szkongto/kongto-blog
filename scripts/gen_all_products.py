"""Generate ALL missing product pages from keyword map (models without pages)."""
import os

SITE = r'd:\code\seo_deploy'

# Existing slugs (skip these)
EXISTING = {f.replace('.html','') for f in os.listdir(os.path.join(SITE, 'products')) if f.endswith('.html')}

PRODUCTS = [
    # === FANUC missing P0 ===
    {'slug': 'fanuc-a61l-0001-0077-lcd-upgrade', 'title': 'FANUC A61L-0001-0077 LCD Replacement | 12.1" TFT | Kongto',
     'desc': 'FANUC A61L-0001-0077 LCD replacement — 12.1-inch TFT, plug-and-play module. No CNC parameter changes. 2-year warranty, ships today.',
     'h1': 'FANUC A61L-0001-0077 LCD Replacement Display', 'brand': 'FANUC', 'brand_page': 'FANUC.html', 'price': '$350', 'sku': 'KONGTO-A61L-0077-LCD', 'mpn': 'A61L-0001-0077-LCD', 'compat': 'FANUC 0/0i/16i/18i Series', 'signal': 'Honda MR-20M 20-pin', 'size': '12.1-inch'},
    {'slug': 'fanuc-a61l-0001-0078-lcd-upgrade', 'title': 'FANUC A61L-0001-0078 LCD Replacement | 12.1" TFT | Kongto',
     'desc': 'FANUC A61L-0001-0078 LCD replacement — 12.1-inch TFT, direct CRT drop-in. Plug-and-play, same Honda connector. 2-year warranty, ships today.',
     'h1': 'FANUC A61L-0001-0078 LCD Replacement Display', 'brand': 'FANUC', 'brand_page': 'FANUC.html', 'price': '$350', 'sku': 'KONGTO-A61L-0078-LCD', 'mpn': 'A61L-0001-0078-LCD', 'compat': 'FANUC 0/0i/16i/18i Series', 'signal': 'Honda MR-20M 20-pin', 'size': '12.1-inch'},
    {'slug': 'fanuc-a61l-0001-0087-lcd-upgrade', 'title': 'FANUC A61L-0001-0087 LCD Replacement | 8.4" TFT | Kongto',
     'desc': 'FANUC A61L-0001-0087 LCD replacement — 8.4-inch TFT, plug-and-play CRT replacement. No rewiring. FANUC 0/0i compatible. 2-year warranty.',
     'h1': 'FANUC A61L-0001-0087 LCD Replacement Display', 'brand': 'FANUC', 'brand_page': 'FANUC.html', 'price': '$299', 'sku': 'KONGTO-A61L-0087-LCD', 'mpn': 'A61L-0001-0087-LCD', 'compat': 'FANUC 0/0i Series', 'signal': 'Honda MR-20M 20-pin', 'size': '8.4-inch'},
    {'slug': 'fanuc-0m-0t-crt-lcd-upgrade', 'title': 'FANUC 0-M/0-T CRT Replacement | LCD Upgrade | Kongto',
     'desc': 'FANUC 0-M/0-T CRT to LCD replacement — 9-inch TFT, plug-and-play for FANUC 0-Mate and 0-T CNC controls. Same 20-pin Honda connector. 2-year warranty.',
     'h1': 'FANUC 0-M/0-T CRT to LCD Replacement', 'brand': 'FANUC', 'brand_page': 'FANUC.html', 'price': '$255', 'sku': 'KONGTO-0M0T-LCD', 'mpn': '0M-0T-LCD', 'compat': 'FANUC 0-M, 0-Mate, 0-T CNC', 'signal': 'Honda MR-20M 20-pin', 'size': '9-inch'},
    {'slug': 'fanuc-16i-18i-21i-lcd-upgrade', 'title': 'FANUC 16i/18i/21i LCD Upgrade | CRT to LCD | Kongto',
     'desc': 'FANUC 16i/18i/21i LCD upgrade — CRT to LCD replacement for FANUC Series 16i/18i/21i CNC controls. Plug-and-play, no parameter changes. 2-year warranty.',
     'h1': 'FANUC 16i/18i/21i LCD Upgrade Display', 'brand': 'FANUC', 'brand_page': 'FANUC.html', 'price': '$299', 'sku': 'KONGTO-16i18i-LCD', 'mpn': '16i-18i-LCD', 'compat': 'FANUC 16i, 18i, 21i Series', 'signal': 'Honda MR-20M 20-pin', 'size': '9-inch'},
    {'slug': 'fanuc-mdt947b-1a-lcd-upgrade', 'title': 'FANUC MDT947B-1A LCD Replacement | CRT to LCD | Kongto',
     'desc': 'FANUC MDT947B-1A LCD replacement — MDT-947B CRT to LCD upgrade. Plug-and-play, direct fit. FANUC CNC compatible. 2-year warranty, ships today.',
     'h1': 'FANUC MDT947B-1A LCD Replacement Display', 'brand': 'FANUC', 'brand_page': 'FANUC.html', 'price': '$299', 'sku': 'KONGTO-MDT947B-LCD', 'mpn': 'MDT947B-1A-LCD', 'compat': 'FANUC CNC with MDT-947B', 'signal': 'Honda MR-20M 20-pin', 'size': '9-inch'},
    {'slug': 'fanuc-tx-1424ab-lcd-upgrade', 'title': 'FANUC TX-1424AB LCD Replacement | CRT to LCD | Kongto',
     'desc': 'FANUC TX-1424AB LCD replacement — CRT to LCD for FANUC OEM displays. Plug-and-play module. 2-year warranty, ships within 24 hours.',
     'h1': 'FANUC TX-1424AB LCD Replacement Display', 'brand': 'FANUC', 'brand_page': 'FANUC.html', 'price': '$350', 'sku': 'KONGTO-TX1424AB-LCD', 'mpn': 'TX-1424AB-LCD', 'compat': 'FANUC CNC systems', 'signal': 'Honda MR-20M 20-pin', 'size': '14-inch'},
    {'slug': 'fanuc-a02b-0200-c071-lcd-upgrade', 'title': 'FANUC A02B-0200-C071 LCD Replacement | CRT Unit | Kongto',
     'desc': 'FANUC A02B-0200-C071 CRT to LCD replacement. Direct replacement for this CRT/MDI unit. Plug-and-play, no parameter changes. 2-year warranty.',
     'h1': 'FANUC A02B-0200-C071 LCD Replacement', 'brand': 'FANUC', 'brand_page': 'FANUC.html', 'price': '$399', 'sku': 'KONGTO-A02B-C071-LCD', 'mpn': 'A02B-0200-C071-LCD', 'compat': 'FANUC CNC systems', 'signal': 'Proprietary FANUC', 'size': '9-inch'},

    # === Mitsubishi missing P0+P1 ===
    {'slug': 'mitsubishi-mdt925ps-lcd-upgrade', 'title': 'Mitsubishi MDT925PS LCD Replacement | CRT to LCD | Kongto',
     'desc': 'Mitsubishi MDT925PS LCD replacement — CRT to LCD for Mitsubishi MELDAS CNC. Plug-and-play, no rewiring. 2-year warranty, ships today.',
     'h1': 'Mitsubishi MDT925PS LCD Replacement Display', 'brand': 'Mitsubishi', 'brand_page': 'Mitsubishi.html', 'price': '$399', 'sku': 'KONGTO-MDT925PS-LCD', 'mpn': 'MDT925PS-LCD', 'compat': 'Mitsubishi MELDAS CNC', 'signal': '10-pin flat cable', 'size': '8-inch'},
    {'slug': 'mitsubishi-mdt947b-lcd-upgrade', 'title': 'Mitsubishi MDT947B LCD Replacement | CRT to LCD | Kongto',
     'desc': 'Mitsubishi MDT947B LCD replacement — CRT to LCD for Mitsubishi CNC. Plug-and-play module. 2-year warranty, ships within 24 hours.',
     'h1': 'Mitsubishi MDT947B LCD Replacement Display', 'brand': 'Mitsubishi', 'brand_page': 'Mitsubishi.html', 'price': '$399', 'sku': 'KONGTO-MDT947B-LCD', 'mpn': 'MDT947B-LCD', 'compat': 'Mitsubishi CNC systems', 'signal': '10-pin flat cable / 20-pin Honda', 'size': '9-inch'},
    {'slug': 'mitsubishi-mdt-1283b-lcd-upgrade', 'title': 'Mitsubishi MDT-1283B LCD Replacement | CRT to LCD | Kongto',
     'desc': 'Mitsubishi MDT-1283B LCD replacement — 12-inch CRT to LCD for Mitsubishi/Mazak CNC. Plug-and-play, no modifications. 2-year warranty, ships today.',
     'h1': 'Mitsubishi MDT-1283B LCD Replacement Display', 'brand': 'Mitsubishi', 'brand_page': 'Mitsubishi.html', 'price': '$435', 'sku': 'KONGTO-MDT1283B-LCD', 'mpn': 'MDT-1283B-LCD', 'compat': 'Mitsubishi MELDAS, Mazak CNC', 'signal': '20-pin Honda', 'size': '12-inch'},
    {'slug': 'mitsubishi-c3470-crt-lcd-upgrade', 'title': 'Mitsubishi C-3470 CRT to LCD Replacement | Kongto',
     'desc': 'Mitsubishi C-3470/C-3470NS CRT to LCD replacement. Plug-and-play module for Mitsubishi CNC displays. 2-year warranty, ships within 24 hours.',
     'h1': 'Mitsubishi C-3470 CRT to LCD Replacement', 'brand': 'Mitsubishi', 'brand_page': 'Mitsubishi.html', 'price': '$399', 'sku': 'KONGTO-C3470-LCD', 'mpn': 'C-3470-LCD', 'compat': 'Mitsubishi C-3470, C-3470NS', 'signal': '26-pin / 20-pin Honda', 'size': '14-inch'},
    {'slug': 'mitsubishi-c5470-lcd-upgrade', 'title': 'Mitsubishi C-5470 LCD Replacement | CRT to LCD | Kongto',
     'desc': 'Mitsubishi C-5470/C-5470NS LCD replacement — 14-inch CRT to LCD for Mitsubishi CNC. Plug-and-play, no rewiring. 2-year warranty.',
     'h1': 'Mitsubishi C-5470 LCD Replacement Display', 'brand': 'Mitsubishi', 'brand_page': 'Mitsubishi.html', 'price': '$480', 'sku': 'KONGTO-C5470-LCD', 'mpn': 'C-5470-LCD', 'compat': 'Mitsubishi C-5470, C-5470NS', 'signal': '26-pin / 20-pin Honda', 'size': '14-inch'},

    # === Mazak missing P0 ===
    {'slug': 'mazak-cd1472-d2m-lcd-upgrade', 'title': 'Mazak CD1472-D2M LCD Replacement | 14" CRT to LCD | Kongto',
     'desc': 'Mazak CD1472-D2M LCD replacement — 14-inch color CRT to LCD for Mazatrol CNC. Plug-and-play, no modifications. 2-year warranty.',
     'h1': 'Mazak CD1472-D2M LCD Replacement Display', 'brand': 'Mazak', 'brand_page': 'MAZAK.html', 'price': '$355', 'sku': 'KONGTO-CD1472D2M-LCD', 'mpn': 'CD1472-D2M-LCD', 'compat': 'Mazak Mazatrol T-32/M-32', 'signal': '26-pin D-Sub', 'size': '14-inch'},
    {'slug': 'mazak-cd1283-d1m-lcd-upgrade', 'title': 'Mazak CD1283-D1M LCD Replacement | CRT to LCD | Kongto',
     'desc': 'Mazak CD1283-D1M LCD replacement — CRT to LCD for Mazak Mazatrol CNC. Plug-and-play module. 2-year warranty, ships today.',
     'h1': 'Mazak CD1283-D1M LCD Replacement Display', 'brand': 'Mazak', 'brand_page': 'MAZAK.html', 'price': '$355', 'sku': 'KONGTO-CD1283D1M-LCD', 'mpn': 'CD1283-D1M-LCD', 'compat': 'Mazak Mazatrol CNC', 'signal': '26-pin D-Sub', 'size': '14-inch'},
    {'slug': 'mazak-cd0910-dm-lcd-upgrade', 'title': 'Mazak CD0910-DM LCD Replacement | T-32 CRT to LCD | Kongto',
     'desc': 'Mazak CD0910-DM LCD replacement — CRT to LCD for Mazak Mazatrol T-32 CNC. Plug-and-play, no rewiring. 2-year warranty, ships today.',
     'h1': 'Mazak CD0910-DM LCD Replacement Display', 'brand': 'Mazak', 'brand_page': 'MAZAK.html', 'price': '$355', 'sku': 'KONGTO-CD0910DM-LCD', 'mpn': 'CD0910-DM-LCD', 'compat': 'Mazak Mazatrol T-32', 'signal': '26-pin D-Sub', 'size': '14-inch'},
    {'slug': 'mazak-du3461g-l-lcd-upgrade', 'title': 'Mazak DU3461G-L LCD Replacement | CRT to LCD | Kongto',
     'desc': 'Mazak DU3461G-L CRT to LCD replacement. Plug-and-play module for Mazak CNC displays. 2-year warranty, ships within 24 hours.',
     'h1': 'Mazak DU3461G-L LCD Replacement Display', 'brand': 'Mazak', 'brand_page': 'MAZAK.html', 'price': '$399', 'sku': 'KONGTO-DU3461G-LCD', 'mpn': 'DU3461G-L-LCD', 'compat': 'Mazak CNC systems', 'signal': '26-pin D-Sub', 'size': '14-inch'},
    {'slug': 'mazak-t3021-ah-lcd-upgrade', 'title': 'Mazak T3021-AH LCD Replacement | M-2 CRT to LCD | Kongto',
     'desc': 'Mazak T3021-AH CRT to LCD replacement for Mazak M-2 CNC controls. Plug-and-play module. 2-year warranty, ships today.',
     'h1': 'Mazak T3021-AH LCD Replacement Display', 'brand': 'Mazak', 'brand_page': 'MAZAK.html', 'price': '$355', 'sku': 'KONGTO-T3021AH-LCD', 'mpn': 'T3021-AH-LCD', 'compat': 'Mazak M-2 CNC', 'signal': '20-pin Honda', 'size': '9-inch'},

    # === Siemens missing P1 ===
    {'slug': 'siemens-6fc5203-lcd-upgrade', 'title': 'Siemens 6FC5203 LCD Replacement | 840D sl Display | Kongto',
     'desc': 'Siemens 6FC5203-0AF00/0AD10 LCD replacement — for SINUMERIK 840D sl. Plug-and-play, no parameter changes. 2-year warranty.',
     'h1': 'Siemens 6FC5203 LCD Replacement Display', 'brand': 'Siemens', 'brand_page': 'Siemens.html', 'price': '$449', 'sku': 'KONGTO-6FC5203-LCD', 'mpn': '6FC5203-LCD', 'compat': 'SINUMERIK 840D sl', 'signal': 'DB-25 / DVI', 'size': '10.4-inch'},
    {'slug': 'siemens-8.4-inch-crt-lcd-upgrade', 'title': 'Siemens 8.4" Industrial CRT to LCD | SINUMERIK | Kongto',
     'desc': 'Siemens 8.4-inch industrial CRT to LCD replacement for SINUMERIK controls. Plug-and-play, no rewiring. 2-year warranty, ships today.',
     'h1': 'Siemens 8.4" Industrial CRT to LCD', 'brand': 'Siemens', 'brand_page': 'Siemens.html', 'price': '$349', 'sku': 'KONGTO-SIEM84-LCD', 'mpn': 'SIEM-84-LCD', 'compat': 'Siemens SINUMERIK 810/820/840D', 'signal': 'DB-25', 'size': '8.4-inch'},

    # === Okuma missing P0 ===
    {'slug': 'okuma-osp7000-crt-lcd-upgrade', 'title': 'Okuma OSP7000 CRT to LCD Upgrade | 14" Display | Kongto',
     'desc': 'Okuma OSP7000 CRT to LCD upgrade — 14-inch color replacement for Okuma OSP7000 CNC. Plug-and-play, 15-30 min install. $450, 2-year warranty.',
     'h1': 'Okuma OSP7000 CRT to LCD Upgrade', 'brand': 'Okuma', 'brand_page': 'OKUMA.html', 'price': '$450', 'sku': 'KONGTO-OSP7000-LCD', 'mpn': 'OSP7000-LCD', 'compat': 'Okuma OSP7000 CNC', 'signal': '14-pin / 20-pin', 'size': '14-inch'},
    {'slug': 'okuma-osp5020-lcd-upgrade', 'title': 'Okuma OSP5020 LCD Replacement | Monitor Upgrade | Kongto',
     'desc': 'Okuma OSP5020 LCD replacement — monitor upgrade for Okuma OSP5020 CNC. Plug-and-play, no modifications. $430, 2-year warranty, ships today.',
     'h1': 'Okuma OSP5020 LCD Replacement Display', 'brand': 'Okuma', 'brand_page': 'OKUMA.html', 'price': '$430', 'sku': 'KONGTO-OSP5020-LCD', 'mpn': 'OSP5020-LCD', 'compat': 'Okuma OSP5020 CNC', 'signal': '14-pin / 20-pin', 'size': '12-inch'},

    # === Haas missing P0 ===
    {'slug': 'haas-9-pin-monochrome-lcd-upgrade', 'title': 'Haas 9-Pin Monochrome LCD Replacement | CRT to LCD | Kongto',
     'desc': 'Haas 9-pin monochrome CRT to LCD replacement for VF series Classic Control. Plug-and-play, 9-pin D-Sub. $399, 2-year warranty, ships today.',
     'h1': 'Haas 9-Pin Monochrome LCD Replacement', 'brand': 'Haas', 'brand_page': 'HAAS.html', 'price': '$399', 'sku': 'KONGTO-HAAS9PIN-LCD', 'mpn': 'HAAS-9PIN-LCD', 'compat': 'Haas VF-0/1/2 Classic Control, 9-pin amber CRT', 'signal': '9-pin D-Sub', 'size': '9-inch'},
    {'slug': 'haas-12inch-9pin-crt-lcd-upgrade', 'title': 'Haas 12" 9-Pin CRT to LCD | VF Series | Kongto',
     'desc': 'Haas 12-inch 9-pin CRT to LCD replacement for VF series CNC. Plug-and-play, DC 12V. $399, 2-year warranty, ships within 24 hours.',
     'h1': 'Haas 12" 9-Pin CRT to LCD Replacement', 'brand': 'Haas', 'brand_page': 'HAAS.html', 'price': '$399', 'sku': 'KONGTO-HAAS12-LCD', 'mpn': 'HAAS-12-LCD', 'compat': 'Haas VF Series, 12" 9-pin CRT', 'signal': '9-pin D-Sub', 'size': '12-inch'},

    # === Heidenhain missing P0 ===
    {'slug': 'heidenhain-be211-lcd-upgrade', 'title': 'Heidenhain BE211 LCD Replacement | 9" CRT to LCD | Kongto',
     'desc': 'Heidenhain BE211 LCD replacement — 9-inch monochrome CRT to LCD for TNC 310/320. Plug-and-play, 15-pin D-Sub. 2-year warranty, ships today.',
     'h1': 'Heidenhain BE211 LCD Replacement Display', 'brand': 'Heidenhain', 'brand_page': 'Heidenhain.html', 'price': '$355', 'sku': 'KONGTO-BE211-LCD', 'mpn': 'BE211-LCD', 'compat': 'Heidenhain TNC 310, TNC 320', 'signal': '15-pin D-Sub (RGBHV)', 'size': '9-inch'},

    # === Matsushita missing P0 ===
    {'slug': 'matsushita-tx1450ab-lcd-upgrade', 'title': 'Matsushita TX-1450AB LCD Replacement | CRT to LCD | Kongto',
     'desc': 'Matsushita TX-1450AB/TX-1404AB LCD replacement — CRT to LCD for Panasonic/Matsushita CNC displays. Mazak OEM. Plug-and-play. 2-year warranty.',
     'h1': 'Matsushita TX-1450AB LCD Replacement Display', 'brand': 'Matsushita', 'brand_page': 'Matsushita.html', 'price': '$399', 'sku': 'KONGTO-TX1450AB-LCD', 'mpn': 'TX-1450AB-LCD', 'compat': 'Matsushita CNC, Mazak OEM', 'signal': '20-pin Honda', 'size': '14-inch'},

    # === Toshiba missing P1 ===
    {'slug': 'toshiba-d15cm-lcd-upgrade', 'title': 'Toshiba D15CM-04A LCD Replacement | CRT to LCD | Kongto',
     'desc': 'Toshiba D15CM-04A/06A CRT to LCD replacement. FANUC OEM equivalent. Plug-and-play module. 2-year warranty, ships within 24 hours.',
     'h1': 'Toshiba D15CM LCD Replacement Display', 'brand': 'Toshiba', 'brand_page': 'Toshiba.html', 'price': '$399', 'sku': 'KONGTO-D15CM-LCD', 'mpn': 'D15CM-LCD', 'compat': 'Toshiba D15CM, FANUC OEM', 'signal': 'Honda MR-20M 20-pin', 'size': '15-inch'},
]

HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="https://cncdisplay.com/products/{slug}.html">
    <link rel="alternate" hreflang="en" href="https://cncdisplay.com/products/{slug}.html">
    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/products/{slug}.html">
    <link rel="stylesheet" href="/css/style.css?v=7">
    <meta property="og:type" content="product">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="https://cncdisplay.com/images/logo_256.png">
    <meta property="product:price:amount" content="{pnum}">
    <meta property="product:price:currency" content="USD">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:image" content="https://cncdisplay.com/images/logo_256.png">
    <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{h1}",
  "description": "{desc}",
  "sku": "{sku}",
  "mpn": "{mpn}",
  "brand": {{ "@type": "Brand", "name": "{brand}" }},
  "image": "https://cncdisplay.com/images/logo_256.png",
  "offers": {{
    "@type": "Offer", "price": "{pnum}.00", "priceCurrency": "USD", "validFrom": "2026-07-13",
    "shippingDetails": {{
      "@type": "OfferShippingDetails",
      "shippingRate": {{ "@type": "MonetaryAmount", "value": "0", "currency": "USD" }},
      "shippingDestination": {{ "@type": "DefinedRegion", "addressCountry": ["CN","US","DE","JP","KR","SG","IN","GB","FR","IT"] }},
      "deliveryTime": {{ "@type": "ShippingDeliveryTime", "handlingTime": {{ "@type": "QuantitativeValue", "minValue": 1, "maxValue": 3, "unitCode": "DAY" }}, "transitTime": {{ "@type": "QuantitativeValue", "minValue": 1, "maxValue": 7, "unitCode": "DAY" }} }}
    }},
    "hasMerchantReturnPolicy": {{"@type":"MerchantReturnPolicy","applicableCountry":"CN","returnPolicyCategory":"https://schema.org/MerchantReturnFiniteReturnWindow","merchantReturnDays":7,"returnMethod":"https://schema.org/ReturnByMail","returnFees":"https://schema.org/FreeReturn"}},
    "availability": "https://schema.org/InStock",
    "url": "https://cncdisplay.com/products/{slug}.html"
  }}
}}
</script>
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
    <main style="max-width:1100px;margin:0 auto;padding:20px;">
    <nav style="font-size:0.9rem;color:#666;margin-bottom:1rem;"><a href="/">Home</a> / <a href="/brands/{brand_page}">{brand}</a> / <strong>{h1}</strong></nav>
    <section style="display:flex;gap:2rem;flex-wrap:wrap;align-items:flex-start;margin:2rem 0;">
    <div style="flex:1;min-width:280px;">
        <h1>{h1}</h1>
        <p>{size} industrial TFT-LCD plug-and-play replacement for {brand} CRT display. No modifications needed. 15-30 minute installation.</p>
        <div style="font-size:2.5rem;font-weight:800;color:#FF6600;">{price} <span style="font-size:1rem;color:#666;">USD</span></div>
        <p style="color:#28a745;font-weight:600;">In Stock &#x2014; 2-Year Warranty</p>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0;"><a href="/quote.html" style="display:inline-block;padding:14px 32px;background:#FF6600;color:#fff;border-radius:8px;text-decoration:none;font-weight:700;">Get a Quote</a><a href="/brands/{brand_page}" style="display:inline-block;padding:14px 32px;background:#667eea;color:#fff;border-radius:8px;text-decoration:none;font-weight:700;">View {brand} Series</a></div>
    </div>
    </section>
    <section>
        <h2>Specifications</h2>
        <table style="width:100%;border-collapse:collapse;margin:1.5rem 0;">
            <tr><th style="padding:10px 14px;border:1px solid #e0e0e0;text-align:left;background:#1a1a2e;color:#fff;width:35%;">Spec</th><th style="padding:10px 14px;border:1px solid #e0e0e0;text-align:left;background:#1a1a2e;color:#fff;">Original CRT</th><th style="padding:10px 14px;border:1px solid #e0e0e0;text-align:left;background:#1a1a2e;color:#fff;">Kongto LCD</th></tr>
            <tr><td style="padding:10px 14px;border:1px solid #e0e0e0;">Technology</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">Monochrome / Color CRT</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">TFT-LCD Industrial Panel</td></tr>
            <tr style="background:#f8f9fa;"><td style="padding:10px 14px;border:1px solid #e0e0e0;">Screen Size</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">{size}</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">{size} LED-backlit LCD</td></tr>
            <tr><td style="padding:10px 14px;border:1px solid #e0e0e0;">Resolution</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">640x400 / 640x480</td><td style="padding:10px 14px;border:1px solid #e0e0e0;"><strong>800x600</strong></td></tr>
            <tr style="background:#f8f9fa;"><td style="padding:10px 14px;border:1px solid #e0e0e0;">Brightness</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">~200 cd/m2</td><td style="padding:10px 14px;border:1px solid #e0e0e0;"><strong>350-450 cd/m2</strong></td></tr>
            <tr><td style="padding:10px 14px;border:1px solid #e0e0e0;">Lifespan</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">~15,000 hrs</td><td style="padding:10px 14px;border:1px solid #e0e0e0;"><strong>50,000+ hrs</strong></td></tr>
            <tr style="background:#f8f9fa;"><td style="padding:10px 14px;border:1px solid #e0e0e0;">Power</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">DC 24V / DC 12V</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">DC 24V / DC 12V (original)</td></tr>
            <tr><td style="padding:10px 14px;border:1px solid #e0e0e0;">Interface</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">{signal}</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">{signal} (direct compatible)</td></tr>
            <tr style="background:#f8f9fa;"><td style="padding:10px 14px;border:1px solid #e0e0e0;">Safety</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">High voltage (10-15kV)</td><td style="padding:10px 14px;border:1px solid #e0e0e0;"><strong>Low voltage DC</strong></td></tr>
        </table>
    </section>
    <section><h2>Compatible Systems</h2><ul>
        <li>{compat}</li>
    </ul></section>
'''

TAIL = '''    <section style="margin:2rem 0;padding:1.5rem;background:#fff8f0;border-radius:8px;border:1px solid #ffe0b2;">
        <h2>Common CRT Failure Symptoms</h2>
        <ul>
            <li><strong>Blank screen</strong> &#x2014; Flyback transformer or heater failure</li>
            <li><strong>Dim / unreadable display</strong> &#x2014; CRT phosphor wear after extended use</li>
            <li><strong>Flickering or rolled image</strong> &#x2014; Capacitor failure in sync circuit</li>
        </ul>
        <p>Our LCD module eliminates all CRT-related failure modes. Plug-and-play, no rewiring needed.</p>
    </section>
    <section style="background:#f0f7ff;padding:24px;border-radius:12px;margin:2rem 0;">
        <h2>Warranty &amp; Service</h2>
        <p><strong>2-Year Warranty</strong> &#x2014; Lifetime Technical Support &#x2014; Free Worldwide Shipping</p>
        <p>info@cncdisplay.com | +86-13686889647 | <a href="https://wa.me/8613686889647">WhatsApp</a></p>
    </section>
    <section style="text-align:center;padding:3rem 1rem;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border-radius:12px;margin:2rem 0;">
        <h2 style="color:#fff;">Ready to replace your CRT?</h2>
        <p>{price} &#x2014; In Stock &#x2014; Ships within 24 hours</p>
        <a href="/quote.html" style="display:inline-block;padding:14px 36px;background:#fff;color:#667eea;border-radius:8px;text-decoration:none;font-weight:700;">Request Quote &#x2192;</a>
    </section>
    </main>
    <div style="background:#f8fafc;padding:1.5rem;border-radius:8px;margin:2rem 0;border:1px solid #e2e8f0;">
        <p style="font-weight:bold;color:#1e40af;margin:0 0 0.75rem 0;">&#x1F4D8; Related Resources</p>
        <ul style="margin:0;padding-left:1.2rem;">
            <li><a href="/brands/{brand_page}">{brand} Display Solutions</a> &#x2014; All {brand} models</li>
            <li><a href="/compatibility-matrix.html">Compatibility Matrix</a> &#x2014; 95+ models</li>
            <li><a href="/crt-dead-symptoms.html">CRT Failure Symptoms</a> &#x2014; Diagnosis guide</li>
            <li><a href="/quote.html">Get a Quote</a> &#x2014; Reply within 24 hours</li>
        </ul>
    </div>
    <footer>
        <div class="footer-content">
            <div class="footer-brand">
                <span class="footer-logo">Kongto Technology &#x6C5F;&#x56FE;&#x79D1;&#x6280;</span>
                <p>Industrial Video Display Solutions &#x2014; CNC CRT-to-LCD Retrofit, Video Signal Converters, Custom Industrial Displays</p>
            </div>
            <div class="footer-links">
                <a href="/posts/">&#x1F4C4; Articles</a>
                <a href="/brands/{brand_page}">{brand}</a>
                <a href="/brands/FANUC.html">FANUC</a>
                <a href="/brands/Mitsubishi.html">Mitsubishi</a>
                <a href="/brands/Siemens.html">Siemens</a>
                <a href="/brands/Heidenhain.html">Heidenhain</a>
                <a href="/docs/">Downloads</a>
                <a href="/about.html">About Us</a>
            </div>
            <p class="footer-copy">&copy; 2013-2026 Kongto Technology | Shenzhen, Guangdong, China | +86-13686889647 | sales@cncdisplay.com</p>
        </div>
    </footer>
</body>
</html>'''

count = 0
skipped = 0
for p in PRODUCTS:
    slug = p['slug']
    fp = os.path.join(SITE, 'products', f'{slug}.html')
    if os.path.exists(fp):
        skipped += 1
        continue
    p['pnum'] = p['price'].replace('$', '')
    html = (HEAD + TAIL).replace('{title}', p['title']).replace('{desc}', p['desc']).replace('{slug}', p['slug'])
    html = html.replace('{h1}', p['h1']).replace('{brand}', p['brand']).replace('{brand_page}', p['brand_page'])
    html = html.replace('{price}', p['price']).replace('{pnum}', p['pnum'])
    html = html.replace('{sku}', p['sku']).replace('{mpn}', p['mpn'])
    html = html.replace('{compat}', p['compat']).replace('{signal}', p['signal']).replace('{size}', p['size'])
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(html)
    count += 1
    print(f'CREATED: {slug}')

print(f'\nCreated: {count}, Skipped (exists): {skipped}')
