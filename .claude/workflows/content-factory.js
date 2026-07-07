export const meta = {
  name: 'content-factory',
  description: '内容工厂：关键词调研→文章生成→GEO优化→多语言→推送',
  phases: [
    { title: '关键词调研' },
    { title: '英文创作' },
    { title: '中文创作' },
    { title: '推送上线' },
  ],
}

// ============================================================
// 配置
// ============================================================
const SITE_DIR = 'd:\\code\\seo_deploy'
const SITE_URL = 'https://cncdisplay.com'
const LANG = ['en', 'zh']

// ============================================================
// Phase 1: 关键词调研
// ============================================================
phase('关键词调研')

const articleTopic = args?.topic || args?.[0]
if (!articleTopic) {
  log('错误: 需要提供文章主题。用法: Workflow({name:"content-factory", args:"FANUC A61L-0001-0093 LCD upgrade guide"})')
  return { error: 'no topic provided' }
}

log(`开始创作: ${articleTopic}`)

const keywordResearch = await agent(
  `为 "${articleTopic}" 做关键词调研:

1. 这个主题的搜索意图是什么? (信息型/商业型/交易型)
2. 主要关键词和相关长尾词
3. 搜索量估算 (低/中/高)
4. 竞争度评估
5. 建议的文章角度/独特卖点 — 为什么用户选我们而不是竞品?

目标网站: ${SITE_URL} (Kongto Technology, CNC CRT转LCD产品)`,
  { label: '关键词调研', phase: '关键词调研', schema: {
    type: 'object',
    properties: {
      search_intent: { type: 'string' },
      primary_keyword: { type: 'string' },
      long_tail_keywords: { type: 'array', items: { type: 'string' } },
      competition_level: { type: 'string', enum: ['low', 'medium', 'high'] },
      angle: { type: 'string' },
      target_audience: { type: 'string' },
    },
    required: ['search_intent', 'primary_keyword', 'long_tail_keywords', 'competition_level', 'angle'],
  }}
)

// ============================================================
// Phase 2: 英文文章创作
// ============================================================
phase('英文创作')

const enArticle = await agent(
  `写一篇英文SEO文章, 主题: ${articleTopic}

关键词调研结果:
- 主要关键词: ${keywordResearch.primary_keyword}
- 长尾词: ${(keywordResearch.long_tail_keywords || []).join(', ')}
- 搜索意图: ${keywordResearch.search_intent}
- 推荐角度: ${keywordResearch.angle}

要求:
1. **标题** — 包含主要关键词, 有吸引力
2. **SEO优化** — 自然融入关键词和长尾词, H1/H2/H3结构
3. **GEO优化** — 段落开头用清晰的问题/答案结构, 便于AI搜索抓取
4. **行动号召** — 引导到 cncdisplay.com 产品页
5. **长度** — 1500-2500字
6. **品牌提及** — 文中自然提到Kongto Technology的解决方案
7. **链接** — 内链到相关页面

直接输出完整HTML文章内容。不要markdown。用中文思考和规划, 输出英文文章。`,
  { label: '写英文文章', phase: '英文创作', schema: {
    type: 'object',
    properties: {
      title: { type: 'string' },
      slug: { type: 'string' },
      html_content: { type: 'string' },
      meta_description: { type: 'string' },
      focus_keyword: { type: 'string' },
      internal_links: { type: 'array', items: { type: 'string' } },
    },
    required: ['title', 'slug', 'html_content', 'meta_description'],
  }}
)

// ============================================================
// Phase 3: 中文文章创作
// ============================================================
phase('中文创作')

const zhArticle = await agent(
  `将以下英文文章翻译并改写为中文版, 适配中文SEO和百度:

英文标题: ${enArticle.title}
英文描述: ${enArticle.meta_description}
关键内容: ${enArticle.html_content.slice(0, 2000)}...

要求:
1. 标题 — 中文SEO优化, 包含中文关键词
2. 不要直译, 要本地化改写
3. 百度SEO优化
4. 链接到 ${SITE_URL}/zh/ 对应页面
5. 直接输出完整HTML

slug用中文拼音或英文短横形式。`,
  { label: '写中文文章', phase: '中文创作', schema: {
    type: 'object',
    properties: {
      title: { type: 'string' },
      slug: { type: 'string' },
      html_content: { type: 'string' },
      meta_description: { type: 'string' },
    },
    required: ['title', 'slug', 'html_content', 'meta_description'],
  }}
)

// ============================================================
// Phase 4: 推送上线
// ============================================================
phase('推送上线')

// 生成文件名
const rawDate = (args?.date || '').slice(0, 10) || '2026-01-01'
const dateStr = rawDate.replace(/-/g, '')
const enFilename = `article_${dateStr}_${enArticle.slug}.html`
const zhFilename = `${zhArticle.slug}.html`
const enPath = `${SITE_DIR}/en/posts/${enFilename}`
const zhPath = `${SITE_DIR}/zh/posts/${zhFilename}`

// 写入文件
const enFull = `<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>${enArticle.title}</title><meta name="description" content="${enArticle.meta_description}"><link rel="canonical" href="${SITE_URL}/en/posts/${enFilename}"></head><body>${enArticle.html_content}</body></html>`

const zhFull = `<html lang="zh"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>${zhArticle.title}</title><meta name="description" content="${zhArticle.meta_description}"><link rel="canonical" href="${SITE_URL}/zh/posts/${zhFilename}"></head><body>${zhArticle.html_content}</body></html>`

// 写入磁盘
const fs = require('fs')
fs.writeFileSync(enPath, enFull, 'utf-8')
fs.writeFileSync(zhPath, zhFull, 'utf-8')

log(`英文文章: ${enPath}`)
log(`中文文章: ${zhPath}`)

// Git提交
const { execSync } = require('child_process')
try {
  execSync(`git -C ${SITE_DIR} add en/posts/${enFilename} zh/posts/${zhFilename}`, { stdio: 'pipe' })
  execSync(`git -C ${SITE_DIR} commit -m "feat: add article - ${enArticle.title}"`, { stdio: 'pipe' })
  execSync(`git -C ${SITE_DIR} push`, { stdio: 'pipe' })
  log('✅ 已推送到 GitHub，自动触发部署')
} catch (e) {
  log(`⚠️ Git操作失败: ${e.message}，文件已保存到本地`)
}

const result = {
  topic: articleTopic,
  keyword: keywordResearch.primary_keyword,
  en: { path: enPath, title: enArticle.title, slug: enArticle.slug },
  zh: { path: zhPath, title: zhArticle.title, slug: zhArticle.slug },
  url: `${SITE_URL}/en/posts/${enFilename}`,
  zh_url: `${SITE_URL}/zh/posts/${zhFilename}`,
}

return result
