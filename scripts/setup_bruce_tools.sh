#!/usr/bin/env bash
# =============================================================================
# setup_bruce_tools.sh
# Give Bruce (OpenClaw agent) autonomous terminal, GitHub, and Vercel access.
#
# Usage:
#   sudo GITHUB_TOKEN=<pat> VERCEL_TOKEN=<token> bash scripts/setup_bruce_tools.sh
#
# Requirements:
#   - Run as root (sudo) — needs to write to /var/lib/openclaw/
#   - GITHUB_TOKEN: fine-grained PAT (Contents/Workflows/PRs/Issues R/W)
#   - VERCEL_TOKEN: Vercel full-account token
# =============================================================================

set -euo pipefail

# ── Paths ────────────────────────────────────────────────────────────────────
OC_HOME="/var/lib/openclaw"
OC_DIR="${OC_HOME}/.openclaw"
OC_BIN="${OC_HOME}/bin"
OC_CFG="${OC_DIR}/openclaw.json"
WORKSPACE="${OC_DIR}/workspace-bruce"
MEMORY_DIR="${WORKSPACE}/memory"
SKILLS_DIR="${WORKSPACE}/skills"
GH_CFG_DIR="${OC_HOME}/.config/gh"
VERCEL_TOKEN_FILE="${OC_HOME}/.vercel-token"
GIT_CREDS="${OC_HOME}/.git-credentials"
GITCONFIG="${OC_HOME}/.gitconfig"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${SCRIPT_DIR}/bruce-config"

# ── Check root ───────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
  echo "ERROR: This script must be run with sudo." >&2
  echo "Usage: sudo GITHUB_TOKEN=<pat> VERCEL_TOKEN=<token> bash $0" >&2
  exit 1
fi

# ── Check tokens ─────────────────────────────────────────────────────────────
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "ERROR: GITHUB_TOKEN is not set." >&2
  echo "Generate one at: github.com/settings/tokens → Fine-grained tokens" >&2
  exit 1
fi
if [[ -z "${VERCEL_TOKEN:-}" ]]; then
  echo "ERROR: VERCEL_TOKEN is not set." >&2
  echo "Generate one at: vercel.com/account/tokens" >&2
  exit 1
fi

echo "=== Bruce Tools Setup ==="
echo

# ── Detect GH and Vercel CLI paths ───────────────────────────────────────────
GH_BIN=""
for p in /opt/homebrew/bin/gh /usr/local/bin/gh /usr/bin/gh; do
  if [[ -x "$p" ]]; then GH_BIN="$p"; break; fi
done

VERCEL_BIN=""
for p in /usr/local/bin/vercel /opt/homebrew/bin/vercel /usr/bin/vercel; do
  if [[ -x "$p" ]]; then VERCEL_BIN="$p"; break; fi
done

# Install Vercel CLI globally if not found
if [[ -z "$VERCEL_BIN" ]]; then
  echo "→ Installing Vercel CLI via npm..."
  npm install -g vercel --quiet
  VERCEL_BIN="$(which vercel 2>/dev/null || echo '/usr/local/bin/vercel')"
  echo "  Vercel CLI installed at: ${VERCEL_BIN}"
else
  echo "✓ Vercel CLI found: ${VERCEL_BIN}"
fi

if [[ -z "$GH_BIN" ]]; then
  echo "ERROR: gh CLI not found. Install with: brew install gh" >&2
  exit 1
fi
echo "✓ GitHub CLI found: ${GH_BIN}"
echo

# ── Create wrappers in OC_BIN ────────────────────────────────────────────────
echo "→ Creating CLI wrappers in ${OC_BIN}/"

cat > "${OC_BIN}/gh-oc" <<WRAPPER
#!/bin/bash
export HOME=/var/lib/openclaw
export GIT_CONFIG_GLOBAL=/var/lib/openclaw/.gitconfig
exec ${GH_BIN} "\$@"
WRAPPER
chmod 755 "${OC_BIN}/gh-oc"
chown openclaw:staff "${OC_BIN}/gh-oc"
echo "  ✓ gh-oc"

cat > "${OC_BIN}/vercel-oc" <<WRAPPER
#!/bin/bash
export HOME=/var/lib/openclaw
export VERCEL_TOKEN="\$(cat /var/lib/openclaw/.vercel-token 2>/dev/null)"
exec ${VERCEL_BIN} "\$@"
WRAPPER
chmod 755 "${OC_BIN}/vercel-oc"
chown openclaw:staff "${OC_BIN}/vercel-oc"
echo "  ✓ vercel-oc"

