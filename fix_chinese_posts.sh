#!/bin/bash
# 修复中文文章页的BOM头和JavaScript语法错误

POSTS_DIR="/d/workspace/kongto-blog/posts"

echo "=== 开始修复中文文章页 ==="

cd "$POSTS_DIR" || exit 1

# 需要修复的文件列表
files=(
  "article_20260507_Siemens_6FC3998-7FA20_LCD.html"
  "article_20260507_Siemens_SM0901_579417_TA.html"
  "article_20260507_MDT1283B_LCD替换方案.html"
  "article_20260506_三菱MDT962B工业液晶显示器CRT替代方案.html"
  "article_20260506_三菱BM09DF工业显示屏E60数控系统TFT替代.html"
  "article_20260506_三菱FCUA-CT100工业显示器M500_M520数控系统TFT替代.html"
  "article_20260507_Mazak_CD1472D1M_LCD替换方案.html"
  "article_20260507_Sharp_AIQA8DSP40_LCD替换方案.html"
)

for file in "${files[@]}"; do
  if [ ! -f "$file" ]; then
    echo "跳过（不存在）: $file"
    continue
  fi
  
  echo "修复: $file"
  
  # 1. 移除BOM头（EF BB BF）
  # 2. 修复JavaScript中的换行符（将多行字符串改成单行）
  sed -i '1s/^\xEF\xBB\xBF//' "$file"
  
  # 修复JavaScript innerHTML字符串中的换行符
  # 将 <div class="wechat-modal-content">\n<h3 ... 改成一行
  sed -i ':a;N;$!ba;s/<div class="wechat-modal-content">\n<h3 id="微信扫码分享">微信扫码分享<\/h3><img src="'"'"' + qrcodeUrl + '"'"'" alt="QR Code"><p>打开微信扫一扫，分享到朋友圈<\/p>\n<button onclick="this.parentElement.parentElement.remove()">关闭<\/button><\/div>'"'"'/ <div class="wechat-modal-content"><h3>微信扫码分享<\/h3><img src="'"'"' + qrcodeUrl + '"'"'" alt="QR Code"><p>打开微信扫一扫，分享到朋友圈<\/p><button onclick="this.parentElement.parentElement.remove()">关闭<\/button><\/div>'"'"'/g' "$file"
  
  echo "  -> 已修复"
done

echo ""
echo "=== 修复完成 ==="
echo "请检查文件，然后提交到GitHub"
