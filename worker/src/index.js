/**
 * cncdisplay order service - self-hosted order desk
 *
 * The order record lives in our own KV store; email is only a notification
 * copy, so a mail filter or a missed webhook cannot lose an order.
 *
 * Public:
 *   GET  /api/health
 *   POST /api/paypal-webhook        PayPal webhook receiver, signature verified
 *   POST /api/inquiry               website contact form (stored in KV, mail copy)
 *
 * Admin (cookie session; ?token=ADMIN_TOKEN still works for scripts):
 *   GET    /admin                   order desk UI: orders / inquiries / traffic
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
 *   GET    /api/inquiries           list (?q=&status=)
 *   PATCH  /api/inquiries/:id       { status, note }
 *   POST   /api/inquiries/:id/reply multipart: text + files[] (mail to customer)
 *   DELETE /api/inquiries/:id
 *   GET    /api/traffic?days=N      Cloudflare RUM + Search Console summary
 *
 * Bindings / secrets:
 *   PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_WEBHOOK_ID
 *   ADMIN_TOKEN      legacy token for scripts and test hooks
 *   ADMIN_PASSWORD   order desk password
 *   SESSION_SECRET   HMAC key for the session cookie
 *   ORDERS           KV namespace
 *   NOTIFY, NOTIFY_TO  optional mail copy
 *   CF_ANALYTICS_TOKEN, CF_ACCOUNT_ID, RUM_SITE_TAG
 *   GSC_CLIENT_ID, GSC_CLIENT_SECRET, GSC_REFRESH_TOKEN, GSC_PROPERTY
 */

import { adminPage } from './admin.js';

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

/* ------------------------------------------------------------- inquiries */

const INQ_PREFIX = 'inquiry:';
const INQ_STAGES = ['new', 'following', 'quoted', 'done', 'spam'];

async function notifyInquiry(rec, env) {
  if (!env.NOTIFY || !env.NOTIFY_TO) return 'skipped';
  try {
    await env.NOTIFY.send({
      to: env.NOTIFY_TO,
      from: { email: 'orders@cncdisplay.com', name: 'cncdisplay website' },
      // Without this, hitting Reply in the mailbox answers orders@cncdisplay.com
      // instead of the visitor.
      replyTo: rec.email || undefined,
      subject: `[INQUIRY] ${rec.name || rec.email || 'website visitor'} - ${(rec.page || 'contact').split('/').pop()}`,
      text: [
        `New website inquiry ${rec.receivedAt}`,
        '',
        `Name    : ${rec.name || '-'}`,
        `Email   : ${rec.email || '-'}`,
        `Phone   : ${rec.phone || '-'}`,
        `Company : ${rec.company || '-'}`,
        `Machine : ${rec.machine || '-'}`,
        `Page    : ${rec.page || '-'}`,
        '',
        rec.message || '',
        '',
        'Order desk: https://cncdisplay.com/admin',
      ].join('\n'),
    });
    return 'sent';
  } catch (e) {
    return `failed: ${e.message || e}`;
  }
}

