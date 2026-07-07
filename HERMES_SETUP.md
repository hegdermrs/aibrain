# Hand this file to Jim's Hermes Agent

**If you're an AI agent reading this (Hermes Agent):** this document is
addressed to you. Someone just said something like "set this up for me" or
pasted this file into your chat. Follow the steps below in order — create
every file exactly as shown, fill in the two values you're given (the
Brain's URL and a Telegram bot token), verify it works, then wire the
scheduled jobs. You should be able to do all of this yourself in this
conversation: `write_file` each file, run the verification commands, call
`hermes cron create` for the schedules. Don't ask the human to do anything
except supply the two config values and, if needed, one Skool login and one
Google OAuth consent (both are browser windows only a human can click
through).

**If you're the human giving this to Hermes Agent:** just paste this whole
file to it and say "please set this up," then answer whatever it asks you
(mainly: the Brain's Railway URL, and the Telegram bot token from
@BotFather). Everything below this line is written for the agent, not you.

---

## What this connects

**Brain thinks, Hermes acts.** The Brain is a separate service (FastAPI,
running on Railway) that reasons over Jim's email/calls/calendar/metrics
and produces morning/evening briefings, call analyses, and strategic
advice — then **texts Jim directly on Telegram** using its own bot token.
You (Hermes) never decide anything in this connection — you gather what
the Brain needs, shape it into its JSON contract, push it via HTTP, and
capture Jim's reactions as feedback so the Brain keeps improving.

```
You read email/Skool/calendar/Fathom → shape as JSON → POST to the Brain
                                                              │
                                                    Brain reasons + decides
                                                              │
                                              texts Jim directly on Telegram
                                                              │
                                          Jim reacts (👍/👎/reply) in that chat
                                                              │
                              You poll for it → POST /feedback → Brain gets smarter
```

This builds a skill called `brain-bridge`. Once created, it's a normal
skill — `/brain-bridge` or its triggers ("brain bridge", "push to brain",
"sync with brain", etc.) will load it in future sessions.

---

## Step 1 — Create the skill files

Create every file below at the exact path shown, with the exact content
shown. Paths are relative to `~/.hermes/skills/brain-bridge/` unless noted.

### `SKILL.md`

