#!/usr/bin/env python3
"""
Minimal helper script to post parsed expense JSON to webhook with HMAC signature.

Usage examples:

1) Post a simple expense:
   export WEBHOOK_SECRET=changeme
   python discord_agent.py --webhook http://localhost:8000/webhook/ingest --merchant Starbucks --date 2026-03-27 --amount 4.25

2) Post from a JSON file:
   python discord_agent.py --webhook http://localhost:8000/webhook/ingest --json sample.json
"""
import os
import sys
import json
import hmac
import hashlib
import argparse
import time

try:
    import requests
except Exception:
    print("requests is required: pip install requests")
    raise


def sign_payload(payload_bytes: bytes, secret: str, timestamp: int = None):
    """Sign payload. If timestamp is provided, sign using '<timestamp>.<body>' to enable replay protection."""
    if timestamp is None:
        return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.new(secret.encode("utf-8"), str(timestamp).encode("utf-8") + b"." + payload_bytes, hashlib.sha256).hexdigest()


def post_to_webhook(url: str, payload: dict, secret: str = None):
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type":"application/json"}
    if secret:
        ts = int(time.time())
        headers["X-Timestamp"] = str(ts)
        headers["X-Signature"] = sign_payload(data, secret, ts)
    resp = requests.post(url, data=data, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp


def main():
    parser = argparse.ArgumentParser(description="Post parsed expense JSON to ingestion webhook with HMAC signature.")
    parser.add_argument("--webhook", required=True, help="Ingestion webhook URL (e.g., http://localhost:8000/webhook/ingest)")
    parser.add_argument("--secret", default=os.getenv("WEBHOOK_SECRET"), help="Webhook secret for HMAC signing. If not provided, will use WEBHOOK_SECRET env var. If empty, no signature is sent.")
    parser.add_argument("--json", help="Path to JSON file containing parsed expense or '-' to read from stdin.")
    parser.add_argument("--merchant", help="Merchant name")
    parser.add_argument("--date", help="Date string (YYYY-MM-DD)")
    parser.add_argument("--amount", type=float, help="Amount")
    parser.add_argument("--currency", default="USD", help="Currency")
    parser.add_argument("--category", default=None, help="Category")
    args = parser.parse_args()
    if args.json and args.json != "-":
        with open(args.json, "r") as f:
            payload = json.load(f)
    elif args.json == "-":
        payload = json.load(sys.stdin)
    else:
        if not (args.merchant and args.date and args.amount is not None):
            parser.error("Either provide --json or merchant/date/amount")
        payload = {
            "merchant": args.merchant,
            "date": args.date,
            "amount": args.amount,
            "currency": args.currency,
            "category": args.category,
            "source": "discord_agent"
        }
    resp = post_to_webhook(args.webhook, payload, args.secret)
    print("Posted:", resp.status_code, resp.text)


if __name__ == "__main__":
    main()
