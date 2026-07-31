#!/usr/bin/env python3
"""Generate zh system hub pages (guides/by-system/ zh versions).
Adds hreflang zh-CN backlinks to EN hub pages too.
"""

import os, json, re

BASE = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE, 'zh', 'guides', 'by-system')

with open(os.path.join(BASE, 'data', 'cnc-crt-to-lcd-compatibility.json'), encoding='utf-8') as f:
    COMPAT = json.load(f)

def models_for(pattern):
    out = []
    for item in COMPAT:
        if pattern.lower() in item.get('cnc_system', '').lower():
            out.append((item['crt_model'], item['url'], item.get('size_type', '')))
    return out

def table_rows(models):
    by_url = {}
    for crt, url, size in models:
        if url not in by_url:
            by_url[url] = {'models': [], 'size': size}
        by_url[url]['models'].append(crt)
    rows = []
    for url, info in by_url.items():
        label = ' / '.join(info['models'])
        size_cn = info['size'].replace('Monochrome', '单色').replace('Color', '彩色').replace('CRT', '')
        rows.append(f'<tr><td><a href="{url}">{label}</a></td><td>{size_cn}</td></tr>')
    return '\n'.join(rows)

NAV = """<header><nav>
<a href="/zh/" class="logo">江图科技 Kongto Technology</a>
<div class="nav-links">
<a href="/zh/">首页</a><a href="/zh/compatibility-matrix.html">兼容查询</a>
<a href="/zh/products/">产品</a><a href="/zh/posts/">文章</a>
<a href="/zh/case-studies.html">案例</a><a href="/zh/docs/">资料</a>
<a href="/zh/about.html">关于</a>
<a href="/zh/quote.html" style="color:#ff9800;font-weight:700;">获取报价</a>
</div>
</nav></header>"""

CSS = """<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.6;color:#1d1d1f;background:#fff;margin:0}
.guide-page{max-width:1000px;margin:2rem auto;padding:0 1.5rem}
.model-table{width:100%;border-collapse:collapse;margin:1.5rem 0}
.model-table th{background:#1a1a2e;color:#fff;padding:10px 12px;text-align:left}
.model-table td{padding:10px 12px;border:1px solid #e2e8f0}
.model-table tr:nth-child(even){background:#f8fafc}
h1{font-size:1.9rem;margin-bottom:0.75rem}
h2{font-size:1.35rem;margin-top:2rem;color:#1a1a2e}
.answer-first{font-size:1.1rem;color:#555;line-height:1.7}
</style>"""

def breadcrumb_ld(name):
    return ('    <script type="application/ld+json">\n'
            '    {\n      "@context": "https://schema.org",\n      "@type": "BreadcrumbList",\n      "itemListElement": [\n'
            f'        {{"@type":"ListItem","position":1,"name":"首页","item":"https://cncdisplay.com/zh/"}},\n'
            f'        {{"@type":"ListItem","position":2,"name":{json.dumps(name, ensure_ascii=False)},"item":""}}\n'
            '      ]\n    }\n    </script>')

def faq_ld(faqs):
    entries = []
    for q, a in faqs:
        entries.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    obj = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': entries}
    return '    <script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + '\n    </script>'