```markdown
---
title: "Brain Bridge"
description: "Connect Jim Harshaw Jr.'s Hermes to his Brain (a separate AI ops co-founder service) — push email/Skool signals, calendar, and Fathom call transcripts to it, and capture Jim's Telegram reactions as feedback"
version: "1.0.0"
category: "productivity"
triggers:
  - "brain bridge"
  - "push to brain"
  - "brain digest"
  - "brain briefing"
  - "sync with brain"
  - "operations brain"
  - "check brain feedback"
---

# Brain Bridge

**Brain thinks, Hermes acts.** The Brain is a separate service (FastAPI on
Railway) that reasons over Jim's email/calls/calendar/metrics and produces
morning/evening briefings, call analyses, and strategic advice — then
**texts Jim directly on Telegram** using its own bot token. You (Hermes)
never decide anything here — you gather what the Brain needs, shape it into
its JSON contract, push it, and capture Jim's reactions as feedback so the
Brain keeps improving.

Full contract (self-contained, no need to fetch the Brain repo):
`references/brain_contract.md`.

## How It Works

\```
You read email/Skool/calendar/Fathom → shape as JSON → POST to the Brain
                                                              │
                                                    Brain reasons + decides
                                                              │
                                              texts Jim directly on Telegram
                                                              │
                                          Jim reacts (👍/👎/reply) in that chat
                                                              │
                              You poll for it → POST /feedback → Brain gets smarter
\```

## When to Use

- Setting up or maintaining Jim's connection between Hermes and his Brain
- "Check for new Brain-relevant signals and push a digest"
- "A Fathom call transcript came in, send it to the Brain"
- "Check if Jim reacted to anything the Brain sent"
- Don't use for: actually deciding what Jim should do about something — that
  judgment belongs to the Brain, not to you. Your job stops at "gather,
  shape, push."

## One-Time Setup

1. `cp config.example.yaml ~/.hermes/brain-bridge/config.yaml` and fill in
   `brain_base_url` (the Railway URL) and `telegram_bot_token` (same token
   the Brain uses to deliver — this skill only reads updates with it, never
   sends briefings itself).
2. `pip install pyyaml` if not already available.
3. Verify: `python scripts/brain_client.py` — should print `OK` and the
   Brain's status.
4. **Calendar** — only if you don't already have your own Google Calendar
   access: fill in `google_oauth_client_secret_file` (download from Google
   Cloud Console → Credentials → OAuth client ID → Desktop app), then
   `python scripts/google_auth.py` once to authorize.
5. **Skool** — only if Jim's community matters here: fill in
   `skool_community_url`, install `playwright` + `playwright install
   chromium`, then `python scripts/setup_skool_profile.py` once to log in
   (real browser window, log in by hand, press Enter to save the session).

## Agent-Driven Operation (Interactive)

This is the PRIMARY path for anything needing judgment — prefer it over the
scripted fallbacks below, since you can read context and adapt to changes
a hardcoded script can't.

1. **"Check for new signals and push a digest"** — read new email (however
   you already do, e.g. `himalaya` if configured) and, if Skool matters,
   check the community using your own browser tool against the persisted
   profile at the path in `config.yaml`'s Skool section. For each item worth
   surfacing, shape it per `references/brain_contract.md` §3 (id, source,
   title, summary, priority, timestamp, raw_text, sender, thread_id,
   requires_response) and write them to a temp JSON file, then run
   `python scripts/push_digest.py --add <file>`. Use your judgment on
   priority — `high` for client/revenue/urgent/VIP items, `low` for FYI.

2. **"A Fathom transcript came in"** — get the full transcript text (from
   the email or wherever Fathom delivered it), then run
   `python scripts/push_transcript.py --id <stable-id> --subject "<title>"
   --text-file <path>` (or pipe the text via stdin). The Brain auto-analyzes
   it and texts Jim the summary — you don't need to do anything else.

3. **"Compute today's metrics"** — gather whatever's available (Skool member
   count via `scripts/scan_skool.py --members`, or another source), shape
   per §4, write to a file, `python scripts/push_metrics.py --add <file>`.
   Only push what's real — an empty/partial set beats a fabricated one.

4. **"Check my calendar"** — if you already have your own Calendar access,
   read the next 7 days, shape per §6, and run
   `python scripts/push_calendar.py --stdin` piping the JSON. Otherwise run
   `python scripts/push_calendar.py` directly (uses Google OAuth via
   `google_auth.py`).

5. **"Check for Jim's feedback"** — run `python scripts/poll_feedback.py`.
   It captures his chat id on `/start` and turns his replies/reactions into
   `POST /feedback` calls, best-effort-attached to the most recent thing the
   Brain sent (see `references/brain_contract.md` §8 for why).

## Scheduled Runs (Cron)

Mechanical, no-judgment jobs run cheapest via `--no-agent` (skips the LLM
entirely — the script's stdout is delivered verbatim, silent if empty):

\```bash
# Every ~2 min: capture Jim's reactions as feedback (pure plumbing)
hermes cron create "2m" --name "brain-feedback" --no-agent \
  --script ~/.hermes/scripts/brain_poll_feedback.py --deliver local

# Every 30 min: keep the digest fresh even if nothing new was added this tick
hermes cron create "30m" --name "brain-digest-refresh" --no-agent \
  --script ~/.hermes/scripts/brain_push_digest_refresh.py --deliver local

# Hourly: recheck calendar (only if using push_calendar.py's direct Google mode)
hermes cron create "1h" --name "brain-calendar" --no-agent \
  --script ~/.hermes/scripts/brain_push_calendar.py --deliver local
\```

Jobs that need judgment go through the agent (omit `--no-agent`, attach the
skill so it has these instructions loaded):

\```bash
# Every 30 min: read email (+ Skool), decide what's signal-worthy, push
hermes cron create "30m" --name "brain-signals" --skill brain-bridge \
  --deliver local \
  "Check for new emails and Skool activity since last run. Decide what's \
   worth surfacing to the Brain per the brain-bridge skill's contract \
   (references/brain_contract.md §3), then push via scripts/push_digest.py \
   --add. Report a one-line summary of what you pushed."

# Daily at 22:40 UTC: compute + push metrics (before the Brain's evening briefing)
hermes cron create "0 22 40 * * *" --name "brain-metrics" --skill brain-bridge \
  --deliver local \
  "Compute today's available metrics (Skool member count via \
   scripts/scan_skool.py --members, and anything else you have access to), \
   then push via scripts/push_metrics.py --add."

# Every 15 min: check for a new Fathom call transcript email
hermes cron create "15m" --name "brain-transcripts" --skill brain-bridge \
  --deliver local \
  "Check email for a new Fathom call-transcript message not yet processed. \
   If found, push it via scripts/push_transcript.py. If none, do nothing."
\```

Use `hermes cron list` to see them, `hermes cron edit <job_id> ...` to
adjust schedule/prompt, `hermes cron pause/resume <job_id>` to toggle one
off temporarily.

## Common Pitfalls

1. **Pushing only new-since-last-time signals to `/webhook/digest`.** The
   Brain only reads the single latest digest push — no merging. Always use
   `push_digest.py`'s `--add`/`--stdin` (which merges into the rolling
   active-signal store) rather than hand-building a digest payload with
   just today's new items, or older-but-unactioned signals will silently
   disappear from every future briefing.
2. **Fabricating metrics you can't actually compute.** Push only what's
   real (see `push_metrics.py`'s docstring) — an incomplete snapshot is
   fine, a made-up number is worse than nothing.
3. **Trusting `scan_skool.py`'s selectors blindly.** They're unverified
   scaffolding — run `--debug` and check `~/.hermes/brain-bridge/data/skool_debug.html`
   before relying on scheduled Skool scans. Prefer the agent-driven path
   (your own browser tool) until you've verified them.
4. **Feedback that doesn't attach to anything.** If `poll_feedback.py`
   reports "No recent Brain message to attach feedback to", the Brain
   hasn't sent anything yet in this session — that's expected on a fresh
   setup, not a bug.
5. **Two Telegram identities confusing Jim.** The Brain's briefings arrive
   from ITS bot; you (Hermes) may be a different bot/chat Jim already talks
   to for other things. That's fine — `poll_feedback.py` uses the Brain's
   token specifically to watch that chat, separate from your own.

## Verification Checklist

- [ ] `~/.hermes/brain-bridge/config.yaml` exists with `brain_base_url` +
      `telegram_bot_token` set
- [ ] `python scripts/brain_client.py` reports `OK`
- [ ] `python scripts/poll_feedback.py` runs without error (even if it does
      nothing yet)
- [ ] If using Calendar: `python scripts/google_auth.py` completed once;
      `python scripts/push_calendar.py` returns a non-error result
- [ ] If using Skool: `python scripts/setup_skool_profile.py` completed
      once; `python scripts/scan_skool.py --debug` dumped a real feed page
      (not a login wall)
- [ ] Cron jobs created (`hermes cron list`) match what you actually want
      running — mechanical ones as `--no-agent --script`, judgment ones
      with `--skill brain-bridge`
```

### `references/brain_contract.md`

