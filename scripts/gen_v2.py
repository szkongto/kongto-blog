# Quick script to regenerate EN product pages with corrected data
import os

MODELS = [
    ('A61L-0001-0072', '0072', '9-inch', '8', '255', 'Monochrome', ['FANUC Series 6M','FANUC Series 6T','FANUC 6-MA','FANUC 6-TA'], '640x400', 'FANUC 6M/6T series', ''),
    ('A61L-0001-0074', '0074', '14-inch', '12.1', '350', 'Color', ['FANUC 15T','FANUC 10','FANUC 10TE-F'], '640x480', 'FANUC 15T/10/10TE-F series', '/en/posts/article_20260503_FANUC_A61L_0001_0074_LCD.html'),
    ('A61L-0001-0076', '0076', '9-inch', '8', '255', 'Monochrome', ['FANUC Series 6','FANUC Series 6B','FANUC Series 6BII'], '640x400', 'FANUC 6/6B/6BII series', ''),
    ('A61L-0001-0086', '0086', '9-inch', '8', '255', 'Monochrome', ['FANUC Series 6','FANUC Series 10','FANUC Series 11','FANUC 0-M','FANUC 0-T'], '640x400', 'FANUC 6/10/11/0-M/0-T series', '/en/posts/article_20260503_FANUC_A61L_0001_0086_LCD.html'),
    ('A61L-0001-0090', '0090', '9-inch', '8', '350', 'Monochrome', ['FANUC 0T','FANUC 0M','FANUC Series 6'], '640x400', 'FANUC 0T/0M/Series 6', '/en/posts/article_20260503_FANUC_A61L_0001_0090_LCD.html'),
    ('A61L-0001-0092', '0092', '9-inch', '8', '255', 'Monochrome', ['FANUC Series 6M','FANUC Series 6T','FANUC 6-MA/B','FANUC 6-TA/B'], '640x400', 'FANUC 6M/6T series', '/en/posts/article_20260503_FANUC_A61L_0001_0092_LCD.html'),
    ('A61L-0001-0093', '0093', '9-inch', '8', '155', 'Monochrome', ['FANUC 0/0-Mate','FANUC 0i','FANUC 16i/18i/21i','FANUC OM-D'], '640x400', 'FANUC 0/0i/16i/18i/21i series', '/en/posts/article_20260503_FANUC_A61L_0001_0093_LCD.html'),
    ('A61L-0001-0094', '0094', '14-inch', '12.1', '350', 'Color', ['FANUC Series 6','FANUC Series 10','FANUC Series 11','FANUC Series 12'], '640x480', 'FANUC Series 6/10/11/12', '/en/posts/article_20260503_FANUC_A61L_0001_0094_LCD.html'),
    ('A61L-0001-0095', '0095', '9-inch', '8', '199', 'Color', ['FANUC 0/0-Mate','FANUC 0i','FANUC 15','FANUC 16/18/21'], '640x400', 'FANUC 0/0i/15/16/18/21 series', '/en/posts/article_20260503_FANUC_A61L_0001_0095_LCD.html'),
    ('A61L-0001-0096', '0096', '14-inch', '12.1', '350', 'Color', ['FANUC 15T','FANUC 16/18/20/21','Toshiba D14CM-01A','Tatung CD14JBS'], '640x480', 'FANUC 15T/16/18/20/21 series', '/en/posts/FANUC_A61L_0001_0096_LCD_CNC_Upgrade_Replacement.html'),
    ('A61L-0001-0097', '0097', '14-inch', '12.1', '350', 'Color', ['FANUC 0/0-Mate','FANUC 0i Mate'], '640x480', 'FANUC 0/0-Mate/0i Mate series', '/en/posts/FANUC_A61L_0001_0097_LCD_CNC_CRT_Replacement.html'),
]

DIR = 'd:/code/seo_deploy/en/products'
for part, sku, size, lcd, price, crt, compat, res, sys, guide in MODELS:
    slug = f"fanuc-{part.lower().replace(' ', '-')}-lcd-upgrade"
    compat_list = '\n'.join([f'<li>{c}</li>' for c in compat])

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FANUC {part} LCD Replacement | {size} CRT to LCD ${price} | Kongto Technology</title>
    <meta name="description" content="FANUC {part} {size} CRT to LCD replacement. ${price} plug-and-play, 800x600, 350-450cd/m2. Compatible with {sys}.">
    <link rel="canonical" href="https://cncdisplay.com/en/products/{slug}.html">
    <link rel="alternate" hreflang="en" href="https://cncdisplay.com/en/products/{slug}.html">
    <link rel="alternate" hreflang="zh-CN" href="https://cncdisplay.com/products/{slug}.html">
    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/en/products/{slug}.html">
    <meta property="og:type" content="product">
    <meta property="og:title" content="FANUC {part} LCD Replacement">
    <meta property="product:price:amount" content="{price}">
    <meta property="product:price:currency" content="USD">
    <meta name="twitter:card" content="summary_large_image">
    <script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "FANUC {part} LCD Replacement Display",
  "sku": "KONGTO-A61L-{sku}",
  "brand": {{ "@type": "Brand", "name": "KONGTO" }},
  "offers": {{
    "@type": "Offer", "price": "{price}.00", "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  }}
}}</script>
</head>
<body>
<h1>FANUC {part} LCD Replacement</h1>
<p>{size} {crt} CRT to {lcd}" TFT-LCD. Plug-and-play. ${price}. 2-year warranty.</p>
<table><tr><th>Spec</th><th>CRT</th><th>LCD</th></tr>
<tr><td>Size</td><td>{size}</td><td>{lcd}"</td></tr>
<tr><td>Type</td><td>{crt}</td><td>TFT-LCD</td></tr>
<tr><td>Resolution</td><td>{res}</td><td>800x600</td></tr></table>
<h2>Compatible Systems</h2><ul>{compat_list}</ul>
<p><strong>${price} - In Stock - Free Shipping - 2-Year Warranty</strong></p>
<p><a href="/en/quote.html">Get a Quote</a></p>
</body></html>'''

    filepath = os.path.join(DIR, slug + '.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(page)
    print(f'{slug}: {size} {crt} CRT -> {lcd}" LCD, ${price}')

print('Done')
