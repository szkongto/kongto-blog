# cncdisplay.com — 严格SOP

## 核心原则

> **pre-commit hook 自动检查。不要用 --no-verify 绕过。**
> hook 挡住就修，别跳过。

## 强制 Skill（改动/审计/重定向，开工第一步）

**任何对本站的改动，先调用对应 skill，再动手：**
- `/cncdisplay-change` — 任何修改的强制 SOP（查关联图→中英平行→5入口→全量验证→活站实证）
- `/cncdisplay-audit` — 全站审计方法论（建基线→核活站→机器+可见元素→闭环回归）
- `/cncdisplay-redirect-rebuild` — 重定向烂账清算重建

**全站关联图（改前必查）**：`data/site_map.json`（由 `scripts/site_map.py` 生成）
- 改型号/产品 → 查 `models`：该型号被哪些页面引用，连带全改
- 查中英孪生 → `zh_en_pairs`
- 任何修改步骤 0 先 query 这张图，**不存在"只改一个文件"的修改**

## 修改流程

### Step 0: 查关联图 + 规划

```bash
python -c "import json; m=json.load(open('data/site_map.json',encoding='utf-8')); print(m['models'].get('A61L00010093'))"
```

- 查型号引用/中英孪生，列"连带修改清单"
- 跨文件/新增功能 → /plan
- **杜绝边猜边写导致连带bug。**

### Step 1: 修改代码

只改目标文件。

- 小改（1-2文件）直接改
- 跨文件/新增功能 → 先 /plan

### Step 2: 自查

git diff --stat          # 确认只改了目标文件
git diff                 # 逐行检查每个改动
python scripts/full_gate.py --quick   # 硬门禁: site_checker+redirect+link+5入口，全过才提交

### Step 3: 审查（改量大时推荐）

对 Claude 发：
```
帮我审查这次修改，看看有没有漏改、改错、引入回归的地方
```
自动调用 reviewer skill 做对抗性审查。

### Step 4: 提交（hook 自动检查）

git add -A
git commit -m "fix: 具体描述改了什么"

pre-commit hook 自动执行：
1. **Auto-fix** — python scripts/site_checker.py --fix
2. **Error check** — ERROR > 50 阻止提交
3. **Link check** — 断链 > 5 个阻止提交

### Step 5: 推送

git push

### Worker 部署规则（重要）

**`_redirects` 是重定向真相源，`cloudflare-worker.js` 会被 `scripts/gen_redirect_worker.py` 覆盖。**

1. 所有重定向加在 `_redirects`，不要直接改 `cloudflare-worker.js`
2. 程序化逻辑（catch-all、PDF canonical）改 `scripts/gen_redirect_worker.py`
3. 改完必须验证：GitHub Actions → deploy-worker job success + **curl 抓活站**确认 301/200 落正确页（不是看文件、不是看 CI 过）
4. **提交前必须跑 `python scripts/audit_redirects.py`**（pre-commit 已内置硬错门禁：自循环/目标404/跨型号错配 阻止提交）。全量审计用 audit_redirects.py，全站每次大改后跑一遍

### 产品页标准布局（2026-08-05 统一，严格位置）

**每个位置严格放什么（勿随意挪动/堆叠）：**
1. `<h1>` 产品标题
2. `<p class="desc">` 产品描述
3. **View Specs & Guide** 按钮（顶部**唯一**文章入口，橙色 #FF6600，padding 12px 24px）
4. `price-row`（价格/库存）
5. `paypal-section`（购买区：数量/国家/运费/合计/PayPal 按钮）
6. 产品详情/规格表
7. Warranty & Service
8. "Ready to replace your CRT?" CTA
9. `id="related-resources"`（**页底**，`</main>` 前）

**禁止**：产品页顶部放 Get a Quote 按钮（批量询价走导航菜单/邮件/电话）；顶部堆叠两个文章链接（View Specs 按钮 与 Related Resources 不得相邻）。

### 排名/流量异常处置（2026-08-05 教训，铁律）

1. **用户报排名掉/流量崩/关键词丢失 → 第一步 curl 活站查重定向 + 跑 audit_redirects.py，禁止回答"SEO 正常/等收录/迁移期掉排名"**
2. 只有查证过重定向、页面 200、无错配，才能谈"等谷歌重新收录"
3. 一切"已确认/已上线/验证过"的结论，必须带 curl/HTTP 实证，空口声明无效

### 关键操作模型分级

**改重定向 / 删页 / 改价 / 部署 / Schema 结构变更 = 关键操作，必须用强模型（opus/sonnet）**，禁止用 flash 档执行或"确认"。flash 档只做内容生成类（文章/翻译/文案）。

### hook 阻止了提交

1. 看错误信息定位问题
2. 修复后重新 git add + git commit
3. **不要**用 --no-verify

## 可用技能

- /site-check — 全站HTML质量扫描
- /plan — 改前出方案（跨文件必用）
- 帮我审查这次修改 — 调用 reviewer 做对抗性审查

## Workflow 自动化指令

### /seo-patrol — 每周SEO/GEO巡检

运行技术SEO + GEO合规 + 内容缺口 + 性能检查，生成报告到 seo_reports/。

```text
/seo-patrol
```

### /competitor-radar — 竞品情报雷达

抓取15+竞品数据 → AI分析 → 对比报告 → 行动建议。

```text
/competitor-radar
```

### /content-factory "文章主题" — 内容工厂

一键完成：关键词调研 → 英文文章 → 中文版本 → Git推送。

```text
/content-factory "FANUC A61L-0001-0093 LCD upgrade complete guide"
```

### /market-research "品类/关键词" — 市场调研

多平台（eBay/Amazon/AliExpress）品类分析 → 价格分布 → 机会点。

```text
/market-research "CNC display"
```

### /price "型号" — 定价×销量速查

Amazon + eBay 实时价格 + 销量估算，适合开新店/上新定价。

```text
/price "FANUC A61L-0001-0093"
/price "Mitsubishi MDT962B"
```

## Forum Outreach Plan

指南: docs/forum-outreach-plan.md

- 目标: Practical Machinist, CNCzone, Reddit (r/Machinists, r/CNC)
- 2-3回复/周/平台，4段结构（共情→排查→方案→协助）
- 模板: CRT闪烁/黑屏/LCD升级/对比
- 4:1 非商业:商业比例；反检测（IP多样化、措辞变换、频率限制）
- 禁联盟链接、禁复制粘贴、禁多账号

## 已知的 CI 警告（可忽略）

- weixin:// 协议链接（微信 deep link，非HTTP）
- zh/ 目录中文 URL 编码的历史遗留断链
- ${r.url} 模板变量（search.html 的 JS 模板）
