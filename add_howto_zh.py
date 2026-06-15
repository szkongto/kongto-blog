#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add HowTo Schema to Chinese installation/guide pages."""

import os
import re

BASE = r'C:\Users\Administrator\WorkBuddy\2026-06-15-17-02-27\repo'

# Define HowTo schema per page (Chinese pages)
HOWTO_SCHEMAS = {
    'posts/fanuc-crt-to-lcd-upgrade-complete-guide-zh.html': {
        "name": "FANUC CRT 显示器升级到 LCD 安装步骤",
        "description": "FANUC 数控显示器从 CRT 升级到 LCD 的完整安装步骤，共7步，无需改动机床结构。",
        "totalTime": "PT30M",
        "tool": [{"@type": "HowToTool", "name": "十字螺丝刀"}, {"@type": "HowToTool", "name": "扭力扳手（≤5Nm）"}, {"@type": "HowToTool", "name": "防静电腕带"}, {"@type": "HowToTool", "name": "清洁棉、酒精（70%）"}],
        "step": [
            {"@type": "HowToStep", "name": "断电和防静电", "text": "关闭数控机床主电源，拔掉显示器电源线；佩戴防静电腕带并接地。确认电源指示灯全部熄灭，防止高压残余。", "url": "https://cncdisplay.com/posts/fanuc-crt-to-lcd-upgrade-complete-guide-zh.html#step1"},
            {"@type": "HowToStep", "name": "拆除原 CRT", "text": "松开固定 CRT 的 4-6 颗螺丝（依据机型）。小心拔出 HONDA 20 针信号线和 24V 电源线。拔线时保持插头正面朝外，防止卡扣损坏。", "url": "https://cncdisplay.com/posts/fanuc-crt-to-lcd-upgrade-complete-guide-zh.html#step2"},
            {"@type": "HowToStep", "name": "清理安装面", "text": "用酒精棉轻拭原支架与机壳接触面，去除油污与灰尘。不要使用腐蚀性溶剂，以免损伤金属表面。", "url": "https://cncdisplay.com/posts/fanuc-crt-to-lcd-upgrade-complete-guide-zh.html#step3"},
            {"@type": "HowToStep", "name": "放置 LCD", "text": "将 FANUC A61L-0001-0093 LCD 对准原孔位，轻压四角使卡扣自动锁定。确认 LCD 完全贴合支架，避免倾斜导致信号接触不良。", "url": "https://cncdisplay.com/posts/fanuc-crt-to-lcd-upgrade-complete-guide-zh.html#step4"},
            {"@type": "HowToStep", "name": "连接线缆", "text": "插入 HONDA 20 针接口（方向标记「1」对齐）。连接 24V DC 电源线（红/黑极性同原 CRT）。插头需扣紧，防止振动脱落。", "url": "https://cncdisplay.com/posts/fanuc-crt-to-lcd-upgrade-complete-guide-zh.html#step5"},
            {"@type": "HowToStep", "name": "固定螺丝", "text": "使用扭力扳手将固定螺丝拧至 4-5 Nm，防止过紧导致面板裂纹。螺纹保持清洁，避免金属屑进入显示器内部。", "url": "https://cncdisplay.com/posts/fanuc-crt-to-lcd-upgrade-complete-guide-zh.html#step6"},
            {"@type": "HowToStep", "name": "通电检查", "text": "开机后进入 FANUC 系统 → 参数 → 画面设置，确认显示分辨率为 800×600（或系统默认）。若画面异常，重新检查信号线插拔情况。首次通电建议观察 5 分钟，确认背光、颜色均匀。", "url": "https://cncdisplay.com/posts/fanuc-crt-to-lcd-upgrade-complete-guide-zh.html#step7"},
        ],
    },
    'posts/fanuc-a61l-0001-0093-lcd-upgrade-guide-v2-zh.html': {
        "name": "FANUC A61L-0001-0093 LCD 升级安装指南",
        "description": "FANUC A61L-0001-0093 工业显示器 LCD 升级方案安装指南，即插即用，适配 0i/16i/18i 等系统。",
        "totalTime": "PT20M",
        "tool": [{"@type": "HowToTool", "name": "十字螺丝刀"}, {"@type": "HowToTool", "name": "扭力扳手"}],
        "step": [
            {"@type": "HowToStep", "name": "断电准备", "text": "关闭机床电源，拔掉显示器电源，佩戴防静电腕带。"},
            {"@type": "HowToStep", "name": "拆除旧显示器", "text": "松开固定螺丝，小心拔出信号线和电源线，记录线序。"},
            {"@type": "HowToStep", "name": "安装新 LCD", "text": "对准原安装孔位，轻压四角使卡扣锁定，无需改动机床结构。"},
            {"@type": "HowToStep", "name": "连接线缆", "text": "插入 HONDA 20 针接口，连接 24V 电源线，确认极性正确。"},
            {"@type": "HowToStep", "name": "通电测试", "text": "开机进入系统参数，确认分辨率为 800×600，检查画面是否正常。"},
        ],
    },
    'posts/industrial-cnc-display-troubleshooting-repair-guide-zh.html': {
        "name": "工业 CNC 显示器故障排查与维修指南",
        "description": "工业数控显示器常见故障现象、排查步骤和维修方案完整指南。",
        "totalTime": "PT45M",
        "tool": [{"@type": "HowToTool", "name": "万用表"}, {"@type": "HowToTool", "name": "螺丝刀套装"}, {"@type": "HowToTool", "name": "备用显示器"}],
        "step": [
            {"@type": "HowToStep", "name": "确认故障现象", "text": "记录显示器异常表现：无显示、画面抖动、颜色异常、闪烁或横纹等。"},
            {"@type": "HowToStep", "name": "检查电源供应", "text": "用万用表测量 24V DC 电源输出是否正常，检查电源线接头是否松动。"},
            {"@type": "HowToStep", "name": "检查信号连接", "text": "确认 HONDA 20 针信号线插头是否完全插入，检查针脚是否弯曲或氧化。"},
            {"@type": "HowToStep", "name": "判断 CRT 或 LCD 故障", "text": "若画面模糊、亮度低或有闪烁横纹，多为 CRT 老化；直接更换为 LCD 升级套件。"},
            {"@type": "HowToStep", "name": "安装 LCD 升级套件", "text": "按照安装步骤更换为 LCD 显示器，即插即用，无需改动系统参数。"},
        ],
    },
    'posts/cga-ega-to-rgbhv-industrial-display-retrofit-guide-zh.html': {
        "name": "CGA/EGA 转 RGBHV 工业显示器改造指南",
        "description": "将老式 CGA/EGA 工业显示器改造为 RGBHV 接口的现代 LCD 显示方案。",
        "totalTime": "PT60M",
        "tool": [{"@type": "HowToTool", "name": "信号转换器"}, {"@type": "HowToTool", "name": "螺丝刀"}, {"@type": "HowToTool", "name": "万用表"}],
        "step": [
            {"@type": "HowToStep", "name": "确认原接口类型", "text": "检查原显示器视频接口是 CGA、EGA 还是 RGBHV，确认针脚定义。"},
            {"@type": "HowToStep", "name": "选择转换器", "text": "根据原接口类型选用对应的视频信号转换器（如 GBS-8219 等）。"},
            {"@type": "HowToStep", "name": "安装转换器", "text": "将转换器固定在机床内部合适位置，连接原信号线到转换器输入。"},
            {"@type": "HowToStep", "name": "连接 LCD 显示器", "text": "用 VGA 线将转换器输出连接到 LCD 显示器，确认供电 24V DC。"},
            {"@type": "HowToStep", "name": "通电调试", "text": "开机测试画面是否正常居中、亮度合适，必要时调整转换器参数。"},
        ],
    },
    'posts/fanuc-0i-display-faq-solutions-zh.html': {
        "name": "FANUC 0i 系列显示器常见问题解决方案",
        "description": "FANUC 0i 数控系统显示器无显示、花屏、闪烁等常见问题的逐步解决方案。",
        "totalTime": "PT30M",
        "tool": [{"@type": "HowToTool", "name": "万用表"}, {"@type": "HowToTool", "name": "系统参数手册"}],
        "step": [
            {"@type": "HowToStep", "name": "检查电源指示灯", "text": "确认显示器电源灯是否亮起，若不亮检查 24V 电源供应。"},
            {"@type": "HowToStep", "name": "检查屏幕显示状态", "text": "若指示灯亮但无显示，尝试调节亮度和对比度旋钮。"},
            {"@type": "HowToStep", "name": "检查信号连接", "text": "重新插拔 HONDA 20 针信号线，确认针脚无弯曲或氧化。"},
            {"@type": "HowToStep", "name": "进入系统诊断", "text": "在 FANUC 系统中查看诊断参数，确认系统是否正常输出视频信号。"},
            {"@type": "HowToStep", "name": "更换 LCD 升级套件", "text": "若 CRT 老化严重，直接更换为即插即用 LCD 升级套件。"},
        ],
    },
}

