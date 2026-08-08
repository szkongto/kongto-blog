#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-off: add TechArticle JSON-LD to article pages missing it (P0-3b).
- EN posts/ + ZH zh/posts/
- Skip files that already have application/ld+json
- Skip redirect stubs (meta refresh)
- Date source: filename article_YYYYMMDD_, else git first commit date (real, not fabricated)
- Type: TechArticle to match existing 233-article site convention
Insert JSON-LD before </head>.
"""
import re, glob, json, subprocess, sys

def git_first_date(path):
    try:
        out = subprocess.run(
            ["git", "log", "--follow", "--format=%cI", "--", path],
            capture_output=True, text=True, cwd=".")
        lines = [l for l in out.stdout.splitlines() if l.strip()]
        if lines:
            return lines[-1][:10]  # first commit date YYYY-MM-DD
    except Exception:
        pass
    return None

def extract_title(h):
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    if not m:
        return None
    t = m.group(1).strip()
    # strip site suffix like " | cncdisplay.com", " - cncdisplay.com", "—Compl..."
    for pat in [r"\s*[|\-–—]\s*cncdisplay\.com\s*$", r"\s*[|\-–—]\s*.*?cncdisplay.*$"]:
        t2 = re.sub(pat, "", t).strip()
        if t2:
            t = t2
    return t

def extract_desc(h):
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', h)
    if not m:
        m = re.search(r'<meta\s+content="([^"]*)"\s+name="description"', h)
    return m.group(1) if m else ""

def extract_date(path):
    m = re.search(r"article_(\d{4})(\d{2})(\d{2})", path)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return git_first_date(path)

def main():
    files = sorted(glob.glob("posts/*.html") + glob.glob("zh/posts/*.html"))
    changed = []
    for path in files:
        h = open(path, encoding="utf-8", errors="ignore").read()
        if "application/ld+json" in h:
            continue
        if 'http-equiv="refresh"' in h or "meta http-equiv=refresh" in h:
            continue  # redirect stub
        title = extract_title(h)
        desc = extract_desc(h)
        date = extract_date(path)
        if not title or not date:
            print(f"SKIP (no title/date): {path} title={title!r} date={date!r}")
            continue
        url = "https://cncdisplay.com/" + path
        block = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": title,
            "description": desc,
            "url": url,
            "author": {"@type": "Person", "name": "Kongto Technology"},
            "publisher": {"@type": "Organization", "name": "Shenzhen Kongto Technology",
                          "url": "https://cncdisplay.com"},
            "datePublished": date,
        }
        ld = json.dumps(block, ensure_ascii=False, indent=2)
        script = f'    <script type="application/ld+json">\n{ld}\n    </script>\n'
        if "</head>" in h:
            h = h.replace("</head>", script + "</head>", 1)
        else:
            print(f"SKIP (no </head>): {path}")
            continue
        open(path, "w", encoding="utf-8").write(h)
        changed.append(path)
        print(f"ADDED: {path} date={date}")

    print(f"\nTotal added: {len(changed)}")

if __name__ == "__main__":
    main()
