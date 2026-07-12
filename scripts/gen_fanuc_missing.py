"""Generate missing FANUC product pages + articles with images."""
import os, sys, json, shutil
from PIL import Image

SITE = r'd:\code\seo_deploy'
IMG_SRC = r'D:\工作资料\KONGTO\产品图片\FANUC'
IMG_DST = os.path.join(SITE, 'images', 'fanuc')
os.makedirs(IMG_DST, exist_ok=True)

def resize_image(src, dst, max_w=800):
    """Copy and resize image to max width 800px, preserving aspect ratio."""
    try:
        img = Image.open(src)
        if img.mode in ('RGBA', 'P'): img = img.convert('RGB')
        w, h = img.size
        if w > max_w:
            ratio = max_w / w
            new_h = int(h * ratio)
            img = img.resize((max_w, new_h), Image.LANCZOS)
        ext = os.path.splitext(dst)[1].lower()
        if ext in ('.jpg', '.jpeg'): img.save(dst, 'JPEG', quality=85)
        else: img.save(dst, 'PNG')
        return os.path.getsize(dst)
    except Exception as e:
        print(f'  Image error {src}: {e}')
        return 0

# ====== MODEL DATA ======
MODELS = [
    {
        'slug': 'fanuc-a02b-0094-c022-lcd-upgrade',
        'title': 'FANUC A02B-0094-C022 CRT/MDI to LCD | Replacement Unit | Kongto',
        'desc': 'FANUC A02B-0094-C022 CRT/MDI combo replacement — LCD retrofit for FANUC 0/0i/16i/18i. Combines display + MDI keyboard panel. Plug-and-play, no parameter changes. 2-year warranty.',
        'h1': 'FANUC A02B-0094-C022 CRT/MDI to LCD Replacement',
        'price': '$499', 'pnum': '499', 'sku': 'KONGTO-A02B-C022', 'mpn': 'A02B-0094-C022-LCD',
        'signal': 'Honda MR-20M 20-pin / MDI parallel',
        'size': '9-inch', 'compat': 'FANUC 0, 0i-A/B/C/D, 16i, 18i Series',
        'brand': 'FANUC', 'brand_page': 'FANUC.html',
        'img_files': ['Fanuc - CRT A02B-0094-C022.jpg', 'Fanuc - CRT A02B-0094-C022-BACK.jpg', 'Fanuc - CRT A02B-0094-C022-LABEL.jpg'],
        'img_src_dir': 'A02B-0094-C022',
        'en_intro': 'The FANUC A02B-0094-C022 is a combined CRT display and MDI (Manual Data Input) keyboard unit used on FANUC 0-series, 0i-series, 16i, and 18i CNC controls. This integrated unit houses both the 9-inch monochrome/color CRT monitor and the operator data entry keypad in a single chassis.',
        'en_detail': 'As CRT components age, the display section of the A02B-0094-C022 commonly experiences flyback transformer failure (causing blank screen or no power), phosphor wear (dim/unreadable display), and capacitor degradation (image flicker or geometry distortion). Our LCD replacement module retains the original MDI keyboard functionality while replacing the CRT display section with a modern industrial TFT-LCD panel. The replacement is a direct fit — same mounting holes, same connector interface, same 24V DC power supply.',
        'zh_title': 'FANUC A02B-0094-C022 CRT/MDI一体机改LCD | 显示+键盘升级 | 江图科技',
        'zh_desc': 'FANUC A02B-0094-C022 CRT/MDI一体机改LCD方案。保留原MDI键盘功能，替换CRT显示部分为工业TFT液晶。即插即用，不改参数。2年质保。',
        'zh_h1': 'FANUC A02B-0094-C022 CRT/MDI一体机改LCD',
        'zh_intro': 'FANUC A02B-0094-C022 是一款CRT显示与MDI（手动数据输入）键盘一体机单元，用于FANUC 0系列、0i系列、16i、18i等数控系统。该一体机将9英寸CRT显示器与操作员数据输入键盘整合在同一机箱内。',
        'zh_detail': '随着CRT元件老化，A02B-0094-C022的显示部分常出现高压包故障（黑屏/无电）、荧光粉老化（显示暗淡）、电容老化（图像闪烁/几何失真）等问题。我们的LCD替换模组保留原MDI键盘功能，仅替换CRT显示部分为工业级TFT-LCD面板。此方案为直接替换——同一安装孔位、同一接口、同一DC 24V电源。',
    },
    {
        'slug': 'fanuc-a61l-0001-0116-lcd-upgrade',
        'title': 'FANUC A61L-0001-0116 LCD Upgrade | CRT Replacement | Kongto',
        'desc': 'FANUC A61L-0001-0116 LCD upgrade — replace aging CRT with 12.1-inch TFT LCD. Compatible with FANUC 0i/16i/18i/21i. Plug-and-play, no parameter changes. 2-year warranty.',
        'h1': 'FANUC A61L-0001-0116 LCD Upgrade Display',
        'price': '$399', 'pnum': '399', 'sku': 'KONGTO-A61L-0116', 'mpn': 'A61L-0001-0116-LCD',
        'signal': 'Honda MR-20M 20-pin',
        'size': '12.1-inch', 'compat': 'FANUC 0i, 16i, 18i, 21i Series',
        'brand': 'FANUC', 'brand_page': 'FANUC.html',
        'img_files': ['A61L-0001-0116 LCD正面图.jpg', 'A61L-0001-0116 LCD背面图.jpg', 'A61L-0001-0116 旧显示背面图2.jpg'],
        'img_src_dir': 'A61L-0001-0116',
        'en_intro': 'The FANUC A61L-0001-0116 is a 12.1-inch CRT display module used on larger-frame FANUC CNC controls including the 0i, 16i, 18i, and 21i series. It provides a larger display area suitable for applications requiring more on-screen information.',
        'en_detail': 'Our LCD replacement for the A61L-0001-0116 delivers 800×600 resolution (vs the original CRT 640×480), 350-450 cd/m² brightness, and 50,000+ hour lifespan — more than triple the original CRT life. The module is pin-compatible with the original Honda MR-20M 20-pin connector, requiring zero modifications to the CNC control cabinet. Installation takes 15-30 minutes.',
        'zh_title': 'FANUC A61L-0001-0116 LCD升级 | 12.1英寸CRT改TFT | 江图科技',
        'zh_desc': 'FANUC A61L-0001-0116 12.1英寸CRT改LCD升级方案。兼容FANUC 0i/16i/18i/21i系列。即插即用，不改参数。2年质保，现货当天发货。',
        'zh_h1': 'FANUC A61L-0001-0116 LCD升级显示屏',
        'zh_intro': 'FANUC A61L-0001-0116 是一种12.1英寸CRT显示模块，用于较大机型的FANUC数控系统，包括0i、16i、18i和21i系列。其更大的显示面积适合需要更多屏幕信息的应用场景。',
        'zh_detail': '我们的A61L-0001-0116 LCD替换方案提供800×600分辨率（原CRT为640×480）、350-450 cd/m²亮度、50,000+小时寿命——超过原CRT的三倍。模组与原Honda MR-20M 20针接口完全兼容，无需对数控柜做任何改造。安装仅需15-30分钟。',
    },
    {
        'slug': 'fanuc-a02b-0099-c094-lcd-upgrade',
        'title': 'FANUC Series 0-P A02B-0099-C094 CRT to LCD | Kongto',
        'desc': 'FANUC Series 0-P / A02B-0099-C094 monochrome CRT to LCD replacement. For FANUC O/OMate classic CNC controls. Plug-and-play, 9-inch green monochrome LCD. 2-year warranty.',
        'h1': 'FANUC Series 0-P A02B-0099-C094 CRT to LCD',
        'price': '$299', 'pnum': '299', 'sku': 'KONGTO-A02B-C094', 'mpn': 'A02B-0099-C094-LCD',
        'signal': '20-pin Honda MR-20M',
        'size': '9-inch', 'compat': 'FANUC Series 0, 0-Mate, 0-P, 0-T CNC controls',
        'brand': 'FANUC', 'brand_page': 'FANUC.html',
        'img_files': ['A02B-0099-C094-PBM 单绿色1.png', 'A02B-0099-C094-PBM 单色1.png', 'A02B-01.jpg', 'A02B-02.jpg'],
        'img_src_dir': 'FANUC Series O-P A02B-0099-C094-PBM单绿色',
        'en_intro': 'The FANUC Series 0-P (also known as the A02B-0099-C094) is a monochrome green-phosphor CRT display assembly used on the classic FANUC 0 series and 0-Mate CNC controls. This 9-inch PBM (Panel Built-in Monitor) unit was standard equipment on countless machine tools from the 1980s through 1990s.',
        'en_detail': 'Our LCD replacement module for the Series 0-P offers a drop-in upgrade: same 9-inch form factor, same 20-pin Honda connector, same DC 24V power. The LCD uses a high-contrast green monochrome TFT panel that preserves the classic CRT aesthetic while delivering 800×600 resolution, no flicker at any refresh rate, and 50,000+ hour reliability. No machine parameter changes, no wiring modifications, no bracket fabrication required.',
        'zh_title': 'FANUC Series 0-P A02B-0099-C094 CRT改LCD | 单绿色显示屏 | 江图科技',
        'zh_desc': 'FANUC Series 0-P A02B-0099-C094 单绿色CRT改LCD方案。用于FANUC 0系列/0-Mate经典数控。9英寸单绿色TFT液晶，即插即用，不改参数。2年质保。',
        'zh_h1': 'FANUC Series 0-P 单绿色CRT改LCD升级',
        'zh_intro': 'FANUC Series 0-P（亦称A02B-0099-C094）是用于经典FANUC 0系列和0-Mate数控系统的单绿色CRT显示器组件。这种9英寸PBM（面板内置显示器）单元从1980年代到1990年代是无数机床的标准配置。',
        'zh_detail': '我们的Series 0-P LCD替换模组提供直接升级方案：相同9英寸外形尺寸、相同20针Honda接口、相同DC 24V电源。LCD采用高对比度单绿色TFT面板，保留经典CRT的显示风格，同时提供800×600分辨率、无闪烁显示和50,000+小时寿命。无需修改机床参数、无需改动线路、无需制作安装支架。',
    },
]

