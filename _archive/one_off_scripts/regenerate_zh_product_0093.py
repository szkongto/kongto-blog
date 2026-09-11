"""Regenerate ZH product page from EN version with clean UTF-8 Chinese.

已归档，勿运行（2026-09-11 从 scripts/ 移入 _archive/one_off_scripts/）。

归档原因：
  1. 第 4 行 DIR 硬编码 d:\\code\\seo_deploy —— 那是同一 remote 的另一份陈旧
     克隆，不是本仓库。跑它读的是那边的旧 EN 页，写回的也还是那边，对本仓库
     零作用；若把 DIR 改成本仓库再跑，则是拿一份旧模板整体覆写 zh 产品页
  2. 第 238-258 行的导航替换针对 /en/posts/、/en/brands/、/en/docs/ 等前缀，
     该 /en/ 目录 2026-08-28 已废弃（GSC 实测 Google 选根版 canonical），
     替换目标已不存在
  3. 里面的文案匹配串已经过时。例如第 20-21 行拿
     '<title>... | 8-inch TFT $199 | Kongto Technology</title>' 去匹配，
     而现价是 $155，匹配不上，该替换实际是静默空操作
  4. 全仓库零引用

  仅剩的两处 HowTo 字样在第 78、84 行的注释，字符串替换两侧自 commit
  0054c52f 起均已不存在，同样是空操作。

需要再生成 zh 产品页时，另写脚本，勿解封此文件。
"""
import os

DIR = r'd:\code\seo_deploy'
EN_PATH = os.path.join(DIR, 'products/fanuc-a61l-0001-0093-lcd-upgrade.html')
ZH_PATH = os.path.join(DIR, 'zh/products/fanuc-a61l-0001-0093-lcd-upgrade.html')

# Read the EN page as template
with open(EN_PATH, 'r', encoding='utf-8') as f:
    en = f.read()

# Build ZH page from EN template, replacing EN content with ZH
zh = en

# HTML lang
zh = zh.replace('html lang="en"', 'html lang="zh-CN"')

# Title
zh = zh.replace(
    '<title>FANUC A61L-0001-0093 LCD Upgrade | 8-inch TFT $199 | Kongto Technology</title>',
    '<title>FANUC A61L-0001-0093 LCD升级显示器 | 8英寸CRT改TFT $155 | 江图科技</title>'
)

# Description
zh = zh.replace(
    '<meta name="description" content="FANUC A61L-0001-0093 8-inch TFT LCD upgrade solution. $155 plug-and-play, 800x600 resolution, 350-450cd/m2 brightness, 50,000+ hour lifespan. Compatible with FANUC 0/0i/16i/18i/21i/OM-D series.">',
    '<meta name="description" content="FANUC A61L-0001-0093 8英寸TFT LCD升级方案，$155即插即用，800x600分辨率，350-450cd/m2亮度，50000+小时寿命。兼容FANUC 0/0i/16i/18i/21i/OM-D系列。">'
)

# Canonical
zh = zh.replace(
    'href="https://cncdisplay.com/products/fanuc-a61l-0001-0093-lcd-upgrade.html">',
    'href="https://cncdisplay.com/zh/products/fanuc-a61l-0001-0093-lcd-upgrade.html">'
)

# OG title
zh = zh.replace(
    '<meta property="og:title" content="FANUC A61L-0001-0093 LCD Upgrade | 8-inch TFT">',
    '<meta property="og:title" content="FANUC A61L-0001-0093 LCD升级显示器 | 8英寸CRT改TFT">'
)

# OG description
zh = zh.replace(
    '<meta property="og:description" content="$155 plug-and-play, 50,000+ hour lifespan, FANUC 0/0i series compatible">',
    '<meta property="og:description" content="$155即插即用，50000+小时寿命，FANUC 0/0i系列兼容">'
)

# OG image
zh = zh.replace(
    'content="https://cncdisplay.com/images/A6100010093_install_effect_2.jpg"',
    'content="https://cncdisplay.com/zh/images/A6100010093_install_effect_2.jpg"'
)

# Twitter title
zh = zh.replace(
    '<meta name="twitter:title" content="FANUC A61L-0001-0093 LCD Upgrade">',
    '<meta name="twitter:title" content="FANUC A61L-0001-0093 LCD升级显示器">'
)

# Product Schema name
zh = zh.replace(
    '"name": "FANUC A61L-0001-0093 LCD Upgrade Display"',
    '"name": "FANUC A61L-0001-0093 LCD升级显示器"'
)

# Product Schema description
zh = zh.replace(
    '"description": "FANUC A61L-0001-0093 8-inch TFT-LCD upgrade. Plug-and-play, 800x600, 350-450cd/m2, 50,000+ hour lifespan."',
    '"description": "FANUC A61L-0001-0093 8英寸TFT-LCD升级。即插即用，800x600，350-450cd/m2，50000+小时寿命。"'
)

