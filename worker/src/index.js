/**
 * cncdisplay order service - self-hosted order desk
 *
 * The order record lives in our own KV store; email is only a notification
 * copy, so a mail filter or a missed webhook cannot lose an order.
 *
 * Public:
 *   GET  /api/health
 *   POST /api/paypal-webhook        PayPal webhook receiver, signature verified
 *
 * Admin (cookie session; ?token=ADMIN_TOKEN still works for scripts):
 *   GET    /admin                   order desk UI
 *   POST   /api/login               { password } -> sets session cookie
 *   POST   /api/logout
 *   GET    /api/orders              JSON list (?q=&stage=&limit=)
 *   GET    /api/orders/:id          JSON detail
 *   PATCH  /api/orders/:id          { stage, carrier, tracking, phone, dest,
 *                                     addressLines, note }
 *   DELETE /api/orders/:id
 *   POST   /api/orders/manual       create an order by hand
 *   GET    /api/orders.csv          spreadsheet export
 *   POST   /api/paypal-sync         pull missing captures from PayPal reporting
 *
 * Bindings / secrets:
 *   PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_WEBHOOK_ID
 *   ADMIN_TOKEN      legacy token for scripts and test hooks
 *   ADMIN_PASSWORD   order desk password
 *   SESSION_SECRET   HMAC key for the session cookie
 *   ORDERS           KV namespace
 *   NOTIFY, NOTIFY_TO  optional mail copy
 */

const PAYPAL_API = 'https://api-m.paypal.com';
const SESSION_COOKIE = 'cncd_admin';
const SESSION_TTL = 7 * 24 * 3600; // seconds
const STAGES = ['new', 'paid', 'packed', 'shipped', 'delivered', 'cancelled'];

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' },
  });
}

function escapeHtml(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

function money(value, currency) {
  const n = Number(value);
  return `${Number.isFinite(n) ? n.toFixed(2) : value} ${currency || ''}`.trim();
}

/* ---------------------------------------------------------------- PayPal */

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

/* ------------------------------------------------------------- buildRecord */

// Shipping cannot be booked without these. Surface gaps instead of letting an
// order sit unnoticed.
function shipWarn({ phone, dest, countryCode, addressLines, addr }) {
  const s = (v) => (v == null ? '' : String(v).trim());
  const warn = [];
  if (!phone) warn.push('No phone number - DHL needs it, ask the buyer before shipping.');
  if (!addressLines.length) {
    warn.push('No ship-to address from PayPal - ask the buyer for the full address.');
  } else if (!s(addr.address_line_1) || !s(addr.admin_area_2) || !s(addr.postal_code)) {
    warn.push('Ship-to address looks incomplete (street / city / postal code missing).');
  }
  if (dest && countryCode && dest !== countryCode) {
    warn.push(`Country mismatch: checkout selected ${dest}, PayPal address is ${countryCode}.`);
  }
  return warn;
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
  const dest = destPart ? destPart.replace('dest=', '') : null;
  const countryCode = line(addr.country_code) || null;

  const phone =
    line(payer.phone?.phone_number?.national_number) ||
    line(cap.payer?.phone?.phone_number?.national_number) ||
    line(ship.phone_number) ||
    sitePhone ||
    null;

  return {
    receivedAt: new Date().toISOString(),
    source: 'webhook',
    stage: 'new',
    captureId: cap.id,
    orderId: cap.supplementary_data?.related_ids?.order_id || (order && order.id),
    paypalStatus: cap.status,
    amount: cap.amount && cap.amount.value,
    currency: cap.amount && cap.amount.currency_code,
    invoiceId: cap.invoice_id,
    customId: cap.custom_id,
    slug: slug || null,
    qty: qtyPart ? qtyPart.replace('qty=', '') : null,
    dest,
    items,
    payerName,
    payerEmail: payer.email_address || null,
    payerId: payer.payer_id || null,
    company: payer.business_name || null,
    phone,
    shipToName: ship.name?.full_name || payerName,
    shipTo: full || null,
    addressLines,
    countryCode,
    warn: shipWarn({ phone, dest, countryCode, addressLines, addr }),
    carrier: null,
    tracking: null,
    notes: [],
    history: [{ at: new Date().toISOString(), what: 'received' }],
    raw: { capture: cap, orderId: order && order.id },
  };
}

/* ------------------------------------------------------------------ email */

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
    '--- CHECKS ---',
    ...(r.warn && r.warn.length
      ? r.warn.map((w) => `WARN: ${w}`)
      : ['OK: phone, address and destination present']),
    '',
    '--- IDS ---',
    `Invoice  : ${r.invoiceId}`,
    `Capture  : ${r.captureId}`,
    `Order ID : ${r.orderId}`,
    '',
    'Open the order desk: https://cncdisplay.com/admin',
    'This mail is only a copy. The order is stored in the order desk.',
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
    ['Checks', r.warn && r.warn.length ? r.warn : ['OK: phone, address and destination present']],
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
  }</table><p>Order desk: <a href="https://cncdisplay.com/admin">https://cncdisplay.com/admin</a></p>`;

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

