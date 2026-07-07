# 🤖 Phase 2 — Automation Server API

Brain is a 24/7 web service. Hermes pushes data in via webhooks; Brain
thinks; **Brain delivers the result to Jim's Telegram itself.**

```
Hermes ──POST──▶ Brain (auto-analyze / schedule / learn) ──▶ Telegram ──▶ Jim
                                         │
                                         └─▶ outbox (audit trail + fallback puller)
```

**Delivery model:** every result is written to a file-based outbox (audit
trail) and, if `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` are set, sent
straight to Jim's Telegram — a direct send self-acks the outbox entry. If
Telegram is *not* configured, the message stays pending in the outbox for a
fallback puller (`GET /outgoing/pending` → deliver → `POST /ack`). So Hermes
no longer has to deliver; it only ingests. See
[`HERMES_BUILD_BRIEF.md`](HERMES_BUILD_BRIEF.md).

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
| POST | `/webhook/transcript` | `CallTranscript` | Auto-analyzes → delivers the summary to Jim |
| POST | `/webhook/digest` | `HermesDigest` | Stores signals for the next briefing |
| POST | `/webhook/metrics` | `MetricsSnapshot` | Stores metrics for the next briefing |
| POST | `/webhook/calendar` | `CalendarSnapshot` | Stores upcoming events for briefings ("what's next / prep") |

### Outbound — fallback puller (only if Telegram is unconfigured)

| Method | Path | What it returns |
|--------|------|-----------------|
| GET | `/outgoing/pending` | All undelivered messages, oldest first |
| POST | `/outgoing/{id}/ack` | Marks one delivered (call after sending to Jim) |
| GET | `/outgoing/recent?limit=20` | Last N messages, delivered or not, newest first |

Under normal operation Brain delivers to Telegram directly, so `/pending`
stays empty — it exists so nothing is lost if Telegram delivery is off or
fails. `/outgoing/recent` exists for the opposite reason: because direct
delivery marks a message delivered immediately, Hermes has no other way to
discover *what was just sent*, which it needs to attach a Telegram reaction
to the right `target_ref` in `POST /feedback` (best-effort match to the most
recent delivery, not a literal Telegram reply thread).

### Self-learning loop — Jim reacts, Brain learns

| Method | Path | Body | What happens |
|--------|------|------|--------------|
| POST | `/feedback` | `FeedbackRecord` | Stores Jim's reaction; auto-reflects once enough accrues |
| POST | `/learn/reflect` | — | Force-distill feedback into lessons now |
| GET | `/learn/lessons` | — | Current learned preferences |
| GET | `/learn/feedback` | — | Raw feedback history (last 50) |

`FeedbackRecord`:
```json
{
  "target_kind": "briefing | analysis | lens",
  "target_ref": "2222d3176c23",       // the outgoing message id Jim reacted to
  "rating": "up | down | neutral",
  "note": "Wrong owner — that follow-up should be Sarah's, not mine.",
  "tags": ["wrong_owner"]
}
```

**The loop:** Brain output → Jim reacts (👍/👎/note) → Hermes `POST /feedback`
→ Brain stores it → reflection distills durable *lessons* → those lessons are
injected into every future briefing / analysis / lens prompt → better output.
Reflection runs automatically once `BRAIN_AUTO_REFLECT_THRESHOLD` (default 5)
unprocessed items accrue, and nightly at `REFLECT_HOUR_UTC:30`. Lessons are
category-scoped, so a briefing correction only reshapes briefings (plus
anything tagged global).

### Control / status

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness (Railway health check) |
| GET | `/status` | Digest age, pending count, lessons learned, feedback counts, Telegram/email config flags |
| POST | `/briefing/run` | Manually trigger a briefing — body `{"type":"morning"}` |
| POST | `/telegram/test` | Send a test message to Jim's Telegram (confirms delivery works) |
| POST | `/poll/email` | Run one email poll now (also runs on an interval; see below) |

`GET /status` returns:
```json
{
  "digest_age_minutes": 12.3,
  "has_api_key": true,
  "pending_outgoing": 0,
  "transcripts": 4,
  "lessons_learned": 7,
  "feedback_total": 11,
  "feedback_unprocessed": 2,
  "telegram_configured": true,
  "email_poll_configured": true
}
```

---

## What Hermes does (the loop)

