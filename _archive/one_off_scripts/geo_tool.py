"""Rebuild interactive compatibility tool pages + definition blocks."""
import re, json
from pathlib import Path

BASE = Path(r"d:\code\seo_deploy")
YOUTUBE = "https://www.youtube.com/@Cncdisplay"
LINKEDIN = "https://www.linkedin.com/in/%E5%AE%87%E6%B3%A2-%E9%83%AD-4b61543b3/"
SAMEAS = ["https://blog.csdn.net/szkongto", "https://github.com/szkongto", YOUTUBE, LINKEDIN]

def w(p, c):
    with open(p, 'w', encoding='utf-8') as f: f.write(c)

def r(p):
    with open(p, 'r', encoding='utf-8') as f: return f.read()

# ═══ Data ═══
COMPAT_EN = [
    ["FANUC","A61L-0001-0074",'14" Color CRT',"0 / 0i / 16i / 18i / 21i",'Kongto 14" Industrial TFT-LCD',"1024×768","Available","/en/posts/article_20260503_FANUC_A61L_0001_0074_LCD.html"],
    ["FANUC","A61L-0001-0086",'14" Color CRT (Panasonic)',"0 / 0i series",'Kongto 14" Industrial TFT-LCD',"1024×768","Available","/en/posts/article_20260503_FANUC_A61L_0001_0086_LCD.html"],
    ["FANUC","A61L-0001-0090",'9" Monochrome CRT',"0-TC / 0-MC",'Kongto 9" TFT-LCD',"800×600","Available","/en/posts/article_20260503_FANUC_A61L_0001_0090_LCD.html"],
    ["FANUC","A61L-0001-0092",'9" Monochrome CRT (MDT947B)',"0 / 0i series",'Kongto 9" TFT-LCD',"800×600","Available","/en/posts/article_20260503_FANUC_A61L_0001_0092_LCD.html"],
    ["FANUC","A61L-0001-0093",'9" Monochrome CRT',"0 / 0i / OM-D",'Kongto 9" Industrial TFT-LCD',"800×600","Available","/en/posts/article_20260503_FANUC_A61L_0001_0093_LCD.html"],
    ["FANUC","A61L-0001-0094",'14" Color CRT',"0i / 16i / 18i",'Kongto 14" Industrial TFT-LCD',"1024×768","Available","/en/posts/article_20260503_FANUC_A61L_0001_0094_LCD.html"],
    ["FANUC","A61L-0001-0095","CRT Display","0i / 16i series","Kongto Industrial TFT-LCD","800×600+","Available","/en/posts/article_20260503_FANUC_A61L_0001_0095_LCD.html"],
    ["FANUC","A61L-0001-0096","CRT Display","0i / Power Mate","Kongto Industrial TFT-LCD","800×600+","Available","/en/posts/FANUC_A61L_0001_0096_LCD_CNC_Upgrade_Replacement.html"],
    ["FANUC","A61L-0001-0097","CRT Display","0i / 16i / 18i","Kongto Industrial TFT-LCD","800×600+","Available","/en/posts/FANUC_A61L_0001_0097_LCD_CNC_CRT_Replacement.html"],
    ["FANUC","D9MM-11A-0093",'9" Monochrome CRT',"0 / 0i series",'Kongto 9" TFT-LCD',"800×600","Available","/en/posts/article_20260503_FANUC_D9MM_11A_0093_LCD.html"],
    ["Mitsubishi","MDT962B-1A",'9" Industrial CRT',"M64 / E60 / M500 / M520",'Kongto 9" TFT-LCD',"800×600","Available","/en/posts/article_20260506_Mitsubishi_MDT962B_Industrial_LCD_CRT_Replacement.html"],
    ["Mitsubishi","MDT962B-4A",'9" Industrial CRT',"M64 / E60",'Kongto 9" TFT-LCD',"800×600","Available","/en/posts/article_20260506_Mitsubishi_MDT962B_Industrial_LCD_CRT_Replacement.html"],
    ["Mitsubishi","BM09DF",'9" Industrial CRT',"E60",'Kongto 9" Color TFT-LCD',"800×600","Available","/en/posts/article_20260506_Mitsubishi_BM09DF_Industrial_Display_E60_TFT_Replacement.html"],
    ["Mitsubishi","FCUA-CT100","Industrial CRT","M500 / M520","Kongto Industrial TFT-LCD","800×600","Available","/en/posts/article_20260506_Mitsubishi_FCUA-CT100_Industrial_Display_M500_M520_TFT_Replacement.html"],
    ["Mitsubishi","MDT1283B","Industrial CRT","M64 / M3 / M300","Kongto TFT-LCD","800×600","Available","/en/posts/article_20260507_MDT1283B_LCD_Replacement.html"],
    ["Siemens","6FC3998-7FA20","Industrial LCD","SINUMERIK 840D / 810D / 802D","Kongto Industrial TFT-LCD","800×600+","Available","/en/posts/article_20260507_Siemens_6FC3998-7FA20_LCD.html"],
    ["Siemens","SM0901-579417-TA","Industrial Display","SINUMERIK series","Kongto Industrial TFT-LCD","800×600+","Available","/en/posts/article_20260507_Siemens_SM0901_579417_TA.html"],
    ["Siemens","6FC5200-series","Industrial Display","SINUMERIK 840D sl","Kongto Industrial TFT-LCD","1024×768","Available","/en/posts/siemens-sinumerik-cnc-display-upgrade-complete-guide.html"],
    ["Mazak","CD1472-D1M",'14" Color CRT',"Mazatrol T-Plus / M-Plus / Fusion 640",'Kongto 10.4" Industrial TFT-LCD',"800×600","Available","/en/posts/article_20260507_Mazak_CD1472D1M_LCD_Replacement.html"],
    ["Mazak","C5470NS","CRT Display","Mazatrol Fusion","Kongto Industrial TFT-LCD","800×600","Available","/en/posts/article_20260508_Mazak_C5470NS.html"],
    ["Mazak","DR5614","CRT Display","Mazatrol series","Kongto Industrial TFT-LCD","800×600","Available","/en/posts/Mazak_DR5614_LCD_CNC_CRT_Replacement.html"],
    ["Okuma",'OSP 5000 CRT','9" Monochrome CRT',"OSP 5000 series",'Kongto 9" Industrial TFT-LCD',"800×600","Available","/en/posts/article_20260508_Okuma_5000_5020_CRT_LCD.html"],
    ["Okuma",'OSP 5020 CRT','10.4" Color CRT',"OSP 5020 series",'Kongto 10.4" Industrial TFT-LCD',"800×600","Available","/en/posts/article_20260508_Okuma_5000_5020_CRT_LCD.html"],
    ["Haas",'VF Series 9" CRT','9" Monochrome CRT (Amber)',"Haas Classic Control",'Kongto 9" Industrial TFT-LCD',"800×600","Available","/en/posts/article_20260508_Haas_CRT_LCD_Case.html"],
    ["Haas",'VF Series 12" CRT','12" Color CRT',"Haas Classic Control",'Kongto 12.1" Industrial TFT-LCD',"800×600","Available","/en/posts/article_20260508_Haas_CRT_LCD_Case.html"],
    ["Haas",'VF Series 15" LCD','15" LCD (Upgrade)',"Haas NGC",'Kongto 15" Industrial TFT-LCD',"1024×768","Available","/en/posts/article_20260508_Haas_CRT_LCD_Case.html"],
]

