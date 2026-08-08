#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-off (P1-3): unify site contact email to info@cncdisplay.com (primary).
- HTML: replace sales@cncdisplay.com -> info@cncdisplay.com in all live pages
  (footer-copy, product copyright, article JSON-LD email, contact lists, prose, mailto)
- Non-HTML live files: replace legacy szkongto01@foxmail.com -> info@cncdisplay.com
  (.well-known/security.txt, schema/organization.jsonld, llms-full.txt, rsl.txt)
- sales@ retained as secondary in data/company-info.json (single source), not deleted.
Skips .git, en_bak (backup), _archive.
"""
import glob, re, sys

FOX = "szkongto01@foxmail.com"
SALES = "sales@cncdisplay.com"
INFO = "info@cncdisplay.com"

def html_files():
    out = []
    for f in glob.glob("**/*.html", recursive=True):
        if ".git" in f or "en_bak" in f or "_archive" in f:
            continue
        out.append(f)
    return out

def main():
    total_sales = 0
    html_changed = 0
    for f in html_files():
        h = open(f, encoding="utf-8", errors="ignore").read()
        n = h.count(SALES)
        if n:
            h = h.replace(SALES, INFO)
            open(f, "w", encoding="utf-8").write(h)
            html_changed += 1
            total_sales += n
    print(f"[HTML] {html_changed} files, {total_sales} sales@ -> info@")

    targets = [".well-known/security.txt", "schema/organization.jsonld",
               "llms-full.txt", "rsl.txt"]
    for t in targets:
        try:
            s = open(t, encoding="utf-8", errors="ignore").read()
        except FileNotFoundError:
            print(f"  MISSING: {t}")
            continue
        if FOX in s:
            s = s.replace(FOX, INFO)
            open(t, "w", encoding="utf-8").write(s)
            print(f"  [NON-HTML] {t}: foxmail -> info@")
        else:
            print(f"  [OK] {t}: no foxmail")

if __name__ == "__main__":
    main()