def make_howto_script(page_url, schema_data):
    """Generate the JSON-LD script block for HowTo schema."""
    import json
    url_base = page_url.replace('-zh.html', '.html').replace('posts/', 'https://cncdisplay.com/posts/')
    schema = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": schema_data["name"],
        "description": schema_data["description"],
        "totalTime": schema_data.get("totalTime", "PT30M"),
        "tool": schema_data.get("tool", []),
        "step": schema_data["step"],
    }
    # Use html-safe JSON (no < > & in JSON needed, but wrap in CDATA is not needed for JSON-LD)
    json_str = json.dumps(schema, ensure_ascii=False, indent=2)
    # Make JSON-LD safe inside HTML script tag
    json_str = json_str.replace('</', r'<\/')
    return f'<script type="application/ld+json">\n{json_str}\n</script>'


def add_howto_to_page(filepath, schema_data):
    """Add HowTo schema before </head> if not already present."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'HowTo"' in content or '"@type": "HowTo"' in content:
        print(f'  [SKIP] Already has HowTo: {os.path.basename(filepath)}')
        return False

    script_block = make_howto_script(
        os.path.relpath(filepath, BASE).replace('\\', '/'),
        schema_data
    )

    # Insert before </head>
    if '</head>' in content:
        content = content.replace('</head>', script_block + '\n\n</head>', 1)
    else:
        print(f'  [WARN] No </head> found: {os.path.basename(filepath)}')
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  [OK] Added HowTo: {os.path.basename(filepath)}')
    return True


if __name__ == '__main__':
    print('Adding HowTo Schema to Chinese installation/guide pages...\n')
    for rel_path, schema_data in HOWTO_SCHEMAS.items():
        filepath = os.path.join(BASE, rel_path)
        if os.path.exists(filepath):
            print(f'Processing: {rel_path}')
            add_howto_to_page(filepath, schema_data)
        else:
            print(f'  [NOT FOUND] {rel_path}')
    print('\nDone!')
