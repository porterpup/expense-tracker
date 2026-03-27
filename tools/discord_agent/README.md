Discord agent helper

This folder contains a minimal helper script (discord_agent.py) that posts parsed expense JSON to the ingestion webhook with an HMAC signature. When WEBHOOK_SECRET is set, the helper sends X-Timestamp and X-Signature headers and signs payloads using HMAC(secret, "<timestamp>.<body>") for replay protection.

For a full Discord bot:
- Use discord.py (pip install discord.py)
- Create a bot and listen for messages or DMs containing attachments
- Download the attachment, run OCR/LLM parsing, then POST the parsed JSON to the ingestion webhook (see discord_agent.py for signing example)
- Reply to the user in Discord with a confirmation or link to the PWA view

Example local usage:

1) Start the ingestion service:
   uvicorn ingestion_service.main:app --reload --port 8000

2) Post a sample expense:
   export WEBHOOK_SECRET=changeme
   python discord_agent.py --webhook http://localhost:8000/webhook/ingest --merchant "Starbucks" --date 2026-03-27 --amount 4.25

