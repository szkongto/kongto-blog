"""Parse _redirects → cloudflare-worker.js (301 redirect engine)."""
import json, re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_redirects')
DST = os.path.join(ROOT, 'cloudflare-worker.js')

REDIRECTS = {}
LINE_ERR = 0

with open(SRC, 'r', encoding='utf-8') as f:
    for line in f:
        raw = line.strip()
        if not raw or raw.startswith('#'):
            continue

        # Remove trailing HTTP status (301 / 302)
        line_clean = re.sub(r'\s+30[12]\s*$', '', raw).strip()

        if not line_clean:
            LINE_ERR += 1
            continue

        # Split on whitespace (preserve URL-encoded chars)
        parts = line_clean.split(None, 1)
        if len(parts) < 2:
            LINE_ERR += 1
            continue

        src, dst_raw = parts[0], parts[1]

        # Normalise source: strip leading scheme+host garbage e.g. /"https://cncdisplay.com/"
        src = src.strip('"\'')
        if src.startswith('http'):
            try:
                from urllib.parse import urlparse
                src = urlparse(src).path
            except Exception:
                pass
        if not src.startswith('/'):
            src = '/' + src

        # Normalise destination
        dst = dst_raw.strip('"\'')
        # If it's a relative path, prepend host (Worker will use request host)
        if not dst.startswith('http'):
            dst = dst if dst.startswith('/') else '/' + dst

        # Sanity check
        if src == dst:
            LINE_ERR += 1
            continue
        # Map source → destination (keep original for Worker logic)
        REDIRECTS[src] = dst

# Also add decoded variants for URLs with percent-encoded Chinese chars
ADDITIONS = {}
for src, dst in list(REDIRECTS.items()):
    decoded = src.encode('utf-8').decode('unicode_escape') if '\\u' in src else ''
    from urllib.parse import unquote
    decoded = unquote(src)
    if decoded != src and decoded not in REDIRECTS:
        ADDITIONS[decoded] = dst

REDIRECTS.update(ADDITIONS)

# Also add /en/posts/ variants for any /posts/ redirect with non-ASCII chars
# Google indexed Chinese-filename URLs under /en/posts/ that don't exist
EN_ADDITIONS = {}
for src, dst in list(REDIRECTS.items()):
    if src.startswith('/posts/') and any(ord(c) > 127 for c in src):
        en_src = '/en' + src
        if en_src not in REDIRECTS:
            EN_ADDITIONS[en_src] = dst
REDIRECTS.update(EN_ADDITIONS)


def flatten_redirects(redirects):
    """Collapse local redirect chains so every source points at its final target."""
    flattened = {}
    flattened_chains = []
    for src in sorted(redirects):
        seen = [src]
        dst = redirects[src]
        while not dst.startswith('http') and dst in redirects:
            if dst in seen:
                cycle = ' -> '.join(seen + [dst])
                raise RuntimeError(f'redirect cycle: {cycle}')
            seen.append(dst)
            dst = redirects[dst]
        if len(seen) > 1:
            flattened_chains.append((src, seen[1:], dst))
        flattened[src] = dst
    return flattened, flattened_chains


REDIRECTS, FLATTENED_CHAINS = flatten_redirects(REDIRECTS)

if '--check' in sys.argv:
    print(f'OK {len(REDIRECTS)} redirect sources, '
          f'{len(FLATTENED_CHAINS)} chains flattened')
    sys.exit(0)

# Build worker JS
def js_escape(s):
    """Escape string for JS single-quoted string literal."""
    return s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')

entries = []
for src, dst in sorted(REDIRECTS.items()):
    entries.append(f"  '{js_escape(src)}': '{js_escape(dst)}',")

entries_str = '\n'.join(entries)

