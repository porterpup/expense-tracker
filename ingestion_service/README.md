Expense ingestion service (webhook)

## Local development (SQLite)

1. Create a virtualenv and install dependencies:

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Configure environment (optional):

   export WEBHOOK_SECRET=changeme    # set for HMAC verification
   export INGEST_DB_PATH=data/expenses.db

3. Run the server (from repo root):

   uvicorn ingestion_service.main:app --reload --host 0.0.0.0 --port 8000

When `DATABASE_URL` is not set, the service stores data in SQLite at `INGEST_DB_PATH`.

## Deploying to Vercel (Postgres)

The service is pre-configured for Vercel serverless deployment via `vercel.json` and `api/index.py`.

### One-time setup

1. **Create a Vercel Postgres database:**
   - Vercel dashboard → Storage → Create Database → Postgres
   - Copy the project name for the next step

2. **Create a Vercel project for this service:**
   - New Project → Import GitHub repo
   - Root directory: `ingestion_service`
   - Framework preset: Other
   - Add environment variables:
     - `WEBHOOK_SECRET` — run `openssl rand -hex 32` to generate
     - `CORS_ORIGINS` — set to your frontend Vercel URL (e.g. `https://expense-tracker.vercel.app`)
   - Link the Vercel Postgres storage you created (this auto-injects `DATABASE_URL`)

3. **Deploy** — Vercel will build and deploy automatically on every push to `main`.

### Verify deployment

```bash
# Health check
curl https://<your-backend>.vercel.app/health
# → {"status":"ok"}

# List expenses (should be empty initially)
curl https://<your-backend>.vercel.app/api/expenses
# → {"expenses":[]}

# Test ingest (no signature required if WEBHOOK_SECRET not set)
curl -X POST https://<your-backend>.vercel.app/webhook/ingest \
  -H "Content-Type: application/json" \
  -d '{"merchant":"Test","date":"2026-01-01","amount":9.99}'
```

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `WEBHOOK_SECRET` | Production | _(none)_ | HMAC-SHA256 signing key. If unset, all requests are accepted (dev mode). |
| `DATABASE_URL` | Vercel | _(auto-injected)_ | Postgres connection string. If unset, SQLite is used. |
| `POSTGRES_URL` | Vercel alt | _(auto-injected)_ | Fallback if `DATABASE_URL` is not set. |
| `INGEST_DB_PATH` | Local | `data/expenses.db` | SQLite DB path. Ignored when `DATABASE_URL` is set. |
| `CORS_ORIGINS` | Production | `*` | Comma-separated list of allowed CORS origins. |
| `WEBHOOK_MAX_AGE` | Optional | `300` | Replay protection window in seconds. |
| `WEBHOOK_RATE_LIMIT` | Optional | `60` | Max requests per window (in-memory, resets on restart). |
| `WEBHOOK_RATE_WINDOW` | Optional | `60` | Rate limit window in seconds. |

## API

- `POST /webhook/ingest` — ingest a parsed expense. Include `X-Signature` and `X-Timestamp` headers for HMAC verification. See tools/discord_agent for a signing helper.
- `GET /api/expenses` — list all expenses (JSON)
- `GET /api/export` — download all expenses as CSV
- `GET /health` — health check

### Signing

The preferred signing scheme is `HMAC-SHA256(secret, "<timestamp>.<body>")`. Include the Unix timestamp (seconds) in `X-Timestamp` and the hex digest in `X-Signature`. Requests with timestamps outside `WEBHOOK_MAX_AGE` seconds are rejected.

