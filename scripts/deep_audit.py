#!/usr/bin/env python3
"""Deep audit: for each WEIGHT_LOSS_HOMEPAGE redirect, check if a proper target exists."""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get all existing HTML files
all_posts = set()
all_products = set()
for f in os.listdir(os.path.join(ROOT, 'posts')):
    if f.endswith('.html'):
        all_posts.add(f)
for f in os.listdir(os.path.join(ROOT, 'products')):
    if f.endswith('.html'):
        all_products.add(f)

# Mapping of Chinese URL keywords to English target files
# Based on the _redirects analysis
checks = [
    # (line, src_description, Chinese_keywords_to_search, search_in_posts)
    (169, "三菱BM09DF", "BM09DF", "Mitsubishi_BM09DF"),
    (170, "三菱FCUA-CT100", "FCUA", "Mitsubishi_FCUA"),
    (171, "三菱MDT962B", "MDT962B", "Mitsubishi_MDT962B"),
    (172, "三菱MDT962B系列", "MDT962B_Series", "Mitsubishi_MDT962B_Series"),
    (87, "FANUC 0i FAQ", "0i", "fanuc-0i-display-faq"),
    (103, "工业数控设备显示器故障诊断", "Troubleshooting", "Industrial_CNC_Display_Troubleshooting"),
    (104, "工业视频信号转换器在CNC", "Video_Signal_Converters", "Video_Signal_Converters_in_CNC"),
    (105, "CGA_EGA转VGA", "Video_Signal_Conversion", "Video_Signal_Conversion_System"),
    (106, "工业视频显示在智能工厂", "Smart_Factory", "Industrial_Video_Display_Smart_Factory"),
    (107, "江图科技工业视频显示产品目录", "Product_Catalog", "Kongto_Technology_Industrial_Video"),
    (85, "工业视频信号转换器选型指南", "video_converter", "comparison_20260501_video_converter"),
    (86, "FANUC 0i系统显示器常见问题", "0i", "fanuc-0i-display-faq"),
    (90, "数控机床显示器更换TOP10", "CNC_display_replacement_FAQ", "faq_20260501_CNC_display_replacement_FAQ"),
    (127, "gbs-8219 converter", "GBS-8219", "article_20260509_GBS-8219_RGB_to_VGA_converter"),
    (128, "kt809 converter", "KT809", "article_20260509_KT809_industrial_converter"),
    (129, "kt819 converter", "KT819", "article_20260509_KT819_industrial_converter"),
    (83, "Mitsubishi M70/M700", "M70", "Mitsubishi_M70"),
    (84, "Siemens ROI", "Siemens", "Siemens_Display_Upgrade_Cost_ROI"),
    (122, "custom-industrial-display-series-zh", "custom_industrial", "custom_industrial_display"),
    (131, "非标订制显示器系列", "custom_industrial", "custom_industrial_display"),
    (168, "工业显示器RGBHV改造", "RGBHV", "Industrial_RGBHV"),
    (173, "江图科技FANUC LCD", "press_release", "Beijing_Zhongbo_FANUC"),
    (174, "数控显示器升级市场动态", "social", "Industrial_Display_Market"),
]

print("=== HOMEPAGE REDIRECTS WITH REAL TARGET PAGES ===\n")
found_count = 0
for line, desc, keyword, search_term in checks:
    matches = [f for f in all_posts if search_term.lower() in f.lower()]
    if matches:
        found_count += 1
        print("  Line %d: %s" % (line, desc))
        print("    CORRECT TARGET EXISTS: %s" % matches[0])
        print()

print("\nTotal homepage redirects with real target pages: %d" % found_count)

# Also check the case-sensitivity 404 issues
print("\n=== CASE SENSITIVITY 404 CHECK ===\n")
case_issues = [
    (76, "GBS-8219_RGB_to_VGA_Converter.html", "GBS-8219_RGB_to_VGA_converter.html"),
    (77, "GBS_8219_RGB_to_VGA_Converter_CN.html", "GBS-8219_RGB_to_VGA_converter.html"),
    (78, "KT809_Industrial_Converter.html", "KT809_industrial_converter.html"),
    (79, "KT819_Industrial_Converter.html", "KT819_industrial_converter.html"),
    (219, "KT809_Industrial_Converter.html", "KT809_industrial_converter.html"),
]
for line, wrong_target, correct_file in case_issues:
    exists = correct_file in all_posts
    print("  Line %d: DST=%s" % (line, wrong_target))
    print("    CORRECT FILE: %s -> %s" % (correct_file, "EXISTS" if exists else "MISSING"))
    print()

# Check faq_20260501_CNC_Display_Replacement_FAQ_TOP10_CN.html
print("=== FAQ TOP10 CN target check ===")
faq_targets = [f for f in all_posts if "CNC_display_replacement_FAQ" in f.lower() or "CNC_Display_Replacement_FAQ" in f]
print("  Files matching: %s" % faq_targets)
# The redirect target is faq_20260501_CNC_Display_Replacement_FAQ_TOP10_CN.html
# But there's also a redirect on line 314 that sends it to faq_20260501_CNC_display_replacement_FAQ.html
# So there's a chain issue

# Check DR5614 LCD CRT file
print("\n=== DR5614 LCD CRT file check ===")
dr5614_files = [f for f in all_posts if "DR5614" in f]
print("  DR5614 files in posts/: %s" % dr5614_files)
# Line 315 redirects to article_20260522_Mazak_DR5614_LCD_CRT.html but this doesn't exist
# The zh version exists though

# Check okuma-osp-crt-lcd-upgrade.html
print("\n=== Okuma OSP product page check ===")
okuma_files = [f for f in all_products if "okuma" in f.lower()]
print("  Okuma product files: %s" % okuma_files)

# Check /docs/ directory
print("\n=== /docs/ directory check ===")
docs_dir = os.path.join(ROOT, 'docs')
if os.path.isdir(docs_dir):
    has_index = os.path.exists(os.path.join(docs_dir, 'index.html'))
    print("  /docs/ exists, has index.html: %s" % has_index)
else:
    print("  /docs/ directory does not exist")