# ====== COPY IMAGES ======
print('=== Copying & resizing images ===')
for m in MODELS:
    src_dir = os.path.join(IMG_SRC, m['img_src_dir'])
    dst_model_dir = os.path.join(IMG_DST, m['slug'].replace('fanuc-', ''))
    os.makedirs(dst_model_dir, exist_ok=True)
    for img_file in m['img_files']:
        src = os.path.join(src_dir, img_file)
        if not os.path.exists(src):
            print(f'  MISSING: {src}')
            continue
        dst = os.path.join(dst_model_dir, img_file)
        if not os.path.exists(dst):
            sz = resize_image(src, dst)
            if sz:
                print(f'  {img_file} -> {dst} ({sz/1024:.0f}KB)')
        else:
            print(f'  EXISTS: {dst}')

# Also make copies with web-friendly names in flat images/fanuc/
for m in MODELS:
    src_dir = os.path.join(IMG_SRC, m['img_src_dir'])
    for i, img_file in enumerate(m['img_files']):
        src = os.path.join(src_dir, img_file)
        if not os.path.exists(src): continue
        ext = os.path.splitext(img_file)[1]
        web_name = f"{m['slug'].replace('fanuc-', '')}_{i+1}{ext}"
        dst = os.path.join(IMG_DST, web_name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f'  {web_name} -> flat copy')

