import re

with open('en/compatibility-matrix.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix meta description
c = c.replace(
    '57 models covered. Plug-and-play with 18-month warranty.',
    '72+ models covered. Plug-and-play with 2-year warranty.')

# Fix stat chips: 6->7 brands, 57->72 models, 18-month->2-year
c = c.replace('🏭 6 Brands</span>', '🏭 7 Brands</span>')
c = c.replace('<span class="stat-chip">57 Models</span>', '<span class="stat-chip">72 Models</span>')
c = c.replace('🛡️ 18-Month Warranty', '🛡️ 2-Year Warranty')

# Fix brand filters - add Toshiba + Heidenhain
old_filters = '''<button type="button" class="brand-btn" onclick="filterBrand('Haas')">Haas</button>
        </div>'''
new_filters = '''<button type="button" class="brand-btn" onclick="filterBrand('Haas')">Haas</button>
            <button type="button" class="brand-btn" onclick="filterBrand('Toshiba')">Toshiba</button>
            <button type="button" class="brand-btn" onclick="filterBrand('Heidenhain')">Heidenhain</button>
        </div>'''
c = c.replace(old_filters, new_filters)

# Fix description text
c = c.replace('across 6 brands', 'across 7 brands')
c = c.replace('6 brands covered', '7 brands covered')
c = c.replace('across 6 brands.', 'across 7 brands.')

# Fix warranty in FAQ
c = c.replace('18-month warranty', '2-year warranty')
c = c.replace('18-Month Warranty', '2-Year Warranty')

# Fix FAQ JSON-LD
c = c.replace('57 models with exact', '72+ models with exact')

# Fix related resources
c = c.replace('FANUC/Mitsubishi/Siemens/Mazak/Okuma/Haas</li>',
    'FANUC/Mitsubishi/Siemens/Mazak/Okuma/Haas/Toshiba/Heidenhain</li>')

# Fix the COMPAT_DATA array - complete replacement
old_data_start = c.find('const COMPAT_DATA = [')
old_data_end = c.find('];', old_data_start) + 2

new_data = '''const COMPAT_DATA = [
    ["FANUC", "A61L-0001-0072", "9\" Monochrome CRT", "FANUC 6M/6T", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/fanuc-a61l-0001-0072-lcd-upgrade.html"],
    ["FANUC", "A61L-0001-0074", "14\" Color CRT", "FANUC 0/0i/16i/18i/21i", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/products/fanuc-a61l-0001-0074-lcd-upgrade.html"],
    ["FANUC", "A61L-0001-0076", "9\" Monochrome CRT", "FANUC 6/6B/6BII", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/fanuc-a61l-0001-0076-lcd-upgrade.html"],
    ["FANUC", "A61L-0001-0077", "12\" Color CRT", "FANUC 6 Series", "Kongto 10.4\" TFT-LCD", "1024x768", "Available", "/en/quote.html"],
    ["FANUC", "A61L-0001-0086", "8.4\" Monochrome CRT", "FANUC 0/0i", "Kongto 8.4\" TFT-LCD", "800x600", "Available", "/en/products/fanuc-a61l-0001-0086-lcd-upgrade.html"],
    ["FANUC", "A61L-0001-0090", "9\" Monochrome CRT", "FANUC 0-TC/0-MC", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/fanuc-a61l-0001-0090-lcd-upgrade.html"],
    ["FANUC", "A61L-0001-0092", "9\" Monochrome CRT", "FANUC 0/0i", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/fanuc-a61l-0001-0092-lcd-upgrade.html"],
    ["FANUC", "A61L-0001-0093", "9\" Monochrome CRT", "FANUC 0/0i/OM-D", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/fanuc-a61l-0001-0093-lcd-upgrade.html"],
    ["FANUC", "A61L-0001-0094", "14\" Color CRT", "FANUC 0i/16i/18i", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/products/fanuc-a61l-0001-0094-lcd-upgrade.html"],
    ["FANUC", "A61L-0001-0095", "9\" Color CRT", "FANUC 0i/16i", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/fanuc-a61l-0001-0095-lcd-upgrade.html"],
    ["FANUC", "A61L-0001-0096", "14\" Color CRT", "FANUC 0i/Power Mate", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/products/fanuc-a61l-0001-0096-lcd-upgrade.html"],
    ["FANUC", "A61L-0001-0097", "14\" Color CRT", "FANUC 0i/16i/18i", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/products/fanuc-a61l-0001-0097-lcd-upgrade.html"],
    ["FANUC", "MDT947B-1A", "9\" Monochrome CRT", "FANUC 0/0i", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/fanuc-a61l-0001-0092-lcd-upgrade.html"],
    ["FANUC", "D9MM-11A-0093", "9\" Monochrome CRT", "FANUC 0/0i", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/toshiba-d9mm-11a-lcd-upgrade.html"],
    ["Toshiba", "D9MM-11A", "9\" Monochrome CRT", "FANUC 0/0i (OEM)", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/toshiba-d9mm-11a-lcd-upgrade.html"],
    ["Toshiba", "D14CM-01A", "14\" Color CRT", "FANUC 16/18 (OEM)", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/products/toshiba-d14cm-01a-lcd-upgrade.html"],
    ["Toshiba", "KF-M7099H", "9\" Monochrome CRT", "FANUC 0/0i (OEM)", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/toshiba-d9mm-11a-lcd-upgrade.html"],
    ["Mitsubishi", "MDT962B", "9\" Monochrome CRT", "Mitsubishi M64/E60", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/mitsubishi-mdt962b-lcd-upgrade.html"],
    ["Mitsubishi", "MDT962B-1A", "9\" Monochrome CRT", "Mitsubishi M64/E60", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/mitsubishi-mdt962b-lcd-upgrade.html"],
    ["Mitsubishi", "MDT962B-4A", "9\" Monochrome CRT", "Mitsubishi M64/E60", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/mitsubishi-mdt962b-lcd-upgrade.html"],
    ["Mitsubishi", "BM09DF", "9\" Monochrome CRT", "Mitsubishi E60/E68", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/mitsubishi-bm09df-lcd-upgrade.html"],
    ["Mitsubishi", "FCUA-CT100", "9\" Monochrome CRT", "Mitsubishi M500/M520", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/mitsubishi-fcua-ct100-lcd-upgrade.html"],
    ["Mitsubishi", "MDT947B", "9\" Monochrome CRT", "Mitsubishi M3/M310", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/quote.html"],
    ["Mitsubishi", "MDT1283B", "12\" Monochrome CRT", "Mitsubishi M64/M3/M300", "Kongto 10.4\" TFT-LCD", "1024x768", "Available", "/en/products/mazak-mdt1283b-lcd-upgrade.html"],
    ["Mitsubishi", "BM14RTA", "14\" Color CRT", "Mitsubishi M700/M70", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/quote.html"],
    ["Siemens", "6FC3988-7FA20", "9\" Monochrome CRT", "SINUMERIK 810/820", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/siemens-6fc3988-7fa20-lcd-upgrade.html"],
    ["Siemens", "SM0901 / 579417TA", "9\" Monochrome CRT", "SINUMERIK 810M", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/products/siemens-sm0901-lcd-upgrade.html"],
    ["Siemens", "6FC5103-0AB01", "15\" Color CRT", "SINUMERIK 840D", "Kongto 15\" TFT-LCD", "1024x768", "Available", "/en/products/siemens-6fc5103-lcd-upgrade.html"],
    ["Siemens", "6FC3997-7FA20", "14\" Color CRT", "SINUMERIK 840C", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/quote.html"],
    ["Mazak", "DR5614", "14\" Color CRT", "Mazatrol T-32/T-PLUS", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/products/mazak-dr5614-lcd-upgrade.html"],
    ["Mazak", "C-5470NS", "14\" Color CRT", "Mazatrol M-32/M-PLUS", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/products/mazak-c5470ns-lcd-upgrade.html"],
    ["Mazak", "AIQA8DSP40", "14\" Color CRT", "Mazatrol T-32/640", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/products/mazak-aiqa8dsp40-lcd-upgrade.html"],
    ["Mazak", "CD1472-D1M", "14\" Color CRT", "Mazatrol T-Plus/M-Plus/Fusion 640", "Kongto 12.1\" TFT-LCD", "1024x768", "Available", "/en/products/mazak-cd1472-lcd-upgrade.html"],
    ["Mazak", "MDT-1283B-1A", "12\" Monochrome CRT", "Mazatrol T-2/T-3/M-2", "Kongto 10.4\" TFT-LCD", "800x600", "Available", "/en/products/mazak-mdt1283b-lcd-upgrade.html"],
    ["Mazak", "TR-120S9C", "9\" Monochrome CRT", "Mazatrol T-32/M-32 (Matsushita)", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/brands/Matsushita.html"],
    ["Okuma", "OSP 5000 CRT", "12\" Monochrome CRT", "OSP 5000", "Kongto 10.4\" TFT-LCD", "800x600", "Available", "/en/products/okuma-osp-crt-lcd-upgrade.html"],
    ["Okuma", "OSP 5020 CRT", "12\" Monochrome CRT", "OSP 5020", "Kongto 10.4\" TFT-LCD", "800x600", "Available", "/en/products/okuma-osp-crt-lcd-upgrade.html"],
    ["Okuma", "OSP 7000 CRT", "12\" Monochrome CRT", "OSP 7000", "Kongto 10.4\" TFT-LCD", "800x600", "Available", "/en/products/okuma-osp-crt-lcd-upgrade.html"],
    ["Haas", "VF Series 9\" CRT", "12\" Monochrome CRT", "Haas Classic Control", "Kongto 10.4\" TFT-LCD", "800x600", "Available", "/en/products/haas-28hm-nm4-lcd-upgrade.html"],
    ["Haas", "VF Series 12\" CRT", "12\" Monochrome CRT", "Haas Classic Control", "Kongto 10.4\" TFT-LCD", "800x600", "Available", "/en/products/haas-28hm-nm4-lcd-upgrade.html"],
    ["Haas", "SL Series CRT", "12\" Monochrome CRT", "Haas NGC", "Kongto 10.4\" TFT-LCD", "800x600", "Available", "/en/products/haas-28hm-nm4-lcd-upgrade.html"],
    ["Haas", "ST Series CRT", "12\" Monochrome CRT", "Haas NGC", "Kongto 10.4\" TFT-LCD", "800x600", "Available", "/en/products/haas-28hm-nm4-lcd-upgrade.html"],
    ["Heidenhain", "BE211", "9\" Monochrome CRT", "TNC 310/320", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/brands/Heidenhain.html"],
    ["Heidenhain", "BE411", "9\" Monochrome CRT", "TNC 410/415", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/brands/Heidenhain.html"],
    ["Heidenhain", "BE510", "9\" Color CRT", "TNC 425/430", "Kongto 8\" TFT-LCD", "800x600", "Available", "/en/brands/Heidenhain.html"]
];'''

c = c[:old_data_start] + new_data + c[old_data_end:]

# Fix the brandClass function to include new brands
c = c.replace(
    "return {'FANUC':'brand-fanuc','Mitsubishi':'brand-mitsubishi','Siemens':'brand-siemens','Mazak':'brand-mazak','Okuma':'brand-okuma','Haas':'brand-haas'}[b]||'';",
    "return {'FANUC':'brand-fanuc','Mitsubishi':'brand-mitsubishi','Siemens':'brand-siemens','Mazak':'brand-mazak','Okuma':'brand-okuma','Haas':'brand-haas','Toshiba':'brand-toshiba','Heidenhain':'brand-heidenhain'}[b]||'';")

# Add Toshiba/Heidenhain brand color CSS
old_css = '.brand-haas{background:#ca8a04}'
new_css = '.brand-haas{background:#ca8a04}.brand-toshiba{background:#8b0000}.brand-heidenhain{background:#2d5016}'
c = c.replace(old_css, new_css)

# Fix render count text
c = c.replace('COMPAT_DATA.length+\' compatible models across 6 brands\'',
    'COMPAT_DATA.length+\' compatible models across 8 brands\'')

with open('en/compatibility-matrix.html', 'w', encoding='utf-8') as f:
    f.write(c)

# Verify
data_entries = c.count('["FANUC"')
print(f"FANUC entries: {data_entries}")
total = c.count('"Available"')
print(f"Total models: ~{total}")
has_toshiba = '"Toshiba"' in c
has_heidenhain = '"Heidenhain"' in c
print(f"Toshiba brand: {has_toshiba}, Heidenhain brand: {has_heidenhain}")
print("en/compatibility-matrix.html updated")
