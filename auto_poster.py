#!/usr/bin/env python3
"""
cncdisplay.com 自动外链发布器
==============================
一键发布到所有有API的平台：Dev.to, Hashnode
其他平台生成URL预填链接

使用：
  python auto_poster.py devto     # 发布到Dev.to
  python auto_poster.py hashnode  # 发布到Hashnode
  python auto_poster.py all       # 发布所有API平台
  python auto_poster.py setup     # 检查配置状态

首次使用：去 https://dev.to/settings/extensions 创建API Key
"""

import json, os, sys, requests
from pathlib import Path

BASE = Path(__file__).parent
OUTPUT = BASE / "backlinks_output"
CONFIG_FILE = BASE / "auto_poster_config.json"

# ============================================================
# 配置管理
# ============================================================
def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
    return {}

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding='utf-8')

def check_setup():
    cfg = load_config()
    print("=== API Key 配置状态 ===\n")
    platforms = {
        "devto": ("Dev.to (DA 92)", "https://dev.to/settings/extensions → Generate API Key", "devto_api_key"),
        "hashnode": ("Hashnode (DA 82)", "https://hashnode.com/settings/developer → Generate PAT", "hashnode_pat"),
        "medium": ("Medium (DA 95)", "https://medium.com/me/settings/security → Integration tokens", "medium_token"),
    }
    for key, (name, url, field) in platforms.items():
        if field in cfg:
            print(f"  [OK] {name} - 已配置")
        else:
            print(f"  [--] {name} - 未配置 → {url}")

    if not cfg:
        print("\n至少配置一个平台即可自动发文。")
        print("推荐从 Dev.to 开始（免费，30秒获取API Key）\n")

# ============================================================
# Dev.to API (最简单，优先)
# ============================================================
def get_devto_article():
    """获取Dev.to文章内容"""
    content_file = OUTPUT / "blog_dev.to.md"
    content = content_file.read_text(encoding='utf-8')
    # 提取标题（第一行 # 后的内容）
    lines = content.split('\n')
    title = ""
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith('### 标题') and i+1 < len(lines):
            title = lines[i+1].strip()
        if line.startswith('### 正文') or line == '### 正文':
            body_start = i + 1
            break
    body = '\n'.join(lines[body_start:]).strip()
    # Remove trailing notes
    if '---' in body:
        body = body.split('---')[0].strip()
    return title, body

def post_to_devto():
    """自动发布到Dev.to"""
    cfg = load_config()
    api_key = cfg.get("devto_api_key")
    if not api_key:
        print("[ERROR] Dev.to API Key 未配置")
        print("获取方法: https://dev.to/settings/extensions → Generate API Key")
        print("然后运行: python auto_poster.py setup devto YOUR_KEY")
        return False

    title, body = get_devto_article()
    print(f"Posting to Dev.to...")
    print(f"Title: {title[:80]}...")

    resp = requests.post(
        "https://dev.to/api/articles",
        headers={"api-key": api_key, "Content-Type": "application/json"},
        json={
            "article": {
                "title": title,
                "body_markdown": body,
                "published": True,
                "tags": ["cnc", "manufacturing", "engineering", "industrial", "hardware"],
                "canonical_url": "https://cncdisplay.com/en/posts/FANUC_CRT_Maintenance_vs_LCD_Upgrade_Module_Comparison.html"
            }
        }
    )

    if resp.status_code in [200, 201]:
        data = resp.json()
        url = data.get("url", "")
        print(f"[OK] Published: {url}")
        return url
    else:
        print(f"[FAIL] HTTP {resp.status_code}: {resp.text[:200]}")
        return None

# ============================================================
# Hashnode API
# ============================================================
def get_hashnode_article():
    content_file = OUTPUT / "blog_hashnode.md"
    content = content_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    title = ""
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith('### 标题') and i+1 < len(lines):
            title = lines[i+1].strip()
        if line.startswith('### 正文') or line == '### 正文':
            body_start = i + 1
            break
    body = '\n'.join(lines[body_start:]).strip()
    if '---' in body:
        body = body.split('---')[0].strip()
    return title, body

