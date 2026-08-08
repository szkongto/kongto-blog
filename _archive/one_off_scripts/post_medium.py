#!/usr/bin/env python3
"""Medium — 打开编辑器 + 生成内容，你粘贴发布（30秒）"""
import webbrowser, csv
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).parent
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
DAY_NUM = datetime.now().timetuple().tm_yday

ARTICLES = [
    {
        "title": "CNC CRT to LCD Retrofit: The Industrial Display Upgrade That Pays for Itself in 3 Months",
        "body": """Every machine shop with legacy CNC equipment faces the same problem: the CRT displays are dying. These screens were designed for 10-15 years. They're now at year 20-30.

## The Economics

CRT repair: $300-800 every 3-12 months. Over 5 years: $2,000-4,000 per machine.

Industrial LCD retrofit: $150-280 once. 10 minute installation. 5-7 year lifespan.

ROI is under 3 months for most shops.

## Multi-Brand Connector Reference

- FANUC: Honda MR-20M (20-pin), DC24V
- Mitsubishi: 20/26-pin, DC24V
- Mazak: 26-pin, DC24V
- Siemens: DB-25, **AC110V** (not DC!)
- Okuma: 14/20-pin, DC24V
- Haas: 9-pin D-Sub, DC12V

The Siemens AC110V difference is the #1 cause of destroyed LCD modules. Always verify before ordering.

Full guides and compatibility matrix: https://cncdisplay.com""",
    },
    {
        "title": "Why Repairing Your CNC CRT Is Throwing Money Away: A 5-Year Cost Analysis",
        "body": """I've watched too many shops spend thousands nursing dying CRTs. Here's the actual math.

## Real Numbers from One Shop

12 FANUC 0i-C CNC lathes. Over 18 months:
- Machine 3: 3 repairs, $1,350 total
- Machine 7: 2 repairs, $750
- Machine 11: 1 repair, $500
- Others: various repairs, $3,000+

**Total: $5,600+ in repairs. Plus 15+ days of downtime.**

## The Fix

Replaced all 12 CRTs with industrial LCD modules. Total cost: under $3,000. Total installation time: 3 hours for the entire fleet.

That was 2023. Zero LCD failures since.

## Why CRT Repairs Always Fail

Global CRT production ended 15+ years ago. Every "repair" uses donor parts from other 20+ year old units. You're not fixing anything — you're transferring remaining lifespan from one dying display to another.

## The Bottom Line

One LCD module costs less than 2 CRT repairs. It lasts 5-7 years. Installation takes 10 minutes with a screwdriver.

For $150-280, you eliminate the CRT failure cycle permanently.

Full cost comparison and model guides: https://cncdisplay.com""",
    },
]

if __name__ == '__main__':
    article = ARTICLES[DAY_NUM % len(ARTICLES)]

    # Save content
    out = BASE / "backlinks_daily" / TODAY
    out.mkdir(exist_ok=True)
    f = out / "medium_post.txt"
    f.write_text(f"TITLE:\n{article['title']}\n\nBODY:\n{article['body']}", encoding='utf-8')
    print(f"[Medium] Content saved → {f}")

    # Open Medium editor
    webbrowser.open("https://medium.com/new-story")
    print("[Medium] Browser opened → paste title + body → click Publish")

    # Track
    tracker = BASE / "backlinks_daily" / "post_tracker.csv"
    with open(tracker, 'a', newline='', encoding='utf-8') as fh:
        csv.writer(fh).writerow([TODAY, "Medium", article["title"][:120], "manual", "pending"])
