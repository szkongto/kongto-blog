"""HTML → PDF using Playwright. Usage:

  python scripts/html2pdf.py input.html output.pdf
  python scripts/html2pdf.py input.html output.pdf --format A4 --margin 15mm
  python scripts/html2pdf.py https://example.com output.pdf
"""
import sys, os
from playwright.sync_api import sync_playwright

def html_to_pdf(source, output, fmt="A4", margin="15mm"):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        if source.startswith("http://") or source.startswith("https://"):
            page.goto(source, wait_until="networkidle")
        else:
            page.goto(f"file:///{os.path.abspath(source)}", wait_until="networkidle")
        page.pdf(path=output, format=fmt, margin={"top": margin, "bottom": margin, "left": margin, "right": margin}, print_background=True)
        browser.close()
    print(f"PDF saved: {output} ({os.path.getsize(output)//1024} KB)")

if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src.rsplit(".", 1)[0] + ".pdf"
    fmt = sys.argv[sys.argv.index("--format") + 1] if "--format" in sys.argv else "A4"
    margin = sys.argv[sys.argv.index("--margin") + 1] if "--margin" in sys.argv else "15mm"
    html_to_pdf(src, dst, fmt, margin)