def post_to_hashnode():
    """自动发布到Hashnode"""
    cfg = load_config()
    pat = cfg.get("hashnode_pat")
    if not pat:
        print("[ERROR] Hashnode PAT 未配置")
        print("获取: https://hashnode.com/settings/developer → Generate PAT")
        return False

    title, body = get_hashnode_article()
    print(f"Posting to Hashnode...")

    # Hashnode GraphQL API
    query = """
    mutation PublishPost($input: PublishPostInput!) {
        publishPost(input: $input) {
            post { url title }
        }
    }
    """
    resp = requests.post(
        "https://gql.hashnode.com/",
        headers={"Authorization": pat, "Content-Type": "application/json"},
        json={
            "query": query,
            "variables": {
                "input": {
                    "title": title,
                    "contentMarkdown": body,
                    "tags": [
                        {"slug": "industrial-automation", "name": "Industrial Automation"},
                        {"slug": "cnc-machining", "name": "CNC Machining"},
                        {"slug": "engineering", "name": "Engineering"}
                    ],
                    "publicationId": cfg.get("hashnode_publication_id", ""),
                }
            }
        }
    )

    if resp.status_code == 200:
        data = resp.json()
        if "errors" not in data:
            url = data.get("data", {}).get("publishPost", {}).get("post", {}).get("url", "")
            print(f"[OK] Published: {url}")
            return url

    print(f"[FAIL] {resp.text[:300]}")
    return None

# ============================================================
# 生成手动平台的预填URL（直接打开浏览器）
# ============================================================
def open_manual_platforms():
    """生成各平台的提交URL"""
    import webbrowser

    print("\n=== 手动发布平台（已用内容预填） ===\n")

    platforms = {
        "Reddit r/CNC": {
            "url": "https://www.reddit.com/r/CNC/submit",
            "note": "已生成无外链版(v2)，发完等人问再贴链接"
        },
        "Reddit r/Machinists": {
            "url": "https://www.reddit.com/r/Machinists/submit",
            "note": "使用 social_reddit_r_machinists.md"
        },
        "Practical Machinist": {
            "url": "https://www.practicalmachinist.com/forum/cnc-machining/",
            "note": "使用 forum_practical_machinist.md"
        },
        "CNCzone": {
            "url": "https://www.cnczone.com/forums/machine-repair/",
            "note": "使用 forum_cnczonecom.md"
        },
        "Quora": {
            "url": "https://www.quora.com/search?q=CNC+CRT+LCD+replacement",
            "note": "找到相关问题用 qna_Quora.md 内容回答"
        },
        "知乎": {
            "url": "https://www.zhihu.com/search?type=content&q=CNC+CRT+LCD+替换",
            "note": "找到相关问题用 qna_知乎.md 内容回答"
        },
        "掘金": {
            "url": "https://juejin.cn/editor/drafts/new",
            "note": "使用 zh_掘金.md"
        },
        "CSDN": {
            "url": "https://editor.csdn.net/md/?not_checkout=1",
            "note": "使用 zh_CSDN博客.md"
        },
    }

    for name, info in platforms.items():
        print(f"  {name}: {info['url']}")
        print(f"    → {info['note']}")

    print("\n按 Enter 在浏览器中打开这些页面...")
    input()
    for name, info in platforms.items():
        webbrowser.open(info['url'])

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python auto_poster.py [setup|devto|hashnode|all|open]")
        print("  setup   - 查看API Key配置状态")
        print("  devto   - 自动发布到Dev.to")
        print("  hashnode - 自动发布到Hashnode")
        print("  all     - 发布到所有已配置API平台")
        print("  open    - 打开所有手动平台URL")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "setup":
        if len(sys.argv) >= 4 and sys.argv[2] == "devto":
            cfg = load_config()
            cfg["devto_api_key"] = sys.argv[3]
            save_config(cfg)
            print("[OK] Dev.to API Key 已保存")
        elif len(sys.argv) >= 4 and sys.argv[2] == "hashnode":
            cfg = load_config()
            cfg["hashnode_pat"] = sys.argv[3]
            save_config(cfg)
            print("[OK] Hashnode PAT 已保存")
        else:
            check_setup()

    elif cmd == "devto":
        post_to_devto()

    elif cmd == "hashnode":
        post_to_hashnode()

    elif cmd == "all":
        results = {}
        r = post_to_devto()
        if r: results["Dev.to"] = r
        r = post_to_hashnode()
        if r: results["Hashnode"] = r
        print(f"\n=== Results: {len(results)} posted ===")
        for k, v in results.items():
            print(f"  {k}: {v}")

    elif cmd == "open":
        open_manual_platforms()
