#!/usr/bin/env python3
"""
智能修复 hreflang 交叉引用
根据内容主题匹配中英文文件，然后修复hreflang标签
"""
import os
import re
from urllib.parse import quote, unquote

BASE_DIR = r"D:\workspace\kongto-blog"

def extract_keywords(filename):
    """从文件名提取关键词"""
    # 去掉扩展名，解码URL编码
    name = unquote(filename).replace('.html', '')
    # 提取关键词：型号、日期、英文缩写
    keywords = set()
    # 提取型号模式 (如 FANUC_A61L_0001_0093, CGA_EGA, MDT1283B)
    keywords.update(re.findall(r'[A-Z]+[0-9A-Z_-]+', name))
    # 提取日期
    keywords.update(re.findall(r'\d{8}', name))
    # 提取中文关键词
    keywords.update(re.findall(r'[\u4e00-\u9fff]+', name))
    return keywords

def build_topic_mapping():
    """构建主题映射：关键词集合 -> 中文文件"""
    zh_mapping = {}  # 关键词集合 -> 中文文件路径

    for zh_file in os.listdir(os.path.join(BASE_DIR, 'posts')):
        if not zh_file.endswith('.html'):
            continue
        keywords = extract_keywords(zh_file)
        # 用型号作为主要key
        model_keys = [k for k in keywords if re.match(r'^[A-Z]{2,}[0-9A-Z_-]+$', k)]
        if model_keys:
            for key in model_keys:
                if key not in zh_mapping:
                    zh_mapping[key] = []
                zh_mapping[key].append(zh_file)
        # 也存储中文关键词
        chinese_keys = [k for k in keywords if '\u4e00' <= k <= '\u9fff']
        for key in chinese_keys:
            if key not in zh_mapping:
                zh_mapping[key] = []
            if zh_file not in zh_mapping[key]:
                zh_mapping[key].append(zh_file)

    return zh_mapping

def find_matching_zh(en_file, zh_mapping):
    """根据英文文件名找到对应的中文文件"""
    en_keywords = extract_keywords(en_file)

    # 优先匹配型号
    model_keys = [k for k in en_keywords if re.match(r'^[A-Z]{2,}[0-9A-Z_-]+$', k)]
    candidates = []

    for key in model_keys:
        if key in zh_mapping:
            candidates.extend(zh_mapping[key])

    # 去重
    candidates = list(set(candidates))

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        # 多个候选，根据日期进一步筛选
        for zh_file in candidates:
            zh_keywords = extract_keywords(zh_file)
            # 找共同关键词
            common = en_keywords & zh_keywords
            if len(common) >= 3:  # 至少3个共同关键词
                return zh_file

    return None