COMPAT_ZH = [
    ["FANUC","A61L-0001-0074","14英寸彩色CRT","0 / 0i / 16i / 18i / 21i 系列","江图 14英寸工业TFT液晶屏","1024×768","有现货","/posts/article_20260503_FANUC_A61L_0001_0074_LCD.html"],
    ["FANUC","A61L-0001-0086","14英寸彩色CRT (松下)","0 / 0i 系列","江图 14英寸工业TFT液晶屏","1024×768","有现货","/posts/article_20260503_FANUC_A61L_0001_0086_LCD.html"],
    ["FANUC","A61L-0001-0090","9英寸单色CRT","0-TC / 0-MC","江图 9英寸TFT液晶屏","800×600","有现货","/posts/article_20260503_FANUC_A61L_0001_0090_LCD.html"],
    ["FANUC","A61L-0001-0092","9英寸单色CRT (MDT947B)","0 / 0i 系列","江图 9英寸TFT液晶屏","800×600","有现货","/posts/article_20260503_FANUC_A61L_0001_0092_LCD.html"],
    ["FANUC","A61L-0001-0093","9英寸单色CRT","0 / 0i / OM-D","江图 9英寸工业TFT液晶屏","800×600","有现货","/posts/article_20260503_FANUC_A61L_0001_0093_LCD.html"],
    ["FANUC","A61L-0001-0094","14英寸彩色CRT","0i / 16i / 18i","江图 14英寸工业TFT液晶屏","1024×768","有现货","/posts/article_20260503_FANUC_A61L_0001_0094_LCD.html"],
    ["FANUC","A61L-0001-0095","CRT显示器","0i / 16i 系列","江图工业TFT液晶屏","800×600+","有现货","/posts/article_20260503_FANUC_A61L_0001_0095_LCD.html"],
    ["FANUC","A61L-0001-0096","CRT显示器","0i / Power Mate","江图工业TFT液晶屏","800×600+","有现货","/posts/article_20260521_FANUC_A61L_0001_0096_LCD.html"],
    ["FANUC","A61L-0001-0097","CRT显示器","0i / 16i / 18i","江图工业TFT液晶屏","800×600+","有现货","/posts/article_20260522_FANUC_A61L_0001_0097_LCD_CRT.html"],
    ["FANUC","D9MM-11A-0093","9英寸单色CRT","0 / 0i 系列","江图 9英寸TFT液晶屏","800×600","有现货","/posts/article_20260503_FANUC_D9MM_11A_0093_LCD.html"],
    ["三菱","MDT962B-1A","9英寸工业CRT","M64 / E60 / M500 / M520","江图 9英寸TFT液晶屏","800×600","有现货","/posts/article_20260506_三菱MDT962B工业液晶显示器CRT替代方案.html"],
    ["三菱","MDT962B-4A","9英寸工业CRT","M64 / E60","江图 9英寸TFT液晶屏","800×600","有现货","/posts/article_20260506_三菱MDT962B工业液晶显示器CRT替代方案.html"],
    ["三菱","BM09DF","9英寸工业CRT","E60","江图 9英寸彩色TFT液晶屏","800×600","有现货","/posts/article_20260506_Mitsubishi_BM09DF_E60_TFT_Replacement_CN.html"],
    ["三菱","FCUA-CT100","工业CRT","M500 / M520","江图工业TFT液晶屏","800×600","有现货","/posts/article_20260506_Mitsubishi_FCUA_CT100_M500_M520_TFT_Replacement_CN.html"],
    ["三菱","MDT1283B","工业CRT","M64 / M3 / M300","江图TFT液晶屏","800×600","有现货","/posts/article_20260507_MDT1283B_LCD.html"],
    ["西门子","6FC3998-7FA20","工业LCD","SINUMERIK 840D / 810D / 802D","江图工业TFT液晶屏","800×600+","有现货","/posts/article_20260507_Siemens_6FC3998-7FA20_LCD.html"],
    ["西门子","SM0901-579417-TA","工业显示器","SINUMERIK 系列","江图工业TFT液晶屏","800×600+","有现货","/posts/article_20260507_Siemens_SM0901_579417_TA.html"],
    ["西门子","6FC5200系列","工业显示器","SINUMERIK 840D sl","江图工业TFT液晶屏","1024×768","有现货","/posts/siemens-sinumerik-cnc-display-upgrade-complete-guide.html"],
    ["Mazak","CD1472-D1M","14英寸彩色CRT","Mazatrol T-Plus / M-Plus / Fusion 640","江图 10.4英寸工业TFT液晶屏","800×600","有现货","/posts/article_20260507_Mazak_CD1472D1M_LCD.html"],
    ["Mazak","C5470NS","CRT显示器","Mazatrol Fusion","江图工业TFT液晶屏","800×600","有现货","/posts/article_20260508_Mazak_C5470NS.html"],
    ["Mazak","DR5614","CRT显示器","Mazatrol 系列","江图工业TFT液晶屏","800×600","有现货","/posts/article_20260522_Mazak_DR5614_LCD_CRT.html"],
    ["大隈","OSP 5000 CRT","9英寸单色CRT","OSP 5000 系列","江图 9英寸工业TFT液晶屏","800×600","有现货","/posts/article_20260508_Okuma_5000_5020_CRT_LCD.html"],
    ["大隈","OSP 5020 CRT","10.4英寸彩色CRT","OSP 5020 系列","江图 10.4英寸工业TFT液晶屏","800×600","有现货","/posts/article_20260508_Okuma_5000_5020_CRT_LCD.html"],
    ["哈斯","VF系列 9英寸CRT","9英寸单色CRT (琥珀色)","Haas Classic Control","江图 9英寸工业TFT液晶屏","800×600","有现货","/posts/article_20260508_Haas_CRT_LCD_Case.html"],
    ["哈斯","VF系列 12英寸CRT","12英寸彩色CRT","Haas Classic Control","江图 12.1英寸工业TFT液晶屏","800×600","有现货","/posts/article_20260508_Haas_CRT_LCD_Case.html"],
    ["哈斯","VF系列 15英寸LCD","15英寸LCD (升级款)","Haas NGC","江图 15英寸工业TFT液晶屏","1024×768","有现货","/posts/article_20260508_Haas_CRT_LCD_Case.html"],
]

