import re, os

# Fix Product schema JSON error in EN brand page
path = 'd:/code/seo_deploy/en/brands/FANUC.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix leading comma in Product schema
content = content.replace(
    ',"hasMerchantReturnPolicy":{"@type":"MerchantReturnPolicy","applicableCountry":"CN","returnPolicyCategory":"https://schema.org/MerchantReturnFiniteReturnWindow","merchantReturnDays":7,"returnMethod":"https://schema.org/ReturnByMail","returnFees":"https://schema.org/FreeReturn"}\n        "availability"',
    '"hasMerchantReturnPolicy": {"@type":"MerchantReturnPolicy","applicableCountry":"CN","returnPolicyCategory":"https://schema.org/MerchantReturnFiniteReturnWindow","merchantReturnDays":7,"returnMethod":"https://schema.org/ReturnByMail","returnFees":"https://schema.org/FreeReturn"},\n    "availability"'
)

# Add product grid between FAQ section and articles section
product_grid = '''        <section style="margin:2rem 0;">
            <h2>FANUC LCD Upgrade Products (Plug-and-Play, $199-$299)</h2>
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem;">
                <a href="/en/products/fanuc-a61l-0001-0092-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0092 LCD</strong><br><small>$199 - FANUC 6M/6T Series</small></a>
                <a href="/en/products/fanuc-a61l-0001-0093-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0093 LCD</strong><br><small>$199 - FANUC 0/0i/16i/18i/21i</small></a>
                <a href="/en/products/fanuc-a61l-0001-0094-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0094 LCD</strong><br><small>$199 - FANUC 6/10/11/12 Series</small></a>
                <a href="/en/products/fanuc-a61l-0001-0095-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0095 LCD</strong><br><small>$199 - FANUC 0/0i/15/16/18/21</small></a>
                <a href="/en/products/fanuc-a61l-0001-0096-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0096 LCD</strong><br><small>$299 - 12"/FANUC 15T/16/18/20/21</small></a>
                <a href="/en/products/fanuc-a61l-0001-0097-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0097 LCD</strong><br><small>$199 - FANUC 0/0-Mate</small></a>
                <a href="/en/products/fanuc-a61l-0001-0072-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0072 LCD</strong><br><small>$199 - FANUC 6M/6T Series</small></a>
                <a href="/en/products/fanuc-a61l-0001-0074-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0074 LCD</strong><br><small>$299 - 14"/FANUC 15T/10 Series</small></a>
                <a href="/en/products/fanuc-a61l-0001-0076-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0076 LCD</strong><br><small>$199 - FANUC 6/6B/6BII Series</small></a>
                <a href="/en/products/fanuc-a61l-0001-0086-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0086 LCD</strong><br><small>$199 - 8.4"/FANUC 6/10/11/0-M</small></a>
                <a href="/en/products/fanuc-a61l-0001-0090-lcd-upgrade.html" style="display:block;padding:1rem;background:#fff;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:#333;">
                    <strong>A61L-0001-0090 LCD</strong><br><small>$199 - FANUC 0T/0M/6 Series</small></a>
            </div>
        </section>

        <section class="brand-articles">
            <h2>All FANUC Solutions</h2>

            <div class="brand-article-grid">'''

content = content.replace(
    '        <section class="brand-articles">\n\n            <h2>All FANUC Solutions</h2>\n\n            <div class="brand-article-grid">',
    product_grid
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('EN FANUC brand page: updated with product grid + schema fix')

# Update sitemap
sitemap_path = 'd:/code/seo_deploy/sitemap.xml'
with open(sitemap_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_urls = []
for m in ['0092','0094','0095','0096','0097','0072','0074','0076','0086','0090']:
    new_urls.append(f'<url><loc>https://cncdisplay.com/en/products/fanuc-a61l-0001-{m}-lcd-upgrade.html</loc><lastmod>2026-06-27</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>')
    new_urls.append(f'<url><loc>https://cncdisplay.com/products/fanuc-a61l-0001-{m}-lcd-upgrade.html</loc><lastmod>2026-06-27</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>')

content = content.replace('</urlset>', '\n'.join(new_urls) + '\n</urlset>')

with open(sitemap_path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Sitemap: +{len(new_urls)} new URLs')

print('\nDone')
