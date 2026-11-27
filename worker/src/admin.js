/**
 * Order desk UI (Chinese). Three tabs: orders, inquiries, traffic.
 * Kept in its own module so index.js stays readable; the page carries no data,
 * it probes the APIs and shows the login form when they return 401.
 */

export function adminPage() {
  return `<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>cncdisplay 后台管理</title>
<style>
*{box-sizing:border-box}
body{margin:0;font:14px/1.5 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;background:#f6f7f9;color:#1c2530}
header{display:flex;align-items:center;gap:12px;padding:11px 18px;background:#10202f;color:#fff;flex-wrap:wrap}
header h1{font-size:16px;margin:0 auto 0 0;font-weight:600}
button,a.btn{font:inherit;padding:6px 12px;border-radius:6px;border:1px solid #cfd6df;background:#fff;color:#1c2530;cursor:pointer;text-decoration:none;white-space:nowrap}
header button{background:#1f3b57;color:#fff;border-color:#35546f}
button:disabled{opacity:.55;cursor:default}
nav.tabs{display:flex;gap:6px;padding:10px 18px 0;background:#fff;border-bottom:1px solid #e0e5eb}
nav.tabs button{border:1px solid transparent;border-bottom:0;border-radius:6px 6px 0 0;background:transparent;padding:9px 16px;color:#48596b}
nav.tabs button.on{background:#f6f7f9;border-color:#e0e5eb;color:#10202f;font-weight:600}
.bar{display:flex;gap:8px;padding:12px 18px;flex-wrap:wrap;align-items:center}
.bar input,.bar select{font:inherit;padding:7px 10px;border:1px solid #cfd6df;border-radius:6px;background:#fff}
.bar input{min-width:240px}
.bar .right{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
#stat{color:#5b6b7c}
table{width:100%;border-collapse:collapse;background:#fff}
th,td{padding:9px 10px;border-bottom:1px solid #e6eaef;text-align:left;vertical-align:top}
th{background:#eef2f6;font-size:12px;letter-spacing:.04em;color:#48596b;font-weight:600}
tr.row{cursor:pointer}
tr.row:hover{background:#f0f6ff}
.pill{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;background:#e4e9ef;white-space:nowrap}
.pill.new{background:#fde8c8}.pill.paid{background:#d8ecff}.pill.packed{background:#e4e0ff}
.pill.shipped{background:#d7f2e2}.pill.delivered{background:#c9edc9}.pill.cancelled,.pill.spam{background:#f3d6d6}
.pill.following{background:#d8ecff}.pill.quoted{background:#e4e0ff}.pill.done{background:#d7f2e2}
.warn{color:#b00020;font-size:12px}
.muted{color:#78889a}
.panel{position:fixed;inset:0;background:rgba(12,20,28,.45);display:flex;justify-content:flex-end;z-index:20}
.panel[hidden]{display:none}
.card{background:#fff;width:min(620px,100%);height:100%;overflow:auto;padding:18px}
.card h2{font-size:16px;margin:0 0 4px}
.grid{display:grid;grid-template-columns:120px 1fr;gap:8px 10px;margin:14px 0;align-items:start}
.grid label{color:#5b6b7c;padding-top:7px}
.grid input,.grid select,.grid textarea{font:inherit;padding:7px 9px;border:1px solid #cfd6df;border-radius:6px;width:100%}
.grid textarea{min-height:70px;resize:vertical}
.actions{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}
.actions .danger{margin-left:auto;color:#b00020;border-color:#e3b4b4}
dl.kv{display:grid;grid-template-columns:110px 1fr;gap:5px 10px;margin:10px 0;font-size:13px}
dl.kv dt{color:#78889a}
dl.kv dd{margin:0;word-break:break-word}
.hist{font-size:12px;color:#5b6b7c;max-height:130px;overflow:auto;border-top:1px solid #e6eaef;padding-top:8px}
.msg{white-space:pre-wrap;background:#f6f8fa;border:1px solid #e6eaef;border-radius:8px;padding:10px;margin:10px 0;font-size:13px}
.login{max-width:340px;margin:80px auto;background:#fff;padding:22px;border-radius:10px;box-shadow:0 6px 24px rgba(16,32,47,.12)}
.login h1{font-size:17px;margin:0 0 14px}
.login input{font:inherit;width:100%;padding:9px 10px;border:1px solid #cfd6df;border-radius:6px}
.login button{margin-top:12px;width:100%;padding:9px;background:#10202f;color:#fff;border:0;border-radius:6px;font:inherit;cursor:pointer}
.err{color:#b00020;font-size:13px;margin-top:8px;min-height:18px}
.sec{font-size:13px;margin:18px 0 6px}
/* traffic */
.wrap{padding:14px 18px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:16px}
.kpi{background:#fff;border:1px solid #e6eaef;border-radius:10px;padding:14px}
.kpi .k{color:#78889a;font-size:12px}
.kpi .v{font-size:24px;font-weight:600;margin-top:4px;font-variant-numeric:tabular-nums}
.kpi .s{color:#78889a;font-size:12px;margin-top:2px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:980px){.cols{grid-template-columns:1fr}}
.box{background:#fff;border:1px solid #e6eaef;border-radius:10px;padding:12px 14px;margin-bottom:16px;overflow:auto}
.box h3{font-size:13px;margin:0 0 8px;color:#10202f}
.box table{border-collapse:collapse;width:100%}
.box th{background:transparent;border-bottom:1px solid #e6eaef;padding:6px 8px;font-size:12px;color:#78889a;font-weight:500}
.box td{padding:6px 8px;border-bottom:1px solid #f0f3f6;font-size:13px}
.box tr:last-child td{border-bottom:0}
.num{text-align:right;font-variant-numeric:tabular-nums}
.notice{background:#fff8e8;border:1px solid #f0dfb4;border-radius:8px;padding:9px 12px;font-size:12px;color:#6b5a2c;margin-bottom:14px}
.seg{display:inline-flex;border:1px solid #cfd6df;border-radius:7px;overflow:hidden}
.seg button{border:0;border-radius:0;background:#fff;padding:6px 14px}
.seg button.on{background:#10202f;color:#fff}
@media (max-width:720px){.bar input{min-width:0;width:100%}table{font-size:13px}th:nth-child(6),td:nth-child(6){display:none}}
</style>
<body>
<div class="login" id="loginBox">
  <h1>cncdisplay 后台管理</h1>
  <input id="pw" type="password" placeholder="登录密码" autocomplete="current-password">
  <button id="loginBtn">登录</button>
  <div class="err" id="loginErr"></div>
</div>
<div id="app" hidden>
  <header>
    <h1>cncdisplay 后台管理</h1>
    <button id="btnPw">修改密码</button>
    <button id="btnOut">退出登录</button>
  </header>
  <nav class="tabs">
    <button data-tab="orders" class="on">订单管理</button>
    <button data-tab="inquiries">寻单留言</button>
    <button data-tab="traffic">流量看板</button>
  </nav>

  <section id="tab-orders">
    <div class="bar">
      <input id="q" placeholder="搜索 姓名 / 邮箱 / 电话 / 交易号 / 型号 / 运单">
      <select id="stage">
        <option value="">全部状态</option>
        <option value="new">新订单</option>
        <option value="paid">已付款</option>
        <option value="packed">已打包</option>
        <option value="shipped">已发货</option>
        <option value="delivered">已签收</option>
        <option value="cancelled">已取消</option>
      </select>
      <span id="stat"></span>
      <span class="right">
        <button id="btnSync" title="补拉 PayPal 已有、webhook 漏掉的交易">补拉 PayPal</button>
        <button id="btnManual">手工建单</button>
        <a class="btn" href="/api/orders.csv">导出 CSV</a>
      </span>
    </div>
    <table>
      <thead><tr><th>收到时间</th><th>状态</th><th>金额</th><th>商品</th><th>买家</th><th>收货地址</th><th>运单号</th></tr></thead>
      <tbody id="rows"></tbody>
    </table>
  </section>

  <section id="tab-inquiries" hidden>
    <div class="bar">
      <input id="iq" placeholder="搜索 姓名 / 邮箱 / 电话 / 内容 / 页面">
      <select id="istatus">
        <option value="">全部状态</option>
        <option value="new">新留言</option>
        <option value="following">跟进中</option>
        <option value="quoted">已报价</option>
        <option value="done">已处理</option>
        <option value="spam">垃圾</option>
      </select>
      <span id="istat"></span>
    </div>
    <table>
      <thead><tr><th>收到时间</th><th>状态</th><th>联系人</th><th>设备 / 型号</th><th>留言摘要</th><th>来源页</th></tr></thead>
      <tbody id="irows"></tbody>
    </table>
  </section>

  <section id="tab-traffic" hidden>
    <div class="wrap">
      <div class="bar" style="padding:0 0 12px">
        <span class="seg" id="segDays">
          <button data-days="1">今日</button>
          <button data-days="7" class="on">近 7 天</button>
          <button data-days="30">近 30 天</button>
        </span>
        <span id="tstat" class="muted"></span>
      </div>
      <div id="tnotice" class="notice" hidden></div>
      <div class="cards" id="tkpi"></div>
      <div class="cols">
        <div>
          <div class="box"><h3>入口来源（外部网站 → 落地页）</h3><div id="tEntries"></div></div>
          <div class="box"><h3>来源网站</h3><div id="tReferers"></div></div>
          <div class="box"><h3>落地页 / 热门页面</h3><div id="tPages"></div></div>
        </div>
        <div>
          <div class="box"><h3>搜索关键词（Bing，按周桶）</h3><div id="tBingQueries"></div></div>
          <div class="box"><h3>Bing 每日点击 / 展示</h3><div id="tBingDaily"></div></div>
          <div class="box"><h3>国家 / 地区</h3><div id="tCountries"></div></div>
          <div class="box"><h3>每日访问</h3><div id="tDaily"></div></div>
        </div>
      </div>
    </div>
  </section>

  <div class="panel" id="panel" hidden>
    <div class="card" id="card"></div>
  </div>
</div>
<script>
(function () {
  var state = { tab: 'orders', orders: [], current: null, inquiries: [], currentInq: null, days: 7 };
  var STAGE_CN = { new: '新订单', paid: '已付款', packed: '已打包', shipped: '已发货', delivered: '已签收', cancelled: '已取消' };
  var ISTAGE_CN = { new: '新留言', following: '跟进中', quoted: '已报价', done: '已处理', spam: '垃圾' };

  function el(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  }); }
  function num(n) { return (n == null ? 0 : n).toLocaleString('zh-CN'); }
  function pct(v) { return (v == null ? 0 : v).toFixed(1) + '%'; }
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

  /* ---------------------------------------------------------------- tabs */
  function showTab(name) {
    state.tab = name;
    Array.prototype.forEach.call(document.querySelectorAll('nav.tabs button'), function (b) {
      b.className = b.getAttribute('data-tab') === name ? 'on' : '';
    });
    ['orders', 'inquiries', 'traffic'].forEach(function (t) {
      el('tab-' + t).hidden = t !== name;
    });
    if (name === 'orders') load();
    if (name === 'inquiries') loadInq();
    if (name === 'traffic') loadTraffic();
  }

  /* -------------------------------------------------------------- orders */
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
        '<td><span class="pill ' + esc(o.stage || 'new') + '">' + esc(STAGE_CN[o.stage] || o.stage || '新订单') + '</span></td>' +
        '<td>' + esc((o.amount == null ? '' : o.amount) + ' ' + (o.currency || '')) + '</td>' +
        '<td>' + esc(o.slug || (o.items && o.items[0] && o.items[0].name) || '-') +
          (issues ? '<div class="warn">' + issues + ' 项待补</div>' : '') + '</td>' +
        '<td>' + esc(o.payerName || o.shipToName || '-') + '<div class="muted">' + esc(o.payerEmail || '') + '</div>' +
          (o.phone ? '<div class="muted">' + esc(o.phone) + '</div>' : '') + '</td>' +
        '<td>' + esc((o.addressLines || []).join(', ') || o.shipTo || '-') + '</td>' +
        '<td>' + esc(o.tracking || '-') + '</td></tr>';
    });
    el('rows').innerHTML = html || '<tr><td colspan="7" class="muted">暂无订单。</td></tr>';
    var c = counts || {};
    el('stat').textContent = Object.keys(c).filter(function (k) { return c[k]; })
      .map(function (k) { return (STAGE_CN[k] || k) + ' ' + c[k]; }).join(' · ');
    Array.prototype.forEach.call(document.querySelectorAll('#rows tr.row'), function (tr) {
      tr.onclick = function () { open(state.orders[Number(tr.getAttribute('data-i'))]); };
    });
  }

  function open(o) {
    state.current = o;
    var stages = ['new', 'paid', 'packed', 'shipped', 'delivered', 'cancelled'];
    var opts = stages.map(function (s) {
      return '<option value="' + s + '"' + (o.stage === s ? ' selected' : '') + '>' + STAGE_CN[s] + '</option>';
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
      '<dt>金额</dt><dd>' + esc((o.amount == null ? '' : o.amount) + ' ' + (o.currency || '')) + '</dd>' +
      '<dt>收到时间</dt><dd>' + esc((o.receivedAt || '').slice(0, 19).replace('T', ' ')) + '</dd>' +
      '<dt>商品</dt><dd>' + esc(items || '-') + '</dd>' +
      '<dt>买家</dt><dd>' + esc(o.payerName || '-') + '</dd>' +
      '<dt>邮箱</dt><dd>' + esc(o.payerEmail || '-') + '</dd>' +
      '</dl>' + warns +
      '<div class="grid">' +
      '<label>状态</label><select id="fStage">' + opts + '</select>' +
      '<label>承运商</label><input id="fCarrier" value="' + esc(o.carrier || '') + '" placeholder="DHL">' +
      '<label>运单号</label><input id="fTracking" value="' + esc(o.tracking || '') + '">' +
      '<label>收件人</label><input id="fShipToName" value="' + esc(o.shipToName || '') + '">' +
      '<label>公司</label><input id="fCompany" value="' + esc(o.company || '') + '">' +
      '<label>电话</label><input id="fPhone" value="' + esc(o.phone || '') + '">' +
      '<label>目的国</label><input id="fDest" value="' + esc(o.dest || o.countryCode || '') + '" placeholder="US">' +
      '<label>收货地址</label><textarea id="fAddress">' + esc((o.addressLines || []).join('\\n')) + '</textarea>' +
      '<label>添加备注</label><textarea id="fNote" placeholder="供应商、预计到货、买家回复……"></textarea>' +
      '</div>' +
      '<div class="actions">' +
      '<button id="btnSave">保存</button>' +
      '<button id="btnClose">关闭</button>' +
      '<button id="btnDel" class="danger">删除</button>' +
      '</div>' +
      '<div class="err" id="saveErr"></div>' +
      '<h3 style="font-size:13px;margin:16px 0 4px">备注</h3><div class="hist">' + (notes || '<span class="muted">无</span>') + '</div>' +
      '<h3 style="font-size:13px;margin:16px 0 4px">操作记录</h3><div class="hist">' + (hist || '<span class="muted">无</span>') + '</div>';

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
    if (!confirm('确定从后台删除订单 ' + o.captureId + '？此操作不可恢复。')) return;
    api('/api/orders/' + encodeURIComponent(o.captureId), { method: 'DELETE' })
      .then(function () { el('panel').hidden = true; load(); })
      .catch(function (e) { el('saveErr').textContent = e.message; });
  }

  function manual() {
    el('card').innerHTML =
      '<h2>手工建单</h2>' +
      '<div class="grid">' +
      '<label>买家姓名</label><input id="mName">' +
      '<label>邮箱</label><input id="mEmail">' +
      '<label>公司</label><input id="mCompany">' +
      '<label>电话</label><input id="mPhone">' +
      '<label>商品</label><input id="mItem" placeholder="FANUC A61L-0001-0093 9-inch CRT to LCD">' +
      '<label>金额</label><input id="mAmount" placeholder="507.00">' +
      '<label>数量</label><input id="mQty" value="1">' +
      '<label>目的国</label><input id="mDest" placeholder="US">' +
      '<label>收货地址</label><textarea id="mAddress" placeholder="街道\\n城市, 州 邮编\\n国家"></textarea>' +
      '<label>PayPal ID</label><input id="mPaypal" placeholder="capture 或 order id">' +
      '<label>备注</label><textarea id="mNote"></textarea>' +
      '</div>' +
      '<div class="actions"><button id="mSave">创建</button><button id="mClose">关闭</button></div>' +
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
    el('btnSync').textContent = '补拉中……';
    api('/api/paypal-sync', { method: 'POST' })
      .then(function (d) {
        el('btnSync').textContent = '已补拉';
        setTimeout(function () { el('btnSync').textContent = '补拉 PayPal'; el('btnSync').disabled = false; }, 1500);
        alert('扫描 ' + d.scanned + ' 笔，新增 ' + d.imported.length + ' 笔。');
        load();
      })
      .catch(function (e) {
        el('btnSync').textContent = '补拉 PayPal';
        el('btnSync').disabled = false;
        alert(e.message);
      });
  }

  /* ----------------------------------------------------------- inquiries */
  function loadInq() {
    var q = encodeURIComponent(el('iq').value.trim());
    var status = encodeURIComponent(el('istatus').value);
    return api('/api/inquiries?q=' + q + '&status=' + status).then(function (d) {
      state.inquiries = d.inquiries;
      renderInq(d.counts);
    }).catch(function (e) {
      if (/unauthorized/.test(e.message)) showApp(false);
      else el('istat').textContent = e.message;
    });
  }

  function renderInq(counts) {
    var html = '';
    state.inquiries.forEach(function (r, i) {
      html += '<tr class="row" data-i="' + i + '">' +
        '<td>' + esc((r.receivedAt || '').slice(0, 16).replace('T', ' ')) + '</td>' +
        '<td><span class="pill ' + esc(r.status || 'new') + '">' + esc(ISTAGE_CN[r.status] || r.status || '新留言') + '</span></td>' +
        '<td>' + esc(r.name || '-') + '<div class="muted">' + esc(r.email || '') + '</div>' +
          (r.phone ? '<div class="muted">' + esc(r.phone) + '</div>' : '') + '</td>' +
        '<td>' + esc(r.machine || r.company || '-') + '</td>' +
        '<td>' + esc((r.message || '').slice(0, 90)) + ((r.message || '').length > 90 ? '…' : '') + '</td>' +
        '<td class="muted">' + esc((r.page || '').replace(/^https?:\\/\\/[^/]+/, '')) + '</td></tr>';
    });
    el('irows').innerHTML = html || '<tr><td colspan="6" class="muted">暂无留言。</td></tr>';
    var c = counts || {};
    el('istat').textContent = Object.keys(c).filter(function (k) { return c[k]; })
      .map(function (k) { return (ISTAGE_CN[k] || k) + ' ' + c[k]; }).join(' · ');
    Array.prototype.forEach.call(document.querySelectorAll('#irows tr.row'), function (tr) {
      tr.onclick = function () { openInq(state.inquiries[Number(tr.getAttribute('data-i'))]); };
    });
  }

  function openInq(r) {
    state.currentInq = r;
    var stages = ['new', 'following', 'quoted', 'done', 'spam'];
    var opts = stages.map(function (s) {
      return '<option value="' + s + '"' + (r.status === s ? ' selected' : '') + '>' + ISTAGE_CN[s] + '</option>';
    }).join('');
    var notes = (r.notes || []).map(function (n) {
      return esc((n.at || '').slice(0, 16).replace('T', ' ')) + ' - ' + esc(n.text);
    }).join('<br>');
    el('card').innerHTML =
      '<h2>' + esc(r.name || r.email || '匿名访客') + '</h2>' +
      '<div class="muted">' + esc(r.id) + ' · ' + esc((r.receivedAt || '').slice(0, 19).replace('T', ' ')) + '</div>' +
      '<dl class="kv">' +
      '<dt>邮箱</dt><dd>' + (r.email ? '<a href="mailto:' + esc(r.email) + '">' + esc(r.email) + '</a>' : '-') + '</dd>' +
      '<dt>电话</dt><dd>' + esc(r.phone || '-') + '</dd>' +
      '<dt>公司</dt><dd>' + esc(r.company || '-') + '</dd>' +
      '<dt>设备/型号</dt><dd>' + esc(r.machine || '-') + '</dd>' +
      '<dt>来源页</dt><dd>' + esc(r.page || '-') + '</dd>' +
      '<dt>国家</dt><dd>' + esc(r.country || '-') + '</dd>' +
      '</dl>' +
      '<div class="msg">' + esc(r.message || '') + '</div>' +
      '<div class="muted" style="font-size:12px">回复客户请直接在自己的邮箱点「回复」——通知邮件的 Reply-To 已设为访客邮箱。</div>' +
      '<div class="err" id="iErr"></div>' +
      '<div class="grid">' +
      '<label>状态</label><select id="iStatus">' + opts + '</select>' +
      '<label>添加备注</label><textarea id="iNote" placeholder="已回复、报价金额、结果……"></textarea>' +
      '</div>' +
      '<div class="actions">' +
      '<button id="iSave">保存</button>' +
      '<button id="iClose">关闭</button>' +
      '<button id="iDel" class="danger">删除</button>' +
      '</div>' +
      '<h3 class="sec">备注</h3><div class="hist">' + (notes || '<span class="muted">无</span>') + '</div>';
    el('panel').hidden = false;

    el('iClose').onclick = function () { el('panel').hidden = true; };
    el('iSave').onclick = function () {
      api('/api/inquiries/' + encodeURIComponent(r.id), {
        method: 'PATCH',
        body: JSON.stringify({ status: el('iStatus').value, note: el('iNote').value })
      }).then(function () { el('panel').hidden = true; loadInq(); })
        .catch(function (e) { el('iErr').textContent = e.message; });
    };
    el('iDel').onclick = function () {
      if (!confirm('确定删除这条留言？此操作不可恢复。')) return;
      api('/api/inquiries/' + encodeURIComponent(r.id), { method: 'DELETE' })
        .then(function () { el('panel').hidden = true; loadInq(); })
        .catch(function (e) { el('iErr').textContent = e.message; });
    };
  }

  /* ------------------------------------------------------------- traffic */
  function table(rows, cols) {
    if (!rows || !rows.length) return '<div class="muted" style="font-size:13px">暂无数据。</div>';
    var html = '<table><thead><tr>' + cols.map(function (c) {
      return '<th' + (c.num ? ' class="num"' : '') + '>' + esc(c.title) + '</th>';
    }).join('') + '</tr></thead><tbody>';
    rows.forEach(function (r) {
      html += '<tr>' + cols.map(function (c) {
        var v = c.get(r);
        return '<td' + (c.num ? ' class="num"' : '') + '>' + (c.html ? c.html(v, r) : esc(v)) + '</td>';
      }).join('') + '</tr>';
    });
    return html + '</tbody></table>';
  }

  function loadTraffic() {
    el('tstat').textContent = '加载中……';
    api('/api/traffic?days=' + state.days).then(function (d) {
      el('tstat').textContent = '生成于 ' + new Date(d.generatedAt).toLocaleString('zh-CN');
      var notices = [];
      if (d.cfError) notices.push('Cloudflare 流量数据不可用：' + d.cfError);
      if (d.bingError) notices.push('Bing 数据不可用：' + d.bingError);
      el('tnotice').hidden = !notices.length;
      el('tnotice').innerHTML = notices.map(esc).join('<br>');

      var cf = d.cf || {};
      var bing = d.bing || {};
      // Internal navigation is not an entry source; keep only outside sites.
      function external(rows) {
        return (rows || []).filter(function (r) {
          var h = (r.host || '').toLowerCase();
          return h !== 'cncdisplay.com' && h !== 'www.cncdisplay.com';
        });
      }
      cf.referers = external(cf.referers);
      cf.entries = external(cf.entries);
      el('tkpi').innerHTML =
        kpi('全站访问数', num(cf.visits), '独立访问（Cloudflare RUM）') +
        kpi('页面浏览', num(cf.pageviews), '所有页面加载次数') +
        kpi('Bing 点击', num(bing.clicks), 'Bing Webmaster') +
        kpi('Bing 展示', num(bing.impressions), 'CTR ' + pct(bing.ctr)) +
        kpi('Bing 平均排名', (bing.position ? bing.position.toFixed(1) : '-'), '按展示加权');

      el('tEntries').innerHTML = table(cf.entries, [
        { title: '来源网站', get: function (r) { return r.host || '直接访问'; } },
        { title: '落地页', get: function (r) { return r.path || '/'; } },
        { title: '页面浏览', num: true, get: function (r) { return num(r.pageviews); } }
      ]);
      el('tReferers').innerHTML = table(cf.referers, [
        { title: '来源网站', get: function (r) { return r.host || '直接访问 / 无来源'; } },
        { title: '页面浏览', num: true, get: function (r) { return num(r.pageviews); } }
      ]);
      el('tPages').innerHTML = table(cf.pages, [
        { title: '页面', get: function (r) { return r.path || '/'; } },
        { title: '页面浏览', num: true, get: function (r) { return num(r.pageviews); } }
      ]);
      var bingNote = bing.queryFallback
        ? '<div class="muted" style="font-size:13px;padding:0 0 8px">Bing 关键词只有周粒度，本窗口无完整周桶，显示最近一周（截至 ' +
          esc((bing.weeks || []).slice(-1)[0] || '-') + '）。</div>'
        : '';
      el('tBingQueries').innerHTML = bingNote + table(bing.queries, [
        { title: '关键词', get: function (r) { return r.query; } },
        { title: '周结束', get: function (r) { return r.weekEnd || '-'; } },
        { title: '点击', num: true, get: function (r) { return num(r.clicks); } },
        { title: '展示', num: true, get: function (r) { return num(r.impressions); } },
        { title: 'CTR', num: true, get: function (r) { return pct(r.ctr); } },
        { title: '排名', num: true, get: function (r) { return r.position ? r.position.toFixed(1) : '-'; } }
      ]);
      el('tBingDaily').innerHTML = table((bing.daily || []).slice(-14), [
        { title: '日期', get: function (r) { return r.date; } },
        { title: '点击', num: true, get: function (r) { return num(r.clicks); } },
        { title: '展示', num: true, get: function (r) { return num(r.impressions); } }
      ]);
      el('tCountries').innerHTML = table(cf.countries, [
        { title: '国家/地区', get: function (r) { return r.name || '-'; } },
        { title: '页面浏览', num: true, get: function (r) { return num(r.pageviews); } }
      ]);
      el('tDaily').innerHTML = table((cf.daily || []).slice(-14), [
        { title: '日期', get: function (r) { return r.date; } },
        { title: '访问', num: true, get: function (r) { return num(r.visits); } },
        { title: '页面浏览', num: true, get: function (r) { return num(r.pageviews); } }
      ]);
    }).catch(function (e) {
      el('tstat').textContent = '';
      el('tnotice').hidden = false;
      el('tnotice').textContent = '流量数据加载失败：' + e.message;
    });
  }

  function kpi(k, v, s) {
    return '<div class="kpi"><div class="k">' + esc(k) + '</div><div class="v">' + esc(v) +
      '</div><div class="s">' + esc(s) + '</div></div>';
  }

  /* ------------------------------------------------------------- common */
  el('loginBtn').onclick = function () {
    fetch('/api/login', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: el('pw').value })
    }).then(function (r) {
      if (r.ok) { el('loginErr').textContent = ''; showApp(true); showTab('orders'); }
      else el('loginErr').textContent = '密码错误。';
    });
  };
  el('pw').onkeydown = function (e) { if (e.key === 'Enter') el('loginBtn').click(); };
  el('btnOut').onclick = function () {
    fetch('/api/logout', { method: 'POST' }).then(function () { showApp(false); });
  };
  function password() {
    el('card').innerHTML =
      '<h2>修改密码</h2>' +
      '<div class="grid">' +
      '<label>当前密码</label><input id="pwCur" type="password" autocomplete="current-password">' +
      '<label>新密码</label><input id="pwNew" type="password" autocomplete="new-password" placeholder="至少 8 位">' +
      '<label>重复新密码</label><input id="pwNew2" type="password" autocomplete="new-password">' +
      '</div>' +
      '<div class="actions"><button id="pwSave">保存</button><button id="pwClose">关闭</button></div>' +
      '<div class="err" id="pwErr"></div>';
    el('panel').hidden = false;
    el('pwClose').onclick = function () { el('panel').hidden = true; };
    el('pwSave').onclick = function () {
      if (el('pwNew').value !== el('pwNew2').value) {
        el('pwErr').textContent = '两次输入的新密码不一致。';
        return;
      }
      api('/api/password', {
        method: 'POST',
        body: JSON.stringify({ current: el('pwCur').value, next: el('pwNew').value })
      }).then(function () {
        el('panel').hidden = true;
        alert('密码已修改。由于 KV 缓存，约一分钟后对新登录生效。');
      }).catch(function (e) { el('pwErr').textContent = e.message; });
    };
  }

  Array.prototype.forEach.call(document.querySelectorAll('nav.tabs button'), function (b) {
    b.onclick = function () { showTab(b.getAttribute('data-tab')); };
  });
  Array.prototype.forEach.call(document.querySelectorAll('#segDays button'), function (b) {
    b.onclick = function () {
      state.days = Number(b.getAttribute('data-days'));
      Array.prototype.forEach.call(document.querySelectorAll('#segDays button'), function (x) {
        x.className = x === b ? 'on' : '';
      });
      loadTraffic();
    };
  });

  el('btnManual').onclick = manual;
  el('btnSync').onclick = sync;
  el('btnPw').onclick = password;
  el('q').oninput = function () { clearTimeout(window.__t); window.__t = setTimeout(load, 250); };
  el('stage').onchange = load;
  el('iq').oninput = function () { clearTimeout(window.__ti); window.__ti = setTimeout(loadInq, 250); };
  el('istatus').onchange = loadInq;

  api('/api/orders?limit=1').then(function () { showApp(true); showTab('orders'); })
    .catch(function () { showApp(false); });
})();
</script>
</body>
</html>`;
}
