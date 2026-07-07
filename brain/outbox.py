"""
Outbox — Brain's outgoing message queue.

Brain stays a pure thinking layer: it never sends anything itself.
When Brain produces a result it wants delivered to Jim (a briefing,
a call analysis, an alert), it drops a message into the outbox.

Hermes polls GET /outgoing/pending, delivers each to Jim (Telegram,
etc.), then POSTs /outgoing/{id}/ack to mark it delivered.

Storage: one JSON file per message under data/outgoing/. File-based
so it survives restarts and is easy to inspect. Delivered messages
are kept (acked) for history/audit, not deleted.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field


OutKind = Literal["briefing", "analysis", "alert"]


class OutgoingMessage(BaseModel):
    """A delivery-ready payload Brain hands to Hermes."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    kind: OutKind
    channel: str = "telegram"          # where Hermes should deliver it
    recipient: str = "jim"             # logical recipient; Hermes maps to chat id
    title: str
    text: str                          # ready-to-send body (Telegram markdown)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delivered: bool = False
    delivered_at: Optional[datetime] = None
    source_ref: Optional[str] = None   # e.g. transcript id or briefing filename
    meta: dict = Field(default_factory=dict)


class Outbox:
    """File-based queue of OutgoingMessages."""

    def __init__(self, outgoing_dir: str | None = None):
        base = outgoing_dir or os.environ.get(
            "BRAIN_OUTGOING_DIR", "./data/outgoing"
        )
        self.dir = Path(base)
        self.dir.mkdir(parents=True, exist_ok=True)

    # ── Write ────────────────────────────────────────────────────────────────

    def enqueue(self, message: OutgoingMessage) -> OutgoingMessage:
        """Persist a message to the outbox."""
        path = self.dir / f"out_{message.id}.json"
        path.write_text(
            json.dumps(message.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
        return message

    # ── Read ─────────────────────────────────────────────────────────────────

    def _load(self, path: Path) -> Optional[OutgoingMessage]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return OutgoingMessage(**data)
        except Exception:
            return None

    def get(self, message_id: str) -> Optional[OutgoingMessage]:
        path = self.dir / f"out_{message_id}.json"
        if not path.exists():
            return None
        return self._load(path)

    def list_pending(self) -> list[OutgoingMessage]:
        """Undelivered messages, oldest first (delivery order)."""
        msgs = []
        for path in self.dir.glob("out_*.json"):
            msg = self._load(path)
            if msg and not msg.delivered:
                msgs.append(msg)
        msgs.sort(key=lambda m: m.created_at)
        return msgs

    def list_all(self, limit: int = 100) -> list[OutgoingMessage]:
        """All messages, newest first."""
        msgs = []
        for path in self.dir.glob("out_*.json"):
            msg = self._load(path)
            if msg:
                msgs.append(msg)
        msgs.sort(key=lambda m: m.created_at, reverse=True)
        return msgs[:limit]

    # ── Acknowledge ──────────────────────────────────────────────────────────

    def ack(self, message_id: str) -> Optional[OutgoingMessage]:
        """Mark a message delivered. Returns the updated message, or None."""
        msg = self.get(message_id)
        if msg is None:
            return None
        msg.delivered = True
        msg.delivered_at = datetime.now(timezone.utc)
        return self.enqueue(msg)  # overwrite same file
