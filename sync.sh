#!/bin/bash
# Sync agent output files to Sean's Documents
# Run as: sudo bash ~/Documents/AgentOutput/sync.sh
set -euo pipefail

OC_DIR="/var/lib/openclaw/.openclaw"
DEST="/Users/seanbutton/Documents/AgentOutput"

total=0
for swarm in flyrely 3cv grantdrive personal bruce; do
    SRC="$OC_DIR/workspace-$swarm/output"
    if [ -d "$SRC" ]; then
        files=( "$SRC"/* )
        # Check glob actually matched something
        if [ -e "${files[0]}" ]; then
            count=${#files[@]}
            cp -f "${files[@]}" "$DEST/$swarm/"
            chown seanbutton:staff "$DEST/$swarm/"*
            echo "  $swarm: synced $count file(s)"
            total=$((total + count))
        fi
    fi
done

if [ "$total" -eq 0 ]; then
    echo "  No new files to sync."
else
    echo "  Total: $total file(s) synced."
fi
echo "Done. Files in: $DEST"
