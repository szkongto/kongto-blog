"""Rebuild all GEO optimizations from last successful commit."""
import os, re, json
from pathlib import Path
from datetime import datetime

BASE = Path(r"d:\code\seo_deploy")
EXCLUDE = {"lang_link_backup_", "geo_backup_", "seo_backup_",
           "images_backup_", "backlinks_", "browser_profile",
           "hashnode_articles", ".git"}

YOUTUBE = "https://www.youtube.com/@Cncdisplay"
LINKEDIN = "https://www.linkedin.com/in/%E5%AE%87%E6%B3%A2-%E9%83%AD-4b61543b3/"
SAMEAS_FULL = ["https://blog.csdn.net/szkongto", "https://github.com/szkongto", YOUTUBE, LINKEDIN]

def find_html_files():
    files = []
    for root, dirs, fnames in os.walk(BASE):
        dirs[:] = [d for d in dirs if not any(d.startswith(e) for e in EXCLUDE)]
        for f in fnames:
            if f.endswith('.html'):
                files.append(Path(root) / f)
    return files

def read_file(p):
    with open(p, 'r', encoding='utf-8') as f: return f.read()
def write_file(p, c):
    with open(p, 'w', encoding='utf-8') as f: f.write(c)

# ═══════════════════════════════════════════
# 1. Update llms.txt
# ═══════════════════════════════════════════
def update_llms():
    content = """# Kongto Technology (cncdisplay.com) - AI-Friendly Content Index
# Generated: 2026-06-20 | Updated for GEO optimization
# Purpose: Help AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google AI) understand our site
# About: Industrial CNC display CRT to LCD upgrade solutions since 2013
# Contact: szkongto01@foxmail.com | +86-13686889647

## Company Overview
- Name: Kongto Technology (深圳市江图科技有限公司)
- Founded: 2013
- Location: Shenzhen, Guangdong, China
- Specialty: Industrial CNC display upgrades, CRT-to-LCD retrofit, video signal converters
- Clients: 500+ enterprises across 12+ countries
- Warranty: 2 years on all products
- Certifications: CE, RoHS 2.0, FCC, ISO 9001:2015, IP65

## Key Facts (Citation-Ready Data Points)
- Industrial LCD lifespan: 50,000+ hours vs CRT 15,000 hours (3.3x improvement)
- LCD power consumption: 8-12W vs CRT 25-30W (60%+ energy savings)
- Installation time: 10-15 minutes per CNC machine, plug-and-play
- Brightness upgrade: LCD 350-450cd/m² vs CRT 200cd/m² (new) / <100cd/m² (aged)
- CRT anode voltage: 10-15kV (safety hazard when aged)
- Working temperature: -20°C to 60°C (LCD) vs 0-40°C (CRT)
- Products: FANUC A61L-0001(0074-0097), D9MM-11A | Mitsubishi MDT962B/BM09DF/FCUA-CT100 | Siemens 6FC3988/SM0901 | Mazak CD1472/C5470/DR5614 | Okuma OSP 5000/5020 | Haas VF/ST/SL

## Key Pages
- Home (EN): https://cncdisplay.com/en/index.html
- Home (ZH): https://cncdisplay.com/
- About: https://cncdisplay.com/about.html
- Compatibility Lookup: https://cncdisplay.com/en/compatibility-matrix.html - Interactive CRT→LCD lookup tool
- Compatibility (ZH): https://cncdisplay.com/compatibility-matrix.html - 中文版兼容性查询

## Brand Pages
- FANUC: https://cncdisplay.com/en/brands/FANUC.html
- Mitsubishi: https://cncdisplay.com/en/brands/Mitsubishi.html
- Siemens: https://cncdisplay.com/en/brands/Siemens.html
- Mazak: https://cncdisplay.com/en/brands/MAZAK.html
- Okuma: https://cncdisplay.com/en/brands/OKUMA.html
- Haas: https://cncdisplay.com/en/brands/HAAS.html

## Social & Video
- YouTube: https://www.youtube.com/@Cncdisplay
- LinkedIn: https://www.linkedin.com/in/%E5%AE%87%E6%B3%A2-%E9%83%AD-4b61543b3/
- CSDN Blog: https://blog.csdn.net/szkongto
- GitHub: https://github.com/szkongto

## FAQ Topics (AI Citation Ready)
- Q: What is FANUC A61L-0001-0093? → A 9-inch monochrome CRT display for FANUC CNC systems, replaced by Kongto's industrial TFT-LCD module (800x600, 350-450cd/m², 50,000+ hour lifespan, plug-and-play)
- Q: How to upgrade FANUC CRT to LCD? → See FANUC brand page; all solutions plug-and-play, 10-15 min install
- Q: Is LCD upgrade compatible with my CNC? → Check compatibility matrix or email photo to szkongto01@foxmail.com
- Q: Do I need to change CNC parameters? → No, all solutions use original connectors, DC 24V power
- Q: Warranty? → 2 years on all products, lifetime technical support

## Sitemap
- XML: https://cncdisplay.com/sitemap.xml
- RSS: https://cncdisplay.com/feed.xml
"""
    write_file(BASE / 'llms.txt', content)
    print("[OK] llms.txt updated")

