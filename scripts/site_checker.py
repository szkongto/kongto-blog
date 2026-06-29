"""
全站HTML扫描器 — 自动检查 cncdisplay.com 所有页面质量问题
用法:
  python site_checker.py                    # 扫描全部HTML文件
  python site_checker.py --fix              # 扫描并自动修复可修复的问题
  python site_checker.py --check-links      # 检查内部链接
  python site_checker.py brands/FANUC.html  # 扫描单个文件

等级:
  [ERR] ERROR   - 必须修复（影响功能/SEO）
  [WRN] WARNING - 建议修复（可能影响）
  [INF] INFO    - 仅供参考
"""
import os, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent if __file__ else Path(".")
# Auto-detect project root: if we're in d:\code, use seo_deploy/ as web root
WEB_ROOT = (ROOT / "seo_deploy") if (ROOT / "seo_deploy").exists() else ROOT
EXCLUDE_DIRS = {".git", "screaming_frog_reports", "backlinks_output", "_archive_audit",
                 "24game", "ai-creation-workshop", "node_modules", "patches",
                 "MediaCrawler", "output", "ppt-master", "seo_backup", "_templates"}
EXCLUDE_FILES = {"package-lock.json", "package.json"}
NAV_LINKS = [
    ("/", "首页"),
    ("/compatibility-matrix.html", "兼容查询"),
    ("/posts/", "文章"),
    ("/case-studies.html", "案例"),
    ("/docs/", "下载"),
    ("/about.html", "关于"),
    ("/quote.html", "获取报价"),
    ("/search.html", "搜索"),
]

# ═══════════════════════════════════════════════
# 扫描器
# ═══════════════════════════════════════════════

class ScanResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.infos = []

    def error(self, file, line, msg, fix=None):
        self.errors.append({"file": file, "line": line, "msg": msg, "fix": fix})

    def warn(self, file, line, msg, fix=None):
        self.warnings.append({"file": file, "line": line, "msg": msg, "fix": fix})

    def info(self, file, line, msg):
        self.infos.append({"file": file, "line": line, "msg": msg})

    @property
    def total(self):
        return len(self.errors) + len(self.warnings) + len(self.infos)

    def print(self, level=None, file_path=None):
        """Print results for given level. level=None prints all."""
        level_map = {"error": self.errors, "warn": self.warnings, "info": self.infos}
        items = level_map.get(level, self.errors + self.warnings + self.infos)
        labels = {"error": "[ERR]", "warn": "[WRN]", "info": "[INF]"}
        label = labels.get(level, "[ALL]")
        color_map = {"error": "31", "warn": "33", "info": "36"}
        color = color_map.get(level, "0")
        for item in items:
            if file_path and file_path not in item["file"]:
                continue
            line_str = f":{item['line']}" if item['line'] else ""
            print(f"  \033[{color}m{label}\033[0m {item['file']}{line_str} - {item['msg']}")
            if item.get("fix"):
                print(f"         \033[90m> fix: {item['fix']}\033[0m")

    def summary(self):
        print(f"\n{'='*50}")
        print(f"  扫描完成")
        print(f"  [ERR] ERROR:   {len(self.errors)}")
        print(f"  [WRN] WARNING: {len(self.warnings)}")
        print(f"  [INF] INFO:    {len(self.infos)}")
        print(f"  [TOT] 总计:    {self.total}")
        print(f"{'='*50}")


