#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'USAGE'
Usage: install_bruce_to_server.sh --host user@host [options]

Options:
  --host HOST                Remote host (user@host) to copy files to (required)
  --ndjson PATH              Local NDJSON file (default: data/bruce_export.ndjson)
  --sqlite PATH              Local SQLite DB file (optional)
  --oc-dir PATH              Remote OC_DIR (default: /var/lib/openclaw/.openclaw)
  --workspace NAME           Workspace name inside OC_DIR (default: workspace-bruce)
  --remote-ndjson NAME       Remote NDJSON filename to place in memory dir (default: bruce.ndjson)
  --remote-sqlite NAME       Remote SQLite filename (default: bruce_memory.sqlite3)
  --yes                      Non-interactive: proceed without confirmation
  -h, --help                 Show this help

Examples:
  ./install_bruce_to_server.sh --host sean@server.example.com --ndjson data/bruce_export.ndjson --sqlite data/brue_memory.sqlite3 --oc-dir /var/lib/openclaw/.openclaw --workspace workspace-bruce

Description:
  This script securely copies the NDJSON (and optional SQLite) to a temporary directory on the remote host,
  backs up any existing memory files in the target OpenClaw workspace memory directory, and atomically
  moves the new files into place using sudo. It leaves a .bak.TIMESTAMP copy of any overwritten files.

USAGE
}

# Defaults
HOST=""
NDJSON="data/bruce_export.ndjson"
SQLITE=""
OC_DIR="/var/lib/openclaw/.openclaw"
WORKSPACE="workspace-bruce"
REMOTE_NDJSON_NAME="bruce.ndjson"
REMOTE_SQLITE_NAME="bruce_memory.sqlite3"
YES=0

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="$2"; shift 2;;
    --ndjson) NDJSON="$2"; shift 2;;
    --sqlite) SQLITE="$2"; shift 2;;
    --oc-dir) OC_DIR="$2"; shift 2;;
    --workspace) WORKSPACE="$2"; shift 2;;
    --remote-ndjson) REMOTE_NDJSON_NAME="$2"; shift 2;;
    --remote-sqlite) REMOTE_SQLITE_NAME="$2"; shift 2;;
    --yes) YES=1; shift;;
    -h|--help) print_usage; exit 0;;
    *) echo "Unknown arg: $1"; print_usage; exit 1;;
  esac
done

if [[ -z "$HOST" ]]; then
  echo "--host is required"
  print_usage
  exit 1
fi

if [[ ! -f "$NDJSON" ]]; then
  echo "Local NDJSON not found: $NDJSON" >&2
  exit 2
fi

if [[ -n "$SQLITE" && ! -f "$SQLITE" ]]; then
  echo "Local SQLite not found: $SQLITE" >&2
  exit 2
fi

echo "Remote host: $HOST"
echo "OC_DIR: $OC_DIR"
echo "Workspace: $WORKSPACE"
echo "Local NDJSON: $NDJSON"
if [[ -n "$SQLITE" ]]; then
  echo "Local SQLite: $SQLITE"
else
  echo "Local SQLite: (none)"
fi

if [[ $YES -ne 1 ]]; then
  read -r -p "Proceed with copying and installing these files to $HOST? [y/N] " resp
  case "$resp" in
    [yY][eE][sS]|[yY]) ;;
    *) echo "Aborted"; exit 0;;
  esac
fi

TS=$(date -u +%Y%m%dT%H%M%SZ)
REMOTE_TMP="/tmp/bruce_import_${TS}_$RANDOM"

# Create remote temp dir
echo "Creating remote temp dir: $REMOTE_TMP"
ssh "$HOST" "mkdir -p '$REMOTE_TMP'"

# Copy files to remote temp
echo "Copying NDJSON to remote..."
scp -q "$NDJSON" "$HOST:$REMOTE_TMP/$REMOTE_NDJSON_NAME"

if [[ -n "$SQLITE" ]]; then
  echo "Copying SQLite to remote..."
  scp -q "$SQLITE" "$HOST:$REMOTE_TMP/$REMOTE_SQLITE_NAME"
fi

# Perform atomic install on remote host (with sudo to write into OC_DIR)
echo "Running remote install steps (may prompt for sudo password)..."
ssh "$HOST" bash -s <<EOF
set -euo pipefail
TS="$TS"
REMOTE_TMP="$REMOTE_TMP"
OC_DIR="$OC_DIR"
WORKSPACE="$WORKSPACE"
REMOTE_NDJSON_NAME="$REMOTE_NDJSON_NAME"
REMOTE_SQLITE_NAME="$REMOTE_SQLITE_NAME"
SQLITE_PROVIDED=$([[ -n "$SQLITE" ]] && echo 1 || echo 0)

MEMORY_DIR="$OC_DIR/$WORKSPACE/memory"

sudo mkdir -p "$MEMORY_DIR"
# Backup existing NDJSON
if [ -f "$MEMORY_DIR/$REMOTE_NDJSON_NAME" ]; then
  sudo cp -a "$MEMORY_DIR/$REMOTE_NDJSON_NAME" "$MEMORY_DIR/$REMOTE_NDJSON_NAME.bak.$TS"
  echo "Backed up existing $REMOTE_NDJSON_NAME"
fi
# Move new NDJSON into place
if [ -f "$REMOTE_TMP/$REMOTE_NDJSON_NAME" ]; then
  sudo mv "$REMOTE_TMP/$REMOTE_NDJSON_NAME" "$MEMORY_DIR/$REMOTE_NDJSON_NAME"
  echo "Installed $REMOTE_NDJSON_NAME"
else
  echo "Warning: expected $REMOTE_NDJSON_NAME not found in $REMOTE_TMP" >&2
fi

if [ "$SQLITE_PROVIDED" -eq 1 ]; then
  if [ -f "$MEMORY_DIR/$REMOTE_SQLITE_NAME" ]; then
    sudo cp -a "$MEMORY_DIR/$REMOTE_SQLITE_NAME" "$MEMORY_DIR/$REMOTE_SQLITE_NAME.bak.$TS"
    echo "Backed up existing $REMOTE_SQLITE_NAME"
  fi
  if [ -f "$REMOTE_TMP/$REMOTE_SQLITE_NAME" ]; then
    sudo mv "$REMOTE_TMP/$REMOTE_SQLITE_NAME" "$MEMORY_DIR/$REMOTE_SQLITE_NAME"
    echo "Installed $REMOTE_SQLITE_NAME"
  else
    echo "Warning: expected $REMOTE_SQLITE_NAME not found in $REMOTE_TMP" >&2
  fi
fi

# Cleanup temp
sudo rm -rf "$REMOTE_TMP"

echo "Remote install complete. Files placed in: $MEMORY_DIR"
EOF

echo "Done. Verify OpenClaw loads the restored memory (restart service if needed)."

exit 0
