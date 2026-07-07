export const meta = {
  name: 'seo-weekly-patrol',
  description: '每周SEO/GEO巡检：技术SEO + GEO合规 + 内容缺口 + 性能检查',
  phases: [
    { title: '技术SEO' },
    { title: 'GEO合规' },
    { title: '内容分析' },
    { title: '报告合成' },
  ],
}

// ============================================================
// 配置区 — 按需修改
// ============================================================
const SITE_URL = 'https://cncdisplay.com'
const SITE_DIR = 'd:\\code\\seo_deploy'
const LANGUAGES = ['en', 'zh']
const CONTENT_DIRS = ['posts', 'docs', 'guides', 'brands']

// ============================================================
// Phase 1: 技术SEO 检查
// ============================================================
phase('技术SEO')

const techResults = await parallel([
  () => agent(
    `检查 ${SITE_URL} 的技术SEO状况:
1. 爬取首页和分析页面结构，检查 title/meta description/h1/h2 标签
2. 找 robots.txt 是否正确
3. 检查 sitemap 是否有
4. 检查规范标签

输出发现问题和修复建议。按严重度分类: critical/major/minor。`,
    { label: '技术SEO扫描', schema: {
      type: 'object',
      properties: {
        issues: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
              category: { type: 'string' },
              finding: { type: 'string' },
              fix: { type: 'string' },
            },
            required: ['severity', 'category', 'finding', 'fix'],
          },
        },
        score: { type: 'number', minimum: 0, maximum: 100 },
      },
      required: ['issues', 'score'],
    }}
  ),
  () => agent(
    `检查 ${SITE_URL} 的页面加载性能:
1. 首页加载速度
2. 图片是否优化
3. Core Web Vitals 信号
4. 移动端适配

列出性能问题和优化建议。`,
    { label: '性能检查', schema: {
      type: 'object',
      properties: {
        issues: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
              finding: { type: 'string' },
              fix: { type: 'string' },
            },
            required: ['severity', 'finding', 'fix'],
          },
        },
        score: { type: 'number', minimum: 0, maximum: 100 },
      },
      required: ['issues', 'score'],
    }}
  ),
  () => agent(
    `检查 ${SITE_URL} 的链接健康度:
1. 找首页上所有链接，检查是否存在断链
2. 找页面中的死链
3. 检查重定向链

输出所有问题链接。`,
    { label: '链接审计', schema: {
      type: 'object',
      properties: {
        broken_links: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              url: { type: 'string' },
              status: { type: 'integer' },
              page: { type: 'string' },
            },
          },
        },
        total_checked: { type: 'integer' },
        broken_count: { type: 'integer' },
      },
      required: ['broken_links', 'total_checked', 'broken_count'],
    }}
  ),
])

// ============================================================
// Phase 2: GEO合规 检查
// ============================================================
phase('GEO合规')

const geoResults = await parallel([
  () => agent(
    `检查 ${SITE_URL} 的GEO/AI搜索准备度:
1. llms.txt 是否存在、内容是否完整
2. 网站是否符合AI搜索爬虫要求
3. 是否有结构化数据标记 (Schema.org)
4. 是否有品牌知识面板信号
5. 内容的可引用性

输出优化建议。`,
    { label: 'GEO准备度', schema: {
      type: 'object',
      properties: {
        issues: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
              finding: { type: 'string' },
              fix: { type: 'string' },
            },
            required: ['severity', 'finding', 'fix'],
          },
        },
        score: { type: 'number', minimum: 0, maximum: 100 },
      },
      required: ['issues', 'score'],
    }}
  ),
  () => agent(
    `检查 ${SITE_URL} 的多语言SEO:
1. hreflang 标签是否正确
2. 中文版(/zh/)内容是否与英文版对应
3. 有没有孤立页面（只在一个语言存在）

输出多语言问题。`,
    { label: '多语言检查', schema: {
      type: 'object',
      properties: {
        issues: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
              finding: { type: 'string' },
              page: { type: 'string' },
              fix: { type: 'string' },
            },
            required: ['severity', 'finding', 'fix'],
          },
        },
      },
      required: ['issues'],
    }}
  ),
])

// ============================================================
// Phase 3: 内容分析
// ============================================================
phase('内容分析')