print('\n=== Creating product pages ===')
# ====== GENERATE PRODUCT PAGES ======
HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="https://cncdisplay.com/products/{slug}.html">
    <link rel="alternate" hreflang="en" href="https://cncdisplay.com/products/{slug}.html">
    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/products/{slug}.html">
    <link rel="stylesheet" href="/css/style.css?v=7">
    <meta property="og:type" content="product">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="https://cncdisplay.com/images/fanuc/{img1}">
    <meta property="product:price:amount" content="{pnum}">
    <meta property="product:price:currency" content="USD">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:image" content="https://cncdisplay.com/images/fanuc/{img1}">
    <script type="application/ld+json">{{
  "@context": "https://schema.org", "@type": "Product",
  "name": "{h1}", "description": "{desc}",
  "sku": "{sku}", "mpn": "{mpn}",
  "brand": {{ "@type": "Brand", "name": "{brand}" }},
  "image": "https://cncdisplay.com/images/fanuc/{img1}",
  "offers": {{
    "@type": "Offer", "price": "{pnum}.00", "priceCurrency": "USD", "validFrom": "2026-07-13",
    "shippingDetails": {{ "@type": "OfferShippingDetails",
      "shippingRate": {{ "@type": "MonetaryAmount", "value": "0", "currency": "USD" }},
      "shippingDestination": {{ "@type": "DefinedRegion", "addressCountry": ["CN","US","DE","JP","KR","SG","IN","GB","FR","IT"] }},
      "deliveryTime": {{ "@type": "ShippingDeliveryTime", "handlingTime": {{ "@type": "QuantitativeValue", "minValue": 1, "maxValue": 3, "unitCode": "DAY" }}, "transitTime": {{ "@type": "QuantitativeValue", "minValue": 1, "maxValue": 7, "unitCode": "DAY" }} }}
    }},
    "hasMerchantReturnPolicy": {{"@type":"MerchantReturnPolicy","applicableCountry":"CN","returnPolicyCategory":"https://schema.org/MerchantReturnFiniteReturnWindow","merchantReturnDays":7,"returnMethod":"https://schema.org/ReturnByMail","returnFees":"https://schema.org/FreeReturn"}},
    "availability": "https://schema.org/InStock",
    "url": "https://cncdisplay.com/products/{slug}.html"
  }}
}}</script>
</head>
<body>
<header><nav>
    <a href="/" class="logo">Kongto Technology</a>
    <div class="nav-links">
        <a href="/">Home</a><a href="/compatibility-matrix.html">Compatibility</a>
        <a href="/products/">Products</a><a href="/posts/">Articles</a>
        <a href="/case-studies.html">Cases</a><a href="/docs/">Downloads</a>
        <a href="/about.html">About</a>
        <a href="/quote.html" style="color:#ff9800;font-weight:700;">Get Quote</a>
    </div>
    <a href="/search.html" class="nav-search">&#x1F50D; Search</a>
    <div class="lang-switch">
        <a href="/zh/products/{slug}.html" lang="zh" class="lang-zh">中文</a>
        <span class="divider">|</span>
        <a href="/products/{slug}.html" lang="en" class="lang-en">English</a>
    </div>
