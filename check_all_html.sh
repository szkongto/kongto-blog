#!/bin/bash
# 批量检测HTML文件的问题

echo "========== 检测BOM头 =========="
echo "以下文件有BOM头(EF BB BF):"
find ./posts ./index.html ./about.html -name "*.html" -type f 2>/dev/null | while read file; do
    if [ -f "$file" ]; then
        first_bytes=$(xxd -l 3 "$file" 2>/dev/null | head -1 | awk '{print $2}')
        if [ "$first_bytes" = "efbbbf" ]; then
            echo "BOM: $file"
        fi
    fi
done

echo ""
echo "========== 检测JS语法错误 =========="
echo "以下文件有JS语法错误:"
find ./posts ./index.html ./about.html -name "*.html" -type f 2>/dev/null | while read file; do
    if [ -f "$file" ]; then
        # 提取JS代码并检查语法
        if node --check "$file" 2>/dev/null; then
            :
        else
            echo "JS Error: $file"
        fi
    fi
done

echo ""
echo "========== 统计 =========="
bom_count=$(find ./posts ./index.html ./about.html -name "*.html" -type f 2>/dev/null | while read file; do
    if [ -f "$file" ]; then
        first_bytes=$(xxd -l 3 "$file" 2>/dev/null | head -1 | awk '{print $2}')
        if [ "$first_bytes" = "efbbbf" ]; then
            echo "$file"
        fi
    fi
done | wc -l)

js_count=$(find ./posts ./index.html ./about.html -name "*.html" -type f 2>/dev/null | while read file; do
    if [ -f "$file" ]; then
        if ! node --check "$file" 2>/dev/null; then
            echo "$file"
        fi
    fi
done | wc -l)

echo "有BOM头的文件: $bom_count"
echo "有JS语法错误的文件: $js_count"
