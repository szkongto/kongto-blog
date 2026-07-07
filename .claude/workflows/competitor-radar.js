export const meta = {
  name: 'competitor-radar',
  description: '竞品情报雷达：抓取竞品数据→AI分析→对比报告',
  phases: [
    { title: '数据采集' },
    { title: 'AI分析' },
    { title: '报告合成' },
  ],
}

// ============================================================
// 配置区 — 按需增删
// ============================================================
const COMPETITORS = [
  // CNC显示器竞品
  { name: 'LCDParts', domain: 'store.lcdparts.net', category: 'CNC Display', notes: 'FANUC/Mitsubishi replacement parts' },
  { name: 'Seawens', domain: 'www.seawens.com', category: 'CNC Display', notes: 'Industrial displays, competitor pricing' },
  { name: 'Vertex Displays', domain: 'www.vertexdisplays.com', category: 'CNC Display', notes: 'CRT replacement specialist' },
  { name: 'CNC Shopping', domain: 'www.cnc-shopping.us', category: 'CNC Display', notes: 'CNC parts & displays' },
  { name: 'LCDPart', domain: 'www.lcdpart.com', category: 'CNC Display', notes: 'LCD replacement parts' },
  { name: 'ZYLCD Shop', domain: 'www.zylcdshop.com', category: 'CNC Display', notes: 'LCD screens and replacements' },
  { name: 'Impact Computers', domain: 'impactcomputers.com', category: 'CNC Display', notes: 'Industrial computer parts' },
  // 平台listing（精选）
  { name: 'eBay Top Seller', domain: 'www.ebay.com', category: 'Marketplace', notes: 'CNC CRT to LCD listings' },
  { name: 'Amazon Top Listing', domain: 'www.amazon.com', category: 'Marketplace', notes: 'CNC display products' },
  { name: 'AliExpress', domain: 'www.aliexpress.com', category: 'Marketplace', notes: 'CNC monitor listings' },
  // 同行独立站
  { name: 'Assembla', domain: 'assemba.com', category: 'Competitor Site', notes: 'CNC display products' },
  { name: 'Electronikz', domain: 'electronikz.com', category: 'Competitor Site', notes: 'Industrial electronics' },
  { name: 'Symportion', domain: 'symportion.com', category: 'Competitor Site', notes: 'CNC parts supplier' },
  { name: 'Machinio', domain: 'www.machinio.com', category: 'Marketplace', notes: 'Used CNC machinery marketplace' },
  { name: 'FridayParts', domain: 'nz.fridayparts.com', category: 'Competitor Site', notes: 'CNC replacement parts' },
]

async function fetchCompetitorPage(comp, ctx) {
  // 用 WebFetch 抓竞品首页或产品页
  try {
    const url = `https://${comp.domain}`
    await ctx.fetch(url, `分析 ${comp.name}(${comp.domain}) 的产品和定位:
1. 首页主要卖什么产品? 价格区间?
2. 和CNC显示器/CRT替换相关吗?
3. 他们的价值主张/独特卖点是什么?
4. 网站质量和SEO水平如何?
5. 和我们(kongto/cncdisplay.com)比, 优劣势是什么?`)
    return { name: comp.name, domain: comp.domain, category: comp.category, status: 'ok', notes: comp.notes }
  } catch (e) {
    return { name: comp.name, domain: comp.domain, category: comp.category, status: 'failed', error: e.message }
  }
}

// ============================================================
// Phase 1: 数据采集
// ============================================================
phase('数据采集')

// 并行抓取竞品页面
log(`开始采集 ${COMPETITORS.length} 个竞品数据...`)

const fetched = await parallel(COMPETITORS.map(comp => () =>
  agent(`抓取并分析竞品 ${comp.name} (${comp.domain})，品类: ${comp.category}
背景: ${comp.notes}

任务:
1. 访问 ${comp.domain} 首页, 了解其产品和定位
2. 找到和CNC显示器/CRT转LCD相关的产品页面
3. 记录: 产品类型、价格区间、独特卖点、网站质量
4. 和 cncdisplay.com (Kongto Technology) 对比优劣势

输出结构化分析结果。`, {
    label: `fetch:${comp.name}`,
    phase: '数据采集',
    schema: {
      type: 'object',
      properties: {
        name: { type: 'string' },
        domain: { type: 'string' },
        category: { type: 'string' },
        products_summary: { type: 'string' },
        price_range: { type: 'string' },
        unique_selling_points: { type: 'array', items: { type: 'string' } },
        seo_quality: { type: 'string', enum: ['poor', 'average', 'good', 'excellent'] },
        strengths_vs_kongto: { type: 'array', items: { type: 'string' } },
        weaknesses_vs_kongto: { type: 'array', items: { type: 'string' } },
        opportunities: { type: 'array', items: { type: 'string' } },
        threats: { type: 'array', items: { type: 'string' } },
        overall_threat_level: { type: 'string', enum: ['low', 'medium', 'high', 'very_high'] },
      },
      required: ['name', 'domain', 'products_summary', 'strengths_vs_kongto', 'weaknesses_vs_kongto', 'overall_threat_level'],
    },
  }))
)

