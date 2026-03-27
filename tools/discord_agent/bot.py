#!/usr/bin/env python3
"""
Discord bot that accepts image attachments (receipts), runs OCR (pytesseract),
parses merchant/date/amount using simple heuristics, and POSTs parsed JSON to
an ingestion webhook (see AGENT_WEBHOOK_URL). Signs payload with WEBHOOK_SECRET
if configured.

Run:
  export DISCORD_TOKEN=<bot token>
  export AGENT_WEBHOOK_URL=http://localhost:8000/webhook/ingest
  export WEBHOOK_SECRET=changeme
  python tools/discord_agent/bot.py

Notes:
- Requires system tesseract installation (apt install tesseract-ocr or brew install tesseract)
- Install python deps: pip install -r tools/discord_agent/requirements.txt
"""
import os
import io
import re
import json
import hmac
import hashlib
import logging
from typing import Optional
from datetime import datetime
import time

from PIL import Image
import pytesseract
import aiohttp
import discord
from discord.ext import commands

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord-agent")

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AGENT_WEBHOOK_URL = os.getenv("AGENT_WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

if not DISCORD_TOKEN:
    logger.error("DISCORD_TOKEN is not set. Exiting.")
    raise SystemExit("Set DISCORD_TOKEN environment variable and restart")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


def sign_payload(payload_bytes: bytes, secret: str, timestamp: int = None) -> str:
    """Sign payload. If timestamp is provided, sign using '<timestamp>.<body>' to enable replay protection."""
    if timestamp is None:
        return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.new(secret.encode("utf-8"), str(timestamp).encode("utf-8") + b"." + payload_bytes, hashlib.sha256).hexdigest()


def extract_amount(text: str) -> Optional[float]:
    # Find dollar amounts with two decimals
    matches = re.findall(r"(?:\$|USD\s*)?([0-9]+(?:[.,][0-9]{2}))", text)
    if matches:
        nums = []
        for m in matches:
            try:
                val = float(m.replace(",", "."))
                nums.append(val)
            except Exception:
                continue
        if nums:
            # Heuristic: choose the largest value (likely the total)
            return max(nums)
    # Fallback: find any integer number > 0
    matches = re.findall(r"([0-9]+(?:[.,][0-9]{0,2}))", text)
    nums = []
    for m in matches:
        try:
            val = float(m.replace(",", "."))
            nums.append(val)
        except Exception:
            continue
    return max(nums) if nums else None


def extract_date(text: str) -> Optional[str]:
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{2}/\d{2}/\d{4})",
        r"(\d{1,2}/\d{1,2}/\d{2,4})",
        r"([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            ds = m.group(1)
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y", "%B %d, %Y", "%m/%d/%y"):
                try:
                    dt = datetime.strptime(ds, fmt)
                    return dt.date().isoformat()
                except Exception:
                    continue
            # If parsing failed, try to normalize simple mm/dd/yy
            try:
                parts = re.split(r"[ /-]", ds)
                if len(parts) >= 3:
                    y = parts[-1]
                    m = parts[0]
                    d = parts[1]
                    if len(y) == 2:
                        y = "20" + y
                    dt = datetime(int(y), int(m), int(d))
                    return dt.date().isoformat()
            except Exception:
                pass
    return None


def extract_merchant(text: str) -> Optional[str]:
    # Heuristic: first non-empty line that looks like a name
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines[:5]:
        # skip lines that look like dates or amounts
        if re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", ln):
            continue
        if re.search(r"\$|USD|AMOUNT|TOTAL|SUBTOTAL|TAX", ln, flags=re.I):
            continue
        if len(ln) >= 2:
            return ln
    return lines[0] if lines else None


async def post_to_webhook(payload: dict) -> dict:
    if not AGENT_WEBHOOK_URL:
        raise RuntimeError("AGENT_WEBHOOK_URL not configured")
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if WEBHOOK_SECRET:
        ts = int(time.time())
        headers["X-Timestamp"] = str(ts)
        headers["X-Signature"] = sign_payload(data, WEBHOOK_SECRET, ts)
    async with aiohttp.ClientSession() as session:
        async with session.post(AGENT_WEBHOOK_URL, data=data, headers=headers, timeout=10) as resp:
            text = await resp.text()
            try:
                return {"status": resp.status, "body": await resp.json()}
            except Exception:
                return {"status": resp.status, "body_text": text}


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (id={bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    # Ignore bot messages
    if message.author.bot:
        return
    # Process attachments
    if message.attachments:
        await message.channel.typing()
        results = []
        for att in message.attachments:
            # Only attempt images
            if att.content_type and not att.content_type.startswith("image"):
                continue
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(att.url) as resp:
                        img_bytes = await resp.read()
                image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                try:
                    ocr_text = pytesseract.image_to_string(image)
                except Exception:
                    ocr_text = ""
                    logger.exception("pytesseract failed")

                merchant = extract_merchant(ocr_text) or "unknown"
                date = extract_date(ocr_text) or None
                amount = extract_amount(ocr_text) or None

                payload = {
                    "merchant": merchant,
                    "date": date or datetime.utcnow().date().isoformat(),
                    "amount": float(amount) if amount is not None else 0.0,
                    "currency": "USD",
                    "category": None,
                    "raw_text": ocr_text,
                    "source": "discord_agent",
                }

                try:
                    resp = await post_to_webhook(payload)
                    if resp.get("status") and 200 <= resp["status"] < 300:
                        body = resp.get("body") or {}
                        saved_id = body.get("id") if isinstance(body, dict) else None
                        results.append((True, saved_id))
                    else:
                        results.append((False, resp))
                except Exception as e:
                    logger.exception("Failed to post to webhook")
                    results.append((False, str(e)))

            except Exception:
                logger.exception("Failed processing attachment")
                results.append((False, "processing error"))

        # Reply with summary
        lines = []
        for ok, info in results:
            if ok:
                lines.append(f"Ingested expense (id={info})")
            else:
                lines.append(f"Failed to ingest: {info}")
        if not lines:
            lines = ["No image attachments processed."]
        await message.reply("\n".join(lines))

    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
