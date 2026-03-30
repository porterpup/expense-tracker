Production README for Expense Tracker

Frontend: https://webapp-rmuuy00i9-porterpups-projects.vercel.app
Backend:  https://ingestionservice.vercel.app

Environment variables (Vercel project: ingestion_service)
- DATABASE_URL: injected by Neon (production)
- WEBHOOK_SECRET: HMAC secret for /webhook/ingest (rotated)
- CLIENT_ID: client id used by the PWA for automatic sync
- CLIENT_PASSWORD: (optional) if set, the frontend requires a password; set this via vercel env add CLIENT_PASSWORD production "<password>"
- CORS_ORIGINS: set to frontend URL
- VITE_API_URL: set in webapp project to backend URL

Secrets:
- WEBHOOK_SECRET is stored in Vercel production env (rotated). Do NOT keep local copies.

Runbook:
- To rotate secret (recommended method, no local file):
  1) SECRET=$(openssl rand -hex 32)
  2) vercel env rm WEBHOOK_SECRET production --cwd ingestion_service --yes
  3) vercel env add WEBHOOK_SECRET production --value "$SECRET" --cwd ingestion_service --yes
  4) vercel --cwd ingestion_service --prod
- To redeploy backend: vercel --cwd ingestion_service --prod
- To check health: GET /health (returns {"status":"ok"})

Notes:
- DB uses Neon Postgres; tables created automatically on first run.
- Ensure only authorized producers can post to /webhook/ingest using the WEBHOOK_SECRET HMAC.
- See PRODUCTION_RUNBOOK.md for full rotation and distribution guidance.

Password note:
- CLIENT_PASSWORD has been set in Vercel production for ingestion_service (no local copy). To rotate or change, use: vercel env add CLIENT_PASSWORD production "<new-password>" --cwd ingestion_service --yes
