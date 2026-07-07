"""
Direct Telegram delivery.

Jim already has Telegram set up, so the Brain sends results straight to his
chat via the Bot API — no Hermes hop for delivery. Hermes' job shrinks to
*ingestion* (reading Skool/email/calls and posting them in).

Config (env):
  TELEGRAM_BOT_TOKEN  — from @BotFather
  TELEGRAM_CHAT_ID    — Jim's chat id (the bot learns it when Jim taps Start)

If either is missing, send is a graceful no-op and the message stays in the
outbox for a fallback puller — nothing breaks.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def _config() -> tuple[str | None, str | None]:
    return (os.environ.get("TELEGRAM_BOT_TOKEN"),
            os.environ.get("TELEGRAM_CHAT_ID"))


def is_configured() -> bool:
    token, chat = _config()
    return bool(token and chat)


def send_message(text: str, chat_id: str | None = None) -> bool:
    """Send `text` to Telegram. Returns True on success.

    Tries Telegram Markdown first; if the body has characters Telegram's
    parser rejects (a 400), retries as plain text so delivery still happens.
    """
    token, default_chat = _config()
    chat = chat_id or default_chat
    if not token or not chat:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for parse_mode in ("Markdown", None):
        payload = {
            "chat_id": chat,
            "text": text,
            "disable_web_page_preview": True,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = json.loads(r.read() or b"{}")
                if body.get("ok"):
                    return True
        except urllib.error.HTTPError:
            # Likely a Markdown parse error — fall through to plain text.
            continue
        except Exception:
            return False
    return False