# ── Store Vercel token ────────────────────────────────────────────────────────
echo "→ Storing Vercel token..."
printf '%s' "${VERCEL_TOKEN}" > "${VERCEL_TOKEN_FILE}"
chmod 600 "${VERCEL_TOKEN_FILE}"
chown root:staff "${VERCEL_TOKEN_FILE}"
echo "  ✓ Token stored at ${VERCEL_TOKEN_FILE}"

# ── Configure gh auth for OpenClaw user ──────────────────────────────────────
echo "→ Configuring GitHub CLI auth..."
mkdir -p "${GH_CFG_DIR}"
chown -R openclaw:staff "${GH_CFG_DIR}"

# Detect github username from token
GH_USER=$(HOME="${OC_HOME}" "${GH_BIN}" api user --header "Authorization: token ${GITHUB_TOKEN}" --jq '.login' 2>/dev/null || echo "porterpup")
echo "  GitHub user: ${GH_USER}"

cat > "${GH_CFG_DIR}/hosts.yml" <<GHCONFIG
github.com:
    oauth_token: ${GITHUB_TOKEN}
    git_protocol: https
    user: ${GH_USER}
GHCONFIG
chmod 600 "${GH_CFG_DIR}/hosts.yml"
chown openclaw:staff "${GH_CFG_DIR}/hosts.yml"
echo "  ✓ gh configured for ${GH_USER}"

# ── Store GitHub token in git credentials ────────────────────────────────────
echo "→ Storing GitHub token in git credentials..."
GH_CRED_LINE="https://${GH_USER}:${GITHUB_TOKEN}@github.com"
# Remove any existing github.com entry for this user, then append fresh
if [[ -f "${GIT_CREDS}" ]]; then
  # Strip existing github.com entries
  grep -v "github.com" "${GIT_CREDS}" > "${GIT_CREDS}.tmp" 2>/dev/null || true
  mv "${GIT_CREDS}.tmp" "${GIT_CREDS}"
fi
echo "${GH_CRED_LINE}" >> "${GIT_CREDS}"
chmod 600 "${GIT_CREDS}"
chown root:staff "${GIT_CREDS}"
echo "  ✓ git credentials updated"

# ── Add github.com to safe git directories ───────────────────────────────────
echo "→ Updating .gitconfig..."
# Add safe directory for Bruce's workspace if not already there
if ! grep -q "workspace-bruce" "${GITCONFIG}" 2>/dev/null; then
  cat >> "${GITCONFIG}" <<GITCFG

[safe]
	directory = /private/var/lib/openclaw/.openclaw/workspace-bruce
	directory = /private/var/lib/openclaw/.openclaw/workspace-bruce/expense-tracker
GITCFG
  echo "  ✓ Safe directories added"
else
  echo "  ✓ Safe directories already configured"
fi

# ── Patch openclaw.json to enable exec ───────────────────────────────────────
echo "→ Patching openclaw.json to enable exec tool..."
if [[ ! -f "${OC_CFG}" ]]; then
  echo "  WARNING: ${OC_CFG} not found — cannot auto-patch exec config." >&2
  echo "  You may need to enable exec manually in the OpenClaw app settings." >&2
else
  # Backup first
  cp "${OC_CFG}" "${OC_CFG}.bak.$(date +%Y%m%dT%H%M%S)"

  # Use python3 to patch JSON (jq may not be available)
  python3 - "${OC_CFG}" <<'PYEOF'
import json, sys, os

cfg_path = sys.argv[1]
with open(cfg_path, 'r') as f:
    raw = f.read()

# Try to parse (openclaw.json may be JSON5 with comments — strip // comments)
import re
cleaned = re.sub(r'//[^\n]*', '', raw)
cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)  # trailing commas

try:
    cfg = json.loads(cleaned)
except json.JSONDecodeError as e:
    print(f"  WARNING: Could not parse openclaw.json ({e}). Skipping exec patch.", file=sys.stderr)
    sys.exit(0)

# Set exec config
tools = cfg.setdefault('tools', {})
exec_cfg = tools.setdefault('exec', {})
exec_cfg['host'] = 'gateway'
exec_cfg['security'] = 'full'
exec_cfg['ask'] = 'off'

with open(cfg_path, 'w') as f:
    json.dump(cfg, f, indent=2)
print("  ✓ exec enabled (host=gateway, security=full, ask=off)")
PYEOF

  chown openclaw:staff "${OC_CFG}"
fi

# ── Create/update Bruce's workspace config files ──────────────────────────────
echo "→ Setting up Bruce's workspace files..."
mkdir -p "${WORKSPACE}" "${MEMORY_DIR}" "${SKILLS_DIR}"
chown -R openclaw:staff "${WORKSPACE}"