def fix_chinese_hreflang_en():
    """修复中文文件的 hreflang="en" 标签"""
    fixed = 0
    no_match = 0

    for zh_file in os.listdir(os.path.join(BASE_DIR, 'posts')):
        if not zh_file.endswith('.html'):
            continue

        zh_path = os.path.join(BASE_DIR, 'posts', zh_file)
        with open(zh_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找 hreflang="en" 标签
        en_match = re.search(r'(<link[^>]*hreflang="en"[^>]*href=")([^"]+)(")', content)
        if not en_match:
            continue

        en_href = en_match.group(2)
        # 检查是否指向中文文件名（错误）
        if any(ord(c) > 127 or c == '%' for c in en_href):
            # 需要修复
            en_filename = en_href.split('/en/posts/')[-1]

            if os.path.exists(os.path.join(BASE_DIR, 'en/posts', en_filename)):
                continue  # 已经正确

            # 尝试在英文文件夹中查找对应文件
            matched_en = None
            for en_file in os.listdir(os.path.join(BASE_DIR, 'en/posts')):
                if not en_file.endswith('.html'):
                    continue
                # 检查英文文件的hreflang="zh"是否指向此中文文件
                en_path = os.path.join(BASE_DIR, 'en/posts', en_file)
                with open(en_path, 'r', encoding='utf-8') as f:
                    en_content = f.read()
                zh_url_pattern = f'https://cncdisplay.com/posts/{quote(zh_file, safe="")}'
                if zh_url_pattern in en_content:
                    matched_en = en_file
                    break

            if matched_en:
                new_en_href = f'https://cncdisplay.com/en/posts/{matched_en}'
                old_tag = en_match.group(1) + en_href + en_match.group(3)
                new_tag = en_match.group(1) + new_en_href + en_match.group(3)
                content = content.replace(old_tag, new_tag)
                with open(zh_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed += 1
                print(f"✓ 修复中文: {zh_file[:50]}...")
                print(f"  -> {matched_en}")
            else:
                no_match += 1

    return fixed, no_match

def fix_english_hreflang_zh():
    """修复英文文件的 hreflang="zh" 标签"""
    fixed = 0
    no_match = 0

    for en_file in os.listdir(os.path.join(BASE_DIR, 'en/posts')):
        if not en_file.endswith('.html') or en_file == 'index.html':
            continue

        en_path = os.path.join(BASE_DIR, 'en/posts', en_file)
        with open(en_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找 hreflang="zh" 标签
        zh_match = re.search(r'(<link[^>]*hreflang="zh"[^>]*href=")([^"]+)(")', content)
        if not zh_match:
            continue

        zh_href = zh_match.group(2)
        zh_filename = unquote(zh_href.split('/posts/')[-1])

        # 检查中文文件是否存在
        zh_path = os.path.join(BASE_DIR, 'posts', zh_filename)
        if os.path.exists(zh_path):
            # 检查URL编码是否正确
            correct_encoding = quote(zh_filename, safe='')
            if zh_href != f'https://cncdisplay.com/posts/{correct_encoding}':
                # URL编码不正确，修复
                new_zh_href = f'https://cncdisplay.com/posts/{correct_encoding}'
                old_tag = zh_match.group(1) + zh_href + zh_match.group(3)
                new_tag = zh_match.group(1) + new_zh_href + zh_match.group(3)
                content = content.replace(old_tag, new_tag)
                with open(en_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed += 1
                print(f"✓ 修复编码: {en_file[:50]}...")
            continue

        # 中文文件不存在，尝试智能匹配
        matched_zh = find_matching_zh(en_file, zh_mapping)
        if matched_zh:
            new_zh_href = f'https://cncdisplay.com/posts/{quote(matched_zh, safe="")}'
            old_tag = zh_match.group(1) + zh_href + zh_match.group(3)
            new_tag = zh_match.group(1) + new_zh_href + zh_match.group(3)
            content = content.replace(old_tag, new_tag)
            with open(en_path, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed += 1
            print(f"✓ 智能匹配: {en_file[:50]}...")
            print(f"  {zh_filename[:40]}... -> {matched_zh[:40]}...")
        else:
            no_match += 1
            print(f"✗ 无匹配: {en_file[:50]}...")
            print(f"  -> {zh_filename[:40]}...")

    return fixed, no_match

def main():
    global zh_mapping

    # 构建主题映射
    zh_mapping = build_topic_mapping()
    zh_count = len(set(f for files in zh_mapping.values() for f in files))
    print(f"构建主题映射：{zh_count} 个中文文件，{len(zh_mapping)} 个关键词")

    print("\n" + "=" * 60)
    print("开始修复 hreflang 交叉引用...")
    print("=" * 60)

    print("\n[1/2] 修复中文文件的 hreflang=\"en\" 标签...")
    fixed_zh, no_match_zh = fix_chinese_hreflang_en()
    print(f"\n中文文件: 修复 {fixed_zh} 个, 无匹配 {no_match_zh} 个")

    print("\n[2/2] 修复英文文件的 hreflang=\"zh\" 标签...")
    fixed_en, no_match_en = fix_english_hreflang_zh()
    print(f"\n英文文件: 修复 {fixed_en} 个, 无匹配 {no_match_en} 个")

    print("\n" + "=" * 60)
    print(f"总计: 中文修复 {fixed_zh} 个, 英文修复 {fixed_en} 个")
    print("=" * 60)

if __name__ == "__main__":
    main()