async function handleInquiry(request, env) {
  const ct = request.headers.get('Content-Type') || '';
  let body = {};
  if (ct.includes('application/json')) {
    body = await request.json().catch(() => ({}));
  } else {
    const form = await request.formData().catch(() => null);
    if (form) {
      for (const [k, v] of form.entries()) body[k] = typeof v === 'string' ? v : '';
    }
  }
  const clean = (v) => String(v == null ? '' : v).trim().slice(0, 2000);

  // Honeypot: real people never fill a hidden field.
  if (clean(body._hp)) return new Response('OK', { status: 200 });

  const rec = {
    id: `${Date.now().toString(36).toUpperCase()}-${randomHex(3)}`,
    receivedAt: new Date().toISOString(),
    status: 'new',
    name: clean(body.name),
    email: clean(body.email),
    phone: clean(body.phone),
    company: clean(body.company),
    machine: clean(body.machine || body.product),
    message: clean(body.message),
    page: clean(body.page) || 'https://cncdisplay.com/contact.html',
    ip: request.headers.get('CF-Connecting-IP') || null,
    country: request.headers.get('CF-IPCountry') || null,
    ua: (request.headers.get('User-Agent') || '').slice(0, 300),
    notes: [],
    history: [{ at: new Date().toISOString(), what: 'received' }],
  };
  if (!rec.email && !rec.phone) return json({ error: 'email or phone required' }, 400);
  if (!rec.message) return json({ error: 'message required' }, 400);

  await env.ORDERS.put(`${INQ_PREFIX}${rec.id}`, JSON.stringify(rec));
  const mail = await notifyInquiry(rec, env);

  const redirect = clean(body.redirect);
  if (redirect && /^https:\/\/cncdisplay\.com\//.test(redirect)) {
    return Response.redirect(redirect, 303);
  }
  return json({ ok: true, id: rec.id, mail });
}

async function loadInquiries(env, limit = 500) {
  const list = await env.ORDERS.list({ prefix: INQ_PREFIX, limit });
  const out = [];
  for (const k of list.keys) {
    const v = await env.ORDERS.get(k.name);
    if (!v) continue;
    try {
      out.push(JSON.parse(v));
    } catch (e) { /* skip broken */ }
  }
  out.sort((a, b) => (a.receivedAt < b.receivedAt ? 1 : -1));
  return out;
}

async function handleInquiryList(url, env) {
  const q = String(url.searchParams.get('q') || '').toLowerCase();
  const status = url.searchParams.get('status') || '';
  let rows = await loadInquiries(env);
  if (status) rows = rows.filter((r) => r.status === status);
  if (q) {
    rows = rows.filter((r) => [r.name, r.email, r.phone, r.company, r.machine, r.message, r.page]
      .join(' ').toLowerCase().includes(q));
  }
  const counts = {};
  for (const s of INQ_STAGES) counts[s] = 0;
  for (const r of await loadInquiries(env)) counts[r.status] = (counts[r.status] || 0) + 1;
  return json({ count: rows.length, counts, inquiries: rows });
}

async function handleInquiryUpdate(request, env, id) {
  const raw = await env.ORDERS.get(`${INQ_PREFIX}${id}`);
  if (!raw) return json({ error: 'not found' }, 404);
  const rec = JSON.parse(raw);
  const body = await request.json().catch(() => ({}));
  const changes = [];
  if (typeof body.status === 'string') {
    if (!INQ_STAGES.includes(body.status)) return json({ error: `bad status, use ${INQ_STAGES.join('|')}` }, 400);
    if (body.status !== rec.status) {
      changes.push(`status ${rec.status} -> ${body.status}`);
      rec.status = body.status;
    }
  }
  if (typeof body.note === 'string' && body.note.trim()) {
    rec.notes = rec.notes || [];
    rec.notes.push({ at: new Date().toISOString(), text: body.note.trim() });
    changes.push('note added');
  }
  if (!changes.length) return json({ ok: true, unchanged: true, inquiry: rec });
  rec.updatedAt = new Date().toISOString();
  rec.history = rec.history || [];
  rec.history.push({ at: rec.updatedAt, what: changes.join('; ') });
  await env.ORDERS.put(`${INQ_PREFIX}${id}`, JSON.stringify(rec));
  return json({ ok: true, changes, inquiry: rec });
}

// Reply straight from the desk. Sends through the send_email binding, so the
// customer gets the mail from orders@cncdisplay.com and the desk keeps a copy.
// Free-plan accounts can only send to verified destination addresses; the raw
// platform error is surfaced instead of being hidden.
const REPLY_MAX_FILES = 5;
const REPLY_MAX_BYTES = 3 * 1024 * 1024;

