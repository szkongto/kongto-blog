# cncdisplay.com 页面建设标准（单一真相源）

> 版本 1.0 / 2026-08-09
> 所有页面创建/修改必须符合本标准。机器校验：`scripts/check_page_standard.py`（挂 full_gate）。
> 新页面推荐走 `scripts/scaffold_page.py` 从模板生成（创建即合规）。

## 1. 页面结构（所有 .html 必含）

```
<!DOCTYPE html>
<html lang="zh-CN|en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>...（唯一、含品牌关键词）</title>
    <meta name="description" content="...（120-160字符，含核心词）">
    <link rel="canonical" href="https://cncdisplay.com/...">   ← 目录形式，不含 index.html
    <link rel="alternate" hreflang="en|zh-CN" href="https://cncdisplay.com/...">  ← 中英孪生
    <link rel="alternate" hreflang="x-default" href="https://cncdisplay.com/">
    <link rel="stylesheet" href="/css/style.css">（或站内统一样式）
  </head>
  <body>
    统一导航栏（含语言切换按钮）
    <main> 页面主体内容 </main>
    统一页脚（公司信息/联系方式/版权）
  </body>
</html>
```

**硬性要求：**
- `charset="utf-8"`，文件必须是合法 UTF-8（无非法字节、无 `�` 替换符、无 mojibake）
- `<title>` 唯一，与 `<h1>` 语义一致
- canonical 用**目录形式**（`/products/` 而非 `/products/index.html`）
- hreflang 中英互指 + x-default
- 语言切换按钮：zh 页 → EN 真实页；EN 页 → zh 真实页

## 2. 内链规范

- 站内链接一律用**目录形式**（`/products/`、`/posts/`），禁止链接 `/xxx/index.html`
- 链接目标必须存在（文件或目录），禁止链到 301 桩/404
- 新增型号文章必须更新 **5 入口**：posts index(EN+ZH) + brand page(EN+ZH) + products index
- 相关文章互链：产品页 → 型号文章（View Specs 按钮唯一入口）+ Related Resources 页底区

## 3. 交互按钮标准位置（产品页严格布局）

| 位置 | 元素 |
|---|---|
| 顶部 `<h1>` 下 | `<p class="desc">` 产品描述 |
| 描述下 | **View Specs & Guide** 按钮（唯一文章入口，橙色 #FF6600，padding 12px 24px） |
| 按钮下 | `price-row`（价格/库存） |
| 再下 | `paypal-section`（购买区） |
| 主体 | 产品详情/规格表 |
| 后 | Warranty & Service |
| 后 | "Ready to replace your CRT?" CTA |
| 页底 `</main>` 前 | `id="related-resources"` |

**禁止**：产品页顶部堆两个文章链接（View Specs 与 Related Resources 不得相邻）；顶部放 Get a Quote 按钮。

## 4. Schema.org 规范

- 产品页必须 `application/ld+json` Product schema，含：name / brand / offers(price, priceCurrency, availability)
- **offers 相关字段（shippingDetails / hasMerchantReturnPolicy / warranty）无真实数据必须写 `null` 或省略，禁止编造**（no-fabricate 铁律）
- 面包屑 BreadcrumbList 必须与页面路径一致

## 5. 乱码/内码规范

- 全站 UTF-8；特殊符号（箭头/图标）用 CSS 或 HTML 实体，**禁止裸 Unicode 特殊字符**（历史乱码根因）
- 校验器字节级扫描：非法 UTF-8 序列、`�`、已知 mojibake 模式（`Ã`/`Â` 序列等）

## 6. 中英双版

- 所有内容页必须有中英孪生（hreflang 互指）
- 修改一处必须同步另一语言（除非纯语言内容）
- 中文站不需要价格页（链接到文章页，见 [[zh-no-price-pages]]）

## 7. 新建页面流程（scaffold）

```bash
python scripts/scaffold_page.py --path posts/new-article.html --lang en
# 生成标准骨架 → 填内容 → 建 zh 孪生 → 补 5 入口 → python scripts/full_gate.py --quick
```

详细流程见 `/cncdisplay-page-create` skill。

## 8. 校验矩阵（full_gate 自动跑）

| 校验 | 脚本 |
|------|------|
| 页面标准（结构/canonical/hreflang/乱码） | check_page_standard.py |
| 5 入口 | site_map.py --check |
| 断链/静态资源 | check_links_ci.py |
| 重定向硬错 + 语义错配 | audit_redirects_hard.py |
| canonical 自引用 | check_canonical.py |
| 语言切换 | check_lang_switch.py |
| 知识数据一致性 | validate_knowledge_data.py |
