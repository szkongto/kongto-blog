#!/usr/bin/env python3
"""
基于内容比对构建中英文文章对照映射表。

策略（按优先级）：
  1. 型号完全相同 → 强制配对（最高优先级）
  2. 型号部分匹配 → 按关键词得分补位
  3. 无型号 → 按关键词得分匹配
  4. 低于阈值或无对应 → 不配对（指向列表页）
"""
import os, re, json

BASE = r"D:\code\seo_deploy"

BRANDS = ['FANUC', 'Mitsubishi', '三菱', 'Siemens', '西门子', 'Mazak', '马扎克', 'MAZAK',
          'Okuma', '大隈', 'OKUMA', 'Haas', '哈斯', 'HAAS']

def extract_article_info(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except:
        return None

    title = ''
    m = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    if m:
        title = m.group(1).strip()

    h1 = ''
    m = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
    if m:
        h1 = m.group(1).strip()

    # 提取完整型号 (A61L-0001-0093, 6FC3988-7FA20 等)
    full_models = set()
    for match in re.finditer(r'[A-Z0-9]+-[0-9]{4}-[0-9]{4}', title + h1 + content[:3000]):
        full_models.add(match.group(0))
    for match in re.finditer(r'[A-Z0-9]{3,10}-[0-9]{2,5}', title + h1 + content[:3000]):
        full_models.add(match.group(0))

    # 提取产品代码 (DR5614, MDT962B, CD1472, SM0901, KTV104, FCUA 等)
    # 仅从标题+H1中提取，避免正文干扰
    for match in re.finditer(r'[A-Z]{2,6}[0-9]{3,6}', title + h1):
        full_models.add(match.group(0))

    # 提取品牌+型号组合 (检查是否同属一个品牌)
    for match in re.finditer(r'(FANUC|Mitsubishi|三菱|Siemens|西门子|Mazak|马扎克|Haas|哈斯|Okuma|大隈)\s*([A-Z0-9][-A-Z0-9]+)', title + h1):
        full_models.add(match.group(2).strip())

    # 品牌
    brands_found = set()
    for brand in BRANDS:
        if brand.lower() in (title + h1).lower():
            brands_found.add(brand)

    is_redirect = 'http-equiv="refresh"' in content

    return {
        'filepath': filepath,
        'title': title,
        'h1': h1,
        'full_models': full_models,
        'brands': brands_found,
        'is_redirect': is_redirect,
        'title_en_words': set(re.findall(r'[A-Za-z0-9]+', title)),
    }

def calculate_keyword_score(zh_info, en_info):
    """仅基于关键词的相似度（型号已匹配上时才用这个）"""
    score = 0

    # 品牌匹配
    common_brands = zh_info['brands'] & en_info['brands']
    score += len(common_brands) * 10

    # 标题关键词
    zh_words = zh_info['title_en_words']
    en_words = en_info['title_en_words']
    # 排除型号编号
    zh_words = {w for w in zh_words if not re.match(r'^\d+$', w)}
    en_words = {w for w in en_words if not re.match(r'^\d+$', w)}
    score += len(zh_words & en_words) * 3

    return score

def main():
    zh_articles = []
    en_articles = []

    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in ('.github', '.well-known', 'backlinks_daily',
                  'backlinks_output', '_archive_audit', '_templates')]
        for f in files:
            if not f.endswith('.html') or f == 'index.html':
                continue
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, BASE).replace(os.sep, '/')
            if not rel.startswith('posts/') and not rel.startswith('en/posts/'):
                continue
            if rel == 'posts/index.html' or rel == 'en/posts/index.html':
                continue
            info = extract_article_info(fp)
            if info and not info['is_redirect']:
                if rel.startswith('en/'):
                    en_articles.append(info)
                else:
                    zh_articles.append(info)

    print(f"中文文章(含真实内容): {len(zh_articles)} 篇")
    print(f"英文文章(含真实内容): {len(en_articles)} 篇\n")

    # === 策略1: 型号完全匹配 ===
    # 按型号分组
    def get_model_key(a):
        return tuple(sorted(a['full_models'])) if a['full_models'] else ('__no_model__',)

    zh_by_model = {}
    for a in zh_articles:
        key = get_model_key(a)
        zh_by_model.setdefault(key, []).append(a)

    en_by_model = {}
    for a in en_articles:
        key = get_model_key(a)
        en_by_model.setdefault(key, []).append(a)

    mapping = []  # (zh_path, en_path, score)
    matched_zh = set()
    matched_en = set()

    # 型号完全相同的优先配对
    for model_key in set(zh_by_model.keys()) & set(en_by_model.keys()):
        if model_key == ('__no_model__',):
            continue
        zh_list = zh_by_model[model_key]
        en_list = en_by_model[model_key]
        # 型号相同的一对一配对，按关键词得分选最优
        used_zh_in_group = set()
        used_en_in_group = set()
        # 贪心匹配：每个中文选最佳英文
        for zh in zh_list:
            best_en = None
            best_score = 0
            for en in en_list:
                if id(en) in used_en_in_group:
                    continue
                score = calculate_keyword_score(zh, en)
                if score > best_score:
                    best_score = score
                    best_en = en
            if best_en and best_score >= 5:
                mapping.append((zh, best_en, best_score + 200))  # 型号匹配加分200
                matched_zh.add(id(zh))
                matched_en.add(id(best_en))
                used_zh_in_group.add(id(zh))
                used_en_in_group.add(id(best_en))

    print(f"型号完全匹配: {len(mapping)} 对\n")

    # === 策略2: 剩余文章按关键词匹配 ===
    remaining_zh = [a for a in zh_articles if id(a) not in matched_zh]
    remaining_en = [a for a in en_articles if id(a) not in matched_en]

    for zh in remaining_zh:
        best_en = None
        best_score = 0
        for en in remaining_en:
            if id(en) in matched_en:
                continue
            score = calculate_keyword_score(zh, en)
            if score > best_score:
                best_score = score
                best_en = en
        if best_en and best_score >= 10:
            mapping.append((zh, best_en, best_score))
            matched_zh.add(id(zh))
            matched_en.add(id(best_en))

    # 统计已在型号匹配中处理的数量
    model_match_count = sum(1 for m in mapping if m[2] > 150)


    # 输出结果
    all_matched_zh = [a for a in zh_articles if id(a) in matched_zh]
    all_matched_en = [a for a in en_articles if id(a) in matched_en]
    print(f"成功配对: {len(mapping)} 对")
    print(f"未配对中文: {len(zh_articles) - len(all_matched_zh)} 篇")
    print(f"未配对英文: {len(en_articles) - len(all_matched_en)} 篇\n")

    for zh, en, score in sorted(mapping, key=lambda x: -x[2]):
        zh_rel = os.path.relpath(zh['filepath'], BASE).replace(os.sep, '/')
        en_rel = os.path.relpath(en['filepath'], BASE).replace(os.sep, '/')
        zh_model = list(zh['full_models'])[:1] if zh['full_models'] else ['--']
        en_model = list(en['full_models'])[:1] if en['full_models'] else ['--']
        print(f"  [{score:3d}] {zh_model[0]} | {zh_rel}")
        print(f"         {en_model[0]} | {en_rel}")
        print(f"         zh: {zh['title'][:55]}")
        print(f"         en: {en['title'][:55]}")
        print()

    if remaining_zh:
        print("未配对中文:")
        for a in [x for x in zh_articles if id(x) not in matched_zh]:
            rel = os.path.relpath(a['filepath'], BASE).replace(os.sep, '/')
            models = list(a['full_models'])[:1] or ['--']
            print(f"  [{models[0]}] {rel} | {a['title'][:60]}")

    if remaining_en:
        print("\n未配对英文:")
        for a in [x for x in en_articles if id(x) not in matched_en]:
            rel = os.path.relpath(a['filepath'], BASE).replace(os.sep, '/')
            models = list(a['full_models'])[:1] or ['--']
            print(f"  [{models[0]}] {rel} | {a['title'][:60]}")

    # 保存映射表
    mapping_data = [{
        'zh': os.path.relpath(m[0]['filepath'], BASE).replace(os.sep, '/'),
        'en': os.path.relpath(m[1]['filepath'], BASE).replace(os.sep, '/'),
        'score': m[2],
    } for m in mapping]

    with open(os.path.join(BASE, 'article_mapping.json'), 'w', encoding='utf-8') as f:
        json.dump(mapping_data, f, ensure_ascii=False, indent=2)
    print(f"\n映射表已保存: article_mapping.json ({len(mapping_data)} 对)")

if __name__ == '__main__':
    main()
