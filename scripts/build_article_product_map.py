# -*- coding: utf-8 -*-
"""生成文章 -> 产品价格页 映射表 data/article_product_map.csv

输入:
  - posts/*.html 的 <h1> 标题文本
  - compatibility-matrix.html 内嵌 COMPAT_DATA（型号 -> 产品页）

规则:
  - 标题含 COMPAT_DATA 里的明确型号 -> 该型号产品页 (match_type=model)
  - 无明确型号（系列/通用文章）    -> /products/ 总览     (match_type=none)
  - 标题含多个型号时取最先出现的那个, 记 note 供人工复核

跳过: meta-refresh 跳转桩、audit 工件。

用法: python scripts/build_article_product_map.py [--check]
  --check  不写文件, 只比对现有 CSV 是否一致 (门禁用)
"""
import csv
import html
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

OUT = 'data/article_product_map.csv'
FIELDS = ['article', 'target_url', 'match_type', 'note']

# 非文章页：posts/index.html 是列表页，不是文章，不给购买入口。
EXCLUDE_FILES = {'index.html'}

# 人工裁决的映射（优先级高于自动匹配）。来源必须写清，否则下轮会被当成脏数据。
OVERRIDES = {
    # 2026-11-26 用户指定：Haas 案例文章对应 12 英寸 9 针 Haas 产品页。
    # 文章正文未写尺寸，属运营口径而非正文推断，故单列 override。
    'posts/article_20260508_Haas_CRT_LCD_Case.html': (
        '/products/haas-12inch-9pin-crt-lcd-upgrade.html', 'manual:user-specified'),
}


def load_compat():
    """返回 [(model_key, product_url)], 同型号多条时取第一条。"""
    text = open('compatibility-matrix.html', encoding='utf-8').read()
    m = re.search(r'const COMPAT_DATA\s*=\s*\[(.*?)\n\s*\];', text, re.DOTALL)
    if not m:
        raise SystemExit('COMPAT_DATA not found in compatibility-matrix.html')
    body = m.group(1).rstrip().rstrip(',')
    rows = json.loads('[' + body + ']')
    out, seen = [], set()
    for row in rows:
        model, url = row[1].strip(), row[7].strip()
        # 排除描述型键（"9\" Green CRT"、"0-M/0-T CRT"、"VF Series 12\" CRT"）：
        # 它们代表一整类屏或一个系统，不是能直接下单的明确件号。
        if '"' in model or model.endswith(' CRT'):
            continue
        if model and url.startswith('/products/') and model not in seen:
            seen.add(model)
            out.append((model, url))
    return out


def canon(s):
    """型号归一: 只留小写字母数字, 抹平 -/_/空格/\\. 差异。"""
    return re.sub(r'[^a-z0-9]', '', s.lower())


def article_files():
    for f in sorted(os.listdir('posts')):
        if not f.endswith('.html'):
            continue
        if 'audit-verification' in f or f in EXCLUDE_FILES:
            continue
        rel = 'posts/' + f
        text = open(rel, encoding='utf-8').read()
        if 'http-equiv="refresh"' in text:
            continue
        yield rel, text


def h1_text(text):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.DOTALL)
    if not m:
        return None
    return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()


def pick_model(title):
    """返回 (model_key, url, note)。多个命中时取标题里最先出现的。"""
    ctitle = canon(title)
    hits = []
    for model, url in COMPAT:
        cm = canon(model)
        if len(cm) < 4:
            continue
        idx = ctitle.find(cm)
        if idx >= 0:
            hits.append((idx, model, url))
    if not hits:
        return None, None, ''
    hits.sort()
    idx, model, url = hits[0]
    others = [h[1] for h in hits[1:]]
    note = 'first-of:' + model
    if others:
        note += ' others=' + '|'.join(others)
    return model, url, note


COMPAT = load_compat()


def build():
    rows = []
    for rel, text in article_files():
        title = h1_text(text)
        if not title:
            rows.append([rel, '/products/', 'none', 'NO_H1'])
            continue
        if rel in OVERRIDES:
            url, note = OVERRIDES[rel]
            rows.append([rel, url, 'model', note])
            continue
        model, url, note = pick_model(title)
        if model:
            rows.append([rel, url, 'model', note])
            continue
        # 标题无型号时, 沿用站内既有的产品链接（既有编辑意图）:
        #   1) 文章里的 btn-pill-orange 产品卡
        #   2) 已有的 cluster-cta 按钮若指向具体产品页（如 FAGOR 案例页）
        for pat, note in (
                (r'<a href="([^"]+)"[^>]*class="btn btn-primary btn-pill-orange"',
                 'inline-card'),
                (r'<p class="cluster-cta[^"]*">\s*<a href="([^"]+)"', 'existing-cta')):
            hm = re.search(pat, text)
            if hm:
                u = hm.group(1)
                p = u.lstrip('/')
                if u.startswith('/products/') and u != '/products/' and \
                        os.path.exists(p if not p.endswith('/') else p + 'index.html'):
                    rows.append([rel, u, 'model', note])
                    break
        else:
            rows.append([rel, '/products/', 'none', ''])
    return rows


def main():
    rows = build()
    if '--check' in sys.argv:
        if not os.path.exists(OUT):
            print(f'[CTA-MAP] MISSING {OUT}')
            sys.exit(1)
        old = list(csv.reader(open(OUT, encoding='utf-8')))
        if old and old[0] == FIELDS:
            old = old[1:]
        if old != rows:
            print('[CTA-MAP] FAIL CSV 与站点实际不一致, 重跑 build_article_product_map.py')
            sys.exit(1)
        print(f'[CTA-MAP] OK {len(rows)} rows')
        return

    os.makedirs('data', exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        w.writerows(rows)

    model = sum(1 for r in rows if r[2] == 'model')
    print(f'wrote {OUT}: {len(rows)} articles, model={model}, none={len(rows)-model}')
    tgt = {}
    for r in rows:
        tgt[r[1]] = tgt.get(r[1], 0) + 1
    print(f'distinct targets: {len(tgt)}')
    for url, n in sorted(tgt.items(), key=lambda x: -x[1])[:8]:
        print(f'  {n:3d}  {url}')


if __name__ == '__main__':
    main()