```markdown
# The Brain's contract (self-contained copy)

This is a condensed copy of the payload shapes from the Brain repo's
HERMES_BUILD_BRIEF.md / PHASE_2_API.md, so this skill works even though
this Mac doesn't have that repo checked out. If the two ever disagree,
the Brain repo is the source of truth — re-sync this file.

All timestamps are ISO 8601 UTC (`2026-07-07T14:30:00Z`).

## §1. Base URL + auth

`brain_base_url` in `~/.hermes/brain-bridge/config.yaml` — the Railway URL.
Optional shared secret: `brain_api_key`, sent as header `X-Brain-Key`.

## §2. Endpoints this skill uses

| Script | Method | Path | Purpose |
|---|---|---|---|
| push_digest.py | POST | `/webhook/digest` | signals for the next briefing |
| push_metrics.py | POST | `/webhook/metrics` | metrics for the next briefing |
| push_transcript.py | POST | `/webhook/transcript` | a call → auto-analyzed → delivered |
| push_calendar.py | POST | `/webhook/calendar` | upcoming events for briefings |
| poll_feedback.py | POST | `/feedback` | Jim's reaction to a delivered message |
| poll_feedback.py | GET | `/outgoing/recent?limit=N` | resolve what Jim might be reacting to |
| brain_client.py | GET | `/health`, `/status` | connectivity check |

## §3. Signal (digest) shape

\```json
{
  "id": "email_<gmail-message-id>",
  "source": "email | skool | telegram | transcript",
  "title": "Enterprise inquiry — ~$50K, Acme Corp",
  "summary": "Fortune 500 wants exec coaching for Q3. VIP-tier lead.",
  "priority": "high | medium | low",
  "timestamp": "2026-07-07T09:15:00Z",
  "raw_text": "Hi Jim, we've heard great things...",
  "sender": "sarah@acme.com",
  "thread_id": "thread_abc123",
  "requires_response": true
}
\```

Priority: `high` = client/revenue/urgent/VIP/decision-needed. `medium` =
routine updates. `low` = FYI only. Set `requires_response: true` when Jim
(or someone) must reply or act.

**Push the FULL currently-active set every time**, not just what's new —
the Brain only ever reads the single most recent digest push, it doesn't
merge across pushes. `push_digest.py` handles this correctly via
`signal_store.py` (48h active window) — just feed it new signals as you
find them via `--add`/`--stdin`.

## §4. Metrics shape

\```json
{"name": "Skool Members", "value": 512, "previous_value": 498, "unit": "", "trend": "up", "note": "..."}
\```

`previous_value`/`trend` are auto-filled by `push_metrics.py` from the last
push of the same metric name if you omit them.

## §5. Transcript shape

\```json
{
  "id": "fathom_abc123",
  "title": "Weekly Strategy Call — Jim & Sarah",
  "date": "2026-07-07T10:00:00Z",
  "participants": ["Jim Harshaw", "Sarah (Assistant)"],
  "duration_minutes": 45,
  "segments": [],
  "full_text": "Jim: Let's start with the community...",
  "source": "fathom"
}
\```

`segments` can be `[]`. `full_text` is all that matters — it's what the
Brain actually analyzes.

## §6. Calendar shape

\```json
{
  "events": [
    {"title": "Coaching — Mark T.", "start": "2026-07-08T15:00:00Z",
     "end": "2026-07-08T15:50:00Z", "attendees": ["Mark T."], "location": "Zoom",
     "notes": "Session 4", "meeting_type": "coaching"}
  ],
  "timestamp": "2026-07-07T23:00:00Z"
}
\```

`meeting_type` ∈ `coaching | podcast | discovery | speaking | personal | other`.
Push the next ~7 days; re-push when the schedule changes.

## §7. Feedback shape

\```json
{
  "target_kind": "briefing | analysis | lens",
  "target_ref": "<the outgoing message id Jim reacted to>",
  "rating": "up | down | neutral",
  "note": "Wrong owner — that follow-up should be Sarah's, not mine.",
  "tags": ["wrong_owner"]
}
\```

The Brain distills feedback into durable *lessons* automatically (after 5
pieces of feedback, and nightly) and injects them into all future
briefings/analyses/advice.

## §8. Delivery — the Brain does this itself

The Brain texts Jim directly on Telegram (its own bot token,
`sendMessage` only — configured on the Brain, not here). This skill does
NOT need to deliver briefings/analyses; it only needs to:
1. Push data in (digest/metrics/transcript/calendar).
2. Capture Jim's reactions as feedback (`poll_feedback.py`).

`GET /outgoing/pending` + ack only matters as a fallback if the Brain's
direct Telegram is ever unconfigured — not part of normal operation.
```

### `config.example.yaml`

```yaml
# Copy this to ~/.hermes/brain-bridge/config.yaml and fill in.

# The Brain's Railway URL (from its CONCIERGE_RUNBOOK.md step A1)
brain_base_url: https://your-brain.up.railway.app

# Optional shared secret, sent as header X-Brain-Key (only if the Brain
# requires it — see HERMES_BUILD_BRIEF.md §10 in the Brain repo)
brain_api_key: ""

# Same bot token the Brain uses for direct delivery (from @BotFather).
# poll_feedback.py only calls getUpdates with it — the Brain only calls
# sendMessage — so they never conflict.
telegram_bot_token: ""

# Jim's Skool community URL, e.g. https://www.skool.com/his-community
skool_community_url: ""

# Only needed if using push_calendar.py's direct Google Calendar API mode
# (skip if the agent already has its own calendar access/connector).
# Path to an OAuth client secret JSON from Google Cloud Console.
google_oauth_client_secret_file: "~/.hermes/brain-bridge/google_credentials.json"
```

### `scripts/_config.py`

```python
"""
Shared config for brain-bridge scripts. Not a package — imported the same
way sibling scripts import each other (sys.path.insert + flat import),
matching the pattern used by other Hermes skills' scripts.

Config file: ~/.hermes/brain-bridge/config.yaml (copy from
config.example.yaml in this skill's folder and fill in).
Data/state:  ~/.hermes/brain-bridge/data/
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

HOME = Path.home()
USER_DIR = HOME / ".hermes" / "brain-bridge"
DATA_DIR = USER_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = USER_DIR / "config.yaml"

CURSORS_FILE = DATA_DIR / "cursors.json"
PROCESSED_IDS_FILE = DATA_DIR / "processed_ids.json"
SIGNALS_FILE = DATA_DIR / "signals.json"
TELEGRAM_STATE_FILE = DATA_DIR / "telegram_state.json"
GOOGLE_TOKEN_FILE = DATA_DIR / "google_token.json"


def _load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


_cfg = _load_config()


def _get(key: str, env_var: str, default: str = "") -> str:
    # Env var wins (lets a cron job or the agent override without editing
    # the file), then config.yaml, then default.
    return os.environ.get(env_var) or _cfg.get(key, default)


BRAIN_BASE_URL: str = _get("brain_base_url", "BRAIN_BASE_URL", "http://localhost:8000").rstrip("/")
BRAIN_API_KEY: str = _get("brain_api_key", "BRAIN_API_KEY", "")
TELEGRAM_BOT_TOKEN: str = _get("telegram_bot_token", "TELEGRAM_BOT_TOKEN", "")
SKOOL_COMMUNITY_URL: str = _get("skool_community_url", "SKOOL_COMMUNITY_URL", "")
GOOGLE_OAUTH_CLIENT_SECRET_FILE: str = _get(
    "google_oauth_client_secret_file", "GOOGLE_OAUTH_CLIENT_SECRET_FILE",
    str(USER_DIR / "google_credentials.json"),
)
PLAYWRIGHT_PROFILE_DIR = HOME / "AppData" / "Local" / "hermes" / "skool-profile" \
    if os.name == "nt" else HOME / ".hermes" / "brain-bridge" / "skool-profile"


def telegram_configured() -> bool:
    return bool(TELEGRAM_BOT_TOKEN)


def google_configured() -> bool:
    return Path(GOOGLE_OAUTH_CLIENT_SECRET_FILE).exists()


def skool_configured() -> bool:
    return bool(SKOOL_COMMUNITY_URL)
```

