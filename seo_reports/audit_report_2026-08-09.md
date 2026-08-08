# cncdisplay.com 首次全站巡检验证报告（2026-08-09）

方法论: /cncdisplay-audit（基线→核活站→机器+可见双维度→修复闭环→沉淀）

## Step 0 基线
full_gate 12 项检查 ALL PASS（site_checker/redirect_hard/link_check/5入口/page_standard/canonical/lang_switch/lang_reverse/link_correctness/knowledge_data/redirect_audit/jsonld）

## Step 1 全页扫描（不漏任何页面）
- URL 清单: 828 个（本地 561 html + sitemap 450 + _redirects 源，去重）
- 活站 curl 实证: 200=542, 重定向=286, 404=0, 异常=0
- 重定向 286 条跟随终态: 全部落 200
- 全 816 URL 跟随验证: 全 200（1 个 503 = 并发限流瞬态, 单独复核 200）

## Step 2 双维度
- 机器: 编码/乱码/字节级扫描 0 硬错; canonical 自引用; 5入口完整; 知识数据一致; 重定向语义零错配; 断链 0
- 用户可见: 中英切换 zh→en + en→zh 双向验证通过; CTA(View Specs/Related Resources)位置正确; 首页/zh 零乱码

## 发现并修复
| 级别 | 问题 | 处理 |
|------|------|------|
| P0 | _redirects /cdn-cgi/l/email-protection 垃圾规则(活站404) | 已删 + worker 重生成 (commit 4172ee78) |
| 工具 | 反向语言切换无门禁 | 新增 check_lang_reverse.py 入 full_gate |

## 结论
站点健康，无遗留功能问题。新增 backlog: 160 页缺 viewport/description(增强债, 不阻塞)。

## 沉淀
- scripts/live_scan.py 全页活站扫描器(入库, 可复用)
- scripts/check_lang_reverse.py 反向语言切换门禁
- 首次审计建立基线，后续审计 diff 基线只看新增问题
