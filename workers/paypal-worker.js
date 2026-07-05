// == Cloudflare Worker — PayPal Orders API ==
// Deploy: npm install -g wrangler && cd workers && wrangler deploy
// Set secrets: wrangler secret put PAYPAL_CLIENT_ID && wrangler secret put PAYPAL_CLIENT_SECRET

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
        const { total } = await request.json()
        const totalStr = parseFloat(total).toFixed(2)

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
              amount: { currency_code: 'USD', value: totalStr },
              shipping: { type: 'SHIPPING' },
            }],
          }),
        })
        const order = await orderResp.json()
        if (!order.id) {
          return new Response(JSON.stringify({ error: 'PayPal API error', details: order }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
        }
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

      // GET / — health check
      if (url.pathname === '/') {
        return new Response(JSON.stringify({ status: 'ok', worker: 'cncdisplay-paypal' }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }

      return new Response(JSON.stringify({ error: 'Not found' }), { status: 404, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }
  },
}