// 扫描本地内容目录
const contentFiles = await parallel(
  LANGUAGES.flatMap(lang =>
    CONTENT_DIRS.filter(d => d !== 'brands').map(dir => () =>
      agent(
        `分析 ${SITE_DIR}/${lang}/${dir}/ 目录的内容情况:
1. 最新发布的5篇文章（按文件名日期）
2. 内容主题分布
3. 有没有陈旧内容需要更新
4. 内容缺口 — 竞争对手在写但你没写的主题

输出分析结果。`,
        { label: `${lang}/${dir} 内容审计`, schema: {
          type: 'object',
          properties: {
            total_pages: { type: 'integer' },
            recent_topics: { type: 'array', items: { type: 'string' } },
            stale_pages: { type: 'array', items: { type: 'string' } },
            content_gaps: { type: 'array', items: { type: 'string' } },
            suggestions: { type: 'array', items: { type: 'string' } },
          },
          required: ['total_pages', 'suggestions'],
        }}
      )
    )
  )
)

// ============================================================
// Phase 4: 报告合成
// ============================================================
phase('报告合成')

const reportDate = (args?.date || '').slice(0, 10) || 'YYYY-MM-DD'
const reportPath = `${SITE_DIR}/seo_reports/seo-patrol-${reportDate}.md`

// 聚合所有发现
const allIssues = [
  ...techResults.filter(Boolean).flatMap(r => r.issues || []),
  ...geoResults.filter(Boolean).flatMap(r => r.issues || []),
]
const criticalCount = allIssues.filter(i => i.severity === 'critical').length
const majorCount = allIssues.filter(i => i.severity === 'major').length
const minorCount = allIssues.filter(i => i.severity === 'minor').length

const techScore = techResults.filter(Boolean).reduce((sum, r) => sum + (r.score || 0), 0) / techResults.filter(Boolean).length
const geoScore = geoResults.filter(Boolean).reduce((sum, r) => sum + (r.score || 0), 0) / geoResults.filter(Boolean).length

// 生成markdown报告
const reportLines = [
  `# SEO/GEO 每周巡检报告 — ${reportDate}`,
  '',
  '## 概览',
  '',
  `| 维度 | 得分 | 问题数 |`,
  `|------|------|--------|`,
  `| 技术SEO | ${Math.round(techScore)}/100 | ${techResults.filter(Boolean).flatMap(r => r.issues || []).length} |`,
  `| GEO合规 | ${Math.round(geoScore)}/100 | ${geoResults.filter(Boolean).flatMap(r => r.issues || []).length} |`,
  `| **合计** | | **${allIssues.length}** (critical:${criticalCount} major:${majorCount} minor:${minorCount}) |`,
  '',
  '## Critical 问题',
  '',
  ...allIssues.filter(i => i.severity === 'critical').map(i => `- [ ] **${i.category || '通用'}**: ${i.finding}\n  → ${i.fix}`),
  '',
  allIssues.filter(i => i.severity === 'critical').length === 0 ? '无\n' : '',
  '## Major 问题',
  '',
  ...allIssues.filter(i => i.severity === 'major').map(i => `- [ ] **${i.category || '通用'}**: ${i.finding}\n  → ${i.fix}`),
  '',
  allIssues.filter(i => i.severity === 'major').length === 0 ? '无\n' : '',
  '## Minor 问题',
  '',
  ...allIssues.filter(i => i.severity === 'minor').map(i => `- [ ] **${i.category || '通用'}**: ${i.finding}\n  → ${i.fix}`),
  '',
  '## 内容分析',
  '',
  ...contentFiles.filter(Boolean).flatMap(r => [
    `- 页面数: ${r.total_pages || 'N/A'}`,
    `- 近期主题: ${(r.recent_topics || []).join(', ')}`,
    `- 陈旧内容: ${(r.stale_pages || []).join(', ') || '无'}`,
    `- 内容缺口: ${(r.content_gaps || []).join(', ') || '无'}`,
    `- 建议: ${(r.suggestions || []).join('; ')}`,
  ]),
  '',
  '## 建议行动项',
  '',
  ...(criticalCount > 0 ? [`1. 🔴 立即修复 ${criticalCount} 个Critical问题`] : []),
  ...(majorCount > 0 ? [`2. 🟡 本周修复 ${majorCount} 个Major问题`] : []),
  `3. 📊 技术SEO得分 ${Math.round(techScore)}/100，目标 >85`,
  `4. 🌐 GEO合规得分 ${Math.round(geoScore)}/100，目标 >80`,
  `5. 🔗 断链 ${techResults[2]?.broken_count || 0} 个`,
]

const report = reportLines.join('\n')

log(`报告已生成: ${reportPath}`)
log(`发现 ${criticalCount} critical + ${majorCount} major + ${minorCount} minor 问题`)
log(`技术SEO得分 ${Math.round(techScore)}/100, GEO得分 ${Math.round(geoScore)}/100`)

return { reportPath, report, summary: { criticalCount, majorCount, minorCount, techScore, geoScore } }
