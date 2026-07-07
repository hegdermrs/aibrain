"""
Hermes simulator — exercises the Brain's full loop against a RUNNING server.

Use it to prove the Brain works locally before pointing your real Hermes at
it. It also doubles as a reference for what Hermes must do:
  push digest/metrics/transcript  →  pull /outgoing/pending  →  ack  →  feedback

Run:
  1) terminal A:  python -m uvicorn brain.server:app --port 8000
  2) terminal B:  python hermes_sim.py
  (override target with BRAIN_BASE_URL, e.g. your Railway URL)
"""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone

BASE = os.environ.get("BRAIN_BASE_URL", "http://localhost:8000").rstrip("/")


def _parse(body: bytes) -> dict:
    try:
        return json.loads(body or b"{}")
    except Exception:
        # Non-JSON body (e.g. a plain-text 500) — surface it instead of crashing
        return {"_raw": (body or b"").decode("utf-8", "replace")[:500]}


def _call(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{BASE}{path}", data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, _parse(r.read())
    except urllib.error.HTTPError as e:
        return e.code, _parse(e.read())


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    print(f"Target Brain: {BASE}\n")

    # 0. Health + status
    _, health = _call("GET", "/health")
    print("health:", health)
    _, status = _call("GET", "/status")
    print("status:", status)
    has_key = status.get("has_api_key", False)
    if not has_key:
        print("\n! No ANTHROPIC_API_KEY on the server — will test plumbing only")
        print("  (briefing + transcript analysis need the key).\n")

    # 1. Push a signals digest (what Hermes sends on a cadence)
    digest = {
        "signals": [{
            "id": "sig_demo_1", "source": "email",
            "title": "Enterprise inquiry — Acme Corp",
            "summary": "Fortune 500 wants exec coaching for Q3. VIP lead.",
            "priority": "high", "timestamp": _now(),
            "raw_text": "Hi Jim, we'd love to talk about a program...",
            "sender": "sarah@acme.com", "requires_response": True,
        }],
        "generated_at": _now(),
        "time_window_start": _now(), "time_window_end": _now(),
    }
    print("push digest:", _call("POST", "/webhook/digest", digest)[1])

    # 2. Push metrics
    metrics = {"metrics": [
        {"name": "Active Clients", "value": 42, "previous_value": 40,
         "unit": "", "trend": "up"},
        {"name": "MRR", "value": 21000, "previous_value": 20000,
         "unit": "$", "trend": "up"},
    ], "timestamp": _now()}
    print("push metrics:", _call("POST", "/webhook/metrics", metrics)[1])

    # 3. Generate a briefing on demand (normally the Brain does this on a
    #    schedule; we force it so you see a result immediately). Needs the key.
    if has_key:
        code, res = _call("POST", "/briefing/run", {"type": "morning"})
        print("run briefing:", code, res)

        # 4. Push a call transcript → auto-analyzed
        transcript = {
            "id": f"call_{datetime.now():%Y%m%d_%H%M%S}",
            "title": "Weekly Strategy Call — Jim & Sarah",
            "date": _now(), "participants": ["Jim Harshaw", "Sarah"],
            "duration_minutes": 30, "segments": [],
            "full_text": (
                "Jim: Community is at 500 members. Let's launch a group program. "
                "Sarah: I'll research platforms by Friday. "
                "Jim: Also automate the invoicing, it eats my time. "
                "Sarah: On it. And the Acme enterprise lead — I'll book a call."
            ),
            "source": "fathom",
        }
        print("push transcript:", _call("POST", "/webhook/transcript", transcript)[1])

    # 5. Pull what the Brain wants delivered, "deliver" it, ack it
    _, pending = _call("GET", "/outgoing/pending")
    print(f"\npending to deliver: {pending['count']}")
    first_id = None
    for m in pending["messages"]:
        first_id = first_id or m["id"]
        print(f"\n----- would send to Jim on Telegram ({m['kind']}) -----")
        print(m["text"][:600])
        print("----- end -----")
        print("ack:", _call("POST", f"/outgoing/{m['id']}/ack", {})[1])

    # 6. Simulate Jim reacting → feedback (this is what makes Brain learn)
    if first_id:
        fb = {"target_kind": "briefing", "target_ref": first_id,
              "rating": "down", "note": "Too long — keep it to 5 bullets.",
              "tags": ["too_long"]}
        print("\nfeedback:", _call("POST", "/feedback", fb)[1])

    # 7. Inspect learning state
    print("lessons:", _call("GET", "/learn/lessons")[1])
    print("\nDone. Re-run after ~5 feedbacks (or POST /learn/reflect) to see lessons form.")


if __name__ == "__main__":
    main()
