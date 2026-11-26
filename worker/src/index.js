/**
 * cncdisplay order service
 *
 * Routes (served from https://cncdisplay.com/api/* or the workers.dev URL):
 *   GET  /api/health                 health probe
 *   POST /api/paypal-webhook         PayPal webhook receiver, signature verified
 *   GET  /api/orders?token=...       order list (JSON, or ?format=html for a table)
 *
 * Bindings / secrets required:
 *   PAYPAL_CLIENT_ID      PayPal REST app client id (live)
 *   PAYPAL_CLIENT_SECRET  PayPal REST app secret (live)
 *   PAYPAL_WEBHOOK_ID     id returned when the webhook was registered
 *   ADMIN_TOKEN           bearer token for /api/orders
 *   ORDERS                KV namespace holding orders
 *   NOTIFY                send_email binding (optional; skipped when absent)
 *   NOTIFY_TO             recipient address for order mail (optional)
 */

const PAYPAL_API = 'https://api-m.paypal.com';

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  });
}

async function paypalToken(env) {
  const auth = btoa(`${env.PAYPAL_CLIENT_ID}:${env.PAYPAL_CLIENT_SECRET}`);
  const res = await fetch(`${PAYPAL_API}/v1/oauth2/token`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${auth}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'grant_type=client_credentials',
  });
  if (!res.ok) {
    throw new Error(`paypal oauth ${res.status}: ${(await res.text()).slice(0, 300)}`);
  }
  return (await res.json()).access_token;
}

async function verifyWebhook(request, event, env) {
  const h = request.headers;
  const token = await paypalToken(env);
  const res = await fetch(`${PAYPAL_API}/v1/notifications/verify-webhook-signature`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      auth_algo: h.get('paypal-auth-algo'),
      cert_url: h.get('paypal-cert-url'),
      transmission_id: h.get('paypal-transmission-id'),
      transmission_sig: h.get('paypal-transmission-sig'),
      transmission_time: h.get('paypal-transmission-time'),
      webhook_id: env.PAYPAL_WEBHOOK_ID,
      webhook_event: event,
    }),
  });
  const data = await res.json().catch(() => ({}));
  return data.verification_status === 'SUCCESS';
}