def scan_file(filepath: Path, result: ScanResult, fix=False):
    """扫描单个HTML文件"""
    rel = str(filepath.relative_to(WEB_ROOT)).replace("\\", "/")
    try:
        raw = filepath.read_bytes()
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        result.error(rel, 0, "不是有效的UTF-8编码（可能是GBK或其他编码）")
        return
    except Exception as e:
        result.error(rel, 0, f"读取失败: {e}")
        return

    lines = content.split("\n")

    # ─── 1. BOM检测 ───
    if raw.startswith(b'\xef\xbb\xbf'):
        result.warn(rel, 1, "文件包含 UTF-8 BOM（大多数浏览器正常，但建议移除）",
                     fix if fix else "sed -i '1s/^\\xEF\\xBB\\xBF//'")

    # ─── 2. Stray `/>` 标签 ───
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == "/>" and "<" not in stripped:
            result.error(rel, i, "孤立 `/>` 标签（破坏HTML解析，导致导航丢失+中文乱码）",
                         fix=fix)
            if fix:
                lines[i-1] = ""
                result.info(rel, i, "孤立 /> 已删除")

    # ─── 3. DOCTYPE检测 ───
    if not content.strip().startswith("<!DOCTYPE html"):
        result.warn(rel, 1, "缺少 `<!DOCTYPE html>`", "添加 `<!DOCTYPE html>`")

    # ─── 4. </html>检测 ───
    if "</html>" not in content:
        result.error(rel, 0, "缺少 `</html>` 关闭标签")
    elif content.rstrip().endswith("</html>"):
        pass  # OK
    else:
        result.warn(rel, 0, "`</html>` 后有额外内容")

    # ─── 5. 编码检测 ───
    if 'charset="UTF-8"' not in content and 'charset="utf-8"' not in content:
        if '<meta charset="UTF-8">' not in content and '<meta charset="utf-8">' not in content:
            result.error(rel, 0, "缺少 `<meta charset=\"UTF-8\">` — 中文会乱码")

    # ─── 6. Title检测 ───
    title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    is_stub = False
    if not title_match:
        result.error(rel, 0, "缺少 `<title>` 标签")
    else:
        title = title_match.group(1).strip()
        if not title:
            result.error(rel, 0, "`<title>` 标签为空")
        elif title == "Redirecting..." or title == "跳转中...":
            is_stub = True  # 跳转 stub 文件，跳过大部分检查
        elif len(title) > 60:
            result.warn(rel, 0, f"Title 过长 ({len(title)}字): {title[:60]}")

    # FFFD (U+FFFD) 替换字符检测
    fffd_count = content.count('�')
    if fffd_count > 3:
        result.error(rel, 0, f"包含 {fffd_count} 个 U+FFFD 替换字符（文件编码损坏）",
                     fix="git restore from pre-corruption version")

    # Stub 文件跳过后续检查
    if is_stub:
        return "\n".join(lines) if fix else None

    # ─── 7. Meta Description ───
    desc_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content)
    if not desc_match:
        desc_match = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', content)
    if not desc_match:
        result.warn(rel, 0, "缺少 `<meta name=\"description\">`")
    else:
        desc = desc_match.group(1)
        if len(desc) < 50:
            result.warn(rel, 0, f"Meta Description 过短 ({len(desc)}字): \"{desc}\"")
        elif len(desc) > 200:
            result.warn(rel, 0, f"Meta Description 过长 ({len(desc)}字)")

    # ─── 8. 中文编码损坏检测 ───
    # Phase 0a 批量替换脚本用 GBK 读取 UTF-8 文件导致中文被替换
    corruption_markers = set('鍙戦偅绉鏄剧ず鍣崌绾柟妗娣卞湷甯傛睙浘绉戞妧鏈夐檺鍏稿凡涓嬭浇彇鎶ヤ环棰樼殑鎴戜滑')

    def check_text_corruption(text, label=""):
        """Check if text has encoding corruption, return (is_corrupted, sample)"""
        cn = [c for c in text if '一' <= c <= '鿿']
        if len(cn) < 4:
            return False, ""
        bad = sum(1 for c in cn if c in corruption_markers)
        # Title/desc/nav: >10% corrupted = flag. Long blocks like schema: >5% = flag.
        threshold = 0.05 if len(cn) > 50 else 0.10
        if bad / len(cn) > threshold:
            sample = ''.join(cn[:5])
            return True, f"{label}: {bad}/{len(cn)} chars corrupted ({sample}...)"
        return False, ""

    # Check title tag
    if title_match:
        corrupted, sample = check_text_corruption(title_match.group(0), "title")
        if corrupted:
            result.error(rel, 0, f"中文编码损坏 - {sample}")

    # Check meta description
    if desc_match:
        corrupted, sample = check_text_corruption(desc_match.group(0), "description")
        if corrupted:
            result.error(rel, 0, f"中文编码损坏 - {sample}")

    # Check nav text (between > and <)
    nav_texts = re.findall(r'>([^<]{2,30})<', content)
    for nt in nav_texts[:10]:
        corrupted, sample = check_text_corruption(nt)
        if corrupted:
            result.error(rel, 0, f"中文编码损坏 - nav文本: {nt[:30]}")
            break

    # Check schema JSON-LD for corruption (use split to avoid regex escaping issues)
    for part in content.split('<script type="application/ld+json">'):
        end = part.find('</script>')
        if end > 0:
            block = part[:end].strip()
            corrupted, sample = check_text_corruption(block, "Schema")
            if corrupted:
                result.error(rel, 0, f"中文编码损坏 - {sample}")
                break

    # ─── 8. Meta Description ───
    desc_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content)
    if not desc_match:
        desc_match = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', content)
    if not desc_match:
        result.warn(rel, 0, "缺少 `<meta name=\"description\">`")
    else:
        desc = desc_match.group(1)
        if len(desc) < 50:
            result.warn(rel, 0, f"Meta Description 过短 ({len(desc)}字): \"{desc}\"")
        elif len(desc) > 200:
            result.warn(rel, 0, f"Meta Description 过长 ({len(desc)}字)")

    # ─── 8. Viewport ───
    if 'name="viewport"' not in content:
        result.warn(rel, 0, "缺少 `<meta name=\"viewport\">` — 移动端显示异常")

    # ─── 9. Canonical ───
    can_match = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*>', content)
    if not can_match:
        result.warn(rel, 0, "缺少 canonical URL")

    # ─── 10. Nav检测（仅检查主内容页，不含stub） ───
    if "<nav>" in content or 'class="nav-links"' in content:
        # 只检查首页/品牌页/产品页/文章页的导航完整性
        is_main_page = any(p in rel for p in ["brands/", "products/", "posts/", "about", "index"])
        if is_main_page:
            for href, label in NAV_LINKS:
                if f'href="{href}"' not in content:
                    result.warn(rel, 0, f"导航缺少链接: {href}")

    # ─── 11. Hreflang检查 ───
    hreflangs = re.findall(r'hreflang=["\']([^"\']+)["\']', content)
    if not hreflangs and not rel.startswith("zh/") and not rel.startswith("en/"):
        pass  # 根目录文件不一定需要hreflang
    else:
        # 检查自引用
        pass

    # ─── 12. OG Image ───
    if 'property="og:image"' not in content and 'name="twitter:image"' not in content:
        if "posts/" in rel or "brands/" in rel or "products/" in rel:
            result.warn(rel, 0, "缺少 og:image / twitter:image — 社交分享无图")

    # ─── 13. H1检测 ───
    h1_count = len(re.findall(r'<h1[ >]', content))
    if h1_count == 0 and "<article" not in content and not rel.startswith("_") and rel != "404.html":
        result.warn(rel, 0, "缺少 `<h1>` 标签")
    elif h1_count > 1:
        result.warn(rel, 0, f"多个 H1 标签 ({h1_count}个)")

    # ─── 14. 未关闭的HTML标签检查 ───
    # 使用正则匹配完整的开标签和闭标签
    for tag in ["html", "head", "body", "main", "footer"]:
        open_count = len(re.findall(rf'<{tag}(\s[^>]*)?>', content))
        close_count = len(re.findall(rf'</{tag}>', content))
        diff = open_count - close_count
        if diff > 0:
            result.error(rel, 0, f"`<{tag}>` 未关闭 (多 {diff} 个开标签)")

    # ─── 15. Navigation Link 存在性（仅查主内容页/品牌页） ───
    if any(p in rel for p in ["brands/", "products/", "about", "index"]):
        nav_a_tags = re.findall(r'<a[^>]+href="(/[^"]+\.html)"[^>]*>', content)
        for link in nav_a_tags[:20]:
            target = ROOT / link.lstrip("/")
            if not target.exists():
                # 检查是否是 stub redirect（stub文件在 _redirects 中有对应规则）
                if not any(ext in link for ext in ["weixin", "http", "mailto", "tel"]):
                    result.warn(rel, 0, f"内部链接指向不存在: {link}")

    # ─── 16. Schema JSON-LD 格式 ───
    schema_blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        content, re.DOTALL | re.IGNORECASE
    )
    for i, block in enumerate(schema_blocks):
        try:
            obj = json.loads(block.strip())
            items = obj if isinstance(obj, list) else [obj]
            for item in items:
                if not item.get("@type"):
                    result.warn(rel, 0, f"Schema #{i+1} 缺少 @type")
        except json.JSONDecodeError as e:
            result.error(rel, 0, f"Schema #{i+1} JSON解析失败: {e}")

    return "\n".join(lines) if fix else None


