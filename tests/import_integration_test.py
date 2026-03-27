#!/usr/bin/env python3
"""
Integration test for import_bruce_export.py
Run: python3 tests/import_integration_test.py
"""
import subprocess
import json
import sys
from pathlib import Path

SCRIPT = Path.cwd() / "tools" / "import_bruce_export.py"
INPUT = Path("/Users/seanbutton/.copilot/session-state/c4074bc8-1d39-45c9-ab6f-3696dfe7ae38/files/paste-1774458116223.txt")
OUT = Path("tests/tmp_bruexport.ndjson")


def main():
    if not SCRIPT.exists():
        print(f"Missing script: {SCRIPT}", file=sys.stderr)
        return 2
    if not INPUT.exists():
        print(f"Missing input: {INPUT}", file=sys.stderr)
        return 2
    if OUT.exists():
        OUT.unlink()
    print("Running import script...")
    res = subprocess.run(["python3", str(SCRIPT), str(INPUT), str(OUT)], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
        return res.returncode
    if not OUT.exists():
        print("Output file not created", file=sys.stderr)
        return 1
    lines = OUT.read_text(encoding='utf-8').splitlines()
    print(f"Wrote {len(lines)} lines to {OUT}")
    if len(lines) < 300:
        print("Parsed too few messages", file=sys.stderr)
        return 1
    first = json.loads(lines[0])
    if 'text' not in first:
        print("First message missing text", file=sys.stderr)
        return 1
    print("Test passed")
    return 0

if __name__ == '__main__':
    sys.exit(main())
