// == Cloudflare Worker — PayPal Orders API ==
// Deploy: npm install -g wrangler && wrangler deploy paypal-worker.js
// Set secrets: wrangler secret put PAYPAL_CLIENT_ID && wrangler secret put PAYPAL_CLIENT_SECRET

// DHL Express reference rates by zone — edit as needed
// Formula: base + rate_per_kg * weight_kg
const ZONES = {
  // Asia
  CN: { name: 'China', base: 8, perKg: 3 },
  JP: { name: 'Japan', base: 15, perKg: 5 },
  KR: { name: 'South Korea', base: 15, perKg: 5 },
  SG: { name: 'Singapore', base: 12, perKg: 4 },
  // North America
  US: { name: 'United States', base: 20, perKg: 7 },
  CA: { name: 'Canada', base: 22, perKg: 8 },
  // Europe
  GB: { name: 'United Kingdom', base: 22, perKg: 8 },
  DE: { name: 'Germany', base: 22, perKg: 8 },
  FR: { name: 'France', base: 22, perKg: 8 },
  IT: { name: 'Italy', base: 22, perKg: 8 },
  ES: { name: 'Spain', base: 22, perKg: 8 },
  // Oceania
  AU: { name: 'Australia', base: 20, perKg: 7 },
  // Rest
  DEFAULT: { name: 'Other Countries', base: 28, perKg: 10 },
}

function calcShipping(zoneCode, weightKg) {
  const zone = ZONES[zoneCode] || ZONES.DEFAULT
  const w = Math.max(0.5, parseFloat(weightKg) || 1.0)
  return Math.round(zone.base + zone.perKg * w)
}

const PAYPAL_API = 'https://api-m.paypal.com'

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
      // POST /create-order — create PayPal order
      if (url.pathname === '/create-order' && request.method === 'POST') {
        const { price, shipping: shippingCode, weight } = await request.json()
        const itemPrice = parseFloat(price)
        const shippingCost = calcShipping(shippingCode, weight)
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
                breakdown: {
                  item_total: { currency_code: 'USD', value: price },
                  shipping: { currency_code: 'USD', value: shippingCost.toFixed(2) }
                }
              },
              items: [{ name: 'CNC LCD Upgrade Kit', unit_amount: { currency_code: 'USD', value: price }, quantity: 1 }],
              shipping: { type: 'SHIPPING' },
            }],
          }),
        })
        const order = await orderResp.json()
        return new Response(JSON.stringify({ orderId: order.id }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }

      // POST /capture-order — capture after approval
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

      // GET /shipping-rates?weight=1.5 — calculate shipping for weight
      if (url.pathname === '/shipping-rates') {
        const weight = url.searchParams.get('weight') || '1.5'
        const list = Object.entries(ZONES).map(([code, info]) => ({
          code, name: info.name, cost: calcShipping(code, weight)
        }))
        return new Response(JSON.stringify(list), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }

      return new Response('Not Found', { status: 404 })
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }
  },
}