async function handleInquiryReply(request, env, id) {
  const raw = await env.ORDERS.get(`${INQ_PREFIX}${id}`);
  if (!raw) return json({ error: 'not found' }, 404);
  const rec = JSON.parse(raw);
  if (!rec.email) return json({ error: '这条留言没有邮箱，无法回复。请先用电话联系，或补一个邮箱。' }, 400);

  const form = await request.formData().catch(() => null);
  if (!form) return json({ error: 'multipart form required' }, 400);
  const text = String(form.get('text') || '').trim().slice(0, 20000);
  const files = form.getAll('files').filter((f) => typeof f === 'object' && f.size > 0);
  if (!text && !files.length) return json({ error: '正文和附件不能都为空' }, 400);
  if (files.length > REPLY_MAX_FILES) return json({ error: `附件最多 ${REPLY_MAX_FILES} 个` }, 400);
  let total = 0;
  for (const f of files) total += f.size;
  if (total > REPLY_MAX_BYTES) {
    return json({ error: `附件合计 ${(total / 1048576).toFixed(1)} MB，上限 3 MB` }, 413);
  }

  const attachments = [];
  const inlines = [];
  for (let i = 0; i < files.length; i++) {
    const f = files[i];
    const buf = await f.arrayBuffer();
    const type = f.type || 'application/octet-stream';
    const name = String(f.name || `file-${i + 1}`).slice(0, 120);
    if (/^image\//.test(type)) {
      const contentId = `img${i}@cncdisplay.com`;
      attachments.push({ content: buf, filename: name, type, disposition: 'inline', contentId });
      inlines.push({ contentId, name });
    } else {
      attachments.push({ content: buf, filename: name, type, disposition: 'attachment' });
    }
  }

  const subject = `Re: ${rec.machine ? `${rec.machine} - ` : ''}your inquiry to cncdisplay`;
  const textBody = [
    text,
    '',
    '--',
    'cncdisplay.com  |  orders@cncdisplay.com',
    '',
    '--- 你原来的留言 ---',
    rec.message || '',
  ].join('\n');
  const htmlBody =
    '<div style="font:14px/1.6 system-ui,-apple-system,Segoe UI,Microsoft YaHei,sans-serif;color:#1c2530">' +
    escapeHtml(text).replace(/\n/g, '<br>') +
    inlines.map((im) => `<div style="margin:12px 0"><img src="cid:${im.contentId}" alt="${escapeHtml(im.name)}" style="max-width:100%"></div>`).join('') +
    '<hr style="border:0;border-top:1px solid #e6eaef;margin:16px 0">' +
    '<div style="color:#78889a;font-size:13px">cncdisplay.com &nbsp;|&nbsp; orders@cncdisplay.com</div>' +
    '<div style="color:#78889a;font-size:12px;margin-top:10px">--- 你原来的留言 ---<br>' +
    escapeHtml(rec.message || '').replace(/\n/g, '<br>') + '</div></div>';

  const payload = {
    to: rec.email,
    from: { email: 'orders@cncdisplay.com', name: 'cncdisplay' },
    subject,
    text: textBody,
    html: htmlBody,
  };
  if (attachments.length) payload.attachments = attachments;
  if (env.NOTIFY_TO) payload.cc = env.NOTIFY_TO;

  try {
    await env.NOTIFY.send(payload);
  } catch (e) {
    const msg = e && e.message ? e.message : String(e);
    let hint = null;
    if (/RECIPIENT_PLAN_RESTRICTED|PLAN_RESTRICTED/i.test(msg)) {
      hint = 'Cloudflare 免费版只能发给已验证地址。要直接回复客户，需要 Workers Paid（约 $5/月），或改用外部邮件 API。';
    } else if (/RECIPIENT_NOT_ALLOWED|recipient/i.test(msg)) {
      hint = 'send_email 绑定设有 destination_address 限制，需在 wrangler.toml 里去掉或改用 allowed_destination_addresses。';
    }
    return json({ error: `发送失败：${msg}`, hint }, 502);
  }

  const now = new Date().toISOString();
  rec.replies = rec.replies || [];
  rec.replies.push({
    at: now,
    text,
    files: files.map((f) => ({ name: f.name, size: f.size, type: f.type })),
    to: rec.email,
  });
  if (rec.status === 'new') rec.status = 'following';
  rec.updatedAt = now;
  rec.history = rec.history || [];
  rec.history.push({ at: now, what: `replied to ${rec.email}${files.length ? ` +${files.length} file(s)` : ''}` });
  await env.ORDERS.put(`${INQ_PREFIX}${id}`, JSON.stringify(rec));
  return json({ ok: true, replies: rec.replies.length, status: rec.status, inquiry: rec });
}

