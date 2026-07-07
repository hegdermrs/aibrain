"""
Brain automation server (Phase 2).

A small FastAPI service that makes the Brain autonomous:

  Inbound (Hermes → Brain):
    POST /webhook/transcript   a call transcript → auto-analyze → outbox
    POST /webhook/digest       a signals digest  → store (used by briefings)
    POST /webhook/metrics      a metrics snapshot → store

  Scheduled (Brain itself):
    Morning + evening briefings generated from the latest stored
    digest/metrics and dropped into the outbox.

  Outbound (Brain → Hermes):
    GET  /outgoing/pending     undelivered messages, oldest first
    POST /outgoing/{id}/ack    mark a message delivered

Brain never sends to Jim directly — it writes to the outbox and Hermes
delivers. "Brain thinks, Hermes acts."

Run locally:   uvicorn brain.server:app --reload --port 8000
Run on Railway: uvicorn brain.server:app --host 0.0.0.0 --port $PORT
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from brain.analyst import analyze_transcript
from brain.briefing import generate_briefing
from brain.formatting import format_analysis, format_briefing
from brain.hermes_interface import HermesInterface
from brain.models import (
    BriefingType,
    CallTranscript,
    HermesDigest,
    MetricsSnapshot,
)
from brain.outbox import Outbox, OutgoingMessage
from brain.learning import FeedbackRecord, get_store


# ── Config ────────────────────────────────────────────────────────────────────

DIGEST_DIR = Path(os.environ.get("HERMES_DIGEST_DIR", "./data/incoming"))
TRANSCRIPT_DIR = Path(os.environ.get("HERMES_TRANSCRIPT_DIR", "./data/transcripts"))
ANALYSIS_DIR = Path(os.environ.get("BRAIN_ANALYSIS_DIR", "./data/analysis"))
BRIEFINGS_DIR = Path(os.environ.get("BRAIN_BRIEFINGS_DIR", "./data/briefings"))

for _d in (DIGEST_DIR, TRANSCRIPT_DIR, ANALYSIS_DIR, BRIEFINGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

hermes = HermesInterface()
outbox = Outbox()
learning = get_store()

# Auto-reflect once this many unprocessed feedback items accumulate.
AUTO_REFLECT_THRESHOLD = int(os.environ.get("BRAIN_AUTO_REFLECT_THRESHOLD", "5"))

app = FastAPI(title="Brain — Operations Co-Founder", version="2.0.0")


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


# ── Health / status ───────────────────────────────────────────────────────────


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "brain", "version": "2.0.0"}


@app.get("/status")
def status() -> dict:
    age = hermes.hermse_digest_age_minutes()
    pending = outbox.list_pending()
    feedback = learning.list_feedback()
    return {
        "digest_age_minutes": age,
        "has_api_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "pending_outgoing": len(pending),
        "transcripts": len(list(TRANSCRIPT_DIR.glob("transcript_*.json"))),
        "lessons_learned": len(learning.get_lessons()),
        "feedback_total": len(feedback),
        "feedback_unprocessed": sum(1 for f in feedback if not f.processed),
    }


# ── Inbound webhooks (Hermes → Brain) ─────────────────────────────────────────


@app.post("/webhook/transcript")
def webhook_transcript(transcript: CallTranscript) -> dict:
    """Receive a transcript, auto-analyze it, queue the result for Jim."""
    # Persist the raw transcript (so it shows up in the dashboard too)
    _save_json(TRANSCRIPT_DIR / f"transcript_{transcript.id or _ts()}.json",
               transcript.model_dump(mode="json"))

    try:
        analysis = analyze_transcript(transcript)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Analysis failed: {e}")

    _save_json(ANALYSIS_DIR / f"call_{_ts()}.json",
               analysis.model_dump(mode="json"))

    msg = outbox.enqueue(OutgoingMessage(
        kind="analysis",
        title=f"Call analysis: {analysis.call_title}",
        text=format_analysis(analysis),
        source_ref=transcript.id,
        meta={"follow_ups": len(analysis.follow_ups),
              "decisions": len(analysis.decisions)},
    ))
    return {"status": "analyzed", "outgoing_id": msg.id,
            "follow_ups": len(analysis.follow_ups)}


@app.post("/webhook/digest")
def webhook_digest(digest: HermesDigest) -> dict:
    """Receive a signals digest. Stored for the next scheduled briefing."""
    _save_json(DIGEST_DIR / f"digest_{_ts()}.json",
               digest.model_dump(mode="json"))
    return {"status": "stored", "signals": len(digest.signals)}


@app.post("/webhook/metrics")
def webhook_metrics(metrics: MetricsSnapshot) -> dict:
    """Receive a metrics snapshot. Stored for the next scheduled briefing."""
    _save_json(DIGEST_DIR / f"metrics_{_ts()}.json",
               metrics.model_dump(mode="json"))
    return {"status": "stored", "metrics": len(metrics.metrics)}


# ── On-demand briefing (also used by the scheduler) ───────────────────────────


class BriefingRequest(BaseModel):
    type: str = "morning"  # "morning" | "evening"


def _run_briefing(briefing_type: BriefingType) -> Optional[OutgoingMessage]:
    """Generate a briefing from the latest stored digest and queue it."""
    digest = hermes.read_latest_digest()
    if digest is None:
        return None
    metrics = hermes.read_metrics()
    briefing = generate_briefing(
        digest=digest, metrics=metrics, briefing_type=briefing_type
    )
    _save_json(
        BRIEFINGS_DIR / f"{briefing_type.value}_{_ts()}.json",
        briefing.model_dump(mode="json"),
    )
    return outbox.enqueue(OutgoingMessage(
        kind="briefing",
        title=f"{briefing_type.value.title()} briefing",
        text=format_briefing(briefing),
        meta={"requires_jim": len(briefing.requires_jim_attention)},
    ))


@app.post("/briefing/run")
def briefing_run(req: BriefingRequest) -> dict:
    bt = BriefingType.MORNING if req.type == "morning" else BriefingType.EVENING
    msg = _run_briefing(bt)
    if msg is None:
        raise HTTPException(status_code=409, detail="No digest available yet")
    return {"status": "generated", "outgoing_id": msg.id}


# ── Outbound (Hermes pulls results) ───────────────────────────────────────────


@app.get("/outgoing/pending")
def outgoing_pending() -> dict:
    msgs = outbox.list_pending()
    return {"count": len(msgs),
            "messages": [m.model_dump(mode="json") for m in msgs]}


@app.post("/outgoing/{message_id}/ack")
def outgoing_ack(message_id: str) -> dict:
    msg = outbox.ack(message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "acked", "id": message_id}


# ── Self-learning loop (feedback → reflection → lessons) ──────────────────────


@app.post("/feedback")
def feedback(fb: FeedbackRecord) -> dict:
    """Hermes posts Jim's reaction to a Brain output.

    Stored immediately. When enough unprocessed feedback accumulates, Brain
    reflects (distills it into lessons) on the spot; otherwise reflection
    waits for the nightly job.
    """
    learning.record_feedback(fb)
    pending = learning.list_feedback(unprocessed_only=True)
    reflected = None
    if len(pending) >= AUTO_REFLECT_THRESHOLD and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            reflected = learning.reflect()
        except Exception as e:
            reflected = {"updated": False, "reason": f"reflection error: {e}"}
    return {"status": "recorded", "id": fb.id,
            "unprocessed": len(pending), "reflected": reflected}


@app.post("/learn/reflect")
def learn_reflect() -> dict:
    """Force a reflection pass now (also runs nightly on a schedule)."""
    try:
        return learning.reflect()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Reflection failed: {e}")


@app.get("/learn/lessons")
def learn_lessons() -> dict:
    lessons = learning.get_lessons()
    return {"count": len(lessons),
            "lessons": [l.model_dump(mode="json") for l in lessons]}


@app.get("/learn/feedback")
def learn_feedback() -> dict:
    fb = learning.list_feedback()
    return {"count": len(fb),
            "unprocessed": sum(1 for f in fb if not f.processed),
            "feedback": [f.model_dump(mode="json") for f in fb[-50:]]}


# ── Scheduler (morning + evening briefings + nightly reflection) ──────────────


def _start_scheduler() -> None:
    """Schedule the daily briefings. Times are UTC; override via env."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        return  # scheduler optional; webhooks still work without it

    morning_hour = int(os.environ.get("BRIEFING_MORNING_HOUR_UTC", "12"))  # 7am ET
    evening_hour = int(os.environ.get("BRIEFING_EVENING_HOUR_UTC", "23"))  # 6pm ET

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        lambda: _run_briefing(BriefingType.MORNING),
        CronTrigger(hour=morning_hour, minute=0),
        id="morning_briefing", replace_existing=True,
    )
    scheduler.add_job(
        lambda: _run_briefing(BriefingType.EVENING),
        CronTrigger(hour=evening_hour, minute=0),
        id="evening_briefing", replace_existing=True,
    )

    # Nightly: fold the day's feedback into lessons (closes the learning loop).
    reflect_hour = int(os.environ.get("REFLECT_HOUR_UTC", "6"))  # ~1am ET
    scheduler.add_job(
        lambda: learning.reflect(),
        CronTrigger(hour=reflect_hour, minute=30),
        id="nightly_reflection", replace_existing=True,
    )
    scheduler.start()


@app.on_event("startup")
def on_startup() -> None:
    if os.environ.get("BRAIN_ENABLE_SCHEDULER", "true").lower() == "true":
        _start_scheduler()
