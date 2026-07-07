export const meta = {
  name: 'quick-price',
  description: '型号定价+销量速查：Amazon + eBay 实时价格/销量/市场容量',
  phases: [
    { title: '采集' },
    { title: '销量估算' },
    { title: '报告' },
  ],
}

const model = (args?.model || args?.[0] || '').trim()
if (!model) {
  log('用法: /price "FANUC A61L-0001-0093"')
  return { error: 'no model' }
}

log(`查询: ${model}（信用点：~5-8）`)

phase('采集')

// Amazon + eBay + 已售数据并行
const results = await parallel([
  () => agent(
    `在 Amazon 搜索 "${model} CNC LCD replacement"，获取定价和销量信号。

输出每个在售商品的：
- 价格 (price)
- 卖家 (seller)
- 评价数 (reviews_count) 和评分 (rating)
- BSR排名 (bsr) — 最好能拿到具体数字
- bought_past_month — 上月购买量
- 库存状态 (in_stock)
- 是否Prime (is_prime)
- ASIN/URL

特别注意：BSR排名可以用来估算月销量，bought_past_month是直接月销量指标。`,
    { label: 'Amazon商品', phase: '采集', schema: {
      type: 'object',
      properties: {
        listings: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              title: { type: 'string' },
              price: { type: 'number' },
              seller: { type: 'string' },
              rating: { type: 'number' },
              reviews_count: { type: 'integer' },
              bsr: { type: 'integer' },
              bought_past_month: { type: 'integer' },
              in_stock: { type: 'boolean' },
              is_prime: { type: 'boolean' },
              asin: { type: 'string' },
            },
          },
        },
      },
      required: ['listings'],
    }}
  ),
  () => agent(
    `搜索 eBay 上 "${model}" 的已售记录（Sold Listings）。
在 eBay 搜索 "${model}"，过滤已售出商品。

输出每个已售商品的：
- 价格 (sold_price)
- 卖家所在地 (seller_location)
- 成交日期 (sold_date) — 如果有的话
- 物品状态 (condition)
- 是拍卖还是固定价 (sale_type)

目标是了解近期的实际成交价和成交量。`,
    { label: 'eBay已售', phase: '采集', schema: {
      type: 'object',
      properties: {
        sold_listings: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              sold_price: { type: 'number' },
              seller_location: { type: 'string' },
              sold_date: { type: 'string' },
              condition: { type: 'string' },
              sale_type: { type: 'string' },
            },
          },
        },
      },
      required: ['sold_listings'],
    }}
  ),
])

phase('销量估算')

const amzData = results[0]
const ebayData = results[1]

// 估算月销量
let amazonMonthlyTotal = 0
let amazonBSREstimate = 0

for (const item of (amzData?.listings || [])) {
  // bought_past_month 是直接数据
  if (item.bought_past_month) amazonMonthlyTotal += item.bought_past_month

  // BSR估算: 在Computer Monitors类目, BSR 5000≈100件/月
  if (item.bsr && item.bsr > 0) {
    const bsrEst = Math.round(50000 / (item.bsr + 50))
    amazonBSREstimate += bsrEst
  }
}

// 用review数估算总销量 (通常2-5%买家留评)
const totalReviews = (amzData?.listings || []).reduce((s, l) => s + (l.reviews_count || 0), 0)
const reviewEstimate = Math.round(totalReviews / 0.03)

// eBay 已售估算
const ebaySoldCount = (ebayData?.sold_listings || []).length
const ebayPrices = (ebayData?.sold_listings || []).map(l => l.sold_price).filter(Boolean)
const ebayAvgPrice = ebayPrices.length ? Math.round(ebayPrices.reduce((a, b) => a + b, 0) / ebayPrices.length) : 0

// 综合估算
const bestMonthlyEstimate = amazonMonthlyTotal || amazonBSREstimate || Math.round(ebaySoldCount / 6)

const report = [
  `# ${model} — 定价×销量速查`,
  '',
  '## 📊 销量估算',
  '',
  `| 指标 | 数据 | 说明 |`,
  `|------|------|------|`,
  `| Amazon上月购买 | ${amazonMonthlyTotal || '未知'}件 | 直接统计 |`,
  `| Amazon BSR估算 | ${amazonBSREstimate || '未知'}件/月 | BSR排名反推 |`,
  `| Amazon总评价数 | ${totalReviews}条 | 推测总销约${reviewEstimate}件 |`,
  `| eBay近期已售 | ${ebaySoldCount}件（采集窗口） | 实际成交记录 |`,
  `| **综合月销量** | **${bestMonthlyEstimate}件** | 多源加权 |`,
  `| **年销量估算** | **${bestMonthlyEstimate * 12}件** | 月均×12 |`,
  '',
  '## 💰 价格分析',
  '',
  '### Amazon 在售',
  ...(amzData?.listings || []).map(l =>
    `- **$${l.price}** — ${l.seller}\n  └ ${l.rating || '-'}★(${l.reviews_count}评) BSR#${l.bsr || 'N/A'} 上月买${l.bought_past_month || 0}件 ${l.is_prime ? 'Prime' : ''} ${l.in_stock ? '有货' : '缺货'}`
  ),
  '',
  '### eBay 近期成交',
  ...(ebayData?.sold_listings || []).map(l =>
    `- **$${l.sold_price}** — ${l.seller_location || '未知'} | ${l.condition || ''} ${l.sold_date ? '('+l.sold_date+')' : ''}`
  ),
  '',
  '---',
  '',
  '## 🎯 Kongto 建议',
  '',
  `| 策略 | 建议价 | 依据 |`,
  `|------|--------|------|`,
  `| 独立站标价 | **$${Math.round(bestMonthlyEstimate * 3)}**-${Math.round(bestMonthlyEstimate * 5)} | 保利润 |`,
  `| Amazon上架 | **$${Math.round(ebayAvgPrice * 0.7) || '待定'}** | 低于均价+Prime |`,
  `| eBay上架 | **$${Math.round(ebayAvgPrice * 0.65) || '待定'}** OBO | 打新品期 |`,
  `| 年可争取量 | **${Math.round(bestMonthlyEstimate * 0.3 * 12)}-${Math.round(bestMonthlyEstimate * 0.5 * 12)}件** | 占30-50%份额 |`,
]

return {
  model,
  report: report.join('\n'),
  marketData: {
    estimatedMonthlySales: bestMonthlyEstimate,
    estimatedAnnualSales: bestMonthlyEstimate * 12,
    amazonAvgPrice: amzData?.listings?.length ? Math.round(amzData.listings.reduce((s,l) => s+(l.price||0),0)/amzData.listings.length) : 0,
    ebayAvgSoldPrice: ebayAvgPrice,
    totalListings: (amzData?.listings?.length || 0) + (ebayData?.sold_listings?.length || 0),
  },
}