</nav></header>
<main style="max-width:1100px;margin:0 auto;padding:20px;">
<nav style="font-size:0.9rem;color:#666;margin-bottom:1rem;"><a href="/">Home</a> / <a href="/brands/FANUC.html">FANUC</a> / <strong>{h1}</strong></nav>
<section class="product-hero" style="display:flex;gap:2rem;flex-wrap:wrap;align-items:flex-start;margin:2rem 0;">
<div style="flex:1;min-width:300px;">
    <h1>{h1}</h1>
    <p>{intro}</p>
    <div class="product-price" style="font-size:2.5rem;font-weight:800;color:#FF6600;">${price} <span style="font-size:1rem;color:#666;">USD</span></div>
    <p style="color:#28a745;font-weight:600;">In Stock &#x2014; 2-Year Warranty</p>
    <div class="cta-buttons" style="display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0;">
        <a href="/quote.html" style="display:inline-block;padding:14px 32px;background:#FF6600;color:#fff;border-radius:8px;text-decoration:none;font-weight:700;">Get a Quote</a>
        <a href="/brands/FANUC.html" style="display:inline-block;padding:14px 32px;background:#667eea;color:#fff;border-radius:8px;text-decoration:none;font-weight:700;">View FANUC Series</a>
    </div>
</div>
<div style="flex:0 0 400px;">
    <img src="/images/fanuc/{img1}" alt="{h1}" style="width:100%;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.1);" loading="lazy">
</div>
</section>
'''

TAIL = '''<section><h2>Specifications</h2>
<table style="width:100%;border-collapse:collapse;margin:1.5rem 0;">
    <tr><th style="padding:10px 14px;border:1px solid #e0e0e0;text-align:left;background:#1a1a2e;color:#fff;">Spec</th><th style="padding:10px 14px;border:1px solid #e0e0e0;text-align:left;background:#1a1a2e;color:#fff;">Original CRT</th><th style="padding:10px 14px;border:1px solid #e0e0e0;text-align:left;background:#1a1a2e;color:#fff;">Kongto LCD</th></tr>
    <tr><td style="padding:10px 14px;border:1px solid #e0e0e0;">Technology</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">CRT Monochrome/Color</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">TFT-LCD Industrial Panel</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px 14px;border:1px solid #e0e0e0;">Screen Size</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">{size}</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">{size} LED-backlit LCD</td></tr>
    <tr><td style="padding:10px 14px;border:1px solid #e0e0e0;">Resolution</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">640x400 / 640x480</td><td style="padding:10px 14px;border:1px solid #e0e0e0;"><strong>800x600</strong></td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px 14px;border:1px solid #e0e0e0;">Brightness</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">~200 cd/m2</td><td style="padding:10px 14px;border:1px solid #e0e0e0;"><strong>350-450 cd/m2</strong></td></tr>
    <tr><td style="padding:10px 14px;border:1px solid #e0e0e0;">Lifespan</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">~15,000 hrs</td><td style="padding:10px 14px;border:1px solid #e0e0e0;"><strong>50,000+ hrs</strong></td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px 14px;border:1px solid #e0e0e0;">Power</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">DC 24V</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">DC 24V (original)</td></tr>
    <tr><td style="padding:10px 14px;border:1px solid #e0e0e0;">Interface</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">{signal}</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">{signal} (direct compatible)</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px 14px;border:1px solid #e0e0e0;">Safety</td><td style="padding:10px 14px;border:1px solid #e0e0e0;">High voltage (10-15kV)</td><td style="padding:10px 14px;border:1px solid #e0e0e0;"><strong>Low voltage DC</strong></td></tr>
</table></section>
<section><h2>Compatible Systems</h2><ul><li>{compat}</li></ul></section>
<section style="margin:2rem 0;padding:1.5rem;background:#fff8f0;border-radius:8px;"><h2>Common CRT Failure Symptoms</h2>
<ul>
    <li><strong>Blank screen / no power</strong> &#x2014; Flyback transformer failure, the most common CRT failure mode</li>
    <li><strong>Dim or unreadable display</strong> &#x2014; CRT phosphor wear after extended operation (15,000+ hours)</li>
    <li><strong>Flickering or image distortion</strong> &#x2014; Capacitor degradation in horizontal/vertical sync circuits</li>
    <li><strong>Color shift or missing colors</strong> &#x2014; Aging electron gun or video amplifier circuit failure</li>
</ul>
<p>Our LCD module eliminates all CRT-related failure modes permanently. Plug-and-play replacement, no rewiring or parameter changes needed.</p>
</section>
<section style="background:#f0f7ff;padding:24px;border-radius:12px;margin:2rem 0;">
    <h2>Warranty &amp; Service</h2>
    <p><strong>2-Year Warranty</strong> &#x2014; Lifetime Technical Support &#x2014; Free Worldwide Shipping</p>
    <p>Email: info@cncdisplay.com | Phone: +86-13686889647 | <a href="https://wa.me/8613686889647">WhatsApp</a></p>
