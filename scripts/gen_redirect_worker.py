"""Parse _redirects → cloudflare-worker.js (301 redirect engine)."""
import json, re, os

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
    return event.respondWith(fetch(request));
  }}

  // Try exact match first
  const exact = REDIRECTS[path];
  if (exact) {{
    const dest = exact.startsWith('http') ? exact : `${{url.origin}}${{exact}}`;
    return event.respondWith(Response.redirect(dest, 301));
  }}

  // Try normalised (decoded) match
  const normalised = normalise(path);
  if (normalised !== path) {{
    const match = REDIRECTS[normalised];
    if (match) {{
      const dest = match.startsWith('http') ? match : `${{url.origin}}${{match}}`;
      return event.respondWith(Response.redirect(dest, 301));
    }}
  }}

  // Try without trailing slash
  if (path.length > 1 && path.endsWith('/')) {{
    const withoutSlash = path.slice(0, -1);
    const match = REDIRECTS[withoutSlash] || REDIRECTS[normalise(withoutSlash)];
    if (match) {{
      const dest = match.startsWith('http') ? match : `${{url.origin}}${{match}}`;
      return event.respondWith(Response.redirect(dest, 301));
    }}
  }}

  // Pass through to origin (GitHub Pages)
  event.respondWith(fetch(request));
}});
'''

with open(DST, 'w', encoding='utf-8') as f:
    f.write(worker_js)

print(f"OK Generated {DST}")
print(f"   {len(REDIRECTS)} redirect rules parsed")
print(f"   {LINE_ERR} lines skipped (errors/invalid)")
