#!/usr/bin/env python3
"""
Import script for Bruce plain-text export -> canonical NDJSON
Optionally installs NDJSON and a SQLite memory DB into an OpenClaw OC_DIR workspace.

Usage:
  python3 tools/import_bruce_export.py [INPUT_FILE] --ndjson-out out.ndjson --oc-dir /path/to/oc_dir --workspace workspace-bruce --create-sqlite

"""
import argparse
import re
import sys
import json
import uuid
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DEFAULT_INPUT = Path('/Users/seanbutton/.copilot/session-state/c4074bc8-1d39-45c9-ab6f-3696dfe7ae38/files/paste-1774458116223.txt')

MSG_HEAD_RE = re.compile(r"^(?P<author>\S+)(?P<ts>[A-Za-z]{3} [A-Za-z]{3} \d{2} \d{4} \d{2}:\d{2}:\d{2} GMT[+-]\d{4} \([^\)]+\))$")


def parse_timestamp(ts_str):
    try:
        m = re.search(r"([A-Za-z]{3} [A-Za-z]{3} \d{2} \d{4} \d{2}:\d{2}:\d{2}) GMT([+-]\d{4})", ts_str)
        if m:
            dt_str = m.group(1)
            tz = m.group(2)
            dt = datetime.strptime(dt_str, '%a %b %d %Y %H:%M:%S')
            sign = 1 if tz.startswith('+') else -1
            hours = int(tz[1:3])
            minutes = int(tz[3:5])
            offset_seconds = sign * (hours*3600 + minutes*60)
            dt_utc = dt - timedelta(seconds=offset_seconds)
            return dt_utc.replace(microsecond=0).isoformat() + 'Z'
    except Exception:
        return None


def parse_transcript(lines):
    msgs = []
    cur = None
    idx = 0
    for line in lines:
        idx += 1
        ln = line.rstrip('\n')
        if not ln.strip():
            if cur and cur.get('text'):
                cur['original_index'] = idx
                msgs.append(cur)
                cur = None
            continue
        m = MSG_HEAD_RE.match(ln)
        if m:
            if cur:
                cur['original_index'] = idx
                msgs.append(cur)
            cur = {
                'message_id': str(uuid.uuid4()),
                'author_raw': m.group('author'),
                'author': m.group('author'),
                'timestamp_raw': m.group('ts'),
                'timestamp': parse_timestamp(m.group('ts')),
                'text': ''
            }
            continue
        if cur is None:
            # start a synthetic message
            cur = {
                'message_id': str(uuid.uuid4()),
                'author_raw': 'unknown',
                'author': 'unknown',
                'timestamp_raw': None,
                'timestamp': None,
                'text': ln
            }
            continue
        if cur['text']:
            cur['text'] += '\n' + ln
        else:
            cur['text'] = ln
    if cur:
        cur['original_index'] = idx
        msgs.append(cur)
    return msgs


def write_ndjson(path: Path, msgs):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as out:
        for m in msgs:
            out.write(json.dumps(m, ensure_ascii=False) + '\n')


def backup_if_exists(path: Path):
    if path.exists():
        stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        bak = path.with_suffix(path.suffix + f'.bak.{stamp}')
        shutil.copy2(path, bak)
        print(f'Backed up existing {path} -> {bak}')


def install_to_oc_dir(oc_dir: Path, workspace: str, msgs, ndjson_name='bruce.ndjson', sqlite_name='bruce_memory.sqlite3', backup=True):
    workspace_dir = oc_dir / workspace / 'memory'
    workspace_dir.mkdir(parents=True, exist_ok=True)
    ndjson_path = workspace_dir / ndjson_name
    if backup and ndjson_path.exists():
        backup_if_exists(ndjson_path)
    write_ndjson(ndjson_path, msgs)
    print(f'Installed NDJSON to {ndjson_path}')
    if sqlite_name:
        db_path = workspace_dir / sqlite_name
        if backup and db_path.exists():
            backup_if_exists(db_path)
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                author TEXT,
                author_raw TEXT,
                timestamp_raw TEXT,
                timestamp TEXT,
                text TEXT,
                original_index INTEGER
            )
        ''')
        insert_rows = []
        for i, m in enumerate(msgs):
            insert_rows.append((m.get('message_id'), m.get('author'), m.get('author_raw'), m.get('timestamp_raw'), m.get('timestamp'), m.get('text'), m.get('original_index', i)))
        c.executemany('INSERT OR REPLACE INTO messages VALUES (?,?,?,?,?,?,?)', insert_rows)
        conn.commit()
        conn.close()
        print(f'Created SQLite DB with {len(insert_rows)} messages at {db_path}')
    return ndjson_path


def main():
    p = argparse.ArgumentParser(description='Import Bruce text export to NDJSON and optionally install to OC_DIR')
    p.add_argument('input', nargs='?', default=str(DEFAULT_INPUT), help='Path to pasted export')
    p.add_argument('--ndjson-out', '-o', default='data/bruce_export.ndjson', help='Local NDJSON output path')
    p.add_argument('--oc-dir', default=None, help='OpenClaw OC_DIR path to install memory into')
    p.add_argument('--workspace', default='workspace-bruce', help='Workspace name inside OC_DIR')
    p.add_argument('--create-sqlite', action='store_true', help='Also create a SQLite memory DB alongside NDJSON')
    p.add_argument('--sqlite-name', default='bruce_memory.sqlite3', help='SQLite filename to create in workspace memory dir')
    p.add_argument('--backup-existing', action='store_true', help='Backup existing files before overwriting')
    args = p.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f'Input file not found: {input_path}', file=sys.stderr)
        sys.exit(2)

    with input_path.open('r', encoding='utf-8') as f:
        lines = f.readlines()
    msgs = parse_transcript(lines)

    ndjson_out = Path(args.ndjson_out)
    write_ndjson(ndjson_out, msgs)
    print(f'Wrote {len(msgs)} messages to {ndjson_out}')

    if args.oc_dir:
        oc_dir = Path(args.oc_dir)
        install_to_oc_dir(oc_dir, args.workspace, msgs, ndjson_name='bruce.ndjson' if not ndjson_out.name else ndjson_out.name, sqlite_name=(args.sqlite_name if args.create_sqlite else None), backup=args.backup_existing)

    print('Done')

if __name__ == '__main__':
    main()