```
1. When a call ends:
   POST /webhook/transcript   (the transcript JSON)
   → Brain auto-analyzes and texts Jim the summary.

2. Continuously / on a cadence:
   POST /webhook/digest        (email + Skool signals)
   POST /webhook/calendar      (upcoming meetings)
   POST /webhook/metrics       (daily numbers)
   → Brain stores them; scheduled briefings use the latest.

3. When Jim reacts to a delivered message (👍 / 👎 / reply):
   POST /feedback  {target_kind, target_ref=<that message's id>, rating, note}
   → this is what makes Brain improve over time.
```

Hermes does **not** deliver — Brain sends to Telegram itself. The webhook
bodies are the exact JSON from
[`HERMES_BUILD_BRIEF.md`](HERMES_BUILD_BRIEF.md) §5, just POSTed instead of
written to files.

---

## Email polling (24/7 call summaries with no Mac)

Brain can pull Fathom call emails over IMAP on its own, so call summaries work
even before Hermes is wired up. It's an **optional fallback** — OFF unless
`EMAIL_ADDRESS` + `EMAIL_APP_PASSWORD` are set. When enabled, each tick reads
new unread mail from the `FATHOM_FROM` sender, analyzes it, and delivers the
summary to Telegram. Interval is `EMAIL_POLL_MINUTES` (default 15). Trigger a
tick manually with `POST /poll/email`.

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
  "created_at": "2026-07-07T12:00:00Z",
  "delivered": true,
  "delivered_at": "2026-07-07T12:00:03Z",
  "source_ref": "call_001",
  "meta": {"follow_ups": 5, "decisions": 1}
}
```

`text` is pre-formatted Telegram Markdown. When Brain delivers directly it
marks the message `delivered` itself; a fallback puller would send `text`
verbatim then ack the `id`.

---

## Scheduled jobs

Brain runs these itself (APScheduler), no trigger needed:

| Job | Default (UTC) | Env var |
|-----|---------------|---------|
| Morning briefing | 12:00 (~7am ET) | `BRIEFING_MORNING_HOUR_UTC` |
| Evening briefing | 23:00 (~6pm ET) | `BRIEFING_EVENING_HOUR_UTC` |
| Nightly reflection | 06:30 (~1am ET) | `REFLECT_HOUR_UTC` (minute is fixed at :30) |
| Email poll | every `EMAIL_POLL_MINUTES` | only if email is configured |

Briefings read the latest digest / calendar / metrics Hermes has pushed, so
Hermes just needs to keep those fresh. Disable the whole scheduler with
`BRAIN_ENABLE_SCHEDULER=false`.

---

## Railway environment variables

```
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxx
BRAIN_MODEL=claude-sonnet-5

# Direct Telegram delivery (Brain texts Jim itself)
TELEGRAM_BOT_TOKEN=...            # from @BotFather
TELEGRAM_CHAT_ID=...              # Jim's chat id (captured when he taps Start)

# Optional: 24/7 Fathom-call ingestion over email (no Mac / no Hermes needed)
EMAIL_ADDRESS=...
EMAIL_APP_PASSWORD=...            # Gmail app password
EMAIL_IMAP_HOST=imap.gmail.com
FATHOM_FROM=fathom
EMAIL_POLL_MINUTES=15

# Scheduling (UTC hours)
BRIEFING_MORNING_HOUR_UTC=12
BRIEFING_EVENING_HOUR_UTC=23
REFLECT_HOUR_UTC=6
BRAIN_ENABLE_SCHEDULER=true
```

⚠️ **Persistence:** Railway's container filesystem is ephemeral. The outbox,
incoming data, feedback, and learned lessons all live under `./data`. Add a
**Railway Volume mounted at `/app/data`** so pending messages, digests, and
lessons survive restarts. (Without it, an undelivered outbox message or the
learning history is lost if the container restarts.)

---

## Quick test (no Hermes, no API key needed for plumbing)

```bash
uvicorn brain.server:app --port 8000 &
curl localhost:8000/health
curl localhost:8000/status
curl -X POST localhost:8000/webhook/digest -H 'content-type: application/json' \
  -d '{"signals":[],"generated_at":"2026-07-07T12:00:00Z","time_window_start":"2026-07-07T06:00:00Z","time_window_end":"2026-07-07T12:00:00Z"}'
curl localhost:8000/outgoing/pending
```

(Analyzing a transcript, generating briefings, and reflection need
`ANTHROPIC_API_KEY`. Delivery to Jim needs `TELEGRAM_BOT_TOKEN` +
`TELEGRAM_CHAT_ID`.)
