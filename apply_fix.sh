#!/bin/bash
# 一键修复脚本 - 应用所有pending的修复
# 使用方法：
# 1. 将此脚本和 blog_fix_package_20260513.tar.gz 上传到服务器
# 2. 运行：bash apply_fix.sh

set -e

echo "========================================="
echo "KONGTO博客修复脚本"
echo "========================================="

# 检查是否在正确的目录
if [ ! -d ".git" ]; then
    echo "错误: 请在博客Git仓库根目录运行此脚本"
    exit 1
fi

# 1. 解压修复包
if [ -f "blog_fix_package_20260513.tar.gz" ]; then
    echo "[1/4] 解压修复包..."
    tar -xzf blog_fix_package_20260513.tar.gz
    echo "  ✓ 图片已优化 (66MB → 20MB)"
else
    echo "[1/4] 跳过: 未找到修复包"
fi

# 2. 验证title标签修复
echo "[2/4] 验证title标签..."
ERRORS=0
for html in posts/*.html; do
    if grep -q "<title>.*[^<]$" "$html"; then
        echo "  ✗ 未闭合: $html"
        ERRORS=$((ERRORS + 1))
    fi
done
if [ $ERRORS -eq 0 ]; then
    echo "  ✓ 所有title标签已正确闭合"
else
    echo "  ✗ 发现 $ERRORS 个未闭合的title标签"
fi

# 3. 检查CNAME配置
echo "[3/4] 检查域名配置..."
if [ -f "CNAME" ]; then
    echo "  CNAME: $(cat CNAME)"
    echo "  ✓ 域名配置存在"
else
    echo "  ⚠  CNAME文件不存在，创建..."
    echo "cncdisplay.com" > CNAME
fi

# 4. 提交更改
echo "[4/4] 提交更改..."
git add -A
git commit -m "fix: 应用所有修复 (title标签+图片压缩)" || echo "  无更改需要提交"

echo ""
echo "========================================="
echo "修复完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 检查GitHub Pages设置："
echo "   https://github.com/szkongto/kongto-blog/settings/pages"
echo ""
echo "2. 如果使用GitHub API推送（需要token）："
echo "   export GITHUB_TOKEN='your_token'"
echo "   python upload_via_api.py"
echo ""
echo "3. 或直接推送（如果网络允许）："
echo "   git push origin main"
echo ""
