# 🤖 Phase 2 — Automation Server API

Brain is now a 24/7 web service. Hermes pushes data in via webhooks;
Brain thinks; Hermes pulls results out and delivers them to Jim.

**Brain still never sends anything itself.** It writes to an outbox.
Hermes delivers. (`Brain thinks, Hermes acts.`)

```
Hermes ──POST──▶ Brain (auto-analyze / schedule) ──▶ outbox ──GET──▶ Hermes ──▶ Telegram ──▶ Jim
```

---

## Run it

**Local:**
```bash
uvicorn brain.server:app --reload --port 8000
# http://localhost:8000/health
```

**Railway:** the `Procfile` / `Dockerfile` already start it:
```
uvicorn brain.server:app --host 0.0.0.0 --port $PORT
```

---

## Endpoints

### Inbound — Hermes pushes to Brain

| Method | Path | Body | What Brain does |
|--------|------|------|-----------------|
| POST | `/webhook/transcript` | `CallTranscript` | Auto-analyzes → queues analysis for Jim |
| POST | `/webhook/digest` | `HermesDigest` | Stores signals for the next briefing |
| POST | `/webhook/metrics` | `MetricsSnapshot` | Stores metrics for the next briefing |

### Outbound — Hermes pulls from Brain

| Method | Path | What it returns |
|--------|------|-----------------|
| GET | `/outgoing/pending` | All undelivered messages, oldest first |
| POST | `/outgoing/{id}/ack` | Marks one delivered (call after sending to Jim) |

### Self-learning loop — Jim reacts, Brain learns

| Method | Path | Body | What happens |
|--------|------|------|--------------|
| POST | `/feedback` | `FeedbackRecord` | Stores Jim's reaction; auto-reflects once enough accrues |
| POST | `/learn/reflect` | — | Force-distill feedback into lessons now |
| GET | `/learn/lessons` | — | Current learned preferences |
| GET | `/learn/feedback` | — | Raw feedback history |

`FeedbackRecord`:
```json
{
  "target_kind": "briefing | analysis | lens",
  "target_ref": "out_2222d3176c23",   // the outgoing message id Jim reacted to
  "rating": "up | down | neutral",
  "note": "Wrong owner — that follow-up should be Sarah's, not mine.",
  "tags": ["wrong_owner"]
}
```

**The loop:** Brain output → Hermes delivers → Jim reacts (👍/👎/note) →
Hermes `POST /feedback` → Brain stores it → reflection distills durable
*lessons* → those lessons are injected into every future briefing /
analysis / lens prompt → better output. Reflection runs automatically once
`BRAIN_AUTO_REFLECT_THRESHOLD` (default 5) unprocessed items accrue, and
nightly at `REFLECT_HOUR_UTC:30`. Lessons are category-scoped, so a
briefing correction only reshapes briefings (plus anything tagged global).

### Control / status

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness (Railway health check) |
| GET | `/status` | Digest age, pending, **lessons learned, feedback counts** |
| POST | `/briefing/run` | Manually trigger a briefing — body `{"type":"morning"}` |

---

## What Hermes does (the loop)

```
1. When a call ends:
   POST /webhook/transcript   (the transcript JSON)
   → Brain auto-analyzes, queues the result.

2. Twice a day (or continuously):
   POST /webhook/digest        (signals)
   POST /webhook/metrics       (metrics)
   → Brain stores them; scheduled briefings use the latest.

3. Every minute or two:
   GET /outgoing/pending
   → for each message: send message["text"] to Jim on Telegram,
     then POST /outgoing/{id}/ack

4. When Jim reacts to a delivered message (👍 / 👎 / reply):
   POST /feedback  {target_kind, target_ref=<that message's id>, rating, note}
   → this is what makes Brain improve over time.
```

The webhook bodies are the **exact same JSON** from
`HERMES_BUILD_BRIEF.md` — just POSTed instead of written to files.

---

## Outgoing message shape

```json
{
  "id": "2222d3176c23",
  "kind": "analysis",          // briefing | analysis | alert
  "channel": "telegram",
  "recipient": "jim",
  "title": "Call analysis: Weekly Sync",
  "text": "📞 *Call Analysis — Weekly Sync*\n\n...",  // ready to send as-is
  "created_at": "2026-06-30T12:00:00Z",
  "delivered": false,
  "source_ref": "call_001",
  "meta": {"follow_ups": 5, "decisions": 1}
}
```

Hermes sends `text` straight to Telegram (it's pre-formatted Markdown),
then acks the `id`.

---

## Scheduled briefings

Brain generates them itself, no trigger needed:

| Briefing | Default (UTC) | Env var |
|----------|---------------|---------|
| Morning | 12:00 (~7am ET) | `BRIEFING_MORNING_HOUR_UTC` |
| Evening | 23:00 (~6pm ET) | `BRIEFING_EVENING_HOUR_UTC` |

Disable with `BRAIN_ENABLE_SCHEDULER=false`. They read the latest digest
Hermes has pushed, so Hermes just needs to keep digests fresh.

---

## Railway environment variables

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
BRAIN_MODEL=claude-sonnet-4-20250514
BRIEFING_MORNING_HOUR_UTC=12
BRIEFING_EVENING_HOUR_UTC=23
```

⚠️ **Persistence:** Railway's container filesystem is ephemeral. The
outbox + incoming data live under `./data`. Add a **Railway Volume
mounted at `/app/data`** so pending messages and digests survive
restarts. (Without it, an undelivered message is lost if the container
restarts before Hermes pulls it.)

---

## Quick test (no Hermes, no API key needed for plumbing)

```bash
uvicorn brain.server:app --port 8000 &
curl localhost:8000/health
curl -X POST localhost:8000/webhook/digest -H 'content-type: application/json' \
  -d '{"signals":[],"generated_at":"2026-06-30T12:00:00Z","time_window_start":"2026-06-30T06:00:00Z","time_window_end":"2026-06-30T12:00:00Z"}'
curl localhost:8000/outgoing/pending
```

(Analyzing a transcript and generating briefings need `ANTHROPIC_API_KEY`.)