### `scripts/state.py`

```python
"""Cursors + processed-id dedupe, so a script never re-sends the same event
twice across cron runs (each run is a fresh process — state must be on
disk, not in memory)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _config as config

_MAX_PROCESSED_PER_SOURCE = 5000


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_cursor(name: str, default: str | None = None) -> str | None:
    return _load(config.CURSORS_FILE).get(name, default)


def set_cursor(name: str, value: str) -> None:
    data = _load(config.CURSORS_FILE)
    data[name] = value
    _save(config.CURSORS_FILE, data)


def is_processed(source: str, item_id: str) -> bool:
    data = _load(config.PROCESSED_IDS_FILE)
    return item_id in data.get(source, [])


def mark_processed(source: str, item_id: str) -> None:
    data = _load(config.PROCESSED_IDS_FILE)
    ids = data.setdefault(source, [])
    if item_id in ids:
        return
    ids.append(item_id)
    if len(ids) > _MAX_PROCESSED_PER_SOURCE:
        del ids[: len(ids) - _MAX_PROCESSED_PER_SOURCE]
    _save(config.PROCESSED_IDS_FILE, data)
```

### `scripts/signal_store.py`

```python
"""
Rolling "currently active" signal store.

The Brain only ever reads the SINGLE most recent digest push (no merging
across pushes — confirmed in brain/hermes_interface.py's
read_latest_digest()). So every digest push must carry the FULL set of
still-relevant signals, not just what's new since the last push, or an
older-but-unactioned item would silently vanish from every future briefing.

`add()` is called whenever the agent (or a script) identifies a new signal
worth surfacing (an email, a Skool post, whatever). `active_signals()` is
what push_digest.py sends.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _config as config

ACTIVE_WINDOW_HOURS = 48
PRUNE_WINDOW_HOURS = 72


def _load() -> dict:
    if not config.SIGNALS_FILE.exists():
        return {}
    try:
        return json.loads(config.SIGNALS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(data: dict) -> None:
    config.SIGNALS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def add(signal: dict) -> None:
    data = _load()
    data[signal["id"]] = signal
    _save(data)


def _parse_ts(signal: dict) -> datetime:
    try:
        ts = datetime.fromisoformat(signal["timestamp"].replace("Z", "+00:00"))
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def active_signals(window_hours: int = ACTIVE_WINDOW_HOURS) -> list[dict]:
    data = _load()
    now = datetime.now(timezone.utc)
    active_cutoff = now - timedelta(hours=window_hours)
    prune_cutoff = now - timedelta(hours=PRUNE_WINDOW_HOURS)

    kept, active = {}, []
    for sig_id, signal in data.items():
        ts = _parse_ts(signal)
        if ts < prune_cutoff:
            continue
        kept[sig_id] = signal
        if ts >= active_cutoff:
            active.append(signal)

    if len(kept) != len(data):
        _save(kept)

    active.sort(key=_parse_ts, reverse=True)
    return active
```

### `scripts/brain_client.py`

```python
"""
Every HTTP call to the Brain (Jim's operations co-founder — see
references/brain_contract.md in this skill for the full payload contract).

Retries on 5xx/network errors with backoff (1s, 4s, 15s); 4xx is not
retried (the payload itself is wrong, retrying won't help).
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _config as config

_BACKOFF_SECONDS = (1, 4, 15)


class BrainError(RuntimeError):
    pass


def _safe_json(raw: bytes) -> dict:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except ValueError:
        return {"_raw": raw.decode("utf-8", "replace")[:500]}


def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    if config.BRAIN_API_KEY:
        h["X-Brain-Key"] = config.BRAIN_API_KEY
    return h


def _request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{config.BRAIN_BASE_URL}{path}"
    data = json.dumps(body).encode() if body is not None else None
    last_error: Exception | None = None

    attempts = (0, *_BACKOFF_SECONDS)
    for attempt, delay in enumerate(attempts):
        if delay:
            time.sleep(delay)
        req = urllib.request.Request(url, data=data, method=method, headers=_headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return _safe_json(r.read())
        except urllib.error.HTTPError as e:
            payload = _safe_json(e.read())
            if e.code < 500:
                raise BrainError(f"{method} {path} -> {e.code}: {payload}") from e
            last_error = BrainError(f"{method} {path} -> {e.code}: {payload}")
            print(f"[brain_client] {method} {path} failed ({e.code}), attempt {attempt+1}/{len(attempts)}", file=sys.stderr)
        except urllib.error.URLError as e:
            last_error = BrainError(f"{method} {path} -> unreachable: {e}")
            print(f"[brain_client] {method} {path} unreachable, attempt {attempt+1}/{len(attempts)}", file=sys.stderr)

    raise last_error or BrainError(f"{method} {path} failed with no response")


def health() -> dict:
    return _request("GET", "/health")


def status() -> dict:
    return _request("GET", "/status")


def push_digest(digest: dict) -> dict:
    return _request("POST", "/webhook/digest", digest)


def push_metrics(metrics: dict) -> dict:
    return _request("POST", "/webhook/metrics", metrics)


def push_transcript(transcript: dict) -> dict:
    return _request("POST", "/webhook/transcript", transcript)


def push_calendar(calendar: dict) -> dict:
    return _request("POST", "/webhook/calendar", calendar)


def send_feedback(feedback: dict) -> dict:
    return _request("POST", "/feedback", feedback)


def list_pending() -> list[dict]:
    return _request("GET", "/outgoing/pending").get("messages", [])


def ack(message_id: str) -> dict:
    return _request("POST", f"/outgoing/{message_id}/ack", {})


def list_recent(limit: int = 20) -> list[dict]:
    return _request("GET", f"/outgoing/recent?limit={limit}").get("messages", [])


def try_health() -> tuple[bool, dict | str]:
    try:
        return True, health()
    except BrainError as e:
        return False, str(e)


if __name__ == "__main__":
    ok, result = try_health()
    print(f"Brain at {config.BRAIN_BASE_URL}: {'OK' if ok else 'UNREACHABLE'} — {result}")
```

