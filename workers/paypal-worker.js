// == Cloudflare Worker — PayPal Orders API ==
// Deploy: npm install -g wrangler && wrangler deploy paypal-worker.js
// Set secrets: wrangler secret put PAYPAL_CLIENT_ID && wrangler secret put PAYPAL_CLIENT_SECRET

// Shipping rates — edit these as needed
const SHIPPING = {
  US: { name: 'United States', cost: 45 },
  CA: { name: 'Canada', cost: 50 },
  GB: { name: 'United Kingdom', cost: 55 },
  DE: { name: 'Germany', cost: 55 },
  FR: { name: 'France', cost: 55 },
  IT: { name: 'Italy', cost: 55 },
  ES: { name: 'Spain', cost: 55 },
  JP: { name: 'Japan', cost: 40 },
  KR: { name: 'South Korea', cost: 40 },
  SG: { name: 'Singapore', cost: 35 },
  AU: { name: 'Australia', cost: 50 },
  CN: { name: 'China', cost: 25 },
  DEFAULT: { name: 'Other Countries', cost: 60 },
}

const PAYPAL_API = 'https://api-m.paypal.com' // Live
// const PAYPAL_API = 'https://api-m.sandbox.paypal.com' // Sandbox (testing)

async function getAccessToken(clientId, clientSecret) {
  const resp = await fetch(`${PAYPAL_API}/v1/oauth2/token`, {
    method: 'POST',
    headers: { Authorization: 'Basic ' + btoa(clientId + ':' + clientSecret) },
    body: 'grant_type=client_credentials',
  })
  const data = await resp.json()
  return data.access_token
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url)
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    }
    if (request.method === 'OPTIONS') return new Response(null, { headers: corsHeaders })

    try {
      if (url.pathname === '/create-order' && request.method === 'POST') {
        const { price, shipping: shippingCode } = await request.json()
        const itemPrice = parseFloat(price)
        const ship = SHIPPING[shippingCode] || SHIPPING.DEFAULT
        const shippingCost = ship.cost
        const total = (itemPrice + shippingCost).toFixed(2)

        const token = await getAccessToken(env.PAYPAL_CLIENT_ID, env.PAYPAL_CLIENT_SECRET)
        const orderResp = await fetch(`${PAYPAL_API}/v2/checkout/orders`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            intent: 'CAPTURE',
            purchase_units: [{
              amount: {
                currency_code: 'USD',
                value: total,
                breakdown: { item_total: { currency_code: 'USD', value: price }, shipping: { currency_code: 'USD', value: shippingCost.toFixed(2) } }
              },
              items: [{ name: 'CNC LCD Upgrade Kit', unit_amount: { currency_code: 'USD', value: price }, quantity: 1 }],
              shipping: { type: 'SHIPPING' },
            }],
          }),
        })
        const order = await orderResp.json()
        return new Response(JSON.stringify({ orderId: order.id }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }

      if (url.pathname === '/capture-order' && request.method === 'POST') {
        const { orderId } = await request.json()
        const token = await getAccessToken(env.PAYPAL_CLIENT_ID, env.PAYPAL_CLIENT_SECRET)
        const captureResp = await fetch(`${PAYPAL_API}/v2/checkout/orders/${orderId}/capture`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        })
        const capture = await captureResp.json()
        return new Response(JSON.stringify(capture), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }

      if (url.pathname === '/shipping-rates') {
        const list = Object.entries(SHIPPING).map(([code, info]) => ({ code, name: info.name, cost: info.cost }))
        return new Response(JSON.stringify(list), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }

      return new Response('Not Found', { status: 404 })
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }
  },
}
