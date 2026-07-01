import re

modified = []

# ===== products/index.html =====
with open('products/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    '<div class="pcard"><a href="/products/mitsubishi-mdt962b-lcd-upgrade.html">MDT962B / BM09DF / FCUA-CT100</a></div>',
    '<div class="pcard"><a href="/products/mitsubishi-mdt962b-lcd-upgrade.html">MDT962B</a></div>\n<div class="pcard"><a href="/products/mitsubishi-bm09df-lcd-upgrade.html">BM09DF</a></div>\n<div class="pcard"><a href="/products/mitsubishi-fcua-ct100-lcd-upgrade.html">FCUA-CT100</a></div>')

c = c.replace(
    '<div class="pcard"><a href="/products/mazak-14-inch-crt-lcd-upgrade.html">DR5614 / C-5470NS / AIQA8DSP40</a></div>',
    '<div class="pcard"><a href="/products/mazak-dr5614-lcd-upgrade.html">DR5614</a></div>\n<div class="pcard"><a href="/products/mazak-c5470ns-lcd-upgrade.html">C-5470NS</a></div>\n<div class="pcard"><a href="/products/mazak-aiqa8dsp40-lcd-upgrade.html">AIQA8DSP40</a></div>')

c = c.replace(
    '<div class="pcard"><a href="/products/siemens-6fc3988-7fa20-lcd-upgrade.html">6FC3988-7FA20 / SM0901</a></div>',
    '<div class="pcard"><a href="/products/siemens-6fc3988-7fa20-lcd-upgrade.html">6FC3988-7FA20</a></div>\n<div class="pcard"><a href="/products/siemens-sm0901-lcd-upgrade.html">SM0901 (579417TA)</a></div>')

