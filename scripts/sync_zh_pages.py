import re

# ======= products/index.html =======
with open('products/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

new_main = '''<main style="max-width:1200px;margin:0 auto;padding:20px;">
<h1>CNC显示器产品中心</h1>
<p style="color:#475569;margin-bottom:0.5rem;">工厂现货直发CRT转LCD替换模块 — 2年质保，48小时发货。</p>
<p style="color:#475569;margin-top:0;"><a href="/wholesale.html">批量采购与OEM定制</a> — 阶梯价格，欢迎来电。</p>

<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin:1.5rem 0;">
<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:0.8rem 1rem;"><a href="/products/no-display.html" style="font-weight:600;color:#c2410c;text-decoration:none;">黑屏无显示</a> — 故障诊断</div>
<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:0.8rem 1rem;"><a href="/products/flickering-screen.html" style="font-weight:600;color:#c2410c;text-decoration:none;">屏幕闪烁</a> — 原因与修复</div>
<div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:0.8rem 1rem;"><a href="/products/image-retention.html" style="font-weight:600;color:#c2410c;text-decoration:none;">残影烧屏</a> — 解决方案</div>
</div>

<style>
.brand-sec{margin-bottom:2.5rem;}
.brand-sec h2{border-bottom:3px solid;padding-bottom:8px;margin-bottom:1rem;font-size:1.3rem;}
.brand-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;}
.pcard{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:0.6rem 1rem;transition:box-shadow .2s;}
.pcard:hover{box-shadow:0 2px 8px rgba(0,0,0,0.1);}
.pcard a{font-weight:600;font-size:0.9rem;color:#1e40af;text-decoration:none;display:block;}
.pcard a:hover{text-decoration:underline;}
.bfanuc h2{border-color:#007bff;} .bhaas h2{border-color:#cc0000;}
.bmazak h2{border-color:#ff6600;} .bmitsubishi h2{border-color:#e60012;}
.bokuma h2{border-color:#003399;} .bsiemens h2{border-color:#009999;}
.btoshiba h2{border-color:#8b0000;}
@media(max-width:640px){.brand-grid{grid-template-columns:1fr;}}
</style>

<section class="brand-sec bfanuc"><h2>FANUC</h2>
<div class="brand-grid">
<div class="pcard"><a href="/products/fanuc-a61l-0001-0072-lcd-upgrade.html">A61L-0001-0072</a></div>
<div class="pcard"><a href="/products/fanuc-a61l-0001-0074-lcd-upgrade.html">A61L-0001-0074</a></div>
<div class="pcard"><a href="/products/fanuc-a61l-0001-0076-lcd-upgrade.html">A61L-0001-0076</a></div>
<div class="pcard"><a href="/products/fanuc-a61l-0001-0086-lcd-upgrade.html">A61L-0001-0086</a></div>
<div class="pcard"><a href="/products/fanuc-a61l-0001-0090-lcd-upgrade.html">A61L-0001-0090</a></div>
<div class="pcard"><a href="/products/fanuc-a61l-0001-0092-lcd-upgrade.html">A61L-0001-0092</a></div>
<div class="pcard"><a href="/products/fanuc-a61l-0001-0093-lcd-upgrade.html">A61L-0001-0093</a></div>
<div class="pcard"><a href="/products/fanuc-a61l-0001-0094-lcd-upgrade.html">A61L-0001-0094</a></div>
<div class="pcard"><a href="/products/fanuc-a61l-0001-0095-lcd-upgrade.html">A61L-0001-0095</a></div>
<div class="pcard"><a href="/products/fanuc-a61l-0001-0096-lcd-upgrade.html">A61L-0001-0096</a></div>
<div class="pcard"><a href="/products/fanuc-a61l-0001-0097-lcd-upgrade.html">A61L-0001-0097</a></div>
</div></section>

<section class="brand-sec bmitsubishi"><h2>Mitsubishi 三菱</h2>
<div class="brand-grid">
<div class="pcard"><a href="/products/mitsubishi-mdt962b-lcd-upgrade.html">MDT962B / BM09DF / FCUA-CT100</a></div>
</div></section>

<section class="brand-sec bmazak"><h2>Mazak 马扎克</h2>
<div class="brand-grid">
<div class="pcard"><a href="/products/mazak-14-inch-crt-lcd-upgrade.html">DR5614 / C-5470NS / AIQA8DSP40</a></div>
<div class="pcard"><a href="/products/mazak-cd1472-lcd-upgrade.html">CD1472-D1M</a></div>
<div class="pcard"><a href="/products/mazak-mdt1283b-lcd-upgrade.html">MDT1283B-1A</a></div>
</div></section>

<section class="brand-sec bsiemens"><h2>Siemens 西门子</h2>
<div class="brand-grid">
<div class="pcard"><a href="/products/siemens-6fc3988-7fa20-lcd-upgrade.html">6FC3988-7FA20 / SM0901</a></div>
<div class="pcard"><a href="/products/siemens-6fc5103-lcd-upgrade.html">6FC5103-0AB01</a></div>
</div></section>

<section class="brand-sec bokuma"><h2>Okuma 大隈</h2>
<div class="brand-grid">
<div class="pcard"><a href="/products/okuma-osp-crt-lcd-upgrade.html">OSP CRT (5000/5020/7000)</a></div>
</div></section>

<section class="brand-sec bhaas"><h2>Haas 哈斯</h2>
<div class="brand-grid">
<div class="pcard"><a href="/products/haas-28hm-nm4-lcd-upgrade.html">28HM-NM4 / 93-5220C</a></div>
</div></section>

<section class="brand-sec btoshiba"><h2>Toshiba 东芝 <span style="font-size:0.85rem;font-weight:400;color:#888;">(FANUC代工)</span></h2>
<div class="brand-grid">
<div class="pcard"><a href="/products/toshiba-d9mm-11a-lcd-upgrade.html">D9MM-11A</a></div>
<div class="pcard"><a href="/products/toshiba-d14cm-01a-lcd-upgrade.html">D14CM-01A</a></div>
</div></section>

<div style="background:#f0f7ff;padding:2rem;border-radius:12px;margin:2rem 0;text-align:center;">
<h2 style="margin-top:0;">不确定选哪个型号？</h2>
<p>查看 <a href="/compatibility-matrix.html">95+型号兼容性对照表</a>，或发CRT标签照片到 <strong>info@cncdisplay.com</strong>，24小时内确认兼容方案。</p>
<a href="/quote.html" style="display:inline-block;padding:12px 28px;background:#2563eb;color:#fff;border-radius:8px;font-weight:600;text-decoration:none;margin-top:0.5rem;">获取报价</a>
</div>
</main>'''

old_main = re.search(r'<main[^>]*>.*?</main>', c, re.DOTALL)
if old_main:
    c = c[:old_main.start()] + new_main + c[old_main.end():]
    with open('products/index.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print('products/index.html updated')
else:
    print('ERROR: no <main> in products/index.html')

# ======= quote.html =======
with open('quote.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace old table with Chinese version
old_start = c.find('<table class="price-table">')
if old_start == -1:
    print('ERROR: no price-table in quote.html')
else:
    old_end = c.find('</table>', old_start)

    zh_table = '''\t        <table class="price-table">
\t            <thead>
\t                <tr>
\t                    <th>品牌</th>
\t                    <th>型号</th>
\t                    <th>CRT类型</th>
\t                    <th>重量</th>
\t                    <th>价格</th>
\t                    <th>详情</th>
\t                </tr>
\t            </thead>
\t            <tbody>
\t                <tr><td rowspan="11" style="font-weight:700;vertical-align:middle;">FANUC</td>
\t                    <td>A61L-0001-0072</td><td>9”单色CRT</td><td>1.5kg</td><td>$255</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0072-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>A61L-0001-0074</td><td>14”彩色CRT</td><td>3.5kg</td><td>$299</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0074-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>A61L-0001-0076</td><td>9”单色CRT</td><td>1.5kg</td><td>$199</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0076-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>A61L-0001-0086</td><td>8.4”单色CRT</td><td>1.5kg</td><td>$199</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0086-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>A61L-0001-0090</td><td>9”单色CRT</td><td>1.5kg</td><td>$199</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0090-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>A61L-0001-0092</td><td>9”单色CRT</td><td>1.5kg</td><td>$199</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0092-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>A61L-0001-0093</td><td>9”单色CRT</td><td>1.5kg</td><td>$155</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0093-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>A61L-0001-0094</td><td>14”彩色CRT</td><td>3.5kg</td><td>$199</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0094-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>A61L-0001-0095</td><td>9”彩色CRT</td><td>1.5kg</td><td>$199</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0095-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>A61L-0001-0096</td><td>14”彩色CRT</td><td>3.5kg</td><td>$299</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0096-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>A61L-0001-0097</td><td>14”彩色CRT</td><td>3.5kg</td><td>$199</td>
\t                    <td><a href="/products/fanuc-a61l-0001-0097-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td style="font-weight:700;">Mitsubishi</td>
\t                    <td>MDT962B / BM09DF / FCUA-CT100</td><td>9”单色CRT</td><td>1.5kg</td><td>$199</td>
\t                    <td><a href="/products/mitsubishi-mdt962b-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td rowspan="3" style="font-weight:700;vertical-align:middle;">Mazak</td>
\t                    <td>DR5614 / C-5470NS / AIQA8DSP40</td><td>14”彩色CRT</td><td>3.5kg</td><td>$355</td>
\t                    <td><a href="/products/mazak-14-inch-crt-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>CD1472-D1M</td><td>14”彩色CRT</td><td>3.5kg</td><td>$355</td>
\t                    <td><a href="/products/mazak-cd1472-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>MDT1283B-1A</td><td>12”单色CRT</td><td>2.5kg</td><td>$355</td>
\t                    <td><a href="/products/mazak-mdt1283b-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td colspan="6" style="background:#f8f9fa;padding:0.3rem;"></td></tr>
\t                <tr><td style="font-weight:700;">Siemens</td>
\t                    <td>6FC3988-7FA20 / SM0901 / 579417TA</td><td>9”单色CRT</td><td>2.0kg</td><td>$380</td>
\t                    <td><a href="/products/siemens-6fc3988-7fa20-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td style="font-weight:700;">Siemens</td>
\t                    <td>6FC5103-0AB01</td><td>15”彩色CRT</td><td>3.5kg</td><td>$449</td>
\t                    <td><a href="/products/siemens-6fc5103-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td style="font-weight:700;">Okuma</td>
\t                    <td>OSP CRT (5000/5020/7000)</td><td>12”单色CRT</td><td>3.0kg</td><td>$430</td>
\t                    <td><a href="/products/okuma-osp-crt-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td style="font-weight:700;">Haas</td>
\t                    <td>28HM-NM4 / 93-5220C</td><td>12”单色CRT</td><td>2.5kg</td><td>$399</td>
\t                    <td><a href="/products/haas-28hm-nm4-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td colspan="6" style="background:#f8f9fa;padding:0.3rem;"></td></tr>
\t                <tr><td rowspan="2" style="font-weight:700;vertical-align:middle;">Toshiba</td>
\t                    <td>D9MM-11A <span style="color:#888;font-size:0.85rem;">(FANUC代工)</span></td><td>9”单色CRT</td><td>1.5kg</td><td>$155</td>
\t                    <td><a href="/products/toshiba-d9mm-11a-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t                <tr><td>D14CM-01A <span style="color:#888;font-size:0.85rem;">(FANUC代工)</span></td><td>14”彩色CRT</td><td>3.5kg</td><td>$350</td>
\t                    <td><a href="/products/toshiba-d14cm-01a-lcd-upgrade.html" style="color:#1a73e8;font-weight:600;">查看详情 →</a></td></tr>
\t            </tbody>
\t        </table>'''

    c = c[:old_start] + zh_table + c[old_end + 8:]
    c = c.replace('1年质保', '2年质保')  # 1年质保 -> 2年质保

    with open('quote.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print('quote.html updated')

print('Both ZH pages synced')