CSS = """        .tool-container { max-width:960px; margin:0 auto; padding:1rem; }
        .tool-hero { text-align:center; padding:2rem 1rem; background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%); color:#fff; border-radius:12px; margin-bottom:2rem; }
        .tool-hero h1 { font-size:2rem; margin-bottom:0.5rem; color:#fff; }
        .tool-hero p { font-size:1.1rem; opacity:0.9; max-width:700px; margin:0 auto 1.5rem; }
        .search-box { position:relative; max-width:600px; margin:0 auto; }
        .search-box input { width:100%; padding:1rem 1.2rem 1rem 3rem; font-size:1.1rem; border:2px solid transparent; border-radius:50px; outline:none; transition:all 0.2s; box-sizing:border-box; }
        .search-box input:focus { border-color:#60a5fa; box-shadow:0 0 0 3px rgba(96,165,250,0.3); }
        .search-icon { position:absolute; left:1.2rem; top:50%; transform:translateY(-50%); font-size:1.2rem; color:#9ca3af; }
        .stats-bar { display:flex; gap:1rem; justify-content:center; flex-wrap:wrap; margin:1.5rem 0; }
        .stat-chip { background:rgba(255,255,255,0.15); padding:0.5rem 1rem; border-radius:50px; font-size:0.9rem; }
        .result-count { text-align:center; padding:0.5rem; color:#6b7280; font-size:0.9rem; }
        .brand-filters { display:flex; gap:0.5rem; flex-wrap:wrap; justify-content:center; margin-bottom:1.5rem; }
        .brand-btn { padding:0.5rem 1.2rem; border:2px solid #e5e7eb; border-radius:50px; background:#fff; cursor:pointer; font-size:0.9rem; transition:all 0.2s; font-weight:500; }
        .brand-btn:hover { border-color:#2563eb; color:#2563eb; }
        .brand-btn.active { background:#2563eb; color:#fff; border-color:#2563eb; }
        .compat-table { width:100%; border-collapse:collapse; background:#fff; border-radius:12px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.1); }
        .compat-table th { background:#f8fafc; padding:0.9rem 1rem; text-align:left; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; color:#64748b; border-bottom:2px solid #e2e8f0; white-space:nowrap; }
        .compat-table td { padding:0.8rem 1rem; border-bottom:1px solid #f1f5f9; font-size:0.95rem; }
        .compat-table tr:hover td { background:#f0f7ff; }
        .compat-table tr.hidden { display:none; }
        .brand-tag { display:inline-block; padding:0.2rem 0.6rem; border-radius:4px; font-size:0.8rem; font-weight:600; }
        .brand-fanuc { background:#fef3c7; color:#92400e; }
        .brand-mitsubishi { background:#fee2e2; color:#991b1b; }
        .brand-siemens { background:#e0f2fe; color:#075985; }
        .brand-mazak { background:#f3e8ff; color:#6b21a8; }
        .brand-okuma { background:#d1fae5; color:#065f46; }
        .brand-haas { background:#fce7f3; color:#9d174d; }
        .action-link { display:inline-block; padding:0.35rem 0.8rem; background:#2563eb; color:#fff; border-radius:4px; text-decoration:none; font-size:0.85rem; white-space:nowrap; transition:background 0.2s; }
        .action-link:hover { background:#1d4ed8; color:#fff; }
        .status-available { color:#059669; font-weight:600; }
        .no-results { text-align:center; padding:3rem 1rem; color:#6b7280; }
        .definition-block { background:#f0f7ff; border-left:4px solid #2563eb; padding:1rem 1.2rem; margin:2rem 0 1rem; border-radius:0 8px 8px 0; font-size:1.05rem; line-height:1.7; }
        .faq-section { margin:2rem 0; }
        .faq-item { margin-bottom:1rem; border:1px solid #e5e7eb; border-radius:8px; overflow:hidden; }
        .faq-q { padding:0.9rem 1rem; background:#f8fafc; font-weight:600; cursor:pointer; display:flex; justify-content:space-between; align-items:center; user-select:none; -webkit-user-select:none; }
        .faq-q:hover { background:#f0f7ff; }
        .faq-a { padding:0.9rem 1rem; border-top:1px solid #e5e7eb; display:none; line-height:1.7; }
        .faq-item.open .faq-a { display:block; }
        .faq-arrow { transition:transform 0.2s; }
        .faq-item.open .faq-arrow { transform:rotate(180deg); }
        @media (max-width:768px) {
            .compat-table { font-size:0.85rem; display:block; overflow-x:auto; }
            .tool-hero h1 { font-size:1.5rem; }
            .brand-filters { gap:0.3rem; }
            .brand-btn { padding:0.4rem 0.8rem; font-size:0.8rem; }
        }"""

