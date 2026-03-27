#!/usr/bin/env python3
"""
Simple ingestion webhook service for the expense app.

- POST /webhook/ingest: accepts parsed expense JSON from agent, verifies HMAC signature (if WEBHOOK_SECRET set), saves to SQLite DB.
- GET /api/expenses: list expenses
- GET /api/export: returns CSV
"""
import os
import hmac
import hashlib
import sqlite3
import uuid
import datetime
import csv
import io
from typing import Optional

from fastapi import FastAPI, Request, Header, HTTPException, Response
from pydantic import BaseModel

# Config
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.getenv("INGEST_DB_PATH", os.path.join(BASE_DIR, "data", "expenses.db"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")  # set to enable HMAC verification

app = FastAPI(title="Expense Ingestion Service")


# Optional in-memory rate limiting for the ingestion webhook.
# Configure with WEBHOOK_RATE_LIMIT (requests per window) and WEBHOOK_RATE_WINDOW (seconds).
RATE_LIMIT = int(os.getenv("WEBHOOK_RATE_LIMIT", "60"))  # requests per window
RATE_WINDOW = int(os.getenv("WEBHOOK_RATE_WINDOW", "60"))  # seconds
_RATE_STORE = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Apply only to the ingestion webhook path
    if request.url.path == "/webhook/ingest":
        client_ip = request.client.host if request.client else "unknown"
        now = int(datetime.datetime.utcnow().timestamp())
        window_start = now - RATE_WINDOW
        timestamps = _RATE_STORE.get(client_ip, [])
        # prune old timestamps
        timestamps = [t for t in timestamps if t >= window_start]
        if len(timestamps) >= RATE_LIMIT:
            return Response(status_code=429, content="Too many requests")
        timestamps.append(now)
        _RATE_STORE[client_ip] = timestamps
    return await call_next(request)


def ensure_db_dir(path: str):
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)


def get_conn():
    ensure_db_dir(DB_PATH)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

_conn = get_conn()


def init_db():
    _conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id TEXT PRIMARY KEY,
            merchant TEXT,
            date TEXT,
            amount REAL,
            currency TEXT,
            category TEXT,
            raw_text TEXT,
            source TEXT,
            created_at TEXT
        )
        """
    )
    _conn.execute(
        """
        CREATE TABLE IF NOT EXISTS replays (
            signature TEXT PRIMARY KEY,
            ts INTEGER
        )
        """
    )
    _conn.commit()


init_db()


MAX_AGE = int(os.getenv("WEBHOOK_MAX_AGE", "300"))  # seconds

def verify_signature(body: bytes, signature_header: Optional[str], timestamp_header: Optional[str] = None) -> bool:
    # If no secret configured, accept payloads (development mode).
    if not WEBHOOK_SECRET:
        return True
    if not signature_header:
        return False
    now = int(datetime.datetime.utcnow().timestamp())
    ts = None
    if timestamp_header:
        try:
            ts = int(timestamp_header)
        except Exception:
            return False
        # Reject if timestamp is outside the allowed window
        if abs(now - ts) > MAX_AGE:
            return False
    try:
        # Support two signing schemes for backward compatibility:
        # 1) HMAC(secret, body)
        # 2) HMAC(secret, "<timestamp>." + body)  (preferred when timestamp provided)
        expected_body_only = hmac.new(WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
        expected_with_ts = None
        if ts is not None:
            expected_with_ts = hmac.new(WEBHOOK_SECRET.encode("utf-8"), str(ts).encode("utf-8") + b"." + body, hashlib.sha256).hexdigest()
        ok = hmac.compare_digest(expected_body_only, signature_header) or (expected_with_ts and hmac.compare_digest(expected_with_ts, signature_header))
        if not ok:
            return False
        # Persistent replay protection using SQLite table
        cur = _conn.execute("SELECT ts FROM replays WHERE signature = ?", (signature_header,))
        if cur.fetchone():
            return False
        # Insert signature (ignore if race) and prune old entries
        _conn.execute("INSERT OR IGNORE INTO replays (signature, ts) VALUES (?, ?)", (signature_header, ts or now))
        cutoff = now - MAX_AGE
        _conn.execute("DELETE FROM replays WHERE ts < ?", (cutoff,))
        _conn.commit()
        return True
    except Exception:
        return False


class IngestPayload(BaseModel):
    merchant: str
    date: str
    amount: float
    currency: Optional[str] = "USD"
    category: Optional[str] = None
    raw_text: Optional[str] = None
    source: Optional[str] = "agent"
    id: Optional[str] = None


@app.post("/webhook/ingest")
async def webhook_ingest(request: Request, x_signature: Optional[str] = Header(None), x_timestamp: Optional[str] = Header(None)):
    body = await request.body()
    if not verify_signature(body, x_signature, x_timestamp):
        raise HTTPException(status_code=401, detail="Invalid or missing signature")
    try:
        payload_json = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    try:
        payload = IngestPayload(**payload_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    _id = payload.id or str(uuid.uuid4())
    created_at = datetime.datetime.utcnow().isoformat()
    _conn.execute(
        "INSERT INTO expenses (id, merchant, date, amount, currency, category, raw_text, source, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (_id, payload.merchant, payload.date, payload.amount, payload.currency, payload.category, payload.raw_text, payload.source, created_at)
    )
    _conn.commit()
    return {"id": _id}


@app.get("/api/expenses")
def api_list_expenses():
    cur = _conn.execute("SELECT * FROM expenses ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    return {"expenses": rows}


@app.get("/api/export")
def api_export_csv():
    cur = _conn.execute("SELECT * FROM expenses ORDER BY created_at DESC")
    rows = cur.fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([ "id","merchant","date","amount","currency","category","raw_text","source","created_at" ])
    for r in rows:
        writer.writerow([r["id"], r["merchant"], r["date"], r["amount"], r["currency"], r["category"], r["raw_text"], r["source"], r["created_at"]])
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=expenses.csv"})


@app.get("/health")
def health():
    return {"status":"ok"}