const successful = fetched.filter(Boolean)
log(`采集完成: ${successful.length}/${COMPETITORS.length} 成功`)

// ============================================================
// Phase 2: AI 聚合分析
// ============================================================
phase('AI分析')

// 汇总数据给分析Agent
const competitorsData = successful.map(c => ({
  name: c.name,
  category: c.category,
  products: c.products_summary,
  price: c.price_range || 'unknown',
  usp: c.unique_selling_points || [],
  strengths: c.strengths_vs_kongto || [],
  weaknesses: c.weaknesses_vs_kongto || [],
  opportunities: c.opportunities || [],
  threat: c.overall_threat_level,
}))

const analysisResult = await agent(
  `你是一个电商竞品分析师。以下是CNC显示器市场竞品分析数据:

${JSON.stringify(competitorsData, null, 2)}

请综合输出:

1. **市场格局总览** — 主要玩家、市场集中度、价格带分布
2. **Kongto的定位** — 相对于竞品的差异化优势和劣势
3. **定价策略建议** — 基于竞品价格区间的定价建议
4. **产品机会** — 竞品覆盖不足、Kongto可以切入的产品方向
5. **排名前5的紧急行动项** — 按影响度排序
6. **关键词机会** — 竞品SEO弱项, Kongto可以进攻的关键词方向

基于实际数据, 不要泛泛而谈。`,
  { label: '竞争分析综合', phase: 'AI分析', schema: {
    type: 'object',
    properties: {
      market_overview: { type: 'string' },
      market_concentration: { type: 'string', enum: ['fragmented', 'moderately_competitive', 'concentrated', 'oligopoly'] },
      kongto_positioning: { type: 'string' },
      pricing_advice: { type: 'string' },
      product_opportunities: { type: 'array', items: { type: 'string' } },
      top_5_actions: { type: 'array', items: { type: 'object', properties: { priority: { type: 'integer' }, action: { type: 'string' }, impact: { type: 'string' }, effort: { type: 'string', enum: ['low', 'medium', 'high'] } }, required: ['priority', 'action', 'impact', 'effort'] } },
      keyword_opportunities: { type: 'array', items: { type: 'string' } },
    },
    required: ['market_overview', 'kongto_positioning', 'pricing_advice', 'product_opportunities', 'top_5_actions'],
  }}
)

// ============================================================
// Phase 3: 报告合成
// ============================================================
phase('报告合成')

const reportDate = (args?.date || '').slice(0, 10) || 'YYYY-MM-DD'
const reportPath = `d:\\code\\seo_deploy\\seo_reports\\competitor-radar-${reportDate}.md`

// 按威胁等级分组
const highThreat = competitorsData.filter(c => c.threat === 'high' || c.threat === 'very_high')
const medThreat = competitorsData.filter(c => c.threat === 'medium')

const reportLines = [
  `# 竞品情报雷达报告 — ${reportDate}`,
  '',
  `> 监控 ${COMPETITORS.length} 个竞品, 成功采集 ${successful.length} 个`,
  '',
  '## 市场概览',
  '',
  analysisResult.market_overview,
  '',
  `**市场集中度**: ${analysisResult.market_concentration}`,
  '',
  '## Kongto 定位',
  '',
  analysisResult.kongto_positioning,
  '',
  '## 定价建议',
  '',
  analysisResult.pricing_advice,
  '',
  '## 高威胁竞品',
  '',
  ...highThreat.map(c => `- **${c.name}** (${c.category}): ${c.products}\n  - 威胁: ${c.threat}\n  - 优势: ${(c.strengths || []).join(', ')}\n  - 可攻击弱点: ${(c.weaknesses || []).join(', ')}`),
  '',
  highThreat.length === 0 ? '无\n' : '',
  '## 中等威胁竞品',
  '',
  ...medThreat.map(c => `- **${c.name}**: ${c.products}`),
  '',
  '## 产品机会',
  '',
  ...(analysisResult.product_opportunities || []).map((o, i) => `${i+1}. ${o}`),
  '',
  '## Top 5 行动项',
  '',
  ...(analysisResult.top_5_actions || []).map(a => `### ${a.priority}. ${a.action}\n- 影响: ${a.impact}\n- 工作量: ${a.effort}\n`),
  '',
  '## 关键词机会',
  '',
  ...(analysisResult.keyword_opportunities || []).map(k => `- ${k}`),
  '',
  '---',
  '',
  '### 全部竞品列表',
  '',
  ...competitorsData.map(c => `- ${c.name} (${c.domain}) — ${c.threat}威胁 — ${c.products}`),
]

const report = reportLines.join('\n')

log(`报告已生成: ${reportPath}`)
log(`高威胁: ${highThreat.length}, 中威胁: ${medThreat.length}`)

return { reportPath, report, summary: { total: competitorsData.length, highThreat: highThreat.length, opportunities: analysisResult.product_opportunities?.length || 0 } }
