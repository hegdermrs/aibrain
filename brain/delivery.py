"""
Delivery — the single path for getting a finished result to Jim.

Save to the outbox (audit trail), then send to Telegram directly if it's
configured. Shared by the webhook handlers and the background poller so
there's exactly one way messages reach Jim.
"""

from __future__ import annotations

from brain import telegram
from brain.outbox import Outbox, OutgoingMessage

_outbox = Outbox()


def queue_and_deliver(msg: OutgoingMessage) -> OutgoingMessage:
    """Persist `msg`, then deliver. Direct Telegram send self-acks."""
    _outbox.enqueue(msg)
    if telegram.is_configured() and telegram.send_message(msg.text):
        _outbox.ack(msg.id)
        msg.delivered = True
    return msg