def build_en():
    data_json = json.dumps(COMPAT_EN, ensure_ascii=False)
    sameas_json = json.dumps(SAMEAS, ensure_ascii=False)
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CNC CRT to LCD Compatibility Lookup Tool | Find Your Replacement | Kongto Technology</title>
    <meta name="description" content="Instantly find the right LCD replacement for your CNC CRT display. Search by brand or model — FANUC A61L, Mitsubishi MDT, Siemens 6FC, Mazak CD1472, Okuma, Haas. 26 models covered. Plug-and-play with 2-year warranty.">
    <link rel="canonical" href="https://cncdisplay.com/en/compatibility-matrix.html">
    <link rel="alternate" hreflang="en" href="https://cncdisplay.com/en/compatibility-matrix.html">
    <link rel="alternate" hreflang="zh" href="https://cncdisplay.com/compatibility-matrix.html">
    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/en/compatibility-matrix.html">
    <meta property="og:type" content="website">
    <meta property="og:title" content="CNC CRT to LCD Compatibility Lookup Tool">
    <meta property="og:description" content="Search 26 CNC display models across 6 brands. Instant LCD replacement match.">
    <meta property="og:url" content="https://cncdisplay.com/en/compatibility-matrix.html">
    <meta property="og:site_name" content="Kongto Technology">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="CNC CRT to LCD Compatibility Lookup Tool">
    <meta name="twitter:description" content="Find your CNC display LCD replacement instantly. 6 brands covered.">
    <link rel="stylesheet" href="/css/style.css?v=7">
    <meta name="google-site-verification" content="google7478b8e743977291"/>
    <style>
{CSS}
    </style>