async function fetchOrder(orderId, env) {
  if (!orderId) return null;
  const token = await paypalToken(env);
  const res = await fetch(`${PAYPAL_API}/v2/checkout/orders/${orderId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.ok ? res.json() : null;
}

function money(value, currency) {
  const n = Number(value);
  return `${Number.isFinite(n) ? n.toFixed(2) : value} ${currency || ''}`.trim();
}

function buildRecord(event, order) {
  const cap = event.resource || {};
  const payer = (order && order.payer) || {};
  const pu = (order && order.purchase_units && order.purchase_units[0]) || {};
  const ship = pu.shipping || {};
  const addr = ship.address || payer.address || {};
  const items = (pu.items || []).map((it) => ({
    name: it.name,
    quantity: Number(it.quantity || 1),
    unit: it.unit_amount && it.unit_amount.value,
  }));
  const line = (v) => (v == null ? '' : String(v).trim());
  const cityLine = [
    line(addr.admin_area_2),
    [line(addr.admin_area_1), line(addr.postal_code)].filter(Boolean).join(' '),
  ].filter(Boolean).join(', ');
  const addressLines = [
    line(addr.address_line_1),
    line(addr.address_line_2),
    cityLine,
    line(addr.country_code),
  ].filter(Boolean);
  const full = addressLines.join(', ');

  const payerName = [payer.name?.given_name, payer.name?.surname].filter(Boolean).join(' ')
    || (typeof cap.payer?.name === 'string' ? cap.payer.name : null);
  const [slug, qtyPart, destPart, telPart] = String(cap.custom_id || '').split('|');
  const sitePhone = telPart ? line(telPart.replace('tel=', '')) : null;

  const phone =
    line(payer.phone?.phone_number?.national_number) ||
    line(cap.payer?.phone?.phone_number?.national_number) ||
    line(ship.phone_number) ||
    sitePhone ||
    null;

  return {
    receivedAt: new Date().toISOString(),
    captureId: cap.id,
    orderId: cap.supplementary_data?.related_ids?.order_id || (order && order.id),
    status: cap.status,
    amount: cap.amount && cap.amount.value,
    currency: cap.amount && cap.amount.currency_code,
    invoiceId: cap.invoice_id,
    customId: cap.custom_id,
    slug: slug || null,
    qty: qtyPart ? qtyPart.replace('qty=', '') : null,
    dest: destPart ? destPart.replace('dest=', '') : null,
    items,
    payerName,
    payerEmail: payer.email_address || null,
    payerId: payer.payer_id || null,
    company: payer.business_name || null,
    phone,
    shipToName: ship.name?.full_name || payerName,
    shipTo: full || null,
    addressLines,
    raw: { capture: cap, orderId: order && order.id },
  };
}

function escapeHtml(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

function emailParts(r) {
  const subject = `[NEW ORDER] ${money(r.amount, r.currency)} - ${r.slug || r.captureId}`;
  const addrBlock = r.addressLines && r.addressLines.length ? r.addressLines : [r.shipTo || '?'];

  const text = [
    `New PayPal order received ${r.receivedAt}`,
    '',
    `Amount   : ${money(r.amount, r.currency)}`,
    `Item     : ${r.items.map((i) => `${i.name} x${i.quantity}`).join('; ') || '(none)'}`,
    `Page     : ${r.slug}`,
    `Link     : ${r.slug ? `https://cncdisplay.com/products/${r.slug}.html` : '-'}`,
    `Qty      : ${r.qty}   Dest: ${r.dest}`,
    '',
    '--- SHIP TO ---',
    `Name     : ${r.shipToName || '?'}`,
    `Company  : ${r.company || '-'}`,
    `Phone    : ${r.phone || '-'}`,
    `Email    : ${r.payerEmail || '?'}`,
    ...addrBlock.map((l, i) => `${i === 0 ? 'Address  : ' : '           '}${l}`),
    '',
    '--- IDS ---',
    `Invoice  : ${r.invoiceId}`,
    `Capture  : ${r.captureId}`,
    `Order ID : ${r.orderId}`,
    '',
    'Next steps: open PayPal Activity, buy the shipping label, then send the',
    'buyer a confirmation with the tracking number.',
  ].join('\n');

  const rows = [
    ['Amount', money(r.amount, r.currency)],
    ['Item', r.items.map((i) => `${i.name} x${i.quantity}`).join('; ')],
    ['Page', r.slug || ''],
    ['Link', r.slug ? `https://cncdisplay.com/products/${r.slug}.html` : ''],
    ['Qty / Dest', `${r.qty} / ${r.dest}`],
    ['Name', r.shipToName || ''],
    ['Company', r.company || ''],
    ['Phone', r.phone || ''],
    ['Email', r.payerEmail || ''],
    ['Address', addrBlock],
    ['Invoice', r.invoiceId],
    ['Capture ID', r.captureId],
    ['Order ID', r.orderId],
    ['Received', r.receivedAt],
  ];
  const html = `<h2>New PayPal order</h2><table cellpadding="6" style="border-collapse:collapse;font:14px system-ui">${
    rows.map(([k, v]) => {
      const cell = Array.isArray(v) ? v.map(escapeHtml).join('<br>') : escapeHtml(v);
      return `<tr><td style="border:1px solid #ddd;font-weight:600">${escapeHtml(k)}</td><td style="border:1px solid #ddd">${cell}</td></tr>`;
    }).join('')
  }</table><p>Next steps: open PayPal Activity, buy the shipping label, then email the buyer the tracking number.</p>`;

  return { subject, text, html };
}

async function notify(record, env) {
  if (!env.NOTIFY || !env.NOTIFY_TO) return 'skipped (no binding)';
  const { subject, text, html } = emailParts(record);
  try {
    await env.NOTIFY.send({
      to: env.NOTIFY_TO,
      from: { email: 'orders@cncdisplay.com', name: 'cncdisplay orders' },
      subject,
      text,
      html,
    });
    return 'sent';
  } catch (e) {
    return `failed: ${e.message || e}`;
  }
}

async function handleWebhook(request, env) {
  const raw = await request.text();
  let event;
  try {
    event = JSON.parse(raw);
  } catch (e) {
    return json({ error: 'bad json' }, 400);
  }

  let verified = false;
  try {
    verified = await verifyWebhook(request, event, env);
  } catch (e) {
    console.error('verify error', e.message);
  }
  if (!verified) return json({ error: 'signature verification failed' }, 401);

  if (event.event_type !== 'PAYMENT.CAPTURE.COMPLETED') {
    return json({ ok: true, ignored: event.event_type });
  }

  const cap = event.resource || {};
  const orderId = cap.supplementary_data?.related_ids?.order_id;
  const order = await fetchOrder(orderId, env).catch(() => null);
  const record = buildRecord(event, order);

  await env.ORDERS.put(`order:${record.receivedAt}:${record.captureId}`, JSON.stringify(record));
  const mail = await notify(record, env);
  console.log('order stored', record.captureId, 'mail', mail);

  return json({ ok: true, captureId: record.captureId, mail });
}

