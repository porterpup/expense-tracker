Expense ingestion service (webhook)

Quickstart:

1. Create a virtualenv and install dependencies:

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Configure environment (optional):

   export WEBHOOK_SECRET=changeme    # set for HMAC verification
   export INGEST_DB_PATH=data/expenses.db

3. Run the server (from repo root):

   uvicorn ingestion_service.main:app --reload --host 0.0.0.0 --port 8000

4. POST parsed JSON to /webhook/ingest (see tools/discord_agent for a helper script). For best security, include the headers X-Signature and X-Timestamp: the payload should be signed with HMAC-SHA256 using your WEBHOOK_SECRET. The preferred signing scheme is HMAC(secret, "<timestamp>.<body>") and the server will reject requests with timestamps outside the allowed window. Legacy body-only signatures are still accepted for compatibility but using X-Timestamp is recommended.

Notes:
- If WEBHOOK_SECRET is not set, the service will accept requests without signature (development mode). Set WEBHOOK_SECRET in production and protect the endpoint behind TLS.
- The service persists seen webhook signatures in the SQLite DB (replays table) to provide replay protection. Adjust the allowed timestamp window with WEBHOOK_MAX_AGE (default 300 seconds).
- The DB defaults to data/expenses.db in the repository.