</head>
<body>
    <header><nav>
        <a href="/en/" class="logo">Kongto Technology</a>
        <div class="nav-links">
            <a href="/en/">Home</a>
            <a href="/en/posts/">Articles</a>
            <a href="/en/compatibility-matrix.html" style="font-weight:700;">Compatibility</a>
            <a href="/en/about.html">About</a>
        </div>
        <div class="lang-switch">
            <a href="/compatibility-matrix.html" lang="zh">中文</a> |
            <a href="/en/compatibility-matrix.html" lang="en" style="font-weight:700;">English</a>
        </div>
    </nav></header>
    <main class="tool-container">
        <div class="tool-hero">
            <h1>CNC CRT → LCD Compatibility Lookup</h1>
            <p>Find the right plug-and-play LCD replacement. Type a model number to search instantly across 6 brands.</p>
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" placeholder="e.g. A61L-0001-0093, MDT962B, CD1472..." autocomplete="off">
            </div>
            <div class="stats-bar">
                <span class="stat-chip">🏭 6 Brands</span>
                <span class="stat-chip">26 Models</span>
                <span class="stat-chip">🛡️ 18-Month Warranty</span>
                <span class="stat-chip">⚡ Plug & Play</span>
            </div>
        </div>
        <div class="definition-block">
            <p><strong>The CNC CRT to LCD compatibility matrix</strong> is a cross-reference tool mapping OEM CRT display part numbers to their industrial TFT-LCD replacement modules. Since FANUC, Mitsubishi, Siemens, Mazak, Okuma, and Haas have all discontinued CRT production, machine shops face rising maintenance costs. Kongto LCD upgrade modules are direct-fit, plug-and-play replacements preserving original mounting dimensions and signal connectors (HONDA 20-pin, Mitsubishi 20/26-pin, Siemens DB-25, Mazak MC712/MC714) with no CNC parameter changes. Each replacement delivers 800×600+ resolution at 350-450cd/m² brightness with 50,000+ hour lifespan — versus the original 640×400 at ~200cd/m² and 15,000 hours. All products include a 2-year warranty and lifetime technical support.</p>
        </div>
        <div class="brand-filters">
            <button type="button" class="brand-btn active" onclick="filterBrand('all')">All</button>
            <button type="button" class="brand-btn" onclick="filterBrand('FANUC')">FANUC</button>
            <button type="button" class="brand-btn" onclick="filterBrand('Mitsubishi')">Mitsubishi</button>
            <button type="button" class="brand-btn" onclick="filterBrand('Siemens')">Siemens</button>
            <button type="button" class="brand-btn" onclick="filterBrand('Mazak')">Mazak</button>
            <button type="button" class="brand-btn" onclick="filterBrand('Okuma')">Okuma</button>
            <button type="button" class="brand-btn" onclick="filterBrand('Haas')">Haas</button>
        </div>
        <div class="result-count" id="resultCount"></div>
        <div style="overflow-x:auto;">
            <table class="compat-table"><thead><tr><th>Brand</th><th>Original CRT Model</th><th>Size/Type</th><th>CNC System</th><th>LCD Replacement</th><th>Resolution</th><th>Status</th><th>Guide</th></tr></thead>
            <tbody id="tableBody"></tbody></table>
        </div>
        <div class="no-results" id="noResults" style="display:none;">
            <h3>No exact match found</h3>
            <p>Send a photo of your CRT display label to <strong>szkongto01@foxmail.com</strong> — our team confirms compatibility within 24 hours.</p>
        </div>
        <div class="faq-section">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">How do I identify my CRT model number?<span class="faq-arrow">▼</span></div><div class="faq-a">Look at the label on the back or side of your CRT display. FANUC models start with "A61L-0001-". Mitsubishi uses "MDT" prefixes. Siemens has "6FC" numbers. Mazak labels are on the CRT housing. Take a photo and email us if unsure.</div></div>
            <div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">Do I need to modify CNC parameters after installing the LCD?<span class="faq-arrow">▼</span></div><div class="faq-a">No. All Kongto LCD upgrade modules are plug-and-play — they use the original signal connectors and power supply. No CNC parameter changes or machine modifications are required. Installation takes 10–15 minutes per machine.</div></div>
            <div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">What if my model isn't listed?<span class="faq-arrow">▼</span></div><div class="faq-a">Email a clear photo of your CRT display's model label to szkongto01@foxmail.com. Our engineering team confirms compatibility within 24 hours. We also offer custom solutions for non-standard models.</div></div>
            <div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">What warranty comes with the LCD replacement?<span class="faq-arrow">▼</span></div><div class="faq-a">All Kongto LCD modules include a 2-year warranty against manufacturing defects — the longest in the industrial CNC display replacement market. Lifetime free technical support for all customers.</div></div>
        </div>
    </main>
    <footer><p>&copy; Kongto Technology | <a href="/en/compatibility-matrix.html">Compatibility Matrix</a> | <a href="mailto:szkongto01@foxmail.com">szkongto01@foxmail.com</a></p></footer>
    <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Kongto Technology",
  "url": "https://cncdisplay.com",
  "description": "Industrial Video Display Solutions - CNC CRT to LCD Upgrade",
  "sameAs": __SAMEAS__
}}
    </script>
    <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "CNC CRT to LCD Compatibility Lookup",
  "url": "https://cncdisplay.com/en/compatibility-matrix.html",
  "description": "Interactive lookup tool to find LCD replacements for CNC CRT displays across 6 brands.",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Any",
  "offers": {{"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
  "author": {{"@type": "Organization", "name": "Kongto Technology", "url": "https://cncdisplay.com"}}
}}
    </script>
    <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type":"Question","name":"How do I find the right LCD replacement for my CNC CRT display?","acceptedAnswer":{{"@type":"Answer","text":"Use the Kongto compatibility lookup tool. Enter your CRT model number to instantly find the matching plug-and-play LCD replacement module with full specifications."}}}},
    {{"@type":"Question","name":"Do I need to change CNC parameters when upgrading from CRT to LCD?","acceptedAnswer":{{"@type":"Answer","text":"No. All Kongto LCD modules use the original signal connectors and DC 24V power supply. Installation is plug-and-play with no CNC parameter changes, taking 10-15 minutes per machine."}}}},
    {{"@type":"Question","name":"What CNC brands are covered by the compatibility matrix?","acceptedAnswer":{{"@type":"Answer","text":"The matrix covers FANUC (A61L-0001 and D9MM series), Mitsubishi (MDT962B, BM09DF, FCUA-CT100), Siemens (6FC3988, SM0901), Mazak (CD1472, C5470NS, DR5614), Okuma (OSP 5000/5020), and Haas (VF/ST/SL series). 26 models with exact cross-references."}}}}
  ]
}}
    </script>
    <script>
        const COMPAT_DATA = __DATA__;
        let activeBrand = 'all', searchTerm = '';
        function brandClass(b) {{ return {{'FANUC':'brand-fanuc','Mitsubishi':'brand-mitsubishi','Siemens':'brand-siemens','Mazak':'brand-mazak','Okuma':'brand-okuma','Haas':'brand-haas'}}[b]||''; }}
        function renderTable() {{
            const filtered = COMPAT_DATA.filter(item => {{
                const bm = activeBrand === 'all' || item[0] === activeBrand;
                const sm = !searchTerm || item.some(v => String(v).toLowerCase().includes(searchTerm.toLowerCase()));
                return bm && sm;
            }});
            document.getElementById('resultCount').textContent = (searchTerm || activeBrand !== 'all') ? 'Showing '+filtered.length+' of '+COMPAT_DATA.length+' models' : COMPAT_DATA.length+' compatible models across 6 brands';
            document.getElementById('noResults').style.display = filtered.length ? 'none' : 'block';
            document.getElementById('tableBody').innerHTML = filtered.map(item => '<tr><td><span class="brand-tag '+brandClass(item[0])+'">'+item[0]+'</span></td><td><strong>'+item[1]+'</strong></td><td>'+item[2]+'</td><td>'+item[3]+'</td><td>'+item[4]+'</td><td>'+item[5]+'</td><td><span class="status-available">'+item[6]+'</span></td><td><a href="'+item[7]+'" class="action-link">View Guide →</a></td></tr>').join('');
        }}
        function filterBrand(brand) {{
            activeBrand = brand;
            document.querySelectorAll('.brand-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            renderTable();
        }}
        document.getElementById('searchInput').addEventListener('input', e => {{ searchTerm = e.target.value.trim(); renderTable(); }});
        renderTable();
    </script>
</body>
</html>'''
    html = page.replace('__DATA__', data_json).replace('__SAMEAS__', sameas_json)
    w(BASE / 'en' / 'compatibility-matrix.html', html)
    print("[OK] EN compatibility tool built")

def build_zh():
    data_json = json.dumps(COMPAT_ZH, ensure_ascii=False)
    sameas_json = json.dumps(SAMEAS, ensure_ascii=False)
    page = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CNC CRT转LCD兼容性查询工具 | 找替换型号 | 江图科技</title>
    <meta name="description" content="快速查找您CNC CRT显示器的LCD替代方案。按品牌或型号搜索——FANUC A61L、三菱MDT、西门子6FC、Mazak CD1472、大隈、哈斯。26型号全覆盖，即插即用，18个月质保。">
    <meta name="keywords" content="CNC CRT LCD兼容表,FANUC A61L替代,三菱MDT962B兼容,Mazak LCD对照,CNC显示器兼容性矩阵">
    <link rel="canonical" href="https://cncdisplay.com/compatibility-matrix.html">
    <link rel="alternate" hreflang="zh" href="https://cncdisplay.com/compatibility-matrix.html">
    <link rel="alternate" hreflang="en" href="https://cncdisplay.com/en/compatibility-matrix.html">
    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/en/compatibility-matrix.html">
    <meta property="og:type" content="website">
    <meta property="og:title" content="CNC CRT转LCD兼容性查询工具">
    <meta property="og:description" content="搜索26个CNC显示器型号，覆盖6大品牌。秒级查询LCD替代方案。">
    <meta property="og:url" content="https://cncdisplay.com/compatibility-matrix.html">
    <meta property="og:site_name" content="深圳市江图科技有限公司">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="CNC CRT转LCD兼容性查询工具">
    <link rel="stylesheet" href="/css/style.css?v=7">
    <meta name="google-site-verification" content="google7478b8e743977291"/>
    <meta name="baidu-site-verification" content="codeva-tHiAG9P4up"/>
    <style>
{CSS}
    </style>
</head>
<body>
    <header><nav>
        <a href="/" class="logo">江图科技</a>
        <div class="nav-links">
            <a href="/">首页</a>
            <a href="/posts/">文章</a>
            <a href="/compatibility-matrix.html" style="font-weight:700;">兼容查询</a>
            <a href="/about.html">关于</a>
        </div>
        <div class="lang-switch">
            <a href="/compatibility-matrix.html" lang="zh" style="font-weight:700;">中文</a> |
            <a href="/en/compatibility-matrix.html" lang="en">English</a>
        </div>
    </nav></header>
    <main class="tool-container">
        <div class="tool-hero">
            <h1>CNC CRT → LCD 兼容性查询</h1>
            <p>输入您的 CRT 显示器型号，秒查对应 LCD 替代方案。覆盖 FANUC、三菱、西门子、Mazak、大隈、哈斯六大品牌。</p>
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" placeholder="输入型号如 A61L-0001-0093、MDT962B、CD1472..." autocomplete="off">
            </div>
            <div class="stats-bar">
                <span class="stat-chip">🏭 6大品牌</span>
                <span class="stat-chip">26 型号</span>
                <span class="stat-chip">🛡️ 18个月质保</span>
                <span class="stat-chip">⚡ 即插即用</span>
            </div>
        </div>
        <div class="definition-block">
            <p><strong>CNC CRT 转 LCD 兼容性查询工具</strong>对照原厂 CRT 型号与工业级 TFT-LCD 替代模块。FANUC、三菱、西门子、Mazak、大隈、哈斯均已停产 CRT，工厂面临高昂维护成本。江图科技 LCD 升级模块即插即用，保留原安装尺寸和信号接口（HONDA 20针、三菱20/26针、西门子DB-25、Mazak MC712/MC714），无需修改 CNC 参数。每款替代方案提供 800×600+ 分辨率、350-450cd/m² 亮度、50,000+ 小时寿命（原 CRT 仅 640×400、约200cd/m²、15,000小时）。所有产品享受 2 年质保和终身技术支持。</p>
        </div>
        <div class="brand-filters">
            <button type="button" class="brand-btn active" onclick="filterBrand('all')">全部</button>
            <button type="button" class="brand-btn" onclick="filterBrand('FANUC')">FANUC</button>
            <button type="button" class="brand-btn" onclick="filterBrand('三菱')">三菱</button>
            <button type="button" class="brand-btn" onclick="filterBrand('西门子')">西门子</button>
            <button type="button" class="brand-btn" onclick="filterBrand('Mazak')">Mazak</button>
            <button type="button" class="brand-btn" onclick="filterBrand('大隈')">大隈</button>
            <button type="button" class="brand-btn" onclick="filterBrand('哈斯')">哈斯</button>
        </div>
        <div class="result-count" id="resultCount"></div>
        <div style="overflow-x:auto;">
            <table class="compat-table"><thead><tr><th>品牌</th><th>原厂CRT型号</th><th>尺寸/类型</th><th>CNC系统</th><th>LCD替代方案</th><th>分辨率</th><th>状态</th><th>详情</th></tr></thead>
            <tbody id="tableBody"></tbody></table>
        </div>
        <div class="no-results" id="noResults" style="display:none;">
            <h3>未找到完全匹配的型号</h3>
            <p>请拍下 CRT 显示器标签照片发送至 <strong>szkongto01@foxmail.com</strong>，我们 24 小时内确认兼容方案。</p>
        </div>
        <div class="faq-section">
            <h2>常见问题</h2>
            <div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">如何识别我的 CRT 显示器型号？<span class="faq-arrow">▼</span></div><div class="faq-a">查看 CRT 显示器背面或侧面的标签。FANUC 型号通常以 "A61L-0001-" 开头，三菱以 "MDT" 开头，西门子以 "6FC" 或 "6FX" 开头，Mazak 标签在 CRT 外壳上。拍一张清晰的照片发送给我们确认。</div></div>
            <div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">安装 LCD 后需要修改 CNC 参数吗？<span class="faq-arrow">▼</span></div><div class="faq-a">不需要。所有江图科技 LCD 升级模块采用即插即用设计，使用原装信号接口和电源。无需修改任何 CNC 参数或设备结构，每台安装仅需 10-15 分钟。</div></div>
            <div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">如果我的型号不在列表中怎么办？<span class="faq-arrow">▼</span></div><div class="faq-a">将 CRT 显示器型号标签的清晰照片发送至 szkongto01@foxmail.com，工程师团队 24 小时内确认兼容性。我们也为非标型号提供定制解决方案。</div></div>
            <div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">LCD 替代模块的质保政策是什么？<span class="faq-arrow">▼</span></div><div class="faq-a">所有江图科技 LCD 升级模块提供 2 年质保（非人为损坏免费换新），工业 CNC 显示器替代市场最长质保期。所有客户享受终身免费技术支持。</div></div>
        </div>
    </main>
    <footer><p>&copy; 深圳市江图科技有限公司 | <a href="/compatibility-matrix.html">兼容性查询</a> | <a href="mailto:szkongto01@foxmail.com">szkongto01@foxmail.com</a></p></footer>
    <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "深圳市江图科技有限公司",
  "alternateName": "Kongto Technology",
  "url": "https://cncdisplay.com",
  "description": "专注工业视频显示升级方案，CNC显示器CRT转LCD升级专家",
  "sameAs": __SAMEAS__
}}
    </script>
    <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "CNC CRT转LCD兼容性查询工具",
  "url": "https://cncdisplay.com/compatibility-matrix.html",
  "description": "交互式查询工具，帮助用户快速找到CNC品牌CRT显示器的LCD替代方案。",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Any",
  "offers": {{"@type": "Offer", "price": "0", "priceCurrency": "CNY"}},
  "author": {{"@type": "Organization", "name": "深圳市江图科技有限公司", "url": "https://cncdisplay.com"}}
}}
    </script>
    <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{"@type":"Question","name":"如何找到适合我CNC CRT显示器的LCD替代方案？","acceptedAnswer":{{"@type":"Answer","text":"使用江图科技兼容性查询工具——输入您的CRT显示器型号，即刻获取匹配的即插即用LCD替代模块及详细规格参数。"}}}},
    {{"@type":"Question","name":"CRT升级LCD需要修改CNC参数吗？","acceptedAnswer":{{"@type":"Answer","text":"不需要。所有江图科技LCD升级模块使用原装信号接口和DC 24V供电。安装为即插即用，无需修改任何CNC参数，每台设备安装仅需10-15分钟。"}}}},
    {{"@type":"Question","name":"兼容性矩阵覆盖哪些CNC品牌？","acceptedAnswer":{{"@type":"Answer","text":"覆盖FANUC、三菱、西门子、Mazak、大隈和哈斯。26个型号精确对照。"}}}}
  ]
}}
    </script>
    <script>
        const COMPAT_DATA = __DATA__;
        let activeBrand = 'all', searchTerm = '';
        function brandClass(b) {{ return {{'FANUC':'brand-fanuc','三菱':'brand-mitsubishi','西门子':'brand-siemens','Mazak':'brand-mazak','大隈':'brand-okuma','哈斯':'brand-haas'}}[b]||''; }}
        function renderTable() {{
            const filtered = COMPAT_DATA.filter(item => {{
                const bm = activeBrand === 'all' || item[0] === activeBrand;
                const sm = !searchTerm || item.some(v => String(v).toLowerCase().includes(searchTerm.toLowerCase()));
                return bm && sm;
            }});
            document.getElementById('resultCount').textContent = (searchTerm || activeBrand !== 'all') ? '显示 '+filtered.length+' / '+COMPAT_DATA.length+' 个型号' : '共 '+COMPAT_DATA.length+' 个兼容型号，覆盖 6 大品牌';
            document.getElementById('noResults').style.display = filtered.length ? 'none' : 'block';
            document.getElementById('tableBody').innerHTML = filtered.map(item => '<tr><td><span class="brand-tag '+brandClass(item[0])+'">'+item[0]+'</span></td><td><strong>'+item[1]+'</strong></td><td>'+item[2]+'</td><td>'+item[3]+'</td><td>'+item[4]+'</td><td>'+item[5]+'</td><td><span class="status-available">'+item[6]+'</span></td><td><a href="'+item[7]+'" class="action-link">查看详情 →</a></td></tr>').join('');
        }}
        function filterBrand(brand) {{
            activeBrand = brand;
            document.querySelectorAll('.brand-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            renderTable();
        }}
        document.getElementById('searchInput').addEventListener('input', e => {{ searchTerm = e.target.value.trim(); renderTable(); }});
        renderTable();
    </script>
</body>
</html>'''
    html = page.replace('__DATA__', data_json).replace('__SAMEAS__', sameas_json)
    w(BASE / 'compatibility-matrix.html', html)
    print("[OK] ZH compatibility tool built")
    print("[OK] ZH compatibility tool built")

# ═══ Add definition blocks to key articles ═══
def add_definition(filepath, html_block):
    c = r(filepath)
    if 'definition-block' in c:
        print(f"  [SKIP] {filepath.name}")
        return
    h1_end = c.find('</h1>')
    if h1_end == -1: return
    c = c[:h1_end+5] + '\n' + html_block + '\n' + c[h1_end+5:]
    w(filepath, c)
    print(f"  [DEF] {filepath.name}")

def add_definitions():
    defs_en = {
        'posts/article_20260503_FANUC_A61L_0001_0093_LCD.html': '<div class="definition-block" style="background:#f0f7ff;border-left:4px solid #2563eb;padding:1rem 1.2rem;margin:1rem 0;border-radius:0 8px 8px 0;font-size:1.05rem;line-height:1.7;"><p><strong>FANUC A61L-0001-0093 是</strong>发那科数控系统广泛使用的 9 英寸单色 CRT 显示器模块，配套 FANUC 0 系列、0i 系列、OM-D 等数控系统。该模块采用 HONDA 20 针信号接口，DC 24V 供电，分辨率 640×400，设计寿命约 15,000 小时。江图科技提供即插即用工业级 TFT-LCD 替代方案——分辨率升级至 800×600，亮度从 200cd/m² 提升至 350-450cd/m²，功耗从 25-30W 降至 8-12W（节能 60% 以上），使用寿命延长至 50,000+ 小时，安装仅需 10-15 分钟，无需修改 CNC 参数。</p></div>',
        'en/posts/article_20260503_FANUC_A61L_0001_0093_LCD.html': '<div class="definition-block" style="background:#f0f7ff;border-left:4px solid #2563eb;padding:1rem 1.2rem;margin:1rem 0;border-radius:0 8px 8px 0;font-size:1.05rem;line-height:1.7;"><p><strong>The FANUC A61L-0001-0093</strong> is a 9-inch monochrome CRT display unit used in FANUC CNC systems including 0 series, 0i series, and OM-D controllers. It features a HONDA 20-pin signal connector, DC 24V power input, 640×400 resolution, and approximately 15,000-hour design life. Kongto Technology provides a plug-and-play industrial TFT-LCD replacement that upgrades resolution to 800×600, boosts brightness from 200cd/m² to 350-450cd/m², reduces power consumption from 25-30W to 8-12W (60%+ savings), extends lifespan to 50,000+ hours, and installs in 10-15 minutes with no CNC parameter changes.</p></div>',
    }
    for path, html in defs_en.items():
        fp = BASE / path
        if fp.exists(): add_definition(fp, html)

# ═══ RUN ═══
if __name__ == "__main__":
    print("=== Building Interactive Tools ===")
    build_en()
    build_zh()
    print("\n=== Adding Definition Blocks ===")
    add_definitions()
    print("\n=== Complete ===")
