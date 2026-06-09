"""Fix broken/short meta descriptions automatically using title/h1 content."""
import re, os

# Product-related keywords for enrichment
PRODUCT_PREFIX = "深圳市江图科技有限公司（Kongto Technology）专注工业视频显示解决方案，"

def generate_desc(filepath, content):
    """Generate a meta description from page title and h1."""
    # Extract title
    m = re.search(r'<title>(.*?)</title>', content)
    title = m.group(1).strip() if m else ""

    # Extract h1
    m = re.search(r'<h1[^>]*>(.*?)</h1>', content)
    h1 = m.group(1).strip() if m else ""

    # Clean HTML tags from h1
    h1 = re.sub(r'<[^>]+>', '', h1)
    title = title.replace(" | 深圳市江图科技有限公司", "").strip()

    # Build description from title or h1
    base = title if title else h1

    # If it's a product article, add enrichment
    if any(kw in base for kw in ['FANUC', '三菱', 'Mitsubishi', 'Siemens', '西门子', 'Mazak', '马扎克', 'LCD', 'CRT', '显示器']):
        desc = f"{base}。江图科技12年工业显示经验，覆盖FANUC发那科、三菱、西门子、马扎克等全品牌CNC数控系统CRT转LCD升级改造方案，即插即用零改装，2年质保。"
    else:
        desc = f"{base}。江图科技专注工业视频显示解决方案，提供CNC数控系统显示器CRT转LCD升级改造、工业视频信号转换器及非标定制工控显示器。"

    # Truncate to ~155 chars
    if len(desc) > 160:
        desc = desc[:157] + "..."

    return desc

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Patterns that indicate a broken/bogus meta description
    BROKEN_PATTERNS = [
        r'content="---"',                          # placeholder
        r'content="> 关键词',                       # keyword list instead of desc
        r'content="作者：',                          # author instead of desc
        r'content="FANUC A61L.*\| 江图科技"',       # too short, just title
        r'content=".{1,69}"',                       # under 69 chars
    ]

    BROKEN_PATTERNS_RE = [re.compile(p) for p in BROKEN_PATTERNS]

    count = 0
    for root, dirs, files in os.walk('.'):
        if 'seo_fix_package' in root or 'output' in root:
            continue
        for fname in files:
            if not fname.endswith('.html'):
                continue
            filepath = os.path.join(root, fname)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Find current meta description
            m = re.search(r'<meta name="description" content="([^"]*)"', content)
            if not m:
                continue
            current = m.group(1)

            # Check if broken
            broken = False
            for pat in BROKEN_PATTERNS_RE:
                if pat.search(f'content="{current}"'):
                    broken = True
                    break
            # Extra checks: just "---" or keyword-only descriptions
            if current.strip() in ('---', '') or current.startswith('> 关键词') or current.startswith('作者：'):
                broken = True

            if not broken:
                continue

            new_desc = generate_desc(filepath, content)
            old = content
            content = content.replace(
                f'content="{current}"',
                f'content="{new_desc}"',
                1,
            )
            if content != old:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  Fixed: {filepath} ({len(current)} -> {len(new_desc)} chars)")
                count += 1

    print(f"\nTotal fixed: {count}")

if __name__ == "__main__":
    main()