# Offer URL
zh = zh.replace(
    '"url": "https://cncdisplay.com/products/fanuc-a61l-0001-0093-lcd-upgrade.html"',
    '"url": "https://cncdisplay.com/zh/products/fanuc-a61l-0001-0093-lcd-upgrade.html"'
)

# HowTo name
zh = zh.replace(
    '"name": "FANUC A61L-0001-0093 CRT to LCD Upgrade Module Installation Guide"',
    '"name": "FANUC A61L-0001-0093 CRT改LCD升级模块安装指南"'
)

# HowTo steps - translate
zh = zh.replace(
    '"text":"Turn off CNC system power. Remove the CRT display housing (4 screws). Disconnect the HONDA 20-pin signal cable and DC 24V power cable from the back."',
    '"text":"关闭CNC系统电源。拆下CRT外壳(4颗螺丝)。拔下HONDA 20针信号线和DC 24V电源线。"'
)
zh = zh.replace(
    '"text":"Place the LCD upgrade module into the original CRT mounting position. Align the mounting holes and secure with original screws (keyed design prevents incorrect installation)."',
    '"text":"将LCD升级模块放入原CRT安装位。对齐安装孔位并用原螺丝固定(防呆设计，方向唯一)。"'
)
zh = zh.replace(
    '"text":"Insert the HONDA 20-pin signal cable into the LCD module signal port (keyed connector prevents incorrect insertion). Connect the DC 24V power cable."',
    '"text":"将HONDA 20针信号线插入LCD模块信号口(有防呆卡扣)。连接DC 24V电源线。"'
)
zh = zh.replace(
    '"text":"Restore power. The LCD will display automatically upon startup. Use the OSD buttons on the module to adjust brightness, contrast, and screen position as needed."',
    '"text":"恢复供电。LCD开机自动显示，通过模块上的OSD按键调整亮度/对比度/画面位置。"'
)

# Nav header - translate
zh = zh.replace(
    '<a href="/" class="logo">Kongto Technology</a>',
    '<a href="/" class="logo">江图科技</a>'
)
zh = zh.replace(
    '<a href="/">Home</a><a href="/compatibility-matrix.html">Compatibility</a>',
    '<a href="/">首页</a><a href="/zh/compatibility-matrix.html">兼容查询</a>'
)
zh = zh.replace(
    '<a href="/products/">Products</a>',
    '<a href="/zh/products/">产品</a>'
)
zh = zh.replace(
    '<a href="/posts/">Articles</a>',
    '<a href="/zh/posts/">文章</a>'
)
zh = zh.replace(
    '<a href="/case-studies.html">Cases</a>',
    '<a href="/zh/case-studies.html">案例</a>'
)
zh = zh.replace(
    '<a href="/docs/">Downloads</a>',
    '<a href="/zh/docs/">下载</a>'
)
zh = zh.replace(
    '<a href="/about.html">About</a>',
    '<a href="/zh/about.html">关于</a>'
)
zh = zh.replace(
    '<a href="/quote.html" style="color:#ff9800;font-weight:700;">Get Quote</a>',
    '<a href="/zh/quote.html" style="color:#ff9800;font-weight:700;">获取报价</a>'
)
zh = zh.replace(
    '<a href="/search.html" class="nav-search">🔍 Search</a>',
    '<a href="/zh/search.html" class="nav-search">🔍 搜索</a>'
)

# Lang switch
zh = zh.replace(
    '<a href="/zh/products/fanuc-a61l-0001-0093-lcd-upgrade.html" lang="zh" class="lang-zh">中文</a>',
    '<a href="/zh/products/fanuc-a61l-0001-0093-lcd-upgrade.html" lang="zh" class="lang-zh">中文</a>'
)
zh = zh.replace(
    '<a href="/products/fanuc-a61l-0001-0093-lcd-upgrade.html" lang="en" class="lang-en">English</a>',
    '<a href="/products/fanuc-a61l-0001-0093-lcd-upgrade.html" lang="en" class="lang-en">English</a>'
)

# Breadcrumb
zh = zh.replace(
    '<a href="/">Home</a> / <strong>FANUC A61L-0001-0093 LCD Upgrade</strong>',
    '<a href="/">首页</a> / <strong>FANUC A61L-0001-0093 LCD升级</strong>'
)