</section>
<section style="text-align:center;padding:3rem;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border-radius:12px;margin:2rem 0;">
    <h2 style="color:#fff;">Ready to replace your CRT?</h2>
    <p>${price} &#x2014; In Stock &#x2014; Ships within 24 hours</p>
    <a href="/quote.html" style="display:inline-block;padding:14px 36px;background:#fff;color:#667eea;border-radius:8px;text-decoration:none;font-weight:700;">Request Quote &#x2192;</a>
</section>
</main>
<div style="background:#f8fafc;padding:1.5rem;border-radius:8px;margin:2rem 0;border:1px solid #e2e8f0;">
    <p style="font-weight:bold;color:#1e40af;margin:0 0 0.75rem 0;">&#x1F4D8; Related Resources</p>
    <ul style="margin:0;padding-left:1.2rem;">
        <li><a href="/guides/fanuc-crt-to-lcd-guide.html">FANUC CRT to LCD Upgrade Guide</a></li>
        <li><a href="/compatibility-matrix.html">Compatibility Matrix</a> &#x2014; 95+ models</li>
        <li><a href="/crt-dead-symptoms.html">CRT Failure Symptoms</a></li>
        <li><a href="/quote.html">Get a Quote</a></li>
    </ul>
</div>
<footer>
<div class="footer-content">
    <div class="footer-brand">
        <span class="footer-logo">Kongto Technology</span>
        <p>Industrial Video Display Solutions &#x2014; CNC CRT-to-LCD Retrofit, Video Signal Converters, Custom Industrial Displays</p>
    </div>
    <div class="footer-links">
        <a href="/posts/">Articles</a>
        <a href="/brands/FANUC.html">FANUC</a>
        <a href="/brands/Mitsubishi.html">Mitsubishi</a>
        <a href="/brands/Siemens.html">Siemens</a>
        <a href="/docs/">Downloads</a>
        <a href="/about.html">About Us</a>
    </div>
    <p class="footer-copy">&copy; 2013-2026 Kongto Technology | Shenzhen, China | sales@cncdisplay.com</p>
