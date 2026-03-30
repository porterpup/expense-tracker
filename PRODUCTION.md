Production README for Expense Tracker

Frontend: https://webapp-rmuuy00i9-porterpups-projects.vercel.app
Backend:  https://ingestionservice.vercel.app

Environment variables (Vercel project: ingestion_service)
- DATABASE_URL: injected by Neon (production)
- WEBHOOK_SECRET: HMAC secret for /webhook/ingest (rotated)
- CORS_ORIGINS: set to frontend URL
- VITE_API_URL: set in webapp project to backend URL

Secrets:
- New WEBHOOK_SECRET saved at /tmp/ve_webhook_secret_rotated.txt on this machine. Copy and update any producers.

Runbook:
- To rotate secret: openssl rand -hex 32 > /tmp/ve_webhook_secret_rotated.txt; vercel env rm WEBHOOK_SECRET production; vercel env add WEBHOOK_SECRET production "$(cat /tmp/ve_webhook_secret_rotated.txt)"
- To redeploy backend: vercel --cwd ingestion_service --prod
- To check health: GET /health (returns {"status":"ok"})

Notes:
- DB uses Neon Postgres; tables created automatically on first run.
- Ensure only authorized producers can post to /webhook/ingest using the WEBHOOK_SECRET HMAC.