PAGES = [
    {
        'slug': 'fanuc-0i.html',
        'en_slug': 'fanuc-0i.html',
        'title': 'FANUC 0i 系列 CRT转LCD升级指南 | 江图科技',
        'meta': 'FANUC 0/0i 系列数控显示器 CRT转LCD升级方案。A61L-0001-0093、0092、0094、0095、0097 等型号即插即用，2年质保。',
        'h1': 'FANUC 0i 系列 CRT 转 LCD 升级指南',
        'intro': 'FANUC 0i 和 0 系列系统使用 9 英寸单色、14 英寸彩色 CRT 显示器。我们的 LCD 升级模组即插即用——同样采用 20 针 Honda 接口，无需改参数。兼容型号：A61L-0001-0093、0092、0094、0095、0097 及 D9MM-11A 等效型号。',
        'sys_cn': 'FANUC 0i',
        'pattern': '0i',
        'faqs': [
            ('如何将 FANUC 0i 显示器从 CRT 升级为 LCD？', '先关闭机床电源，拔下原有 CRT（多数型号为 20 针 Honda MR-20M 接口），接上 LCD 模组，通电即可。无需改任何系统参数或重新接线，安装约 10-15 分钟。'),
            ('覆盖哪些 FANUC 0i CRT 型号？', 'A61L-0001-0093、0092、0094、0095、0097、MDT947B-1A，以及东芝 D9MM-11A（0093 的 OEM 等效型号）。'),
            ('LCD 模组支持 FANUC 0i-C 或 0i-D 吗？', '支持。0093、0092 模组广泛用于 FANUC 0、0i-C、0i-D、16i、18i、21i 系统。确认你的 CRT 型号和接口类型即可完全兼容。'),
        ],
    },
    {
        'slug': 'fanuc-16i-18i-21i.html',
        'en_slug': 'fanuc-16i-18i-21i.html',
        'title': 'FANUC 16i/18i/21i CRT转LCD升级指南 | 江图科技',
        'meta': 'FANUC 16i/18i/21i 数控显示器 CRT转LCD升级方案。A61L-0001-0094、0095、0097 14英寸彩色 LCD 模组，2年质保。',
        'h1': 'FANUC 16i/18i/21i CRT 转 LCD 升级指南',
        'intro': 'FANUC 16i、18i、21i 系统使用 14 英寸彩色 CRT 显示器。我们的 LCD 模组适配原机框和接口——无需改参数、无需重新接线。兼容型号：A61L-0001-0094、0095、0097。',
        'sys_cn': 'FANUC 16i/18i/21i',
        'pattern': '16i',
        'faqs': [
            ('如何升级 FANUC 16i/18i/21i CRT 显示器？', '关机断电，拔下彩色 CRT，用原接口连接 LCD 模组，通电即可。安装约 10-15 分钟，无需改参数。'),
            ('覆盖哪些 CRT 型号？', 'A61L-0001-0094（14 英寸彩色）、A61L-0001-0095（9 英寸彩色）、A61L-0001-0097（14 英寸彩色）。0094 是 16i/18i 系统最常见的 14 英寸彩色模组。'),
            ('图像质量会比旧彩色 CRT 更好吗？', '会。LCD 模组分辨率更高、无闪烁、无残影，寿命 5 万小时以上，同时消除高压行变故障隐患。'),
        ],
    },
    {
        'slug': 'mitsubishi-e60.html',
        'en_slug': 'mitsubishi-e60.html',
        'title': '三菱 E60 CRT转LCD升级指南 | 江图科技',
        'meta': '三菱 E60/E68 数控显示器 CRT转LCD升级方案。MDT962B、BM09DF 9英寸单色 LCD 模组，2年质保。',
        'h1': '三菱 E60 CRT 转 LCD 升级指南',
        'intro': '三菱 E60/E68 系统使用 9 英寸单色 CRT 显示器。我们的 LCD 模组即插即用——采用原机接口。兼容型号：MDT962B 和 BM09DF。',
        'sys_cn': '三菱 E60',
        'pattern': 'E60',
        'faqs': [
            ('如何将三菱 E60 显示器升级为 LCD？', '关机断电，拔下 MDT962B 或 BM09DF CRT，用原接口连接 LCD 模组，通电即可。无需改参数。'),
            ('覆盖哪些三菱 E60 CRT 型号？', 'MDT962B（含 -1A、-4A 变体）和 BM09DF，均为 E60/E68 系统使用的 9 英寸单色显示器。'),
            ('支持国际运输吗？', '支持。通过 DHL/FedEx 全球发货——美国 5-7 天、欧洲 5-10 天、亚洲 3-5 天。每个模组含 2 年质保和终身技术支持。'),
        ],
    },
    {
        'slug': 'mitsubishi-m64.html',
        'en_slug': 'mitsubishi-m64.html',
        'title': '三菱 M64 CRT转LCD升级指南 | 江图科技',
        'meta': '三菱 M64 数控显示器 CRT转LCD升级方案。MDT962B、MDT1283B 模组，2年质保。',
        'h1': '三菱 M64 CRT 转 LCD 升级指南',
        'intro': '三菱 M64 系统使用 9 英寸和 12 英寸单色 CRT 显示器。我们的 LCD 模组即插即用——采用原机接口。兼容型号：MDT962B（9 英寸）和 MDT1283B（12 英寸）。',
        'sys_cn': '三菱 M64',
        'pattern': 'M64',
        'faqs': [
            ('如何将三菱 M64 显示器升级为 LCD？', '关机断电，拔下 CRT，用原接口连接 LCD 模组，通电即可。安装约 10-15 分钟，无需改参数。'),
            ('覆盖哪些三菱 M64 CRT 型号？', 'MDT962B（9 英寸单色，也用于 M3/M300）和 MDT1283B（12 英寸单色，与马扎克系统共用）。'),
            ('MDT1283B 模组和马扎克的一样吗？', '一样。MDT1283B 为三菱 M64 与马扎克 Mazatrol 系统共用，一个模组覆盖两者。'),
        ],
    },
    {
        'slug': 'siemens-810-820.html',
        'en_slug': 'siemens-810-820.html',
        'title': '西门子 SINUMERIK 810/820 CRT转LCD升级指南 | 江图科技',
        'meta': '西门子 SINUMERIK 810/820/810M 数控显示器 CRT转LCD升级方案。6FC3988-7FA20、SM0901 模组，2年质保。',
        'h1': '西门子 SINUMERIK 810/820 CRT 转 LCD 升级指南',
        'intro': '西门子 SINUMERIK 810/820 系统使用 9 英寸单色 CRT 显示器。我们的 LCD 模组即插即用——采用原机接口。兼容型号：6FC3988-7FA20 和 SM0901/579417TA。',
        'sys_cn': '西门子 SINUMERIK 810/820',
        'pattern': 'SINUMERIK 810',
        'faqs': [
            ('如何升级西门子 810/820 显示器为 LCD？', '关闭控制系统电源，拔下 6FC3988-7FA20 CRT，连接 LCD 模组，通电即可。无需改参数或重新接线。'),
            ('覆盖哪些西门子型号？', '6FC3988-7FA20（SINUMERIK 810/820）和 SM0901/579417TA（SINUMERIK 810M），均为 9 英寸单色显示器。'),
            ('LCD 模组支持 840C 或 840D 吗？', '不支持。840C/840D 使用不同尺寸和接口。请联系我们提供确切型号以获取兼容方案。'),
        ],
    },
]