</div>
</footer>
</body>
</html>'''

def gen_html(slug, img1, title, desc, h1, price, pnum, sku, mpn, signal, size, compat, brand, brand_page, intro):
    t = (HEAD + TAIL).replace('{slug}', slug).replace('{img1}', img1)
    for k, v in [('title',title),('desc',desc),('h1',h1),('price',price),('pnum',pnum),
                 ('sku',sku),('mpn',mpn),('signal',signal),('size',size),
                 ('compat',compat),('brand',brand),('brand_page',brand_page),('intro',intro)]:
        t = t.replace(f'{{{k}}}', str(v))
    return t

for m in MODELS:
    slug = m['slug']
    img1 = os.path.basename(m['img_files'][0]) if m['img_files'] else 'logo_256.png'
    img1_path = f"{m['slug'].replace('fanuc-', '')}/{img1}" if os.path.exists(os.path.join(IMG_DST, m['slug'].replace('fanuc-', ''), img1)) else f"fanuc/{m['slug'].replace('fanuc-', '')}_{1}{os.path.splitext(img1)[1]}"

    # EN product page
    en_html = gen_html(slug, img1_path, m['title'], m['desc'], m['h1'],
                       m['price'], m['pnum'], m['sku'], m['mpn'], m['signal'],
                       m['size'], m['compat'], m['brand'], m['brand_page'], m['en_intro'])
    en_fp = os.path.join(SITE, 'products', f"{slug}.html")
    if not os.path.exists(en_fp):
        with open(en_fp, 'w', encoding='utf-8') as f:
            f.write(en_html)
        print(f'  CREATED: products/{slug}.html')
    else:
        print(f'  EXISTS: products/{slug}.html')

    # ZH product page
    zh_slug = slug
    zh_html = gen_html(zh_slug, img1_path, m['zh_title'], m['zh_desc'], m['zh_h1'],
                       m['price'], m['pnum'], m['sku'], m['mpn'], m['signal'],
                       m['size'], m['compat'], m['brand'], m['brand_page'], m['zh_intro'])
    zh_dir = os.path.join(SITE, 'zh', 'products')
    os.makedirs(zh_dir, exist_ok=True)
    zh_fp = os.path.join(zh_dir, f"{zh_slug}.html")
    if not os.path.exists(zh_fp):
        with open(zh_fp, 'w', encoding='utf-8') as f:
            f.write(zh_html)
        print(f'  CREATED: zh/products/{zh_slug}.html')
    else:
        print(f'  EXISTS: zh/products/{zh_slug}.html')

print('\n=== Creating EN + ZH articles ===')
# ====== GENERATE ARTICLES ======
for m in MODELS:
    slug = m['slug']
    img1 = os.path.basename(m['img_files'][0]) if m['img_files'] else 'logo_256.png'
    img1_path = f"fanuc/{m['slug'].replace('fanuc-', '')}_{1}{os.path.splitext(img1)[1]}"

    # EN article
    en_article = f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{m['h1']} - Complete CRT to LCD Upgrade Guide | Kongto</title>
<meta name="description" content="{m['desc']}">
<link rel="canonical" href="https://cncdisplay.com/posts/{slug}-guide.html">
<link rel="stylesheet" href="/css/style.css?v=7">
</head>
<body>
<header><nav>
    <a href="/" class="logo">Kongto Technology</a>
    <div class="nav-links">
        <a href="/">Home</a><a href="/compatibility-matrix.html">Compatibility</a>
        <a href="/products/">Products</a><a href="/posts/">Articles</a>
        <a href="/quote.html" style="color:#ff9800;font-weight:700;">Get Quote</a>
    </div>
</nav></header>
<main style="max-width:860px;margin:0 auto;padding:20px;">
<article>
<h1>{m['h1']} - Complete CRT to LCD Upgrade Guide</h1>
<p><strong>Model:</strong> {m['mpn']} | <strong>Compatibility:</strong> {m['compat']} | <strong>Reading time:</strong> 8 min</p>

<h2>Overview</h2>
<p>{m['en_intro']}</p>

<h2>Original CRT Display</h2>
<p>The original CRT display in the {m['mpn']} is a {m['size']} CRT unit with {m['signal']} interface. Key characteristics of the original CRT include:</p>
<ul>
    <li><strong>Resolution:</strong> 640x400 or 640x480 pixels</li>
    <li><strong>Brightness:</strong> Approximately 200 cd/m² (degrades over time)</li>
    <li><strong>Lifespan:</strong> 15,000-20,000 hours typical</li>
    <li><strong>Power:</strong> DC 24V, approximately 40-60W</li>
    <li><strong>Signal:</strong> TTL-level RGB via {m['signal']}</li>
</ul>

<h2>Common Failure Modes</h2>
<p>After 15-25 years of service, the {m['mpn']} CRT display will exhibit one or more of these failure modes:</p>
<table style="width:100%;border-collapse:collapse;margin:1rem 0;">
    <tr style="background:#1a1a2e;color:#fff;"><th style="padding:10px;border:1px solid #333;">Symptom</th><th style="padding:10px;border:1px solid #333;">Root Cause</th><th style="padding:10px;border:1px solid #333;">LCD Upgrade</th></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">Blank screen / no display</td><td style="padding:10px;border:1px solid #e2e8f0;">Flyback transformer failure (most common)</td><td style="padding:10px;border:1px solid #e2e8f0;">Permanent fix</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px;border:1px solid #e2e8f0;">Dim / unreadable display</td><td style="padding:10px;border:1px solid #e2e8f0;">CRT phosphor wear, electron gun aging</td><td style="padding:10px;border:1px solid #e2e8f0;">Permanent fix</td></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">Flickering / rolling image</td><td style="padding:10px;border:1px solid #e2e8f0;">Capacitor failure in sync circuits</td><td style="padding:10px;border:1px solid #e2e8f0;">Permanent fix</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px;border:1px solid #e2e8f0;">No power / dead unit</td><td style="padding:10px;border:1px solid #e2e8f0;">Internal power supply failure</td><td style="padding:10px;border:1px solid #e2e8f0;">Permanent fix</td></tr>
</table>

<h2>LCD Replacement Solution</h2>
<p>{m['en_detail']}</p>

<h2>Specification Comparison</h2>
<table style="width:100%;border-collapse:collapse;margin:1rem 0;">
    <tr style="background:#1a1a2e;color:#fff;"><th style="padding:10px;border:1px solid #333;">Spec</th><th style="padding:10px;border:1px solid #333;">Original CRT</th><th style="padding:10px;border:1px solid #333;">Kongto LCD</th></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">Display Type</td><td style="padding:10px;border:1px solid #e2e8f0;">CRT</td><td style="padding:10px;border:1px solid #e2e8f0;">TFT-LCD Industrial</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px;border:1px solid #e2e8f0;">Resolution</td><td style="padding:10px;border:1px solid #e2e8f0;">640x400</td><td style="padding:10px;border:1px solid #e2e8f0;">800x600</td></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">Brightness</td><td style="padding:10px;border:1px solid #e2e8f0;">~200 cd/m²</td><td style="padding:10px;border:1px solid #e2e8f0;">350-450 cd/m²</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px;border:1px solid #e2e8f0;">Lifespan</td><td style="padding:10px;border:1px solid #e2e8f0;">15,000 hrs</td><td style="padding:10px;border:1px solid #e2e8f0;">50,000+ hrs</td></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">Power Consumption</td><td style="padding:10px;border:1px solid #e2e8f0;">40-60W</td><td style="padding:10px;border:1px solid #e2e8f0;">~12W</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px;border:1px solid #e2e8f0;">Installation</td><td style="padding:10px;border:1px solid #e2e8f0;">N/A</td><td style="padding:10px;border:1px solid #e2e8f0;">15-30 min, plug-and-play</td></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">Warranty</td><td style="padding:10px;border:1px solid #e2e8f0;">Obsolete</td><td style="padding:10px;border:1px solid #e2e8f0;">2-Year Warranty</td></tr>
</table>

<h2>Installation Guide</h2>
<ol>
    <li><strong>Power off</strong> the CNC machine and lockout/tagout per safety procedures</li>
    <li><strong>Remove CRT housing:</strong> Unscrew the 4 mounting screws, disconnect signal and power cables</li>
    <li><strong>Mount LCD module:</strong> Position the LCD module in the same opening, secure with original screws</li>
    <li><strong>Connect cables:</strong> Plug the original signal cable into the LCD module port, reconnect DC 24V power</li>
    <li><strong>Power on and test:</strong> Restore power. The LCD will display automatically. Adjust brightness/contrast using OSD buttons if needed</li>
</ol>
<p><strong>Note:</strong> No CNC parameter changes, no wiring modifications, no special tools required. Total installation time: 15-30 minutes.</p>

<h2>Ordering Information</h2>
<p><strong>Price:</strong> ${m['price']} USD | <strong>Stock:</strong> In Stock | <strong>Warranty:</strong> 2 Years</p>
<p><strong>Contact:</strong> <a href="mailto:info@cncdisplay.com">info@cncdisplay.com</a> | +86-13686889647 | <a href="/quote.html">Request Quote</a></p>

<h2>Related Resources</h2>
<ul>
    <li><a href="/products/{slug}.html">Product Page: {m['h1']}</a></li>
    <li><a href="/guides/fanuc-crt-to-lcd-guide.html">FANUC CRT to LCD Upgrade Guide</a></li>
    <li><a href="/compatibility-matrix.html">CNC Display Compatibility Matrix</a></li>
    <li><a href="/crt-dead-symptoms.html">CRT Failure Symptom Checker</a></li>
</ul>
</article>
</main>
<footer><div class="footer-content">
    <p>&copy; 2013-2026 Kongto Technology | Shenzhen, China | <a href="mailto:info@cncdisplay.com">info@cncdisplay.com</a></p>
</div></footer>
</body>
</html>'''

    en_article_fp = os.path.join(SITE, 'posts', f'{slug}-guide.html')
    if not os.path.exists(en_article_fp):
        with open(en_article_fp, 'w', encoding='utf-8') as f:
            f.write(en_article)
        print(f'  CREATED: posts/{slug}-guide.html')
    else:
        print(f'  EXISTS: posts/{slug}-guide.html')

    # ZH article
    zh_article = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{m['zh_h1']} - CRT转LCD完整升级指南 | 江图科技</title>
