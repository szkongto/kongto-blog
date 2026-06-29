"""Configuration for cross-poster."""
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEO_DEPLOY_DIR = os.path.dirname(BASE_DIR)  # d:/code/seo_deploy

# Article directories
CN_POSTS_DIR = os.path.join(SEO_DEPLOY_DIR, "posts")
EN_POSTS_DIR = os.path.join(SEO_DEPLOY_DIR, "en", "posts")

# Session storage
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

# Tracking
TRACKER_FILE = os.path.join(BASE_DIR, "published.json")

# Platform configs
PLATFORMS = {
    # Chinese platforms
    "zhihu": {
        "name": "知乎",
        "login_url": "https://www.zhihu.com/signin",
        "editor_url": "https://zhuanlan.zhihu.com/write",
        "lang": "zh",
        "enabled": True,
    },
    "baijiahao": {
        "name": "百家号",
        "login_url": "https://baijiahao.baidu.com/",
        "editor_url": "https://baijiahao.baidu.com/write",
        "lang": "zh",
        "enabled": True,
    },
    "csdn": {
        "name": "CSDN",
        "login_url": "https://passport.csdn.net/login",
        "editor_url": "https://blog.csdn.net/weixin_xxx/article/list/0",
        "lang": "zh",
        "enabled": True,
    },
    # English platforms
    "medium": {
        "name": "Medium",
        "login_url": "https://medium.com/m/signin",
        "editor_url": "https://medium.com/new-story",
        "lang": "en",
        "enabled": True,
    },
    "linkedin": {
        "name": "LinkedIn",
        "login_url": "https://www.linkedin.com/login",
        "editor_url": "https://www.linkedin.com/post/new/",
        "lang": "en",
        "enabled": True,
    },
    "facebook": {
        "name": "Facebook",
        "login_url": "https://www.facebook.com/",
        "editor_url": "https://www.facebook.com/notes/",
        "lang": "en",
        "enabled": True,
    },
}

# Human-like behavior
TYPING_SPEED = lambda: random.randint(30, 80)  # ms per character
ACTION_DELAY = lambda: random.uniform(0.5, 2.0)  # seconds between actions
BETWEEN_PLATFORMS = lambda: random.randint(7200, 14400)  # 2-4 hours between platforms

# Retry
MAX_RETRIES = 3
RETRY_DELAY = 1800  # 30 min between retries

# Viewport
VIEWPORT = {"width": 1366, "height": 768}

# User agents pool
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
]