# Product hero
zh = zh.replace(
    'alt="FANUC A61L-0001-0093 LCD upgrade installed on CNC machine front view"',
    'alt="FANUC A61L-0001-0093 LCD升级模块安装效果图"'
)
zh = zh.replace(
    '<h1>FANUC A61L-0001-0093<br>LCD Upgrade Display</h1>',
    '<h1>FANUC A61L-0001-0093<br>LCD升级显示器</h1>'
)
zh = zh.replace(
    '<p>Factory direct — 8-inch TFT-LCD plug-and-play replacement. No CNC parameter changes needed. 30-minute installation.</p>',
    '<p>厂家现货直发 — 8英寸TFT-LCD即插即用替代方案。无需修改CNC参数，30分钟安装完成。</p>'
)
zh = zh.replace(
    '<p style="color:#28a745;font-weight:600;">In Stock — 2-Year Warranty</p>',
    '<p style="color:#28a745;font-weight:600;">现货 — 2年质保</p>'
)
zh = zh.replace(
    'Get a Quote',
    '获取报价'
)
zh = zh.replace(
    'Installation Guide',
    '安装指南'
)

# Product spec section - translate the rest
zh = zh.replace(
    '<h2>Technical Specifications</h2>',
    '<h2>技术规格</h2>'
)

# Brand table
zh = zh.replace(
    '<h2>Compatible CNC Control Systems</h2>',
    '<h2>兼容CNC控制系统</h2>'
)

# FAQ section
zh = zh.replace(
    '<h2>Frequently Asked Questions</h2>',
    '<h2>常见问题</h2>'
)

# Translate FAQ questions/answers
zh = zh.replace(
    'Does the LCD replacement work with all FANUC CNC models',
    '这款LCD替换件是否兼容所有FANUC CNC型号'
)
zh = zh.replace(
    'Yes. The LCD module uses the same HONDA 20-pin connector and TTL-level signal protocol as the original CRT.',
    '是的。LCD模块使用与原CRT相同的HONDA 20针接口和TTL信号协议。'
)
zh = zh.replace(
    'It is a drop-in replacement for any machine originally equipped with the A61L-0001-0093',
    '它是A61L-0001-0093原装CRT的直接替换方案'
)
zh = zh.replace(
    'including FANUC 0, 0-Mate, 0i-A/B/C/D, 16i, 18i, and 21i series controls.',
    '兼容FANUC 0, 0-Mate, 0i-A/B/C/D, 16i, 18i, 21i系列控制器。'
)
zh = zh.replace(
    'No parameter changes, adapter cables, or signal converters are required.',
    '无需修改参数，无需转接线或信号转换器。'
)

# Related products
zh = zh.replace(
    '<h2>Related Products</h2>',
    '<h2>相关产品</h2>'
)

# Footer
zh = zh.replace(
    '<span class="footer-logo">Kongto Technology 江图科技</span>',
    '<span class="footer-logo">江图科技 Kongto Technology</span>'
)
zh = zh.replace(
    '<p>Industrial Video Display Solutions — CNC CRT-to-LCD Retrofit, Video Signal Converters, Custom Industrial Displays</p>',
    '<p>专注工业视频显示解决方案 — CNC显示器CRT转LCD升级、工业视频信号转换器、非标定制工控显示器</p>'
)
zh = zh.replace(
    '<a href="/en/posts/">📄 Articles</a>',
    '<a href="/posts/">📄 技术文章</a>'
)
zh = zh.replace(
    '<a href="/en/brands/FANUC.html">FANUC</a>',
    '<a href="/brands/FANUC.html">FANUC方案</a>'
)
zh = zh.replace(
    '<a href="/en/brands/Mitsubishi.html">Mitsubishi</a>',
    '<a href="/brands/Mitsubishi.html">三菱方案</a>'
)
zh = zh.replace(
    '<a href="/en/brands/Siemens.html">Siemens</a>',
    '<a href="/brands/Siemens.html">西门子方案</a>'
)
zh = zh.replace(
    '<a href="/en/docs/">Downloads</a>',
    '<a href="/docs/">资料下载</a>'
)
zh = zh.replace(
    '<a href="/en/about.html">About Us</a>',
    '<a href="/about.html">关于我们</a>'
)
zh = zh.replace(
    '<p class="footer-copy">© 2013-2026 Kongto Technology | Shenzhen, Guangdong, China | +86-13686889647 | sales@cncdisplay.com</p>',
    '<p class="footer-copy">© 2013-2026 深圳市江图科技有限公司 | 龙岗区横岗街道深坑综合楼2号楼C栋4楼 | 13686889647 | sales@cncdisplay.com</p>'
)

# Write the ZH file
with open(ZH_PATH, 'w', encoding='utf-8') as f:
    f.write(zh)

print('ZH product page regenerated successfully')

# Verify no garbled bytes
with open(ZH_PATH, 'rb') as f:
    raw = f.read()
if b'\xef\xbf\xbd' in raw:
    print('WARNING: still has replacement characters!')
else:
    print('OK: no replacement characters found')
if b'\xe9\x8d\x97' in raw:
    print('WARNING: still has old garbled patterns!')
else:
    print('OK: no old garbled patterns found')

# Verify title
import re
t = re.search(r'<title>(.*?)</title>', zh)
print(f'Title: {t.group(1) if t else "NOT FOUND"}')
