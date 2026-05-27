"""Unify company info across all HTML files in seo_deploy/."""
import json, os, re, glob

ROOT = "d:/code/seo_deploy"

def fix_file(filepath):
    with open(filepath, "rb") as f:
        raw = f.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False  # binary file

    original = text

    # 1. Remove 1688 from visible HTML (list items and links)
    text = re.sub(
        r'<a\s+href="https://szkongto\.1688\.com"[^>]*>.*?</a>',
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'<li[^>]*>.*?szkongto\.1688\.com.*?</li>\s*', "", text, flags=re.IGNORECASE
    )
    text = re.sub(
        r'<li><strong>1688[^<]*</strong>.*?</li>\s*', "", text, flags=re.IGNORECASE
    )

    # 2. Replace sales@cncdisplay.com with szkongto01@foxmail.com
    text = text.replace("sales@cncdisplay.com", "szkongto01@foxmail.com")

    # 3. Fix address: 龙华区 → 龙岗区
    text = text.replace("龙华区大浪街道陶元社区恒昌荣工业园C栋2楼", "龙岗区横岗街道深坑综合楼2号楼C栋4楼")
    # Fix geo placename
    text = text.replace('content="深圳龙华"', 'content="深圳龙岗"')

    # 4. Fix company name format
    text = text.replace("Kongto Technology Co., Ltd.", "Kongto Technology Co.,LTD")
    text = text.replace("Kongto Technology Co., Ltd", "Kongto Technology Co.,LTD")
    text = text.replace("Kongto Technology Co.,Ltd.", "Kongto Technology Co.,LTD")
    text = text.replace("Kongto Technology Co.,Ltd", "Kongto Technology Co.,LTD")

    # 5. Remove 1688 from JSON-LD sameAs arrays
    # Strategy: find all <script type="application/ld+json"> blocks, parse, fix, re-serialize
    def fix_jsonld(match):
        block = match.group(0)
        try:
            # Extract JSON content
            json_start = block.index("{")
            json_end = block.rindex("}") + 1
            json_str = block[json_start:json_end]
            data = json.loads(json_str)

            # Remove 1688 from sameAs
            if "sameAs" in data and isinstance(data["sameAs"], list):
                data["sameAs"] = [s for s in data["sameAs"] if "1688.com" not in s]

            # Fix address
            if "address" in data and isinstance(data["address"], dict):
                addr = data["address"]
                if "streetAddress" in addr and "龙华" in addr["streetAddress"]:
                    addr["streetAddress"] = "龙岗区横岗街道深坑综合楼2号楼C栋4楼"

            new_json = json.dumps(data, ensure_ascii=False, indent=2)
            return block[:json_start] + new_json + block[json_end:]
        except (json.JSONDecodeError, ValueError, KeyError):
            return block

    text = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        fix_jsonld,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if text != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    return False


def main():
    count = 0
    for root_dir, dirs, files in os.walk(ROOT):
        # Skip non-seo_deploy dirs
        if "seo_fix_package" in root_dir or "output" in root_dir:
            continue
        for fname in files:
            if fname.endswith((".html", ".jsonld", ".md")):
                path = os.path.join(root_dir, fname)
                if fix_file(path):
                    print(f"  Fixed: {os.path.relpath(path, ROOT)}")
                    count += 1

    print(f"\nTotal files modified: {count}")

    # Also handle standalone JSON-LD files in schema/
    schema_dir = os.path.join(ROOT, "schema")
    if os.path.isdir(schema_dir):
        for fname in os.listdir(schema_dir):
            path = os.path.join(schema_dir, fname)
            if fix_file(path):
                print(f"  Fixed: schema/{fname}")
                count += 1

    print(f"\nGrand total: {count}")


if __name__ == "__main__":
    main()