worker_js = f'''// Cloudflare Worker — cncdisplay.com 301 Redirect Engine
// Auto-generated from _redirects — do not edit directly.
// Service Worker format (compatible with Dashboard-created workers)

const REDIRECTS = {{
{entries_str}
}};

// ── 安全响应头 ─────────────────────────────────────────────
// GitHub Pages 上 _headers / netlify.toml 是死配置（实测线上 6 个头全缺），
// 改由边缘 Worker 注入。CSP 刻意放宽：站点内含 1605 处内联脚本 /
// 866 处内联事件处理器，收紧 script-src 会直接打断 PayPal 结账等交互；
// 仍保留 object-src / base-uri / frame-ancestors 三项硬限制。
const SECURITY_HEADERS = {{
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'SAMEORIGIN',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=(), payment=*',
  'Content-Security-Policy': "default-src 'self' https: data: blob:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: blob: https:; font-src 'self' data: https:; connect-src 'self' https:; media-src 'self' https: data: blob:; frame-src 'self' https:; object-src 'none'; base-uri 'self'; form-action 'self' https:; frame-ancestors 'self'; upgrade-insecure-requests",
}};

// 只给真正的内容响应注入（301 不必包，浏览器会跟到最终响应）
function harden(resp) {{
  const out = new Response(resp.body, resp);
  for (const k in SECURITY_HEADERS) {{
    out.headers.set(k, SECURITY_HEADERS[k]);
  }}
  return out;
}}

// Normalise a URL path: decode percent-encoding once, collapse double slashes
function normalise(p) {{
  try {{ p = decodeURIComponent(p); }} catch(e) {{}}
  p = p.replace(/\\/\\/+/g, '/');
  return p;
}}

addEventListener('fetch', event => {{
  const request = event.request;
  const url = new URL(request.url);
  let path = url.pathname;

  // Skip root
  if (path === '/' || path === '') {{
    return event.respondWith(fetch(request).then(harden));
  }}

  // Block access to config files (2026-08-08 audit: _redirects was publicly downloadable)
  if (path === '/_redirects' || path === '/_headers') {{
    return event.respondWith(new Response('Not Found', {{ status: 404 }}));
  }}

  const redirectTo = target => {{
    const destination = target.startsWith('http') ? target : `${{url.origin}}${{target}}`;
    return event.respondWith(Response.redirect(destination, 301));
  }};

  const lookupRedirect = rawPath => {{
    const candidates = [rawPath];
    const normalisedPath = normalise(rawPath);
    if (normalisedPath !== rawPath) candidates.push(normalisedPath);
    if (rawPath.length > 1 && rawPath.endsWith('/')) {{
      candidates.push(rawPath.slice(0, -1));
    }}
    for (const candidate of candidates) {{
      const match = REDIRECTS[candidate];
      if (match) return match;
    }}
    return null;
  }};

  // Collapse double slashes → 301 to clean URL
  // Google indexed some // URLs (e.g. /en//posts/...) as duplicates
  if (path.includes('//')) {{
    const clean = path.replace(/\\/\\/+/g, '/');
    const match = lookupRedirect(clean);
    return redirectTo(match || clean);
  }}

  // Try exact/normalised/trailing-slash match once. The generated map is
  // flattened, so a matching source already points at its final target.
  const exact = lookupRedirect(path);
  if (exact) {{
    return redirectTo(exact);
  }}

  // Strip /en/ prefix — all old /en/ URLs redirect to root path
  // Phase 0b migration: /en/brands/ /en/products/ /en/guides/ etc.
  if (path.startsWith('/en/') || path === '/en') {{
    const stripped = path === '/en' ? '/' : path.replace(/^\\/en/, '');
    const match = lookupRedirect(stripped);
    return redirectTo(match || stripped);
  }}

  // Strip /en_bak/ prefix — backup directory leaked to production
  if (path.startsWith('/en_bak/') || path === '/en_bak') {{
    const stripped = path === '/en_bak' ? '/' : path.replace(/^\\/en_bak/, '');
    const match = lookupRedirect(stripped);
    return redirectTo(match || stripped);
  }}

  // Pass through to origin (GitHub Pages)
  event.respondWith(fetch(request).then(harden));
}});
'''

with open(DST, 'w', encoding='utf-8') as f:
    f.write(worker_js)

print(f"OK Generated {DST}")
print(f"   {len(REDIRECTS)} redirect rules parsed")
print(f"   {LINE_ERR} lines skipped (errors/invalid)")