with open('products/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
modified.append('products/index.html')
print('products/index.html updated')

# ===== en/products/index.html =====
with open('en/products/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    'MDT962B / BM09DF / FCUA-CT100',
    'MDT962B')

# Add BM09DF and FCUA-CT100 after MDT962B in the grid
c = c.replace(
    '<div class="product-card">\n        <a href="/en/products/mitsubishi-mdt962b-lcd-upgrade.html" class="model">MDT962B</a>\n        </div>\n    <!-- Mitsubishi -->',
    '<div class="product-card">\n        <a href="/en/products/mitsubishi-mdt962b-lcd-upgrade.html" class="model">MDT962B</a>\n        </div>\n    <div class="product-card">\n        <a href="/en/products/mitsubishi-bm09df-lcd-upgrade.html" class="model">BM09DF</a>\n        </div>\n    <div class="product-card">\n        <a href="/en/products/mitsubishi-fcua-ct100-lcd-upgrade.html" class="model">FCUA-CT100</a>\n        </div>\n    <!-- Mitsubishi -->')

# Mazak
c = c.replace(
    'DR5614 / C-5470NS / AIQA8DSP40',
    'DR5614')
c = c.replace(
    '<div class="product-card">\n        <a href="/en/products/mazak-dr5614-lcd-upgrade.html" class="model">DR5614</a>\n        </div>\n    <div class="product-card">\n        <a href="/en/products/mazak-cd1472-lcd-upgrade.html" class="model">CD1472-D1M</a>',
    '<div class="product-card">\n        <a href="/en/products/mazak-dr5614-lcd-upgrade.html" class="model">DR5614</a>\n        </div>\n    <div class="product-card">\n        <a href="/en/products/mazak-c5470ns-lcd-upgrade.html" class="model">C-5470NS</a>\n        </div>\n    <div class="product-card">\n        <a href="/en/products/mazak-aiqa8dsp40-lcd-upgrade.html" class="model">AIQA8DSP40</a>\n        </div>\n    <div class="product-card">\n        <a href="/en/products/mazak-cd1472-lcd-upgrade.html" class="model">CD1472-D1M</a>')

# Siemens
c = c.replace(
    '6FC3988-7FA20 / SM0901 / 579417TA',
    '6FC3988-7FA20')
c = c.replace(
    '<div class="product-card">\n        <a href="/en/products/siemens-6fc3988-7fa20-lcd-upgrade.html" class="model">6FC3988-7FA20</a>\n        </div>\n    <div class="product-card">\n        <a href="/en/products/siemens-6fc5103-lcd-upgrade.html" class="model">6FC5103-0AB01</a>',
    '<div class="product-card">\n        <a href="/en/products/siemens-6fc3988-7fa20-lcd-upgrade.html" class="model">6FC3988-7FA20</a>\n        </div>\n    <div class="product-card">\n        <a href="/en/products/siemens-sm0901-lcd-upgrade.html" class="model">SM0901 (579417TA)</a>\n        </div>\n    <div class="product-card">\n        <a href="/en/products/siemens-6fc5103-lcd-upgrade.html" class="model">6FC5103-0AB01</a>')

with open('en/products/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
modified.append('en/products/index.html')
print('en/products/index.html updated')

# ===== quote.html =====
with open('quote.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('MDT962B / BM09DF / FCUA-CT100', 'MDT962B')

# Add BM09DF and FCUA-CT100 rows after Mitsubishi MDT962B
c = c.replace(
    '<td><a href="/products/mitsubishi-mdt962b-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td style="font-weight:700;">Mitsubishi</td>',
    '<td><a href="/products/mitsubishi-mdt962b-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td style="font-weight:700;">Mitsubishi</td>\n\t\t\t\t\t<td>BM09DF</td><td>9”单色CRT</td><td>1.5kg</td><td>$199</td>\n\t\t\t\t\t<td><a href="/products/mitsubishi-bm09df-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td style="font-weight:700;">Mitsubishi</td>\n\t\t\t\t\t<td>FCUA-CT100</td><td>9”单色CRT</td><td>1.5kg</td><td>$199</td>\n\t\t\t\t\t<td><a href="/products/mitsubishi-fcua-ct100-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td style="font-weight:700;">Mitsubishi</td>')

c = c.replace('DR5614 / C-5470NS / AIQA8DSP40', 'DR5614')

c = c.replace(
    '<td><a href="/products/mazak-dr5614-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td>CD1472-D1M</td>',
    '<td><a href="/products/mazak-dr5614-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td style="font-weight:700;">Mazak</td>\n\t\t\t\t\t<td>C-5470NS</td><td>14”彩色CRT</td><td>3.5kg</td><td>$355</td>\n\t\t\t\t\t<td><a href="/products/mazak-c5470ns-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td style="font-weight:700;">Mazak</td>\n\t\t\t\t\t<td>AIQA8DSP40</td><td>14”彩色CRT</td><td>3.5kg</td><td>$355</td>\n\t\t\t\t\t<td><a href="/products/mazak-aiqa8dsp40-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td>CD1472-D1M</td>')

c = c.replace('6FC3988-7FA20 / SM0901 / 579417TA', '6FC3988-7FA20')

c = c.replace(
    '<td><a href="/products/siemens-6fc3988-7fa20-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td style="font-weight:700;">Siemens</td>\n\t\t\t\t\t<td>6FC5103-0AB01</td>',
    '<td><a href="/products/siemens-6fc3988-7fa20-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td style="font-weight:700;">Siemens</td>\n\t\t\t\t\t<td>SM0901 (579417TA)</td><td>9”单色CRT</td><td>2.0kg</td><td>$380</td>\n\t\t\t\t\t<td><a href="/products/siemens-sm0901-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>\n\t\t\t\t<tr><td style="font-weight:700;">Siemens</td>\n\t\t\t\t\t<td>6FC5103-0AB01</td>')

with open('quote.html', 'w', encoding='utf-8') as f:
    f.write(c)
modified.append('quote.html')
print('quote.html updated')

# ===== en/quote.html =====
with open('en/quote.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('MDT962B / BM09DF / FCUA-CT100', 'MDT962B')
c = c.replace(
    'View Details →</a></td></tr>\n\t                <tr><td rowspan="3" style="font-weight:700;vertical-align:middle;">Mazak</td>',
    'View Details →</a></td></tr>\n\t                <tr><td style="font-weight:700;">Mitsubishi</td>\n\t                    <td>BM09DF</td><td>9" Mono CRT</td><td>1.5kg</td><td>$199</td>\n\t                    <td><a href="/en/products/mitsubishi-bm09df-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">View Details →</a></td></tr>\n\t                <tr><td style="font-weight:700;">Mitsubishi</td>\n\t                    <td>FCUA-CT100</td><td>9" Mono CRT</td><td>1.5kg</td><td>$199</td>\n\t                    <td><a href="/en/products/mitsubishi-fcua-ct100-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">View Details →</a></td></tr>\n\t                <tr><td rowspan="3" style="font-weight:700;vertical-align:middle;">Mazak</td>')

c = c.replace('DR5614 / C-5470NS / AIQA8DSP40', 'DR5614')
c = c.replace(
    'View Details →</a></td></tr>\n\t                <tr><td>CD1472-D1M</td>',
    'View Details →</a></td></tr>\n\t                <tr><td style="font-weight:700;">Mazak</td>\n\t                    <td>C-5470NS</td><td>14" Color CRT</td><td>3.5kg</td><td>$355</td>\n\t                    <td><a href="/en/products/mazak-c5470ns-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">View Details →</a></td></tr>\n\t                <tr><td style="font-weight:700;">Mazak</td>\n\t                    <td>AIQA8DSP40</td><td>14" Color CRT</td><td>3.5kg</td><td>$355</td>\n\t                    <td><a href="/en/products/mazak-aiqa8dsp40-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">View Details →</a></td></tr>\n\t                <tr><td>CD1472-D1M</td>')

c = c.replace('6FC3988-7FA20 / SM0901 / 579417TA', '6FC3988-7FA20')
c = c.replace(
    'View Details →</a></td></tr>\n\t                <tr><td style="font-weight:700;">Siemens</td>\n\t                    <td>6FC5103-0AB01</td>',
    'View Details →</a></td></tr>\n\t                <tr><td style="font-weight:700;">Siemens</td>\n\t                    <td>SM0901 (579417TA)</td><td>9" Mono CRT</td><td>2.0kg</td><td>$380</td>\n\t                    <td><a href="/en/products/siemens-sm0901-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">View Details →</a></td></tr>\n\t                <tr><td style="font-weight:700;">Siemens</td>\n\t                    <td>6FC5103-0AB01</td>')

with open('en/quote.html', 'w', encoding='utf-8') as f:
    f.write(c)
modified.append('en/quote.html')
print('en/quote.html updated')

print(f'\nModified {len(modified)} files:')
for f in modified:
    print(f'  {f}')