### `scripts/push_digest.py`

```python
#!/usr/bin/env python3
"""
Push a digest to the Brain — the full active signal set (see
signal_store.py for why it's the full set, not just what's new).

Usage:
  python push_digest.py                        # push whatever's already active
  python push_digest.py --add signals.json      # add signals from a file, then push
  python push_digest.py --stdin                 # add signals from stdin JSON, then push

Signal JSON shape (a list of these — see references/brain_contract.md §5.1):
  {
    "id": "email_<gmail-message-id>" | "skool_<post-id>" | ...  (stable, unique)
    "source": "email" | "skool" | "telegram" | "transcript",
    "title": "...", "summary": "...", "priority": "high"|"medium"|"low",
    "timestamp": "2026-07-07T12:00:00Z", "raw_text": "...",
    "sender": "..." | null, "thread_id": "..." | null,
    "requires_response": true|false
  }

The agent (or a future scan script) is responsible for DECIDING what's
signal-worthy and shaping it into this JSON — this script just persists +
pushes. Run with no args on a schedule (--no-agent cron) to keep the digest
fresh even if nothing new came in since the last agent-driven pass.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import brain_client
import signal_store


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", help="JSON file with a list of new signals to add")
    parser.add_argument("--stdin", action="store_true", help="Read new signals as JSON from stdin")
    args = parser.parse_args()

    new_signals = []
    if args.add:
        new_signals = json.loads(Path(args.add).read_text(encoding="utf-8"))
    elif args.stdin:
        new_signals = json.loads(sys.stdin.read())

    for sig in new_signals:
        signal_store.add(sig)

    signals = signal_store.active_signals()
    now = datetime.now(timezone.utc)
    digest = {
        "signals": signals,
        "generated_at": now.isoformat(),
        "time_window_start": (now - timedelta(hours=signal_store.ACTIVE_WINDOW_HOURS)).isoformat(),
        "time_window_end": now.isoformat(),
    }

    try:
        res = brain_client.push_digest(digest)
    except brain_client.BrainError as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1

    print(f"Pushed digest: {len(signals)} active signals ({len(new_signals)} new). {res}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/push_metrics.py`

```python
#!/usr/bin/env python3
"""
Push a metrics snapshot to the Brain. Unlike digest, metrics are NOT a
rolling store — supply the full current set you want in today's briefing
each time (the Brain reads only the latest push per
brain/hermes_interface.py's read_metrics()).

Usage:
  python push_metrics.py --add metrics.json
  echo '[{"name":"Skool Members","value":512}]' | python push_metrics.py --stdin

Metric JSON shape (a list of these — see references/brain_contract.md §5.2):
  {"name": "Skool Members", "value": 512, "unit": "", "note": "..."}

`previous_value`/`trend` are computed automatically from the last push of
the same metric name (tracked in state.py) if you don't supply them.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import brain_client
import state


def _slug(name: str) -> str:
    return "metric_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _fill_trend(metric: dict) -> dict:
    cursor_key = _slug(metric["name"])
    prev = state.get_cursor(cursor_key)

    if "previous_value" not in metric or metric["previous_value"] is None:
        metric["previous_value"] = float(prev) if prev is not None else None

    if "trend" not in metric or metric["trend"] is None:
        if metric["previous_value"] is not None:
            if metric["value"] > metric["previous_value"]:
                metric["trend"] = "up"
            elif metric["value"] < metric["previous_value"]:
                metric["trend"] = "down"
            else:
                metric["trend"] = "flat"

    state.set_cursor(cursor_key, str(metric["value"]))
    return metric


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", help="JSON file with a list of metrics")
    parser.add_argument("--stdin", action="store_true", help="Read metrics as JSON from stdin")
    args = parser.parse_args()

    if args.add:
        metrics = json.loads(Path(args.add).read_text(encoding="utf-8"))
    elif args.stdin:
        metrics = json.loads(sys.stdin.read())
    else:
        print("FAILED: supply --add <file> or --stdin", file=sys.stderr)
        return 1

    metrics = [_fill_trend(dict(m, unit=m.get("unit", ""))) for m in metrics]

    snapshot = {"metrics": metrics, "timestamp": datetime.now(timezone.utc).isoformat()}
    try:
        res = brain_client.push_metrics(snapshot)
    except brain_client.BrainError as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1

    print(f"Pushed {len(metrics)} metrics: {res}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/push_transcript.py`

```python
#!/usr/bin/env python3
"""
Push a call transcript to the Brain — auto-analyzed, delivered to Jim.

Usage:
  python push_transcript.py --subject "Weekly Sync" --date 2026-07-07T10:00:00Z \
      --id fathom_abc123 --text-file transcript.txt

  cat transcript.txt | python push_transcript.py --subject "Weekly Sync" --id fathom_abc123

Dedupe: --id should be stable across retries (e.g. the source email's
Message-ID) — the Brain doesn't dedupe transcripts itself, so re-posting
the same id just re-analyzes and re-delivers it. Track what's already been
processed with state.py in the caller if you're scanning a mailbox.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import brain_client


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, help="Stable unique id for this call")
    parser.add_argument("--subject", default="Call", help="Call title")
    parser.add_argument("--date", default=None, help="ISO 8601 timestamp; default now")
    parser.add_argument("--participants", nargs="*", default=[])
    parser.add_argument("--duration-minutes", type=float, default=0.0)
    parser.add_argument("--source", default="fathom-email")
    parser.add_argument("--text-file", help="File with the transcript text; omit to read stdin")
    args = parser.parse_args()

    text = Path(args.text_file).read_text(encoding="utf-8") if args.text_file else sys.stdin.read()
    if not text.strip():
        print("FAILED: empty transcript text", file=sys.stderr)
        return 1

    date = args.date or datetime.now(timezone.utc).isoformat()
    transcript = {
        "id": args.id,
        "title": args.subject,
        "date": date,
        "participants": args.participants,
        "segments": [],
        "full_text": text,
        "source": args.source,
        "duration_minutes": args.duration_minutes,
    }

    try:
        res = brain_client.push_transcript(transcript)
    except brain_client.BrainError as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1

    print(f"Pushed transcript {args.id}: {res}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/push_calendar.py`

