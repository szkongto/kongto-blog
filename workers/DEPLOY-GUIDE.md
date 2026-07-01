# PayPal Worker 部署指南

## 1. 安装 Wrangler

```bash
npm install -g wrangler
```

## 2. 设置 PayPal API 密钥

```bash
cd workers
wrangler secret put PAYPAL_CLIENT_ID
# 输入: pZZE7aJYt_BHaE90VcuFZszvlropHBHtR9gOLd5O

wrangler secret put PAYPAL_CLIENT_SECRET
# 输入: <你的PayPal Client Secret>
```

## 3. 部署 Worker

```bash
wrangler deploy
```

部署后得到 Worker URL，例如：`https://cncdisplay-paypal.workers.dev`

## 4. 更新产品页中的 Worker URL

编辑 `workers/paypal-button-template.html`，将 `WORKER_URL` 改为实际 URL，
然后重新运行注入脚本。

## 5. 调整运费

编辑 `workers/paypal-worker.js` 中的 `SHIPPING` 对象修运费。
