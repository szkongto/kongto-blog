#!/usr/bin/env python3
"""Audit live redirect chains for URLs in a GSC coverage drilldown."""
import argparse
import csv
import io
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

USER_AGENT = 'Mozilla/5.0 (compatible; cncdisplay-redirect-audit/1.0)'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


OPENER = urllib.request.build_opener(NoRedirect())


def load_urls(path):
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    urls = set()
    for ws in wb.worksheets:
        for row in ws.iter_rows(min_row=2, values_only=True):
            for value in row:
                if isinstance(value, str) and value.startswith('https://cncdisplay.com/'):
                    urls.add(value)
    wb.close()
    return sorted(urls)


def probe(url, timeout):
    parts = urlsplit(url)
    request_url = urlunsplit((parts.scheme, parts.netloc,
                              quote(parts.path, safe="/%:@!$&'()*+,;=-._~"),
                              quote(parts.query, safe="=&%+"), parts.fragment))
    req = urllib.request.Request(request_url, headers={'User-Agent': USER_AGENT})
    for attempt in range(2):
        try:
            response = OPENER.open(req, timeout=timeout)
            code = response.status
            headers = response.headers
            break
        except urllib.error.HTTPError as exc:
            code = exc.code
            headers = exc.headers
            break
        except Exception as exc:
            if attempt == 0:
                time.sleep(0.5)
                continue
            return None, None, str(exc)

    location = headers.get('Location')
    if location:
        location = urljoin(url, location)
    return code, location, None


def audit_url(url, max_hops, timeout):
    chain = [url]
    statuses = []
    current = url
    for _ in range(max_hops + 1):
        code, location, error = probe(current, timeout)
        if error:
            return {'source': url, 'redirects': len(chain) - 1, 'final': current,
                    'status': 'error', 'chain': ' -> '.join(chain), 'error': error}
        statuses.append(str(code))
        if code in (301, 302, 303, 307, 308) and location:
            current = location
            chain.append(current)
            continue
        return {'source': url, 'redirects': len(chain) - 1, 'final': current,
                'status': code, 'chain': ' -> '.join(chain), 'error': ''}
    return {'source': url, 'redirects': len(chain) - 1, 'final': current,
            'status': 'max-hops', 'chain': ' -> '.join(chain), 'error': 'too many redirects'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--excel', required=True, help='GSC coverage drilldown .xlsx')
    parser.add_argument('--csv', help='Write the full audit to this CSV path')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--max-hops', type=int, default=8)
    parser.add_argument('--timeout', type=int, default=20)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--fail-on-multi', action='store_true')
    args = parser.parse_args()

    urls = load_urls(args.excel)
    if args.limit:
        urls = urls[:args.limit]

    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(audit_url, url, args.max_hops, args.timeout) for url in urls]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda item: (-item['redirects'], item['source']))
    multi = [item for item in results if item['redirects'] > 1]
    errors = [item for item in results if item['status'] == 'error' or item['status'] == 'max-hops']
    bad_final = [item for item in results if item['status'] not in (200, 301, 302, 303, 307, 308,
                                                                   'error', 'max-hops')]

    print(f'URLs={len(results)} multi_hop={len(multi)} errors={len(errors)} bad_final={len(bad_final)}')
    for item in multi[:80]:
        print(f"[{item['redirects']}] {item['chain']}")

    if args.csv:
        with open(args.csv, 'w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=['source', 'redirects', 'final', 'status',
                                                        'chain', 'error'])
            writer.writeheader()
            writer.writerows(results)

    if args.fail_on_multi and multi:
        return 2
    if errors or bad_final:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