async function handleInquiryDelete(env, id) {
  const raw = await env.ORDERS.get(`${INQ_PREFIX}${id}`);
  if (!raw) return json({ error: 'not found' }, 404);
  await env.ORDERS.delete(`${INQ_PREFIX}${id}`);
  return json({ ok: true, deleted: id });
}

/* --------------------------------------------------------------- traffic */

async function cfGql(env, query) {
  if (!env.CF_ANALYTICS_TOKEN) throw new Error('CF_ANALYTICS_TOKEN not configured');
  const res = await fetch('https://api.cloudflare.com/client/v4/graphql', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.CF_ANALYTICS_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  const data = await res.json().catch(() => ({}));
  if (data.errors) throw new Error(`Cloudflare GraphQL: ${JSON.stringify(data.errors).slice(0, 300)}`);
  return data.data;
}

function isoDaysAgo(n) {
  return new Date(Date.now() - n * 86400000).toISOString().slice(0, 10);
}

async function trafficRum(env, days) {
  const acc = env.CF_ACCOUNT_ID;
  const tag = env.RUM_SITE_TAG;
  if (!acc || !tag) throw new Error('CF_ACCOUNT_ID / RUM_SITE_TAG not configured');
  const start = isoDaysAgo(days - 1);
  const filter = `date_geq:"${start}", siteTag:"${tag}", bot:0`;
  const grp = (alias, dims, order = 'count_DESC', limit = 25) => (
    `${alias}: rumPageloadEventsAdaptiveGroups(limit:${limit}, orderBy:[${order}], filter:{${filter}}){count sum{visits} dimensions{${dims}}}`
  );
  const query = `query {viewer{accounts(filter:{accountTag:"${acc}"}){`
    + `total: rumPageloadEventsAdaptiveGroups(limit:1, filter:{${filter}}){count sum{visits}} `
    + `daily: rumPageloadEventsAdaptiveGroups(limit:100, orderBy:[date_ASC], filter:{${filter}}){count sum{visits} dimensions{date}} `
    + grp('pages', 'requestPath', 'count_DESC', 30) + ' '
    + grp('referers', 'refererHost', 'count_DESC', 20) + ' '
    // Entry pair: which outside site sent people to which page. This is the
    // most specific referrer the browser sends; search terms are not attached.
    + grp('entries', 'refererHost requestPath', 'count_DESC', 30) + ' '
    + grp('countries', 'countryName', 'count_DESC', 15) + ' '
    + '}}}';
  const data = await cfGql(env, query);
  const a = data.viewer.accounts[0] || {};
  const t = (a.total && a.total[0]) || { count: 0, sum: { visits: 0 } };
  const map = (rows, fn) => (rows || []).map((r) => fn(r.dimensions, r.count, (r.sum || {}).visits || 0));
  return {
    days,
    pageviews: t.count || 0,
    visits: (t.sum || {}).visits || 0,
    daily: map(a.daily, (d, c, v) => ({ date: d.date, pageviews: c, visits: v })),
    pages: map(a.pages, (d, c, v) => ({ path: d.requestPath, pageviews: c, visits: v })),
    referers: map(a.referers, (d, c, v) => ({ host: d.refererHost || '', pageviews: c, visits: v })),
    entries: map(a.entries, (d, c, v) => ({
      host: d.refererHost || '', path: d.requestPath, pageviews: c, visits: v,
    })),
    countries: map(a.countries, (d, c, v) => ({ name: d.countryName, pageviews: c, visits: v })),
  };
}

async function gscToken(env) {
  const body = new URLSearchParams({
    client_id: env.GSC_CLIENT_ID || '',
    client_secret: env.GSC_CLIENT_SECRET || '',
    refresh_token: env.GSC_REFRESH_TOKEN || '',
    grant_type: 'refresh_token',
  });
  const res = await fetch('https://oauth2.googleapis.com/token', { method: 'POST', body });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`GSC oauth ${res.status}: ${data.error_description || data.error || ''}`);
  return data.access_token;
}

