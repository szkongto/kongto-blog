"""Batch restore Chinese text from pre-corruption git version"""
import subprocess, re, sys
from pathlib import Path

ROOT = Path("d:/code/seo_deploy")
sys.stdout.reconfigure(encoding='utf-8')

FILES = [
    "en/brands/MAZAK.html",
    "en/posts/article_20260508_Haas_CRT_LCD_Case.html",
    "en/posts/article_20260508_KTV104_custom_industrial_display.html",
    "en/posts/article_20260508_KTV148_custom_industrial_display.html",
    "en/posts/article_20260508_KTV800M_custom_industrial_display.html",
    "en/posts/article_20260508_KTV804_custom_industrial_display.html",
    "en/posts/comparison_20260501_video_converter_buying_guide.html",
    "en/posts/faq_20260501_FANUC_0idisplay_faq.html",
    "products/fanuc-a61l-0001-0093-lcd-upgrade.html",
    "products/mitsubishi-mdt962b-lcd-upgrade.html",
    "products/siemens-6fc3988-7fa20-lcd-upgrade.html",
    "zh/brands/FANUC.html",
    "zh/brands/MAZAK.html",
    "zh/products/fanuc-a61l-0001-0093-lcd-upgrade.html",
    "zh/products/mitsubishi-mdt962b-lcd-upgrade.html",
    "zh/products/siemens-6fc3988-7fa20-lcd-upgrade.html",
]

def restore(rel):
    f = ROOT / rel
    if not f.exists():
        print(f"  SKIP {rel}")
        return False
    r = subprocess.run(["git", "show", f"7001d17c^:{rel}"],
        capture_output=True, encoding='utf-8', cwd=ROOT, timeout=10)
    if r.returncode != 0:
        print(f"  FAIL {rel} (no history)")
        return False
    text = r.stdout.replace('sales@cncdisplay.com', 'info@cncdisplay.com')
    f.write_text(text, 'utf-8')
    print(f"  RESTORED: {rel}")
    return True

print(f"Restoring {len(FILES)} files...\n")
fixed = sum(1 for rel in FILES if restore(rel))
print(f"\nFixed: {fixed}/{len(FILES)}")