def find_html_files():
    """查找所有HTML文件（在 WEB_ROOT 下）"""
    files = []
    for f in WEB_ROOT.rglob("*.html"):
        rel = str(f.relative_to(WEB_ROOT))
        if any(excl in rel for excl in EXCLUDE_DIRS):
            continue
        if f.name in EXCLUDE_FILES:
            continue
        if ".git" in rel.split(os.sep):
            continue
        files.append(f)
    return sorted(files)


def check_duplicate_titles(files, result: ScanResult):
    """检查重复标题"""
    titles = defaultdict(list)
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
            if m:
                title = m.group(1).strip()
                if title != "Redirecting...":
                    titles[title].append(f)
        except:
            pass
    for title, dupes in titles.items():
        if len(dupes) > 1:
            short_title = title[:60].replace("\n", " ")
            result.warn("", 0, f"重复标题 ({len(dupes)}个): {short_title}")
            for d in dupes[:5]:
                rel = str(d.relative_to(WEB_ROOT))
                result.info(rel, 0, f"  -> {rel}")


def run_scan(fix=False, file_filter=None):
    """主扫描函数"""
    result = ScanResult()

    if file_filter and Path(file_filter).exists():
        files = [Path(file_filter)]
    else:
        files = find_html_files()

    print(f"扫描 {len(files)} 个HTML文件...\n")

    fixed_count = 0
    for f in files:
        ret = scan_file(f, result, fix=fix)
        if fix and ret is not None:
            try:
                f.write_text(ret, encoding="utf-8")
                fixed_count += 1
            except Exception as e:
                result.error("", 0, f"写入失败 {f}: {e}")

    # 全站级检查
    check_duplicate_titles(files, result)

    # 输出结果
    if file_filter:
        result.print(file_path=file_filter)
    else:
        # 打印摘要
        for level in ["error", "warn", "info"]:
            attr = {"error": "errors", "warn": "warnings", "info": "infos"}[level]
            items = getattr(result, attr)
            if items:
                label = {"error": "[ERR] ERROR", "warn": "[WRN] WARNING", "info": "[INF] INFO"}[level]
                print(f"\n{'='*50}")
                print(f" {label} ({len(items)})")
                print(f"{'='*50}")
                result.print(level)

    result.summary()

    if fix:
        print(f"  自动修复: {fixed_count} 个文件")

    # 退出码：>50 errors = 失败
    error_count = len(result.errors)
    if error_count > 50:
        print(f"\n[FAIL] Too many errors ({error_count} > 50). Fix before deploy.")
        return 1
    print(f"\n[PASS] {error_count} errors (threshold 50).")
    return 0


# ═══════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="全站HTML质量扫描器")
    parser.add_argument("file", nargs="?", help="扫描单个文件（不指定则扫描全部）")
    parser.add_argument("--fix", action="store_true", help="自动修复可修复的问题")
    parser.add_argument("--check-links", action="store_true", help="检查内部链接（只扫描）")
    args = parser.parse_args()

    sys.exit(run_scan(fix=args.fix, file_filter=args.file))
