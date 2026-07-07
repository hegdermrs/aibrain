"""
Background poller — an OPTIONAL email-ingestion FALLBACK.

Division of labor: Hermes (on Jim's Mac) is the workhorse that reads email,
calendar, Skool, and calls, and pushes them to the Brain. The Brain is the
decision-maker and does not normally gather data itself.

This poller exists only as a bootstrap/fallback: for the cloud-only path, or
before Hermes is wired up, the Brain can pull Fathom call emails over IMAP so
call summaries work day one. It is OFF unless the email env vars are set —
leave them unset and the Brain gathers nothing; Hermes does all reading.

When enabled, each tick checks the inbox for new Fathom call emails, turns
each into a transcript, analyzes it, and delivers the summary to Telegram.

Config (env):
  EMAIL_IMAP_HOST      default imap.gmail.com
  EMAIL_ADDRESS        the mailbox to read
  EMAIL_APP_PASSWORD   an app password (Gmail: Account → App passwords)
  FATHOM_FROM          sender substring to match (default "fathom")
  EMAIL_POLL_MINUTES   interval (default 15)

Unconfigured → graceful no-op. Any failure is caught so a bad tick never
takes the server down.
"""

from __future__ import annotations

import email
import imaplib
import os
from datetime import datetime, timezone
from email.message import Message

from brain.analyst import analyze_transcript
from brain.delivery import queue_and_deliver
from brain.formatting import format_analysis
from brain.models import CallTranscript
from brain.outbox import OutgoingMessage


def is_configured() -> bool:
    return bool(os.environ.get("EMAIL_ADDRESS")
                and os.environ.get("EMAIL_APP_PASSWORD"))


def poll_minutes() -> int:
    try:
        return max(2, int(os.environ.get("EMAIL_POLL_MINUTES", "15")))
    except ValueError:
        return 15


def _body_text(msg: Message) -> str:
    """Prefer text/plain; fall back to a naive strip of text/html."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True) or b""
                return payload.decode(part.get_content_charset() or "utf-8",
                                      errors="replace")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True) or b""
                html = payload.decode(part.get_content_charset() or "utf-8",
                                      errors="replace")
                return _strip_html(html)
        return ""
    payload = msg.get_payload(decode=True) or b""
    return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")


def _strip_html(html: str) -> str:
    import re
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+\n", "\n", text).strip()


def poll_email() -> dict:
    """One poll tick. Returns a small summary dict; never raises."""
    if not is_configured():
        return {"polled": False, "reason": "email not configured"}

    host = os.environ.get("EMAIL_IMAP_HOST", "imap.gmail.com")
    addr = os.environ["EMAIL_ADDRESS"]
    pw = os.environ["EMAIL_APP_PASSWORD"]
    sender = os.environ.get("FATHOM_FROM", "fathom")

    processed = 0
    try:
        M = imaplib.IMAP4_SSL(host)
        M.login(addr, pw)
        M.select("INBOX")
        # Unread mail from the Fathom sender.
        typ, data = M.search(None, "UNSEEN", "FROM", f'"{sender}"')
        if typ == "OK":
            for num in data[0].split():
                typ, msgdata = M.fetch(num, "(RFC822)")
                if typ != "OK" or not msgdata or not msgdata[0]:
                    continue
                msg = email.message_from_bytes(msgdata[0][1])
                subject = str(email.header.make_header(
                    email.header.decode_header(msg.get("Subject", "Call"))))
                body = _body_text(msg)
                if not body.strip():
                    continue

                transcript = CallTranscript(
                    id=(msg.get("Message-ID") or f"email_{num.decode()}").strip("<> "),
                    title=subject or "Fathom call",
                    date=datetime.now(timezone.utc),
                    participants=[],
                    segments=[],
                    full_text=body,
                    source="fathom-email",
                    duration_minutes=0.0,
                )
                analysis = analyze_transcript(transcript)
                queue_and_deliver(OutgoingMessage(
                    kind="analysis",
                    title=f"Call analysis: {analysis.call_title}",
                    text=format_analysis(analysis),
                    source_ref=transcript.id,
                    meta={"follow_ups": len(analysis.follow_ups)},
                ))
                M.store(num, "+FLAGS", "\\Seen")  # don't reprocess
                processed += 1
        M.logout()
        return {"polled": True, "processed": processed}
    except Exception as e:
        # Never let a bad tick crash the scheduler.
        return {"polled": True, "processed": processed, "error": str(e)}