/* ---------------------------------------------------------------- storage */

function newOrderId(prefix) {
  return `${prefix}-${Date.now().toString(36).toUpperCase()}`;
}

async function saveRecord(env, rec) {
  const key = `order:${rec.captureId}`;
  await env.ORDERS.put(key, JSON.stringify(rec));
  // Legacy keys were order:<receivedAt>:<captureId>; drop them once migrated.
  const list = await env.ORDERS.list({ prefix: 'order:' });
  for (const k of list.keys) {
    if (k.name !== key && k.name.endsWith(`:${rec.captureId}`)) {
      await env.ORDERS.delete(k.name);
    }
  }
}

async function loadAll(env, limit = 500) {
  const list = await env.ORDERS.list({ prefix: 'order:', limit });
  const records = [];
  const seen = new Set();
  for (const key of list.keys) {
    const value = await env.ORDERS.get(key.name);
    if (!value) continue;
    let rec;
    try {
      rec = JSON.parse(value);
    } catch (e) {
      continue;
    }
    if (!rec.captureId || seen.has(rec.captureId)) continue;
    seen.add(rec.captureId);
    records.push(rec);
  }
  records.sort((a, b) => (a.receivedAt < b.receivedAt ? 1 : -1));
  return records;
}

async function findRecord(env, id) {
  const direct = await env.ORDERS.get(`order:${id}`);
  if (direct) return JSON.parse(direct);
  const all = await loadAll(env);
  return all.find((r) => r.captureId === id) || null;
}

/* ------------------------------------------------------------------- auth */

const enc = new TextEncoder();

async function hmacHex(secret, data) {
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), {
    name: 'HMAC', hash: 'SHA-256',
  }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(data));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

function safeEqual(a, b) {
  const x = String(a || '');
  const y = String(b || '');
  if (x.length !== y.length) return false;
  let diff = 0;
  for (let i = 0; i < x.length; i += 1) diff |= x.charCodeAt(i) ^ y.charCodeAt(i);
  return diff === 0;
}

// Password lives in KV once changed from the desk, so the owner can rotate it
// without touching Cloudflare secrets. ADMIN_PASSWORD stays as the bootstrap
// value until then.
const PW_KEY = 'admin:password';

