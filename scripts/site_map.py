# -*- coding: utf-8 -*-
"""全站关联图生成器 — cncdisplay.com
把"改X必须连带改Y"从靠记忆变成查图。生成 data/site_map.json：
  models          型号 → 引用该型号的所有文件（改型号时查这张图）
  zh_en_pairs     zh ↔ EN 文件配对（改一个语言查孪生）
  article_entries 每篇产品文章 → 5入口完整性（posts EN/ZH + brand EN/ZH + products index）

用法: python scripts/site_map.py          # 生成 data/site_map.json
      python scripts/site_map.py --check  # 打印所有文章入口缺失(给 full_gate/pre-commit 用)
"""
import re, os, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = os.path.join(ROOT, 'data', 'site_map.json')

MODEL_RE = re.compile(
    r'(A61L[- ]0001[- ]\d{4}|A02B[- ]\d{4}[- ][A-Z]\d{3}|A05B[- ]\d{4}[- ][A-Z]\d{3}|'
    r'\d{4}-\d{5}|009\d|008\d|007\d|006\d|D9MM[- ]11A|MDT[- ]?94\d|TX[- ]\d+|'
    r'C14C[- ]1472DF|DR5614|6FC3\d{3}|BM09DF|A20B[- ]\d{4}|C5470NS|CD1472|KFM7099H|'
    r'MDT962B|MDT947B|MDT1283B|SM0901|A61L0001\d{4})')

SKIP_DIRS = {'en_bak', '_archive_audit', '_templates', '__pycache__',
             'backlinks_daily', 'backlinks_output', 'node_modules',
             'fonts', 'images', 'output', 'screaming_frog_reports', 'data',
             '.git', '.github', 'schema', 'css', 'patches'}


def html_files():
    """产出统一格式相对路径（正斜杠、无 ./ 前缀），如 posts/x.html、zh/posts/x.html"""
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in SKIP_DIRS]
        for f in files:
            if f.endswith('.html'):
                p = os.path.relpath(os.path.join(root, f), '.')
                yield p.replace('\\', '/')


def build_models():
    """型号 → 引用文件列表"""
    models = {}
    for fp in html_files():
        try:
            content = open(fp, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        for m in set(MODEL_RE.findall(content)):
            norm = m.replace(' ', '').replace('-', '')
            models.setdefault(norm, [])
            if fp not in models[norm]:
                models[norm].append(fp.replace('\\', '/'))
    return models


def build_zh_en_pairs():
    """通过 hreflang 检测 zh ↔ EN 孪生。返回 {zh_path: en_path} + {en_path: zh_path}"""
    zh2en, en2zh = {}, {}
    alt_re = re.compile(r'hreflang="(en|zh-CN|zh)" href="(?:https://cncdisplay\.com)?([^"]+)"')
    for fp in html_files():
        n = fp.replace('\\', '/')
        try:
            content = open(fp, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        for lang, path in alt_re.findall(content):
            path = path.lstrip('/')
            if not path:
                continue
            if n.startswith('zh/') and lang == 'en':
                zh2en[n] = path
            elif not n.startswith('zh/') and lang in ('zh-CN', 'zh'):
                en2zh[n] = path
    return {**zh2en, **{v: k for k, v in en2zh.items()}}


MODEL_ART_RE = re.compile(r'/(article_|comparison_|faq_)')


def build_article_entries():
    """模型文章入口检查（CLAUDE.md铁律3）。
    只对 article_/comparison_ 前缀的型号文章硬校验 posts index（EN/ZH）——
    这些是"新增型号必须更新入口"规则的直接对象，低噪声高价值。
    品牌页/products index 受型号归属影响，不做硬门禁（由 cncdisplay-change skill 人工核对）。"""
    def read(p):
        try:
            return open(p, encoding='utf-8', errors='ignore').read()
        except Exception:
            return ''

    posts_en_idx = read('posts/index.html')
    posts_zh_idx = read('zh/posts/index.html')

    entries = {}
    for fp in html_files():
        n = fp.replace('\\', '/')
        is_zh = n.startswith('zh/')
        if not is_zh and not n.startswith('posts/'):
            continue
        if not MODEL_ART_RE.search(n):
            continue
        if 'http-equiv="refresh"' in read(n):
            continue  # 重定向壳页,真内容在别处,不要求入口
        base = os.path.basename(n)
        if is_zh:
            if base not in posts_zh_idx:
                entries[n] = ['zh_posts_index']
        else:
            if base not in posts_en_idx:
                entries[n] = ['posts_index_EN']
    return entries


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    data = {
        'generated': 'auto',
        'models': build_models(),
        'zh_en_pairs': build_zh_en_pairs(),
        'article_entries_missing': build_article_entries(),
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        # sort_keys 保证确定性输出，避免每次 commit 因字典顺序变化产生巨量 diff
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)

    print(f"site_map.json 生成: {len(data['models'])} 型号, "
          f"{len(data['zh_en_pairs'])} 中英对, "
          f"{len(data['article_entries_missing'])} 篇文章入口缺失")

    if '--check' in sys.argv:
        if data['article_entries_missing']:
            print(f"\n[FAIL] {len(data['article_entries_missing'])} 篇文章入口不完整:")
            for art, miss in sorted(data['article_entries_missing'].items()):
                print(f"  {art}: 缺 {' '.join(miss)}")
            sys.exit(1)
        print("\n[PASS] 所有文章 5 入口完整")
    sys.exit(0)


if __name__ == '__main__':
    main()