async function handleTestNotify(url, env) {
  if (url.searchParams.get('token') !== env.ADMIN_TOKEN) {
    return json({ error: 'unauthorized' }, 401);
  }
  const sample = {
    receivedAt: new Date().toISOString(),
    captureId: 'TEST-CAPTURE',
    orderId: 'TEST-ORDER',
    status: 'COMPLETED',
    amount: '507.00',
    currency: 'USD',
    invoiceId: 'CNCD-TEST',
    customId: 'fanuc-a61l-0001-0072-lcd-upgrade|qty=1|dest=US',
    slug: 'fanuc-a61l-0001-0072-lcd-upgrade',
    qty: '1',
    dest: 'US',
    items: [{ name: 'FANUC A61L-0001-0072 9-inch CRT to LCD Upgrade', quantity: 1, unit: '480.00' }],
    payerName: 'Test Buyer',
    payerEmail: 'buyer@example.com',
    payerId: null,
    company: 'Example Manufacturing Inc.',
    phone: '248-555-0100',
    shipTo: '2635 Paldan Drive, Auburn Hills, MI 48326, US',
    shipToName: 'Test Buyer',
    addressLines: ['2635 Paldan Drive', 'Auburn Hills, MI 48326', 'US'],
  };
  const result = await notify(sample, env);
  return json({ ok: result === 'sent', result, to: env.NOTIFY_TO || null });
}

async function handlePaypalSelftest(url, env) {
  if (url.searchParams.get('token') !== env.ADMIN_TOKEN) {
    return json({ error: 'unauthorized' }, 401);
  }
  try {
    const tk = await paypalToken(env);
    const res = await fetch(`${PAYPAL_API}/v1/notifications/webhooks`, {
      headers: { Authorization: `Bearer ${tk}` },
    });
    const data = await res.json().catch(() => ({}));
    return json({
      ok: res.ok,
      webhookId: env.PAYPAL_WEBHOOK_ID || null,
      registered: (data.webhooks || []).map((h) => ({
        id: h.id,
        url: h.url,
        events: (h.event_types || []).map((e) => e.name),
      })),
    });
  } catch (e) {
    return json({ ok: false, error: e.message || String(e) }, 500);
  }
}

async function handleList(url, env) {
  const token = url.searchParams.get('token');
  if (!token || token !== env.ADMIN_TOKEN) return json({ error: 'unauthorized' }, 401);

  const list = await env.ORDERS.list({ prefix: 'order:', limit: 200 });
  const records = [];
  for (const key of list.keys) {
    const value = await env.ORDERS.get(key.name);
    if (value) records.push(JSON.parse(value));
  }
  records.sort((a, b) => (a.receivedAt < b.receivedAt ? 1 : -1));

  if (url.searchParams.get('format') === 'html') {
    const rows = records.map((r) => `<tr><td>${escapeHtml(r.receivedAt)}</td><td>${escapeHtml(money(r.amount, r.currency))}</td><td>${escapeHtml(r.slug)}</td><td>${escapeHtml(r.payerName)}<br>${escapeHtml(r.payerEmail)}<br>${escapeHtml(r.phone)}</td><td>${escapeHtml(r.shipToName)}${r.company ? `<br>${escapeHtml(r.company)}` : ''}<br>${(r.addressLines || [r.shipTo || '']).map(escapeHtml).join('<br>')}</td><td>${escapeHtml(r.captureId)}</td></tr>`).join('');
    return new Response(
      `<!doctype html><meta charset="utf-8"><title>cncdisplay orders</title><body style="font:14px system-ui;padding:20px"><h2>Orders (${records.length})</h2><table cellpadding="6" style="border-collapse:collapse"><tr><th>Received</th><th>Amount</th><th>Page</th><th>Buyer</th><th>Ship to</th><th>Capture</th></tr>${rows}</table></body>`,
      { headers: { 'Content-Type': 'text/html; charset=utf-8' } },
    );
  }
  return json({ count: records.length, orders: records });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api/health') return json({ ok: true });
    if (url.pathname === '/api/paypal-webhook' && request.method === 'POST') {
      return handleWebhook(request, env);
    }
    if (url.pathname === '/api/paypal-selftest' && request.method === 'GET') {
      return handlePaypalSelftest(url, env);
    }
    if (url.pathname === '/api/orders' && request.method === 'GET') {
      return handleList(url, env);
    }
    if (url.pathname === '/api/test-notify' && request.method === 'POST') {
      return handleTestNotify(url, env);
    }
    return json({ error: 'not found' }, 404);
  },
};