```python
#!/usr/bin/env python3
"""
Push the next 7 days of calendar events to the Brain.

Two modes:
  python push_calendar.py               # fetch via Google Calendar API directly (needs google_auth.py set up)
  python push_calendar.py --stdin       # push pre-fetched events JSON (agent already read the calendar itself)

Event JSON shape (see references/brain_contract.md §5.4):
  {"title": "...", "start": "iso", "end": "iso"|null, "attendees": [...],
   "location": "...", "notes": "...", "meeting_type": "coaching|podcast|discovery|speaking|personal|other"}
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import brain_client

_PODCAST_HINTS = ("podcast", "interview", "guest")
_DISCOVERY_HINTS = ("discovery", "intro call", "consult")
_COACHING_HINTS = ("coaching", "session")


def _guess_meeting_type(title: str) -> str:
    t = title.lower()
    if any(h in t for h in _PODCAST_HINTS):
        return "podcast"
    if any(h in t for h in _DISCOVERY_HINTS):
        return "discovery"
    if any(h in t for h in _COACHING_HINTS):
        return "coaching"
    return "other"


def _fetch_via_google(days_ahead: int = 7) -> list[dict]:
    import google_auth
    from googleapiclient.discovery import build

    creds = google_auth.get_credentials()
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    now = datetime.now(timezone.utc)

    result = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=(now + timedelta(days=days_ahead)).isoformat(),
        singleEvents=True, orderBy="startTime", maxResults=100,
    ).execute()

    events = []
    for item in result.get("items", []):
        if not item.get("start"):
            continue
        title = item.get("summary", "(no title)")
        events.append({
            "title": title,
            "start": item["start"].get("dateTime") or item["start"].get("date"),
            "end": item.get("end", {}).get("dateTime") or item.get("end", {}).get("date"),
            "attendees": [a.get("displayName") or a.get("email", "")
                          for a in item.get("attendees", []) if not a.get("self")],
            "location": item.get("location", ""),
            "notes": item.get("description", "") or "",
            "meeting_type": _guess_meeting_type(title),
        })
    return events


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdin", action="store_true", help="Read events JSON from stdin instead of fetching via Google")
    args = parser.parse_args()

    if args.stdin:
        events = json.loads(sys.stdin.read())
    else:
        try:
            events = _fetch_via_google()
        except Exception as e:
            print(f"FAILED to fetch calendar: {e}", file=sys.stderr)
            return 1

    snapshot = {"events": events, "timestamp": datetime.now(timezone.utc).isoformat()}
    try:
        res = brain_client.push_calendar(snapshot)
    except brain_client.BrainError as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1

    print(f"Pushed {len(events)} calendar events: {res}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/google_auth.py`

```python
"""
Google OAuth for Calendar read access — only needed if Jim's Hermes Agent
doesn't already have a Google Calendar connector/tool of its own. If it
does, prefer that (natural language: "check my calendar, format as a
CalendarSnapshot per references/brain_contract.md §5.4, run push_calendar.py
--stdin") over this script.

First run opens a browser for sign-in/consent. After that the refresh token
is cached at GOOGLE_TOKEN_FILE.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _config as config

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_credentials() -> Credentials:
    creds = None
    if config.GOOGLE_TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(config.GOOGLE_TOKEN_FILE), SCOPES)

    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save(creds)
        return creds

    secret_file = Path(config.GOOGLE_OAUTH_CLIENT_SECRET_FILE)
    if not secret_file.exists():
        raise RuntimeError(
            f"No Google OAuth client secret at {secret_file}. Download one "
            "from Google Cloud Console (Credentials -> OAuth client ID -> "
            "Desktop app) and save it there, or set "
            "GOOGLE_OAUTH_CLIENT_SECRET_FILE in config.yaml."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(secret_file), SCOPES)
    creds = flow.run_local_server(port=0)
    _save(creds)
    return creds


def _save(creds: Credentials) -> None:
    config.GOOGLE_TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")


if __name__ == "__main__":
    get_credentials()
    print(f"Authorized. Token cached at {config.GOOGLE_TOKEN_FILE}")
```

### `scripts/setup_skool_profile.py`

```python
#!/usr/bin/env python3
"""
One-time Skool login. Opens a real, visible browser window; log in as Jim
(2FA is fine, do it by hand), then press Enter here to save the session.
The persisted browser profile is then reused headless by scan_skool.py (or
by the agent itself, if it drives this same profile via its own browser
tool — see SKILL.md's "Agent-Driven Operation" section, which is the
recommended primary path since it adapts to Skool's DOM better than
scan_skool.py's hardcoded selectors).

Usage: python setup_skool_profile.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _config as config


def main() -> int:
    if not config.skool_configured():
        print("Set skool_community_url in config.yaml first.", file=sys.stderr)
        return 1

    from playwright.sync_api import sync_playwright

    config.PLAYWRIGHT_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(config.PLAYWRIGHT_PROFILE_DIR), headless=False,
        )
        page = context.new_page()
        page.goto(config.SKOOL_COMMUNITY_URL)
        print(
            "\nA browser window has opened. Log into Skool as Jim.\n"
            "Once you can see the community feed, come back here and press "
            "Enter to save the session.\n"
        )
        input("Press Enter once logged in... ")
        context.close()

    print(f"Session saved at {config.PLAYWRIGHT_PROFILE_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/scan_skool.py`

