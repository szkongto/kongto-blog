"""Register (or look up) the PayPal webhook that feeds the order notifier worker.

Needs a PayPal REST app's client id + secret. Live by default; pass --sandbox for
the sandbox endpoint.

    python scripts/setup_paypal_webhook.py --client-id XXX --client-secret YYY \
        --url https://cncdisplay-orders.<subdomain>.workers.dev/api/paypal-webhook

Prints the webhook id. Set it as the PAYPAL_WEBHOOK_ID worker secret.
"""

import argparse
import json
import sys
import urllib.request
import base64

sys.stdout.reconfigure(encoding="utf-8")

EVENTS = ["PAYMENT.CAPTURE.COMPLETED"]


def token(base, cid, secret):
    auth = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    req = urllib.request.Request(
        base + "/v1/oauth2/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": "Basic " + auth,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["access_token"]


def call(base, path, tk, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        base + path,
        data=data,
        headers={"Authorization": "Bearer " + tk, "Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--client-secret", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--sandbox", action="store_true")
    args = ap.parse_args()

    base = "https://api-m.sandbox.paypal.com" if args.sandbox else "https://api-m.paypal.com"
    tk = token(base, args.client_id, args.client_secret)

    existing = call(base, "/v1/notifications/webhooks", tk).get("webhooks", [])
    for hook in existing:
        if hook.get("url") == args.url:
            print("existing webhook_id:", hook["id"])
            print("event_types:", ", ".join(e["name"] for e in hook.get("event_types", [])))
            return

    hook = call(
        base,
        "/v1/notifications/webhooks",
        tk,
        "POST",
        {"url": args.url, "event_types": [{"name": e} for e in EVENTS]},
    )
    print("created webhook_id:", hook["id"])


if __name__ == "__main__":
    main()