<meta name="description" content="{m['zh_desc']}">
<link rel="canonical" href="https://cncdisplay.com/zh/posts/{slug}-guide.html">
<link rel="stylesheet" href="/css/style.css?v=7">
</head>
<body>
<header><nav>
    <a href="/" class="logo">江图科技</a>
    <div class="nav-links">
        <a href="/zh/">首页</a><a href="/zh/products/">产品</a><a href="/zh/posts/">文章</a>
        <a href="/zh/quote.html" style="color:#ff9800;font-weight:700;">获取报价</a>
    </div>
</nav></header>
<main style="max-width:860px;margin:0 auto;padding:20px;">
<article>
<h1>{m['zh_h1']} - CRT转LCD完整升级指南</h1>
<p><strong>型号：</strong>{m['mpn']} | <strong>兼容系统：</strong>{m['compat']} | <strong>阅读时间：</strong>8分钟</p>

<h2>概述</h2>
<p>{m['zh_intro']}</p>

<h2>原CRT显示器</h2>
<p>{m['mpn']} 原装CRT显示器为{m['size']} CRT单元，采用{m['signal']}接口。主要技术参数如下：</p>
<ul>
    <li><strong>分辨率：</strong>640×400 或 640×480 像素</li>
    <li><strong>亮度：</strong>约200 cd/m²（随时间衰减）</li>
    <li><strong>寿命：</strong>典型15,000-20,000小时</li>
    <li><strong>电源：</strong>DC 24V，功耗约40-60W</li>
    <li><strong>信号：</strong>TTL电平RGB信号，通过{m['signal']}传输</li>
</ul>

<h2>常见故障</h2>
<p>经过15-25年服役后，{m['mpn']} CRT显示器会出现以下一种或多种故障：</p>
<table style="width:100%;border-collapse:collapse;margin:1rem 0;">
    <tr style="background:#1a1a2e;color:#fff;"><th style="padding:10px;border:1px solid #333;">症状</th><th style="padding:10px;border:1px solid #333;">根本原因</th><th style="padding:10px;border:1px solid #333;">LCD升级效果</th></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">黑屏/无显示</td><td style="padding:10px;border:1px solid #e2e8f0;">高压包故障（最常见）</td><td style="padding:10px;border:1px solid #e2e8f0;">彻底解决</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px;border:1px solid #e2e8f0;">显示暗淡/看不清</td><td style="padding:10px;border:1px solid #e2e8f0;">CRT荧光粉老化、电子枪衰减</td><td style="padding:10px;border:1px solid #e2e8f0;">彻底解决</td></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">闪烁/抖动</td><td style="padding:10px;border:1px solid #e2e8f0;">同步电路电容老化</td><td style="padding:10px;border:1px solid #e2e8f0;">彻底解决</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px;border:1px solid #e2e8f0;">无电/不开机</td><td style="padding:10px;border:1px solid #e2e8f0;">内部电源故障</td><td style="padding:10px;border:1px solid #e2e8f0;">彻底解决</td></tr>
