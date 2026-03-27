# Importing Bruce Export

This document explains how to use tools/import_bruce_export.py to convert a plain-text Bruce conversation export into NDJSON for ingestion into OpenClaw.

Usage

- Convert the pasted export to NDJSON:

  python3 tools/import_bruce_export.py /path/to/paste.txt /path/to/output.ndjson

- Defaults:
  - Input: the pasted export saved at /Users/seanbutton/.copilot/session-state/.../paste-*.txt
  - Output: data/bruce_export.ndjson (relative to repository root)

Next steps

- Review the NDJSON for PII and sensitive content before ingesting into production memory.
- To restore into OpenClaw (server): copy the NDJSON into the OpenClaw workspace memory directory, e.g.:

  sudo cp /path/to/output.ndjson /var/lib/openclaw/.openclaw/workspace-bruce/memory/bruce.ndjson

- Alternatively, adapt the import script to write directly into your OpenClaw memory store or vector DB.

Privacy

- Confirm you have the right to ingest these conversations. Remove or redact any PII before moving to production.

