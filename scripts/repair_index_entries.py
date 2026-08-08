# -*- coding: utf-8 -*-
"""清算 posts index 缺失入口 — 把 site_map.py 报出的缺失模型文章补进索引。
幂等：已存在的文章跳过。插入到 </main> 前的 "Additional Model Articles" 区。

用法: python scripts/fix_missing_entries.py --apply   # 实际插入
      python scripts/fix_missing_entries.py           # 只报告不插入
"""
import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

MODEL_ART_RE = re.compile(r'/(article_|comparison_|faq_)')


def read(p):
    try:
        return open(p, encoding='utf-8', errors='ignore').read()
    except Exception:
        return ''


def article_title(fp):
    content = read(fp)
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.S)
    if h1:
        return re.sub(r'\s+', ' ', h1.group(1)).strip()
    t = re.search(r'<title>(.*?)</title>', content, re.S)
    if t:
        title = t.group(1).strip()
        # 去掉站点名尾巴
        for sep in (' | cncdisplay', ' - cncdisplay', ' | Kongto', ' | 江图科技'):
            if sep in title:
                title = title.split(sep)[0]
                break
        return title
    return os.path.basename(fp).replace('.html', '')


def missing_articles():
    """返回 {index_path: [article_relpath, ...]}。跳过 meta-refresh 壳页(重定向桩,不链进索引)"""
    posts_en_idx = read('posts/index.html')
    posts_zh_idx = read('zh/posts/index.html')
    out = {'posts/index.html': [], 'zh/posts/index.html': []}
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('en_bak', '_archive_audit', '.git',
                                                '__pycache__', 'backlinks_daily')]
        for f in files:
            if not f.endswith('.html'):
                continue
            n = os.path.relpath(os.path.join(root, f), '.').replace('\\', '/')
            if not MODEL_ART_RE.search(n):
                continue
            content = read(n)
            if 'http-equiv="refresh"' in content:
                continue  # 重定向壳页,真内容在别处
            base = os.path.basename(n)
            if n.startswith('zh/posts/') and n.count('/') == 2:
                if base not in posts_zh_idx:
                    out['zh/posts/index.html'].append(n)
            elif n.startswith('posts/') and n.count('/') == 1:
                if base not in posts_en_idx:
                    out['posts/index.html'].append(n)
    return out


def insert_section(index_path, articles):
    idx = read(index_path)
    if 'id="additional-model-articles"' in idx:
        print(f"[SKIP] {index_path} 已有 Additional Model Articles 区，合并中")
        # 已有区: 在 </section> 前追加
        section_end = idx.rfind('</section>')
        anchor = section_end if section_end > 0 else idx.rfind('</main>')
    else:
        anchor = idx.rfind('</main>')

    block = []
    for art in articles:
        title = article_title(art)
        block.append(f'    <h3><a href="/{art}">{title}</a></h3>\n')
    if not block:
        return idx, 0

    if 'id="additional-model-articles"' in idx:
        # 已有区，直接追加 <h3> 到 </section> 前
        new_idx = idx[:anchor] + ''.join(block) + idx[anchor:]
    else:
        section = ('\n    <section id="additional-model-articles">\n'
                   '        <h2>📚 Additional Model Articles</h2>\n'
                   '        <p>完整型号文章索引（按需补充）</p>\n' + ''.join(block) + '    </section>\n')
        new_idx = idx[:anchor] + section + idx[anchor:]
    return new_idx, len(block)


def main():
    apply = '--apply' in sys.argv
    missing = missing_articles()
    total = sum(len(v) for v in missing.values())
    print(f'缺失 {total} 篇: ' + ', '.join(f'{k}={len(v)}' for k, v in missing.items()))

    for index_path, arts in missing.items():
        if not arts:
            continue
        if apply:
            new_idx, added = insert_section(index_path, sorted(arts))
            if added:
                open(index_path, 'w', encoding='utf-8').write(new_idx)
                print(f'  ✓ {index_path}: 插入 {added} 篇')
            else:
                print(f'  - {index_path}: 无需插入')
        else:
            print(f'  [{index_path}]')
            for a in sorted(arts)[:10]:
                print(f'    - {a}')
            if len(arts) > 10:
                print(f'    ... 还有 {len(arts) - 10} 篇')

    if not apply:
        print('\n加 --apply 实际写入')


if __name__ == '__main__':
    main()