</table>

<h2>LCD替换方案</h2>
<p>{m['zh_detail']}</p>

<h2>技术参数对比</h2>
<table style="width:100%;border-collapse:collapse;margin:1rem 0;">
    <tr style="background:#1a1a2e;color:#fff;"><th style="padding:10px;border:1px solid #333;">参数</th><th style="padding:10px;border:1px solid #333;">原CRT</th><th style="padding:10px;border:1px solid #333;">江图LCD</th></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">显示类型</td><td style="padding:10px;border:1px solid #e2e8f0;">CRT</td><td style="padding:10px;border:1px solid #e2e8f0;">TFT-LCD工业级</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px;border:1px solid #e2e8f0;">分辨率</td><td style="padding:10px;border:1px solid #e2e8f0;">640×400</td><td style="padding:10px;border:1px solid #e2e8f0;">800×600</td></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">亮度</td><td style="padding:10px;border:1px solid #e2e8f0;">~200 cd/m²</td><td style="padding:10px;border:1px solid #e2e8f0;">350-450 cd/m²</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px;border:1px solid #e2e8f0;">寿命</td><td style="padding:10px;border:1px solid #e2e8f0;">15,000小时</td><td style="padding:10px;border:1px solid #e2e8f0;">50,000+小时</td></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">功耗</td><td style="padding:10px;border:1px solid #e2e8f0;">40-60W</td><td style="padding:10px;border:1px solid #e2e8f0;">~12W</td></tr>
    <tr style="background:#f8f9fa;"><td style="padding:10px;border:1px solid #e2e8f0;">安装</td><td style="padding:10px;border:1px solid #e2e8f0;">N/A</td><td style="padding:10px;border:1px solid #e2e8f0;">15-30分钟，即插即用</td></tr>
    <tr><td style="padding:10px;border:1px solid #e2e8f0;">质保</td><td style="padding:10px;border:1px solid #e2e8f0;">已停产</td><td style="padding:10px;border:1px solid #e2e8f0;">2年质保</td></tr>
</table>

<h2>安装步骤</h2>
<ol>
    <li><strong>断电</strong>：关闭数控机床电源并执行上锁挂牌安全程序</li>
    <li><strong>拆除CRT外壳</strong>：旋下4颗安装螺丝，断开信号线和电源线</li>
    <li><strong>安装LCD模组</strong>：将LCD模组放入原安装位，用原螺丝固定</li>
    <li><strong>连接线缆</strong>：将原信号线插入LCD模组接口，重新连接DC 24V电源</li>
    <li><strong>通电测试</strong>：恢复电源，LCD将自动显示画面。如有需要可使用OSD按键调节亮度和对比度</li>
</ol>
<p><strong>注意：</strong>无需修改CNC参数、无需改动线路、无需专用工具。安装总时间15-30分钟。</p>

<h2>联系方式</h2>
<p><strong>价格：</strong>${m['price']} USD | <strong>库存：</strong>现货 | <strong>质保：</strong>2年</p>
<p><strong>邮箱：</strong><a href="mailto:info@cncdisplay.com">info@cncdisplay.com</a> | <strong>电话：</strong>+86-13686889647 | <a href="/zh/quote.html">获取报价</a></p>

<h2>相关资源</h2>
<ul>
    <li><a href="/zh/products/{slug}.html">产品页：{m['zh_h1']}</a></li>
    <li><a href="/zh/guides/fanuc-crt-to-lcd-guide.html">FANUC CRT转LCD升级指南</a></li>
    <li><a href="/zh/compatibility-matrix.html">CNC显示器兼容性查询</a></li>
    <li><a href="/zh/crt-dead-symptoms.html">CRT故障症状排查</a></li>
</ul>
</article>
</main>
<footer><div class="footer-content">
    <p>&copy; 2013-2026 深圳市江图科技有限公司 | 深圳 | <a href="mailto:info@cncdisplay.com">info@cncdisplay.com</a></p>
</div></footer>
</body>
</html>'''

    zh_article_fp = os.path.join(SITE, 'zh', 'posts', f'{slug}-guide.html')
    os.makedirs(os.path.dirname(zh_article_fp), exist_ok=True)
    if not os.path.exists(zh_article_fp):
        with open(zh_article_fp, 'w', encoding='utf-8') as f:
            f.write(zh_article)
        print(f'  CREATED: zh/posts/{slug}-guide.html')
    else:
        print(f'  EXISTS: zh/posts/{slug}-guide.html')

print(f'\n=== Done! ===')