async function sha256Hex(s) {
  const d = await crypto.subtle.digest('SHA-256', enc.encode(s));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

function randomHex(bytes) {
  const a = new Uint8Array(bytes);
  crypto.getRandomValues(a);
  return [...a].map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function checkPassword(env, pw) {
  const raw = await env.ORDERS.get(PW_KEY);
  if (raw) {
    const rec = JSON.parse(raw);
    return safeEqual(await sha256Hex(`${rec.salt}|${pw}`), rec.hash);
  }
  return !!env.ADMIN_PASSWORD && safeEqual(pw, env.ADMIN_PASSWORD);
}

async function setPassword(env, pw) {
  const salt = randomHex(16);
  await env.ORDERS.put(PW_KEY, JSON.stringify({
    salt,
    hash: await sha256Hex(`${salt}|${pw}`),
    updatedAt: new Date().toISOString(),
  }));
}

async function handlePassword(request, env) {
  const body = await request.json().catch(() => ({}));
  const current = String(body.current || '');
  const next = String(body.next || '');
  if (!(await checkPassword(env, current))) return json({ error: 'current password wrong' }, 401);
  if (next.length < 8) return json({ error: 'new password must be at least 8 characters' }, 400);
  await setPassword(env, next);
  return json({ ok: true });
}

async function makeSession(env) {
  const exp = String(Date.now() + SESSION_TTL * 1000);
  return `${exp}.${await hmacHex(env.SESSION_SECRET, `v1|${exp}`)}`;
}

function readCookie(request, name) {
  const raw = request.headers.get('Cookie') || '';
  const m = raw.match(new RegExp(`(?:^|;\\s*)${name}=([^;]+)`));
  return m ? decodeURIComponent(m[1]) : null;
}

async function isAdmin(request, url, env) {
  if (env.ADMIN_TOKEN && safeEqual(url.searchParams.get('token'), env.ADMIN_TOKEN)) return true;
  const cookie = readCookie(request, SESSION_COOKIE);
  if (!cookie) return false;
  const [exp, sig] = cookie.split('.');
  if (!exp || !sig || Number(exp) < Date.now()) return false;
  return safeEqual(sig, await hmacHex(env.SESSION_SECRET, `v1|${exp}`));
}

function sessionCookie(value, maxAge) {
  return `${SESSION_COOKIE}=${value}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
}

/* -------------------------------------------------------------- handlers */

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

  const existing = await env.ORDERS.get(`order:${record.captureId}`);
  if (existing) {
    // Webhook retries must not wipe stage / tracking / notes set in the desk.
    return json({ ok: true, duplicate: record.captureId });
  }

  await saveRecord(env, record);
  const mail = await notify(record, env);
  console.log('order stored', record.captureId, 'mail', mail);
  return json({ ok: true, captureId: record.captureId, mail });
}

async function handleLogin(request, env) {
  const body = await request.json().catch(() => ({}));
  const password = String(body.password || '');
  if (!(await checkPassword(env, password))) return json({ error: 'wrong password' }, 401);
  const cookie = await makeSession(env);
  return new Response(JSON.stringify({ ok: true }), {
    headers: {
      'Content-Type': 'application/json',
      'Set-Cookie': sessionCookie(cookie, SESSION_TTL),
    },
  });
}

async function handleList(url, env) {
  const q = String(url.searchParams.get('q') || '').toLowerCase();
  const stage = url.searchParams.get('stage') || '';
  const limit = Math.min(Number(url.searchParams.get('limit') || 500), 1000);
  let records = await loadAll(env, limit);
  if (stage) records = records.filter((r) => r.stage === stage);
  if (q) {
    records = records.filter((r) => [
      r.captureId, r.orderId, r.invoiceId, r.payerName, r.payerEmail, r.phone,
      r.company, r.shipToName, r.slug, r.shipTo, r.tracking,
    ].join(' ').toLowerCase().includes(q));
  }
  const counts = {};
  for (const s of STAGES) counts[s] = 0;
  for (const r of await loadAll(env, limit)) counts[r.stage || 'new'] = (counts[r.stage || 'new'] || 0) + 1;
  return json({ count: records.length, counts, orders: records });
}

async function handleDetail(env, id) {
  const rec = await findRecord(env, id);
  if (!rec) return json({ error: 'not found' }, 404);
  return json(rec);
}

async function handleUpdate(request, env, id) {
  const rec = await findRecord(env, id);
  if (!rec) return json({ error: 'not found' }, 404);
  const body = await request.json().catch(() => ({}));
  const changes = [];

  if (typeof body.stage === 'string') {
    if (!STAGES.includes(body.stage)) return json({ error: `bad stage, use ${STAGES.join('|')}` }, 400);
    if (body.stage !== rec.stage) {
      changes.push(`stage ${rec.stage || 'new'} -> ${body.stage}`);
      rec.stage = body.stage;
    }
  }
  for (const f of ['carrier', 'tracking', 'phone', 'dest', 'shipToName', 'company', 'payerEmail']) {
    if (typeof body[f] === 'string' && body[f].trim() !== (rec[f] || '')) {
      changes.push(`${f} set`);
      rec[f] = body[f].trim() || null;
    }
  }
  if (Array.isArray(body.addressLines)) {
    const lines = body.addressLines.map((l) => String(l).trim()).filter(Boolean);
    if (lines.join('\n') !== (rec.addressLines || []).join('\n')) {
      changes.push('address updated');
      rec.addressLines = lines;
      rec.shipTo = lines.join(', ') || null;
    }
  }
  if (typeof body.note === 'string' && body.note.trim()) {
    rec.notes = rec.notes || [];
    rec.notes.push({ at: new Date().toISOString(), text: body.note.trim() });
    changes.push('note added');
  }
  if (body.recheck) {
    const lines = rec.addressLines || [];
    const warn = [];
    if (!rec.phone) warn.push('No phone number - DHL needs it, ask the buyer before shipping.');
    if (!lines.length) {
      warn.push('No ship-to address - ask the buyer for the full address.');
    } else if (lines.length < 3) {
      warn.push('Ship-to address looks incomplete (street / city / postal code missing).');
    }
    if (rec.dest && rec.countryCode && rec.dest !== rec.countryCode) {
      warn.push(`Country mismatch: checkout selected ${rec.dest}, PayPal address is ${rec.countryCode}.`);
    }
    rec.warn = warn;
  }
  if (!changes.length) return json({ ok: true, unchanged: true, order: rec });

  rec.updatedAt = new Date().toISOString();
  rec.history = rec.history || [];
  rec.history.push({ at: rec.updatedAt, what: changes.join('; ') });
  await saveRecord(env, rec);
  return json({ ok: true, changes, order: rec });
}

async function handleDelete(env, id) {
  const rec = await findRecord(env, id);
  if (!rec) return json({ error: 'not found' }, 404);
  await env.ORDERS.delete(`order:${id}`);
  const list = await env.ORDERS.list({ prefix: 'order:' });
  for (const k of list.keys) {
    if (k.name.endsWith(`:${id}`)) await env.ORDERS.delete(k.name);
  }
  return json({ ok: true, deleted: id });
}

async function handleManual(request, env) {
  const body = await request.json().catch(() => ({}));
  // Accepting a real capture id lets the webhook de-dupe against this record
  // if PayPal later delivers the same payment.
  const id = String(body.captureId || '').trim() || newOrderId('MAN');
  if (await env.ORDERS.get(`order:${id}`)) {
    return json({ error: 'order already exists', captureId: id }, 409);
  }
  const now = new Date().toISOString();
  const addressLines = (Array.isArray(body.addressLines) ? body.addressLines : String(body.address || '').split('\n'))
    .map((l) => String(l).trim())
    .filter(Boolean);
  const rec = {
    receivedAt: body.receivedAt || now,
    source: 'manual',
    stage: STAGES.includes(body.stage) ? body.stage : 'paid',
    captureId: id,
    orderId: body.orderId || null,
    paypalStatus: body.paypalStatus || null,
    amount: body.amount || null,
    currency: body.currency || 'USD',
    invoiceId: body.invoiceId || null,
    customId: null,
    slug: body.slug || null,
    qty: body.qty || null,
    dest: body.dest || null,
    items: Array.isArray(body.items) ? body.items : (body.item ? [{ name: body.item, quantity: Number(body.qty || 1) }] : []),
    payerName: body.payerName || null,
    payerEmail: body.payerEmail || null,
    payerId: null,
    company: body.company || null,
    phone: body.phone || null,
    shipToName: body.shipToName || body.payerName || null,
    shipTo: addressLines.join(', ') || null,
    addressLines,
    countryCode: body.countryCode || null,
    warn: [],
    carrier: body.carrier || null,
    tracking: body.tracking || null,
    notes: body.note ? [{ at: now, text: String(body.note).trim() }] : [],
    history: [{ at: now, what: 'created by hand' }],
  };
  rec.warn = [];
  if (!rec.phone) rec.warn.push('No phone number - DHL needs it, ask the buyer before shipping.');
  if (!addressLines.length) {
    rec.warn.push('No ship-to address - ask the buyer for the full address.');
  } else if (addressLines.length < 3) {
    rec.warn.push('Ship-to address looks incomplete (street / city / postal code missing).');
  }
  await saveRecord(env, rec);
  return json({ ok: true, order: rec });
}

function csvCell(v) {
  const s = v == null ? '' : String(v);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

async function handleCsv(env) {
  const records = await loadAll(env, 1000);
  const head = ['capture_id', 'received_at', 'stage', 'source', 'amount', 'currency', 'product',
    'qty', 'destination', 'buyer', 'email', 'company', 'phone', 'ship_to',
    'carrier', 'tracking', 'invoice', 'warnings', 'notes'];
  const lines = [head.join(',')];
  for (const r of records) {
    lines.push([
      r.captureId, r.receivedAt, r.stage, r.source, r.amount, r.currency, r.slug, r.qty, r.dest,
      r.payerName, r.payerEmail, r.company, r.phone, (r.addressLines || []).join(' | '),
      r.carrier, r.tracking, r.invoiceId, (r.warn || []).join(' | '),
      (r.notes || []).map((n) => n.text).join(' | '),
    ].map(csvCell).join(','));
  }
  return new Response(`﻿${lines.join('\r\n')}\r\n`, {
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': `attachment; filename="cncdisplay-orders-${new Date().toISOString().slice(0, 10)}.csv"`,
    },
  });
}

// Pull captures straight from PayPal reporting, so a missed webhook or a mail
// filter cannot hide an order. Requires the Transaction Search feature on the
// REST app; when unavailable the error is returned to the admin UI.
async function handlePaypalSync(url, env) {
  // PayPal caps one reporting query at 31 days.
  const days = Math.min(Math.max(Number(url.searchParams.get('days') || 30), 1), 31);
  const end = new Date();
  const start = new Date(end.getTime() - days * 86400 * 1000);
  const fmt = (d) => d.toISOString().replace(/\.\d+Z$/, 'Z');
  let token;
  try {
    token = await paypalToken(env);
  } catch (e) {
    return json({ ok: false, error: `paypal oauth: ${e.message || e}` }, 500);
  }
  const params = new URLSearchParams({
    start_date: fmt(start), end_date: fmt(end), fields: 'all', page_size: '100',
  });
  const res = await fetch(`${PAYPAL_API}/v1/reporting/transactions?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    return json({
      ok: false,
      status: res.status,
      error: data.message || data.name || 'transaction search failed',
      hint: 'Enable Transaction Search on the PayPal REST app, or keep using the webhook.',
    }, 502);
  }

  const existing = await loadAll(env);
  const known = new Set(existing.map((r) => r.captureId));
  const imported = [];
  for (const t of data.transaction_details || []) {
    const info = t.transaction_info || {};
    const amount = Number(info.transaction_amount && info.transaction_amount.value);
    if (!info.transaction_id || known.has(info.transaction_id)) continue;
    if (!(amount > 0)) continue;
    if (info.transaction_status !== 'S') continue;

    const payer = t.payer_info || {};
    const name = [payer.payer_name && payer.payer_name.alternate_full_name,
      payer.email_address].filter(Boolean)[0] || null;
    const now = new Date().toISOString();
    const rec = {
      receivedAt: info.transaction_initiation_date || now,
      source: 'paypal-sync',
      stage: 'paid',
      captureId: info.transaction_id,
      orderId: info.paypal_reference_id || null,
      paypalStatus: info.transaction_status,
      amount: info.transaction_amount && info.transaction_amount.value,
      currency: info.transaction_amount && info.transaction_amount.currency_code,
      invoiceId: info.invoice_id || null,
      customId: info.custom_field || null,
      slug: null,
      qty: null,
      dest: null,
      items: [],
      payerName: name,
      payerEmail: payer.email_address || null,
      payerId: payer.account_id || null,
      company: null,
      phone: null,
      shipToName: null,
      shipTo: null,
      addressLines: [],
      countryCode: null,
      warn: ['Imported from PayPal reporting - no product / address detail, check PayPal for the order.'],
      carrier: null,
      tracking: null,
      notes: [{ at: now, text: `event code ${info.transaction_event_code || '?'}` }],
      history: [{ at: now, what: 'imported by paypal sync' }],
    };
    await saveRecord(env, rec);
    imported.push(rec.captureId);
  }
  return json({ ok: true, scanned: (data.transaction_details || []).length, imported });
}

async function handleTestNotify(url, env) {
  if (url.searchParams.get('token') !== env.ADMIN_TOKEN) {
    return json({ error: 'unauthorized' }, 401);
  }
  const incomplete = url.searchParams.get('incomplete') === '1';
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
    countryCode: 'US',
    warn: [],
  };
  if (incomplete) {
    Object.assign(sample, {
      phone: null,
      company: null,
      shipTo: null,
      addressLines: [],
      countryCode: null,
      dest: 'US',
      payerName: 'Incomplete Test Buyer',
    });
    sample.warn = shipWarn({
      phone: sample.phone,
      dest: sample.dest,
      countryCode: sample.countryCode,
      addressLines: sample.addressLines,
      addr: {},
    });
  }
  const result = await notify(sample, env);
  return json({ ok: result === 'sent', result, to: env.NOTIFY_TO || null, incomplete });
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

/* -------------------------------------------------------------- admin UI */

function adminPage() {
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>cncdisplay order desk</title>
<style>
*{box-sizing:border-box}
body{margin:0;font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:#f6f7f9;color:#1c2530}
header{display:flex;align-items:center;gap:12px;padding:12px 18px;background:#10202f;color:#fff;flex-wrap:wrap}
header h1{font-size:16px;margin:0 auto 0 0;font-weight:600}
button,a.btn{font:inherit;padding:7px 12px;border-radius:6px;border:1px solid #cfd6df;background:#fff;color:#1c2530;cursor:pointer;text-decoration:none}
header button,header a.btn{background:#1f3b57;color:#fff;border-color:#35546f}
.bar{display:flex;gap:8px;padding:12px 18px;flex-wrap:wrap;align-items:center}
.bar input,.bar select{font:inherit;padding:7px 10px;border:1px solid #cfd6df;border-radius:6px;background:#fff}
.bar input{min-width:260px}
#stat{color:#5b6b7c;margin-left:auto}
table{width:100%;border-collapse:collapse;background:#fff}
th,td{padding:9px 10px;border-bottom:1px solid #e6eaef;text-align:left;vertical-align:top}
th{background:#eef2f6;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#48596b}
tr.row{cursor:pointer}
tr.row:hover{background:#f0f6ff}
.pill{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;background:#e4e9ef}
.pill.new{background:#fde8c8}.pill.paid{background:#d8ecff}.pill.packed{background:#e4e0ff}
.pill.shipped{background:#d7f2e2}.pill.delivered{background:#c9edc9}.pill.cancelled{background:#f3d6d6}
.warn{color:#b00020;font-size:12px}
.muted{color:#78889a}
.panel{position:fixed;inset:0;background:rgba(12,20,28,.45);display:flex;justify-content:flex-end;z-index:20}
.panel[hidden]{display:none}
.card{background:#fff;width:min(560px,100%);height:100%;overflow:auto;padding:18px}
.card h2{font-size:16px;margin:0 0 4px}
.grid{display:grid;grid-template-columns:120px 1fr;gap:8px 10px;margin:14px 0;align-items:start}
.grid label{color:#5b6b7c;padding-top:7px}
.grid input,.grid select,.grid textarea{font:inherit;padding:7px 9px;border:1px solid #cfd6df;border-radius:6px;width:100%}
.grid textarea{min-height:70px;resize:vertical}
.actions{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}
.actions .danger{margin-left:auto;color:#b00020;border-color:#e3b4b4}
dl.kv{display:grid;grid-template-columns:120px 1fr;gap:4px 10px;margin:10px 0;font-size:13px}
dl.kv dt{color:#78889a}
dl.kv dd{margin:0;word-break:break-word}
.hist{font-size:12px;color:#5b6b7c;max-height:120px;overflow:auto;border-top:1px solid #e6eaef;padding-top:8px}
.login{max-width:320px;margin:80px auto;background:#fff;padding:22px;border-radius:10px;box-shadow:0 6px 24px rgba(16,32,47,.12)}
.login h1{font-size:17px;margin:0 0 14px}
.login input{font:inherit;width:100%;padding:9px 10px;border:1px solid #cfd6df;border-radius:6px}
.login button{margin-top:12px;width:100%;padding:9px;background:#10202f;color:#fff;border:0;border-radius:6px;font:inherit;cursor:pointer}
.err{color:#b00020;font-size:13px;margin-top:8px;min-height:18px}
@media (max-width:720px){.bar input{min-width:0;width:100%}table{font-size:13px}th:nth-child(6),td:nth-child(6){display:none}}
</style>
<body>
<div class="login" id="loginBox">
  <h1>cncdisplay order desk</h1>
  <input id="pw" type="password" placeholder="Password" autocomplete="current-password">
  <button id="loginBtn">Log in</button>
  <div class="err" id="loginErr"></div>
</div>
<div id="app" hidden>
  <header>
    <h1>Order desk</h1>
    <button id="btnSync" title="Import captures PayPal knows about but the webhook missed">Sync PayPal</button>
    <button id="btnManual">Manual order</button>
    <a class="btn" href="/api/orders.csv">CSV</a>
    <button id="btnPw">Change password</button>
    <button id="btnOut">Log out</button>
  </header>
  <div class="bar">
    <input id="q" placeholder="Search name, email, phone, capture, product">
    <select id="stage">
      <option value="">All stages</option>
      <option value="new">New</option>
      <option value="paid">Paid</option>
      <option value="packed">Packed</option>
      <option value="shipped">Shipped</option>
      <option value="delivered">Delivered</option>
      <option value="cancelled">Cancelled</option>
    </select>
    <span id="stat"></span>
  </div>
  <table>
    <thead><tr><th>Received</th><th>Stage</th><th>Amount</th><th>Item</th><th>Buyer</th><th>Ship to</th><th>Tracking</th></tr></thead>
    <tbody id="rows"></tbody>
  </table>
  <div class="panel" id="panel" hidden>
    <div class="card" id="card"></div>
  </div>
</div>
<script>
(function () {
  var state = { orders: [], current: null };

  function el(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  }); }
  function api(path, opts) {
    opts = opts || {};
    opts.headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
    return fetch(path, opts).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok) throw new Error(d.error || (path + ' -> ' + r.status));
        return d;
      });
    });
  }

  function showApp(on) {
    el('loginBox').hidden = on;
    el('app').hidden = !on;
  }

  function load() {
    var q = encodeURIComponent(el('q').value.trim());
    var stage = encodeURIComponent(el('stage').value);
    return api('/api/orders?q=' + q + '&stage=' + stage).then(function (d) {
      state.orders = d.orders;
      render(d.counts);
    }).catch(function (e) {
      if (/unauthorized/.test(e.message)) showApp(false);
      else el('stat').textContent = e.message;
    });
  }

  function render(counts) {
    var html = '';
    state.orders.forEach(function (o, i) {
      var issues = (o.warn || []).length;
      html += '<tr class="row" data-i="' + i + '">' +
        '<td>' + esc((o.receivedAt || '').slice(0, 16).replace('T', ' ')) + '</td>' +
        '<td><span class="pill ' + esc(o.stage || 'new') + '">' + esc(o.stage || 'new') + '</span></td>' +
        '<td>' + esc((o.amount == null ? '' : o.amount) + ' ' + (o.currency || '')) + '</td>' +
        '<td>' + esc(o.slug || (o.items && o.items[0] && o.items[0].name) || '-') +
          (issues ? '<div class="warn">' + issues + ' issue(s)</div>' : '') + '</td>' +
        '<td>' + esc(o.payerName || o.shipToName || '-') + '<div class="muted">' + esc(o.payerEmail || '') + '</div>' +
          (o.phone ? '<div class="muted">' + esc(o.phone) + '</div>' : '') + '</td>' +
        '<td>' + esc((o.addressLines || []).join(', ') || o.shipTo || '-') + '</td>' +
        '<td>' + esc(o.tracking || '-') + '</td></tr>';
    });
    el('rows').innerHTML = html || '<tr><td colspan="7" class="muted">No orders yet.</td></tr>';
    var c = counts || {};
    el('stat').textContent = Object.keys(c).filter(function (k) { return c[k]; })
      .map(function (k) { return k + ': ' + c[k]; }).join('  ');
    Array.prototype.forEach.call(document.querySelectorAll('tr.row'), function (tr) {
      tr.onclick = function () { open(state.orders[Number(tr.getAttribute('data-i'))]); };
    });
  }

  function open(o) {
    state.current = o;
    var stages = ['new', 'paid', 'packed', 'shipped', 'delivered', 'cancelled'];
    var opts = stages.map(function (s) {
      return '<option value="' + s + '"' + (o.stage === s ? ' selected' : '') + '>' + s + '</option>';
    }).join('');
    var items = (o.items || []).map(function (i) { return i.name + ' x' + i.quantity; }).join('; ');
    var hist = (o.history || []).map(function (h) {
      return esc((h.at || '').slice(0, 16).replace('T', ' ')) + ' - ' + esc(h.what);
    }).join('<br>');
    var warns = (o.warn || []).map(function (w) { return '<div class="warn">' + esc(w) + '</div>'; }).join('');
    var notes = (o.notes || []).map(function (n) {
      return esc((n.at || '').slice(0, 16).replace('T', ' ')) + ' - ' + esc(n.text);
    }).join('<br>');

    el('card').innerHTML =
      '<h2>' + esc(o.slug || o.captureId) + '</h2>' +
      '<div class="muted">' + esc(o.captureId) + (o.source ? ' - ' + esc(o.source) : '') + '</div>' +
      '<dl class="kv">' +
      '<dt>Amount</dt><dd>' + esc((o.amount == null ? '' : o.amount) + ' ' + (o.currency || '')) + '</dd>' +
      '<dt>Received</dt><dd>' + esc((o.receivedAt || '').slice(0, 19).replace('T', ' ')) + '</dd>' +
      '<dt>Items</dt><dd>' + esc(items || '-') + '</dd>' +
      '<dt>Payer</dt><dd>' + esc(o.payerName || '-') + '</dd>' +
      '<dt>Email</dt><dd>' + esc(o.payerEmail || '-') + '</dd>' +
      '</dl>' + warns +
      '<div class="grid">' +
      '<label>Stage</label><select id="fStage">' + opts + '</select>' +
      '<label>Carrier</label><input id="fCarrier" value="' + esc(o.carrier || '') + '" placeholder="DHL">' +
      '<label>Tracking</label><input id="fTracking" value="' + esc(o.tracking || '') + '">' +
      '<label>Ship name</label><input id="fShipToName" value="' + esc(o.shipToName || '') + '">' +
      '<label>Company</label><input id="fCompany" value="' + esc(o.company || '') + '">' +
      '<label>Phone</label><input id="fPhone" value="' + esc(o.phone || '') + '">' +
      '<label>Destination</label><input id="fDest" value="' + esc(o.dest || o.countryCode || '') + '" placeholder="US">' +
      '<label>Address</label><textarea id="fAddress">' + esc((o.addressLines || []).join('\\n')) + '</textarea>' +
      '<label>Add note</label><textarea id="fNote" placeholder="Supplier, ETA, buyer reply..."></textarea>' +
      '</div>' +
      '<div class="actions">' +
      '<button id="btnSave">Save</button>' +
      '<button id="btnClose">Close</button>' +
      '<button id="btnDel" class="danger">Delete</button>' +
      '</div>' +
      '<div class="err" id="saveErr"></div>' +
      '<h3 style="font-size:13px;margin:16px 0 4px">Notes</h3><div class="hist">' + (notes || '<span class="muted">none</span>') + '</div>' +
      '<h3 style="font-size:13px;margin:16px 0 4px">History</h3><div class="hist">' + (hist || '<span class="muted">none</span>') + '</div>';

    el('panel').hidden = false;
    el('btnClose').onclick = function () { el('panel').hidden = true; };
    el('btnSave').onclick = save;
    el('btnDel').onclick = del;
  }

  function save() {
    var o = state.current;
    var body = {
      stage: el('fStage').value,
      carrier: el('fCarrier').value,
      tracking: el('fTracking').value,
      shipToName: el('fShipToName').value,
      company: el('fCompany').value,
      phone: el('fPhone').value,
      dest: el('fDest').value,
      addressLines: el('fAddress').value.split('\\n'),
      note: el('fNote').value
    };
    api('/api/orders/' + encodeURIComponent(o.captureId), { method: 'PATCH', body: JSON.stringify(body) })
      .then(function (d) { el('panel').hidden = true; state.current = d.order; load(); })
      .catch(function (e) { el('saveErr').textContent = e.message; });
  }

  function del() {
    var o = state.current;
    if (!confirm('Delete ' + o.captureId + ' from the order desk?')) return;
    api('/api/orders/' + encodeURIComponent(o.captureId), { method: 'DELETE' })
      .then(function () { el('panel').hidden = true; load(); })
      .catch(function (e) { el('saveErr').textContent = e.message; });
  }

  function manual() {
    el('card').innerHTML =
      '<h2>Manual order</h2>' +
      '<div class="grid">' +
      '<label>Buyer</label><input id="mName">' +
      '<label>Email</label><input id="mEmail">' +
      '<label>Company</label><input id="mCompany">' +
      '<label>Phone</label><input id="mPhone">' +
      '<label>Item</label><input id="mItem" placeholder="FANUC A61L-0001-0093 9-inch CRT to LCD">' +
      '<label>Amount</label><input id="mAmount" placeholder="507.00">' +
      '<label>Qty</label><input id="mQty" value="1">' +
      '<label>Destination</label><input id="mDest" placeholder="US">' +
      '<label>Address</label><textarea id="mAddress" placeholder="street\\ncity, state zip\\ncountry"></textarea>' +
      '<label>PayPal ID</label><input id="mPaypal" placeholder="capture or order id">' +
      '<label>Note</label><textarea id="mNote"></textarea>' +
      '</div>' +
      '<div class="actions"><button id="mSave">Create</button><button id="mClose">Close</button></div>' +
      '<div class="err" id="mErr"></div>';
    el('panel').hidden = false;
    el('mClose').onclick = function () { el('panel').hidden = true; };
    el('mSave').onclick = function () {
      var body = {
        payerName: el('mName').value, payerEmail: el('mEmail').value, company: el('mCompany').value,
        phone: el('mPhone').value, item: el('mItem').value, amount: el('mAmount').value,
        qty: el('mQty').value, dest: el('mDest').value, address: el('mAddress').value,
        orderId: el('mPaypal').value, note: el('mNote').value,
        paypalStatus: null, stage: 'paid'
      };
      api('/api/orders/manual', { method: 'POST', body: JSON.stringify(body) })
        .then(function () { el('panel').hidden = true; load(); })
        .catch(function (e) { el('mErr').textContent = e.message; });
    };
  }

  function sync() {
    el('btnSync').disabled = true;
    el('btnSync').textContent = 'Syncing...';
    api('/api/paypal-sync', { method: 'POST' })
      .then(function (d) {
        el('btnSync').textContent = 'Synced';
        setTimeout(function () { el('btnSync').textContent = 'Sync PayPal'; el('btnSync').disabled = false; }, 1500);
        alert('Scanned ' + d.scanned + ', imported ' + d.imported.length + '.');
        load();
      })
      .catch(function (e) {
        el('btnSync').textContent = 'Sync PayPal';
        el('btnSync').disabled = false;
        alert(e.message);
      });
  }

  el('loginBtn').onclick = function () {
    fetch('/api/login', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: el('pw').value })
    }).then(function (r) {
      if (r.ok) { el('loginErr').textContent = ''; showApp(true); load(); }
      else el('loginErr').textContent = 'Wrong password.';
    });
  };
  el('pw').onkeydown = function (e) { if (e.key === 'Enter') el('loginBtn').click(); };
  el('btnOut').onclick = function () {
    fetch('/api/logout', { method: 'POST' }).then(function () { showApp(false); });
  };
  function password() {
    el('card').innerHTML =
      '<h2>Change password</h2>' +
      '<div class="grid">' +
      '<label>Current</label><input id="pwCur" type="password" autocomplete="current-password">' +
      '<label>New</label><input id="pwNew" type="password" autocomplete="new-password" placeholder="at least 8 characters">' +
      '<label>Repeat new</label><input id="pwNew2" type="password" autocomplete="new-password">' +
      '</div>' +
      '<div class="actions"><button id="pwSave">Save</button><button id="pwClose">Close</button></div>' +
      '<div class="err" id="pwErr"></div>';
    el('panel').hidden = false;
    el('pwClose').onclick = function () { el('panel').hidden = true; };
    el('pwSave').onclick = function () {
      if (el('pwNew').value !== el('pwNew2').value) {
        el('pwErr').textContent = 'New passwords do not match.';
        return;
      }
      api('/api/password', {
        method: 'POST',
        body: JSON.stringify({ current: el('pwCur').value, next: el('pwNew').value })
      }).then(function () {
        el('panel').hidden = true;
        alert('Password changed. It takes effect for new logins within about a minute.');
      }).catch(function (e) { el('pwErr').textContent = e.message; });
    };
  }

  el('btnManual').onclick = manual;
  el('btnSync').onclick = sync;
  el('btnPw').onclick = password;
  el('q').oninput = function () { clearTimeout(window.__t); window.__t = setTimeout(load, 250); };
  el('stage').onchange = load;

  api('/api/orders?limit=1').then(function () { showApp(true); load(); })
    .catch(function () { showApp(false); });
})();
</script>
</body>
</html>`;
}

/* ------------------------------------------------------------------ router */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === '/api/health') return json({ ok: true });

    if (path === '/api/paypal-webhook' && request.method === 'POST') {
      return handleWebhook(request, env);
    }

    if (path === '/api/login' && request.method === 'POST') return handleLogin(request, env);
    if (path === '/api/logout' && request.method === 'POST') {
      return new Response(JSON.stringify({ ok: true }), {
        headers: { 'Content-Type': 'application/json', 'Set-Cookie': sessionCookie('', 0) },
      });
    }

    if (path === '/api/paypal-selftest' && request.method === 'GET') {
      return handlePaypalSelftest(url, env);
    }
    if (path === '/api/test-notify' && request.method === 'POST') {
      return handleTestNotify(url, env);
    }

    const authed = await isAdmin(request, url, env).catch(() => false);

    // The page itself carries no data: it probes /api/orders and shows a login
    // box when that returns 401.
    if (path === '/admin' || path.startsWith('/admin/') || path === '/api/admin') {
      return new Response(adminPage(), {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': 'no-store',
          'X-Robots-Tag': 'noindex, nofollow',
        },
      });
    }

    if (!authed) return json({ error: 'unauthorized' }, 401);

    if (path === '/api/password' && request.method === 'POST') return handlePassword(request, env);
    if (path === '/api/orders.csv' && request.method === 'GET') return handleCsv(env);
    if (path === '/api/orders' && request.method === 'GET') return handleList(url, env);
    if (path === '/api/orders' && request.method === 'POST') return handleManual(request, env);
    if (path === '/api/orders/manual' && request.method === 'POST') return handleManual(request, env);
    if (path === '/api/paypal-sync' && request.method === 'POST') return handlePaypalSync(url, env);

    const m = path.match(/^\/api\/orders\/([^/]+)$/);
    if (m) {
      const id = decodeURIComponent(m[1]);
      if (request.method === 'GET') return handleDetail(env, id);
      if (request.method === 'PATCH') return handleUpdate(request, env, id);
      if (request.method === 'DELETE') return handleDelete(env, id);
    }

    return json({ error: 'not found' }, 404);
  },
};