os.makedirs(OUT_DIR, exist_ok=True)

for p in PAGES:
    models = models_for(p['pattern'])
    rows = table_rows(models)
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{p['title']}</title>
<meta name="description" content="{p['meta']}">
<link rel="canonical" href="https://cncdisplay.com/zh/guides/by-system/{p['slug']}">
<link rel="alternate" hreflang="en" href="https://cncdisplay.com/guides/by-system/{p['en_slug']}" />
<link rel="alternate" hreflang="zh-CN" href="https://cncdisplay.com/zh/guides/by-system/{p['slug']}" />
<link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/" />
<link rel="stylesheet" href="/css/style.css?v=9">
{CSS}
{breadcrumb_ld(p['sys_cn'])}
{faq_ld(p['faqs'])}
</head>
<body>
{NAV}
<div class="guide-page">
<h1>{p['h1']}</h1>
<p class="answer-first">{p['intro']}</p>

<h2>{p['sys_cn']} 兼容显示器型号</h2>
<p>在下方找到你的 CRT 型号——全部采用原机接口即插即用，无需改参数、无需重新接线。</p>
<table class="model-table">
<thead><tr><th>CRT 型号</th><th>LCD 尺寸</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>

<h2>为什么要把 {p['sys_cn']} CRT 升级为 LCD？</h2>
<p>{p['sys_cn']} 系统的 CRT 会逐步老化：屏幕变暗、闪烁、残影，最终黑屏。LCD 模组消除了所有 CRT 特有故障点——没有行变、没有高压管、没有偏转板。升级后 800x600 分辨率、350+ cd/m² 亮度、5 万小时寿命（CRT 仅约 1.5 万小时）。</p>

<h2>即插即用安装</h2>
<p>每个模组采用与原 CRT 相同的接口（多数型号为 20 针 Honda MR-20M）。关机、拔旧 CRT、插 LCD、通电。典型安装 10-15 分钟。每个模组含 2 年质保和终身技术支持。</p>

<h2>常见问题</h2>
"""
    for q, a in p['faqs']:
        page += f'<h3>{q}</h3>\n<p>{a}</p>\n'

    page += f"""
<div style="margin-top:2rem;padding:1.5rem;background:#f8fafc;border-radius:8px;">
<p style="margin:0;font-size:0.95rem;">需要其他品牌或系统？浏览<a href="/zh/compatibility-matrix.html">完整兼容矩阵</a>（52+ 型号、12 品牌）或查看<a href="/zh/guides/by-size/8-inch.html">8 英寸 LCD 升级方案</a>（最常见尺寸）。</p>
</div>
</div>
</body>
</html>
"""
    fp = os.path.join(OUT_DIR, p['slug'])
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(page)
    print(f'GENERATED: zh/guides/by-system/{p["slug"]}')

# Add zh-CN hreflang to EN hub pages (they currently lack it)
print('\n=== Adding zh-CN hreflang to EN hub pages ===')
for p in PAGES:
    en_fp = os.path.join(BASE, 'guides', 'by-system', p['en_slug'])
    with open(en_fp, encoding='utf-8') as f:
        en_c = f.read()
    zh_hreflang = f'<link rel="alternate" hreflang="zh-CN" href="https://cncdisplay.com/zh/guides/by-system/{p["slug"]}" />'
    if 'hreflang="zh-CN"' not in en_c:
        # insert after en hreflang
        en_tag = f'<link rel="alternate" hreflang="en" href="https://cncdisplay.com/guides/by-system/{p["en_slug"]}" />'
        if en_tag in en_c:
            en_c = en_c.replace(en_tag, en_tag + '\n' + zh_hreflang, 1)
            with open(en_fp, 'w', encoding='utf-8') as f:
                f.write(en_c)
            print(f'  ADDED zh-CN hreflang: guides/by-system/{p["en_slug"]}')
        else:
            print(f'  WARN: en hreflang not found in guides/by-system/{p["en_slug"]}')
    else:
        print(f'  already has zh-CN: guides/by-system/{p["en_slug"]}')

print('\nDone.')
