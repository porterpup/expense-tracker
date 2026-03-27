#!/usr/bin/env bash
set -euo pipefail

# Script to automate GitHub repo creation and Vercel deploys for the expense-tracker project.
# This script requires the GitHub CLI (gh) and/or a GITHUB_TOKEN, and the Vercel CLI and/or VERCEL_TOKEN.
# It will print exact commands to run if it cannot perform actions automatically.

REPO_NAME="expense-tracker"
LOCAL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND_DIR="$LOCAL_ROOT/webapp"
BACKEND_DIR="$LOCAL_ROOT/ingestion_service"

# Helper: print a header
header(){ echo; echo "=== $1 ==="; }

# Check tools
which gh >/dev/null 2>&1 && GH_CLI=1 || GH_CLI=0
which vercel >/dev/null 2>&1 && VERCEL_CLI=1 || VERCEL_CLI=0

header "Environment"
echo "GH CLI: $([ $GH_CLI -eq 1 ] && echo yes || echo no)"
echo "Vercel CLI: $([ $VERCEL_CLI -eq 1 ] && echo yes || echo no)"

# Step 1: Create GitHub repo (if gh available and authenticated)
header "Create GitHub repository"
if [ $GH_CLI -eq 1 ]; then
  if gh auth status >/dev/null 2>&1; then
    echo "Creating GitHub repo via gh..."
    gh repo create "${REPO_NAME}" --public --source "$LOCAL_ROOT" --remote origin --push || true
    echo "Repo created or already exists. Ensure branch 'fix/lint-security' was pushed:"
    echo "  git push -u origin fix/lint-security:main"
  else
    echo "gh present but not authenticated. Run: gh auth login"
    echo "Or run the following to create the repo using the GitHub web UI or a token:"
    echo "  gh repo create ${REPO_NAME} --public --source ${LOCAL_ROOT} --remote origin --push"
  fi
else
  echo "gh CLI not found. Please create a repo on GitHub named '${REPO_NAME}' and then run:" 
  echo "  git remote add origin https://github.com/YOUR-USERNAME/${REPO_NAME}.git"
  echo "  git push -u origin fix/lint-security:main"
fi

# Step 2: Deploy frontend to Vercel
header "Deploy frontend (webapp) to Vercel"
if [ $VERCEL_CLI -eq 1 ]; then
  echo "If not logged in, run: vercel login"
  echo "Then from this directory run:"
  echo "  vercel --cwd ${FRONTEND_DIR} --prod"
  echo "To set VITE_API_URL after backend is live:"
  echo "  vercel env add VITE_API_URL production https://<backend>.vercel.app"
else
  echo "Vercel CLI not found. You can deploy via the Vercel web UI:"
  echo "  1) Import the repo, choose root: webapp"
  echo "  2) Build command: npm run build, Output dir: dist"
fi

# Step 3: Create Vercel Postgres (manual step via web UI)
header "Provision Vercel Postgres"
echo "Go to Vercel dashboard → Storage → Create Database → Postgres → name 'expense-db'"

# Step 4: Deploy backend to Vercel
header "Deploy backend (ingestion_service) to Vercel"
if [ $VERCEL_CLI -eq 1 ]; then
  echo "Deploy backend with Vercel CLI:"
  echo "  vercel --cwd ${BACKEND_DIR} --prod"
  echo "Then link the Vercel Postgres instance in the dashboard to inject DATABASE_URL, and add env vars:"
  echo "  WEBHOOK_SECRET (generate with: openssl rand -hex 32)",
  echo "  CORS_ORIGINS = https://your-frontend.vercel.app"
else
  echo "Use the Vercel web UI to create a project from the repo with root 'ingestion_service'."
  echo "In project settings: set WEBHOOK_SECRET and CORS_ORIGINS, then connect the Postgres storage and redeploy."
fi

header "Done"

echo "If you want, run this script locally after installing gh and vercel and authenticating both CLIs. It will fast-track the steps above." 