async function gscRows(env, token, start, end, dims, limit) {
  const site = encodeURIComponent(env.GSC_PROPERTY || 'https://cncdisplay.com/');
  const res = await fetch(`https://www.googleapis.com/webmasters/v3/sites/${site}/searchAnalytics/query`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ startDate: start, endDate: end, dimensions: dims, rowLimit: limit, dataState: 'final' }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`GSC ${res.status}: ${data.error?.message || ''}`);
  return data.rows || [];
}

async function trafficGsc(env, days) {
  const token = await gscToken(env);
  // GSC lags 2-3 days, so the window ends yesterday.
  const end = isoDaysAgo(1);
  const start = isoDaysAgo(days);
  const daily = await gscRows(env, token, start, end, ['date'], 200);
  const totals = daily.reduce((acc, r) => {
    acc.clicks += r.clicks; acc.impressions += r.impressions;
    acc.pos += r.position * r.impressions;
    return acc;
  }, { clicks: 0, impressions: 0, pos: 0 });
  const queries = await gscRows(env, token, start, end, ['query'], 30);
  const queryPages = await gscRows(env, token, start, end, ['query', 'page'], 30);
  return {
    range: { start, end },
    clicks: totals.clicks,
    impressions: totals.impressions,
    ctr: totals.impressions ? (totals.clicks / totals.impressions) * 100 : 0,
    position: totals.impressions ? totals.pos / totals.impressions : 0,
    queries: queries.map((r) => ({
      query: r.keys[0], clicks: r.clicks, impressions: r.impressions,
      ctr: r.ctr * 100, position: r.position,
    })),
    queryPages: queryPages.map((r) => ({
      query: r.keys[0], page: r.keys[1], clicks: r.clicks,
      impressions: r.impressions, ctr: r.ctr * 100, position: r.position,
    })),
  };
}

async function handleTraffic(url, env) {
  const days = Math.min(Math.max(Number(url.searchParams.get('days') || 7), 1), 90);
  const out = { days, generatedAt: new Date().toISOString() };
  try {
    out.cf = await trafficRum(env, days);
  } catch (e) {
    out.cfError = e.message || String(e);
  }
  try {
    out.gsc = await trafficGsc(env, days);
  } catch (e) {
    out.gscError = e.message || String(e);
  }
  return json(out);
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

    // Public contact form. No auth: this is what the website posts to.
    if (path === '/api/inquiry' && request.method === 'POST') {
      return handleInquiry(request, env);
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
    if (path === '/api/traffic' && request.method === 'GET') return handleTraffic(url, env);
    if (path === '/api/inquiries' && request.method === 'GET') return handleInquiryList(url, env);

    const mr = path.match(/^\/api\/inquiries\/([^/]+)\/reply$/);
    if (mr && request.method === 'POST') return handleInquiryReply(request, env, decodeURIComponent(mr[1]));

    const mi = path.match(/^\/api\/inquiries\/([^/]+)$/);
    if (mi) {
      const id = decodeURIComponent(mi[1]);
      if (request.method === 'PATCH') return handleInquiryUpdate(request, env, id);
      if (request.method === 'DELETE') return handleInquiryDelete(env, id);
    }

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