```python
#!/usr/bin/env python3
"""
Fallback scripted Skool scan — no LLM reasoning, cheap enough to run on a
schedule via --no-agent cron. SECONDARY to the agent-driven path (see
SKILL.md): these CSS selectors are best-effort scaffolding, not verified
against a live Skool community. Run with --debug first to dump the real
DOM and check/fix `_extract_posts` below before trusting this script's
output on a schedule.

Requires setup_skool_profile.py to have been run once.

Usage:
  python scan_skool.py               # print new signals as JSON (for push_digest.py --stdin)
  python scan_skool.py --debug       # dump screenshot + HTML for selector debugging
  python scan_skool.py --members     # print just the member count (int)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _config as config
import state


def _context(p, headless: bool):
    return p.chromium.launch_persistent_context(
        user_data_dir=str(config.PLAYWRIGHT_PROFILE_DIR), headless=headless,
    )


def debug_dump() -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        context = _context(p, headless=True)
        page = context.new_page()
        page.goto(config.SKOOL_COMMUNITY_URL)
        page.wait_for_timeout(3000)
        shot = config.DATA_DIR / "skool_debug.png"
        html = config.DATA_DIR / "skool_debug.html"
        page.screenshot(path=str(shot), full_page=True)
        html.write_text(page.content(), encoding="utf-8")
        context.close()
    print(f"Wrote {shot} and {html}")


def member_count() -> int | None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        context = _context(p, headless=True)
        page = context.new_page()
        page.goto(config.SKOOL_COMMUNITY_URL)
        page.wait_for_timeout(2000)
        text = page.inner_text("body")
        context.close()
    match = re.search(r"([\d,]+)\s+Members", text, re.IGNORECASE)
    return int(match.group(1).replace(",", "")) if match else None


def _extract_posts(page) -> list[dict]:
    """SEE MODULE DOCSTRING — verify against skool_debug.html before trusting."""
    posts = []
    for card in page.query_selector_all("a[href*='/posts/']"):
        href = card.get_attribute("href") or ""
        m = re.search(r"/posts/([a-zA-Z0-9_-]+)", href)
        if not m:
            continue
        posts.append({"id": m.group(1), "text": (card.inner_text() or "").strip()})
    return posts


def new_signals(limit: int = 20) -> list[dict]:
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            context = _context(p, headless=True)
            page = context.new_page()
            page.goto(config.SKOOL_COMMUNITY_URL)
            page.wait_for_timeout(2000)
            raw_posts = _extract_posts(page)
            context.close()
    except Exception as e:
        print(f"Skool fetch failed: {e}", file=sys.stderr)
        return []

    now = datetime.now(timezone.utc).isoformat()
    signals = []
    for post in raw_posts[:limit]:
        if state.is_processed("skool", post["id"]):
            continue
        state.mark_processed("skool", post["id"])
        title = post["text"].splitlines()[0][:120] if post["text"] else "Skool post"
        signals.append({
            "id": f"skool_{post['id']}", "source": "skool", "title": title,
            "summary": post["text"][:500], "priority": "medium", "timestamp": now,
            "raw_text": post["text"], "sender": None, "thread_id": post["id"],
            "requires_response": "?" in post["text"],
        })
    return signals


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--members", action="store_true")
    args = parser.parse_args()

    if not config.skool_configured():
        print("skool_community_url not set in config.yaml", file=sys.stderr)
        return 1

    if args.debug:
        debug_dump()
    elif args.members:
        print(member_count())
    else:
        print(json.dumps(new_signals(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/poll_feedback.py`

```python
#!/usr/bin/env python3
"""
One-shot Telegram poll: capture Jim's chat id on /start, and turn his
reactions/replies to Brain-delivered messages into feedback.

Uses the SAME bot token as the Brain (Brain only calls sendMessage; this
only calls getUpdates — they never collide). Meant to run on a schedule
(every ~2 min via --no-agent cron), not as a persistent loop — each run is
a short poll (timeout=15s) that picks up from where the last run left off
(offset cursor in state.py).

Feedback attribution is best-effort: since the Brain delivers directly and
marks a message delivered instantly, there's no literal reply-thread to
follow — this resolves to "the most recent thing the Brain sent"
(GET /outgoing/recent). See references/brain_contract.md.

Usage: python poll_feedback.py
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _config as config
import brain_client
import state

_API = "https://api.telegram.org/bot{token}/{method}"

_UP_MARKERS = {"👍", "❤", "❤️", "🔥", "💯", "+1"}
_DOWN_MARKERS = {"👎", "-1"}
_UP_WORDS = ("good", "nice", "great", "perfect", "love", "yes", "correct")
_DOWN_WORDS = ("wrong", "bad", "no", "not right", "too long", "incorrect", "hate")


def _call(method: str, **params) -> dict:
    url = _API.format(token=config.TELEGRAM_BOT_TOKEN, method=method)
    req = urllib.request.Request(url, data=json.dumps(params).encode(),
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.loads(r.read())
        if not body.get("ok"):
            raise RuntimeError(f"Telegram {method} failed: {body}")
        return body["result"]


def _contains_word(text: str, word: str) -> bool:
    return re.search(r"\b" + re.escape(word) + r"\b", text) is not None


def _classify(text: str) -> str:
    t = (text or "").strip().lower()
    if any(m in t for m in _UP_MARKERS) or any(_contains_word(t, w) for w in _UP_WORDS):
        return "up"
    if any(m in t for m in _DOWN_MARKERS) or any(_contains_word(t, w) for w in _DOWN_WORDS):
        return "down"
    return "neutral"


def _load_telegram_state() -> dict:
    if not config.TELEGRAM_STATE_FILE.exists():
        return {}
    try:
        return json.loads(config.TELEGRAM_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_telegram_state(data: dict) -> None:
    config.TELEGRAM_STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _capture_chat_id(chat_id: int) -> None:
    data = _load_telegram_state()
    if data.get("chat_id") == chat_id:
        return
    data["chat_id"] = chat_id
    _save_telegram_state(data)
    print(f"Captured Telegram chat_id={chat_id} — set this as TELEGRAM_CHAT_ID "
          f"on the Brain and redeploy.")


def _record_feedback(note: str) -> None:
    try:
        recent = brain_client.list_recent(limit=1)
    except brain_client.BrainError as e:
        print(f"Could not resolve feedback target: {e}", file=sys.stderr)
        return
    if not recent:
        print(f"No recent Brain message to attach feedback to; dropping: {note!r}")
        return

    target = recent[0]
    fb = {
        "target_kind": target["kind"], "target_ref": target["id"],
        "rating": _classify(note), "note": note, "tags": [],
    }
    try:
        brain_client.send_feedback(fb)
        print(f"Recorded feedback on {target['id']} ({target['kind']}): {note!r}")
    except brain_client.BrainError as e:
        print(f"Failed to record feedback: {e}", file=sys.stderr)


def _handle_message(msg: dict) -> None:
    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").strip()

    if text.startswith("/start"):
        if chat_id is not None:
            _capture_chat_id(chat_id)
            try:
                _call("sendMessage", chat_id=chat_id,
                      text="Connected. Your assistant is getting set up — you'll "
                           "start getting briefings and call summaries here soon.")
            except Exception:
                pass
        return

    if text:
        _record_feedback(text)


def _handle_message_reaction(reaction: dict) -> None:
    emojis = [r.get("emoji") for r in reaction.get("new_reaction", []) if r.get("type") == "emoji"]
    if emojis:
        _record_feedback(" ".join(emojis))


def main() -> int:
    if not config.telegram_configured():
        print("telegram_bot_token not set in config.yaml — nothing to do.")
        return 0

    offset = state.get_cursor("telegram_update_offset")
    offset = int(offset) if offset else None

    params = {"timeout": 15, "allowed_updates": ["message", "message_reaction"]}
    if offset is not None:
        params["offset"] = offset

    try:
        updates = _call("getUpdates", **params)
    except Exception as e:
        print(f"getUpdates failed: {e}", file=sys.stderr)
        return 1

    processed = 0
    for update in updates:
        try:
            if "message" in update:
                _handle_message(update["message"])
            elif "message_reaction" in update:
                _handle_message_reaction(update["message_reaction"])
            processed += 1
        except Exception as e:
            print(f"Failed processing update {update.get('update_id')}: {e}", file=sys.stderr)
        offset = update["update_id"] + 1

    if offset is not None:
        state.set_cursor("telegram_update_offset", str(offset))

    if processed:
        print(f"Processed {processed} Telegram update(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Step 2 — Create the cron dispatcher shims

`hermes cron create --script` requires the script path to live under
`~/.hermes/scripts/` (not inside the skill folder). Create these three thin
shims there — they just run the real scripts above:

### `~/.hermes/scripts/brain_poll_feedback.py`

```python
"""Thin dispatcher so `hermes cron create` (which requires --script to point
under ~/.hermes/scripts/) can run the real script that lives in the
brain-bridge skill folder, without duplicating it."""
import runpy
from pathlib import Path