# AGENTS.md — append our tools section if not already present
AGENTS_FILE="${WORKSPACE}/AGENTS.md"
AGENTS_MARKER="## Tools Available to Bruce"
if [[ -f "${AGENTS_FILE}" ]]; then
  if grep -q "${AGENTS_MARKER}" "${AGENTS_FILE}" 2>/dev/null; then
    echo "  ✓ AGENTS.md already has tools section — skipping"
  else
    echo "" >> "${AGENTS_FILE}"
    cat "${CONFIG_DIR}/AGENTS_append.md" >> "${AGENTS_FILE}"
    echo "  ✓ AGENTS.md updated (tools section appended)"
  fi
else
  cp "${CONFIG_DIR}/AGENTS_append.md" "${AGENTS_FILE}"
  echo "  ✓ AGENTS.md created"
fi
chown openclaw:staff "${AGENTS_FILE}"

# TOOLS.md — overwrite (this is environment-specific, safe to replace)
cp "${CONFIG_DIR}/TOOLS.md" "${WORKSPACE}/TOOLS.md"
chown openclaw:staff "${WORKSPACE}/TOOLS.md"
echo "  ✓ TOOLS.md installed"

# Vercel skill
mkdir -p "${SKILLS_DIR}/vercel"
cp "${CONFIG_DIR}/skills/vercel/SKILL.md" "${SKILLS_DIR}/vercel/SKILL.md"
chown -R openclaw:staff "${SKILLS_DIR}"
echo "  ✓ Vercel skill installed"

# ── Clone expense-tracker repo into Bruce's workspace if not present ──────────
REPO_DIR="${WORKSPACE}/expense-tracker"
if [[ ! -d "${REPO_DIR}/.git" ]]; then
  echo "→ Cloning expense-tracker into Bruce's workspace..."
  HOME="${OC_HOME}" GIT_CONFIG_GLOBAL="${GITCONFIG}" \
    git clone "https://github.com/porterpup/expense-tracker.git" "${REPO_DIR}" 2>&1 | sed 's/^/  /'
  chown -R openclaw:staff "${REPO_DIR}"
  echo "  ✓ Repo cloned to ${REPO_DIR}"
else
  echo "  ✓ expense-tracker repo already present — pulling latest..."
  HOME="${OC_HOME}" GIT_CONFIG_GLOBAL="${GITCONFIG}" \
    git -C "${REPO_DIR}" pull --quiet origin HEAD 2>&1 | sed 's/^/  /' || true
fi

# ── Restart OpenClaw gateway to pick up config changes ───────────────────────
echo "→ Reloading OpenClaw gateway..."
OC_PLIST="/var/lib/openclaw/Library/LaunchAgents/ai.openclaw.gateway.plist"
if [[ -f "${OC_PLIST}" ]]; then
  # Unload and reload as the openclaw user
  launchctl unload "${OC_PLIST}" 2>/dev/null || true
  sleep 1
  launchctl load "${OC_PLIST}" 2>/dev/null || true
  echo "  ✓ Gateway reloaded"
else
  echo "  NOTE: Could not find LaunchAgent plist. Restart OpenClaw manually." >&2
fi

# ── Verify ───────────────────────────────────────────────────────────────────
echo
echo "=== Verification ==="
echo -n "  gh-oc auth: "
HOME="${OC_HOME}" "${GH_BIN}" auth status 2>&1 | grep -E "Logged in|Token" | head -1 || echo "check manually"

echo -n "  vercel-oc auth: "
VERCEL_TOKEN="$(cat ${VERCEL_TOKEN_FILE})" "${VERCEL_BIN}" whoami 2>/dev/null || echo "check manually"

echo -n "  git credentials: "
grep -c "github.com" "${GIT_CREDS}" 2>/dev/null && echo "github.com entry present" || echo "WARNING: missing"

echo
echo "=== Done! ==="
echo "Bruce now has:"
echo "  ✓ Terminal (exec tool, host=gateway, security=full)"
echo "  ✓ GitHub CLI (gh-oc) authenticated as ${GH_USER}"
echo "  ✓ Vercel CLI (vercel-oc) with token"
echo "  ✓ git push credentials for github.com"
echo "  ✓ Vercel skill in workspace-bruce"
echo "  ✓ expense-tracker repo cloned into Bruce's workspace"
echo
echo "Next: Open OpenClaw and tell Bruce to test with:"
echo "  gh-oc repo list && vercel-oc ls"
