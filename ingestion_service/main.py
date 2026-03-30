#!/usr/bin/env python3
"""
Simple ingestion webhook service for the expense app.

- POST /webhook/ingest: accepts parsed expense JSON from agent, verifies HMAC signature (if WEBHOOK_SECRET set), saves to DB.
- GET /api/expenses: list expenses
- GET /api/export: returns CSV

Database: uses Postgres when DATABASE_URL env var is set (Vercel), otherwise falls back to SQLite (local dev).
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
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Config
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.getenv("INGEST_DB_PATH", os.path.join(BASE_DIR, "data", "expenses.db"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
PH = "%s" if DATABASE_URL else "?"  # SQL placeholder differs between Postgres and SQLite

app = FastAPI(title="Expense Ingestion Service")

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Optional in-memory rate limiting for the ingestion webhook.
# Configure with WEBHOOK_RATE_LIMIT (requests per window) and WEBHOOK_RATE_WINDOW (seconds).
RATE_LIMIT = int(os.getenv("WEBHOOK_RATE_LIMIT", "60"))  # requests per window
RATE_WINDOW = int(os.getenv("WEBHOOK_RATE_WINDOW", "60"))  # seconds
_RATE_STORE = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Apply only to the ingestion webhook and client ingest paths
    if request.url.path in ("/webhook/ingest", "/api/client_ingest"):
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


class _DbConn:
    """Thin wrapper that normalizes sqlite3 and psycopg2 connection interfaces."""

    def __init__(self):
        if DATABASE_URL:
            import psycopg2  # type: ignore
            self._raw = psycopg2.connect(DATABASE_URL)
            self._is_pg = True
        else:
            ensure_db_dir(DB_PATH)
            self._raw = sqlite3.connect(DB_PATH, check_same_thread=False)
            self._raw.row_factory = sqlite3.Row
            self._is_pg = False

    def execute(self, sql: str, params=()):
        if self._is_pg:
            import psycopg2.extras  # type: ignore
            cur = self._raw.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql, params if params else None)
            return cur
        return self._raw.execute(sql, params)

    def commit(self):
        self._raw.commit()


_conn = None
_init_exception = None

def _init_conn_and_db():
    global _conn, _init_exception
    if _conn is not None:
        return
    try:
        _conn = _DbConn()
        # Initialize DB schema when connection established
        init_db()
    except Exception as e:
        _conn = None
        _init_exception = e


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
            created_at TEXT,
            receipt_blob TEXT
        )
        """
    )
    # Ensure receipt_blob column exists on existing tables (ALTER TABLE if needed)
    try:
        _conn.execute("SELECT receipt_blob FROM expenses LIMIT 1")
    except Exception:
        try:
            _conn.execute("ALTER TABLE expenses ADD COLUMN receipt_blob TEXT")
        except Exception:
            pass

    _conn.execute(
        """
        CREATE TABLE IF NOT EXISTS replays (
            signature TEXT PRIMARY KEY,
            ts INTEGER
        )
        """
    )
    _conn.commit()


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
        # Replay protection only when DB available
        _init_conn_and_db()
        if _conn is None:
            # Can't check replays without DB; skip replay protection
            return ok
        cur = _conn.execute(f"SELECT ts FROM replays WHERE signature = {PH}", (signature_header,))
        if cur.fetchone():
            return False
        if DATABASE_URL:
            _conn.execute(
                f"INSERT INTO replays (signature, ts) VALUES ({PH}, {PH}) ON CONFLICT DO NOTHING",
                (signature_header, ts or now)
            )
        else:
            _conn.execute(
                f"INSERT OR IGNORE INTO replays (signature, ts) VALUES ({PH}, {PH})",
                (signature_header, ts or now)
            )
        cutoff = now - MAX_AGE
        _conn.execute(f"DELETE FROM replays WHERE ts < {PH}", (cutoff,))
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
    receipt_blob: Optional[str] = None


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
    _init_conn_and_db()
    if _conn is None:
        raise HTTPException(status_code=503, detail="Database not available")
    _conn.execute(
        f"INSERT INTO expenses (id, merchant, date, amount, currency, category, raw_text, source, created_at, receipt_blob) VALUES ({PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH})",
        (_id, payload.merchant, payload.date, payload.amount, payload.currency, payload.category, payload.raw_text, payload.source, created_at, getattr(payload, 'receipt_blob', None))
    )
    _conn.commit()
    return {"id": _id}


@app.post("/api/client_ingest")
async def client_ingest(request: Request):
    # Client-side ingestion endpoint for the PWA. Simple checks: Origin + CLIENT_ID header.
    origin = request.headers.get("origin")
    server_client_id = os.getenv("CLIENT_ID")
    # Verify origin is allowed
    if origin not in CORS_ORIGINS:
        raise HTTPException(status_code=403, detail="Origin not allowed")
    header_id = request.headers.get("x-client-id")
    if not server_client_id or header_id != server_client_id:
        raise HTTPException(status_code=401, detail="Invalid client id")
    # Optional password protection: if CLIENT_PASSWORD is set, require X-Client-Auth header
    server_password = os.getenv("CLIENT_PASSWORD")
    if server_password:
        header_auth = request.headers.get("x-client-auth")
        if not header_auth or header_auth != server_password:
            raise HTTPException(status_code=401, detail="Invalid client auth")
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
    _init_conn_and_db()
    if _conn is None:
        raise HTTPException(status_code=503, detail="Database not available")
    _conn.execute(
        f"INSERT INTO expenses (id, merchant, date, amount, currency, category, raw_text, source, created_at, receipt_blob) VALUES ({PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH},{PH})",
        (_id, payload.merchant, payload.date, payload.amount, payload.currency, payload.category, payload.raw_text, payload.source, created_at, getattr(payload, 'receipt_blob', None))
    )
    _conn.commit()
    return {"id": _id}


@app.get("/api/auth_required")
def api_auth_required():
    # Returns whether the server requires a client password (CLIENT_PASSWORD env)
    return {"required": bool(os.getenv("CLIENT_PASSWORD"))}


@app.get("/api/expenses")
def api_list_expenses():
    _init_conn_and_db()
    if _conn is None:
        return {"expenses": []}
    cur = _conn.execute("SELECT * FROM expenses ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    return {"expenses": rows}


@app.get("/api/export")
def api_export_csv():
    _init_conn_and_db()
    if _conn is None:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([ "id","merchant","date","amount","currency","category","raw_text","source","created_at" ])
        return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=expenses.csv"})
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
    _init_conn_and_db()
    if _conn is None:
        return Response(content='{"status":"degraded","db":"unavailable"}', media_type="application/json", status_code=503)
    return {"status":"ok"}