runpy.run_path(
    str(Path.home() / ".hermes" / "skills" / "brain-bridge" / "scripts" / "poll_feedback.py"),
    run_name="__main__",
)
```

### `~/.hermes/scripts/brain_push_calendar.py`

```python
"""Thin dispatcher — see brain_poll_feedback.py for why this exists.
Runs push_calendar.py's direct Google Calendar API mode (no --stdin)."""
import runpy
from pathlib import Path

runpy.run_path(
    str(Path.home() / ".hermes" / "skills" / "brain-bridge" / "scripts" / "push_calendar.py"),
    run_name="__main__",
)
```

### `~/.hermes/scripts/brain_push_digest_refresh.py`

```python
"""Thin dispatcher — see brain_poll_feedback.py for why this exists.
No-arg push_digest.py run: re-pushes the current active signal set so the
Brain's digest doesn't look stale even on a tick with nothing new."""
import runpy
from pathlib import Path

runpy.run_path(
    str(Path.home() / ".hermes" / "skills" / "brain-bridge" / "scripts" / "push_digest.py"),
    run_name="__main__",
)
```

## Step 3 — Get two values and configure

Ask whoever gave you this document:

1. **The Brain's Railway URL** (e.g. `https://aibrain-production.up.railway.app`)
2. **The Telegram bot token** the Brain uses to deliver (from @BotFather —
   same token, you're only reading updates with it, never sending)

Then:

```bash
mkdir -p ~/.hermes/brain-bridge
cp ~/.hermes/skills/brain-bridge/config.example.yaml ~/.hermes/brain-bridge/config.yaml
# edit ~/.hermes/brain-bridge/config.yaml: set brain_base_url and telegram_bot_token
pip install pyyaml
```

## Step 4 — Verify

```bash
python ~/.hermes/skills/brain-bridge/scripts/brain_client.py
# should print: Brain at https://...: OK — {'status': 'ok', ...}

python ~/.hermes/skills/brain-bridge/scripts/poll_feedback.py
# should run without error (fine if it says nothing to process yet)
```

If `brain_client.py` says UNREACHABLE, stop and flag it — the Brain's
Railway deploy needs fixing before anything else here will work.

## Step 5 — Wire the scheduled jobs

Run these (adjust which ones apply — Calendar/Skool ones only if those are
in scope):

```bash
hermes cron create "2m" --name "brain-feedback" --no-agent \
  --script ~/.hermes/scripts/brain_poll_feedback.py --deliver local

hermes cron create "30m" --name "brain-digest-refresh" --no-agent \
  --script ~/.hermes/scripts/brain_push_digest_refresh.py --deliver local

hermes cron create "30m" --name "brain-signals" --skill brain-bridge \
  --deliver local \
  "Check for new emails and Skool activity since last run. Decide what's \
   worth surfacing to the Brain per the brain-bridge skill's contract \
   (references/brain_contract.md §3), then push via scripts/push_digest.py \
   --add. Report a one-line summary of what you pushed."

hermes cron create "15m" --name "brain-transcripts" --skill brain-bridge \
  --deliver local \
  "Check email for a new Fathom call-transcript message not yet processed. \
   If found, push it via scripts/push_transcript.py. If none, do nothing."

hermes cron create "0 22 40 * * *" --name "brain-metrics" --skill brain-bridge \
  --deliver local \
  "Compute today's available metrics (Skool member count via \
   scripts/scan_skool.py --members, and anything else you have access to), \
   then push via scripts/push_metrics.py --add."
```

Skip the calendar/Skool-specific ones (`brain-calendar` cron,
`setup_skool_profile.py`) unless those sources are actually in scope for
this setup — ask if unsure.

## Step 6 — Report back

Tell whoever's running this session:
- Whether `brain_client.py` connected successfully
- Which cron jobs got created (`hermes cron list`)
- Whether Skool/Calendar setup needs a human to click through a login (flag
  it, don't skip silently)
- That the loop is: Jim finishes a call → `brain-transcripts` picks it up
  within 15 min → Brain analyzes it → Jim gets it on Telegram within
  minutes. That's the thing to demo first.