# ═══════════════════════════════════════════
# 2. Update robots.txt with RSL annotation
# ═══════════════════════════════════════════
def update_robots():
    c = read_file(BASE / 'robots.txt')
    if 'RSL' not in c:
        c = c.replace("Content-Signal:", "# RSL 1.0: Allow AI search, disallow AI training\nContent-Signal:")
        write_file(BASE / 'robots.txt', c)
        print("[OK] robots.txt RSL annotation added")
    else:
        print("[OK] robots.txt already has RSL")

# ═══════════════════════════════════════════
# 3. Add sameAs + Person schema to all pages
# ═══════════════════════════════════════════
def process_html_files():
    files = find_html_files()
    person_added = sameas_updated = 0

    person_schema = '''    <script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "江图科技技术部",
  "alternateName": "Kongto Technical Team",
  "jobTitle": "Industrial Display Engineer",
  "worksFor": {
    "@type": "Organization",
    "name": "深圳市江图科技有限公司",
    "url": "https://cncdisplay.com"
  },
  "description": "专注工业视频显示领域12年以上的工程师团队，提供CNC数控系统CRT转LCD升级解决方案",
  "url": "https://cncdisplay.com",
  "sameAs": [SAMEAS_PLACEHOLDER]
}
    </script>
'''

    for fp in files:
        try:
            c = read_file(fp)
            orig = c
            modified = False

            # Add sameAs to Organization/LocalBusiness schemas
            if '"sameAs"' in c:
                def fix_sameas(m):
                    nonlocal modified
                    block = m.group(0)
                    jm = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>\s*(.*?)\s*</script>', block, re.DOTALL)
                    if not jm: return block
                    try:
                        d = json.loads(jm.group(1))
                        if isinstance(d, dict) and 'sameAs' in d:
                            ex = [str(x) for x in d['sameAs']] if isinstance(d['sameAs'], list) else [str(d['sameAs'])]
                            for p in SAMEAS_FULL:
                                if p not in ex: ex.append(p)
                            d['sameAs'] = ex
                            nj = json.dumps(d, ensure_ascii=False, indent=2)
                            modified = True
                            return block.replace(jm.group(1), nj, 1)
                    except: pass
                    return block
                pattern = r'<script[^>]*type="application/ld\+json"[^>]*>.*?</script>'
                c = re.sub(pattern, fix_sameas, c, flags=re.DOTALL)
                if c != orig: sameas_updated += 1

            # Add Person schema to article pages (has Article schema, no Person)
            has_article = '"@type": "Article"' in c or '"@type":"Article"' in c
            has_person = '"@type": "Person"' in c or '"@type":"Person"' in c
            if has_article and not has_person:
                ps = person_schema.replace('SAMEAS_PLACEHOLDER', json.dumps(SAMEAS_FULL, ensure_ascii=False))
                last_sc = c.rfind('</script>', 0, c.find('</head>'))
                if last_sc != -1:
                    c = c[:last_sc+9] + '\n' + ps + c[last_sc+9:]
                else:
                    he = c.find('</head>')
                    if he != -1: c = c[:he] + ps + '\n' + c[he:]
                if c != orig: person_added += 1

            if c != orig: write_file(fp, c)
        except Exception as e:
            print(f"  [ERR] {fp.name}: {e}")

    print(f"[OK] Person schema added: {person_added} | sameAs updated: {sameas_updated}")

# ═══════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════
if __name__ == "__main__":
    print("=== GEO Rebuild ===")
    update_llms()
    update_robots()
    process_html_files()
    print("=== Complete ===")
