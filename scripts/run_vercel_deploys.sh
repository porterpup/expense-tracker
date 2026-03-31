#!/usr/bin/env bash
# Run Vercel deploys as the openclaw user for Bruce's workspace
# Usage: sudo bash scripts/run_vercel_deploys.sh
set -euo pipefail

OC_REPO="/var/lib/openclaw/.openclaw/workspace-bruce/expense-tracker"
WEBAPP_DIR="${OC_REPO}/webapp"
INGEST_DIR="${OC_REPO}/ingestion_service"
VERCEL_WRAPPER="/var/lib/openclaw/bin/vercel-oc"

echo "== Verifying vercel-oc (as openclaw) =="
sudo -u openclaw "${VERCEL_WRAPPER}" --version || true

echo "\n== Listing Vercel projects =="
sudo -u openclaw "${VERCEL_WRAPPER}" projects ls || true

echo "\n== Deploying webapp to production =="
sudo -u openclaw "${VERCEL_WRAPPER}" --cwd "${WEBAPP_DIR}" --prod || {
  echo "Webapp deploy failed" >&2
  exit 1
}

echo "\n== Deploying ingestion_service to production =="
sudo -u openclaw "${VERCEL_WRAPPER}" --cwd "${INGEST_DIR}" --prod || {
  echo "Backend deploy failed" >&2
  exit 1
}

echo "\n== Done: Deploys attempted =="
