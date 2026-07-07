# Operations Co-Founder — Brain

An AI operations brain for Jim Harshaw Jr.'s coaching business. It reads what's
happening across his email, calls, and calendar, and tells him **what needs his
attention, what to delegate, and what's next** — delivered to Telegram.

## Architecture

Two agents, one job each:

- **Brain** (this repo) — the decision-maker. Runs 24/7 in the cloud. Takes in
  emails, call transcripts, calendar, and metrics; reasons over them; produces
  briefings, call analyses, and strategic advice; and texts Jim on Telegram. It
  never touches an app directly. Learns from Jim's reactions.
- **Hermes** (separate, runs on Jim's Mac) — the workhorse. This is Jim's
  existing [Hermes Agent](https://hermes-agent.nousresearch.com/) (Nous
  Research), a general-purpose AI agent already connected to his
  Telegram/email — not custom-built software. It reads email, calendar,
  Skool, and calls, and pushes the data to the Brain's webhooks via a skill
  (`brain-bridge`) loaded into it. Contract:
  [`HERMES_BUILD_BRIEF.md`](HERMES_BUILD_BRIEF.md).

```
Hermes (reads email/calendar/Skool/calls) ──▶ Brain (decides) ──▶ Telegram ──▶ Jim
                                                 ▲ learns from Jim's reactions ┘
```

## What's in here

```
brain/
  server.py          FastAPI automation server (webhooks in, Telegram out, scheduler)
  briefing.py        Morning/evening briefings (attention / delegate / next)
  analyst.py         Call-transcript analysis (decisions, follow-ups, delegation)
  lens.py            Strategic lens — pressure-test decisions via personas
  learning.py        Feedback → distilled "lessons" injected into every prompt
  poller.py          Optional email-ingestion fallback (IMAP; off unless configured)
  telegram.py        Direct delivery to Jim's Telegram
  delivery.py        Shared queue-and-deliver path
  hermes_interface.py, outbox.py, formatting.py, models.py, client.py
config/
  prompts.yaml       Prompt templates    personas.yaml   Strategic personas
dashboard.py         Operator UI (Streamlit) — for you, not Jim
main.py              CLI (brief / analyze / lens)
hermes_sim.py        Reference client: simulates Hermes' push/pull loop
Dockerfile, Procfile, docker-compose.yml   Deployment (Railway)
```

## Run it locally

```bash
pip install -r requirements.txt
cp .env.example .env        # set ANTHROPIC_API_KEY (and Telegram/email if testing those)
uvicorn brain.server:app --port 8000
```

Then exercise the whole loop against the running server:

```bash
python hermes_sim.py        # pushes data, generates a briefing, delivers, acks, feedback
```

Operator UI (optional): `streamlit run dashboard.py`.

## The Brain's API

Full contract in [`PHASE_2_API.md`](PHASE_2_API.md). In short:

- **In:** `POST /webhook/transcript` · `/webhook/digest` · `/webhook/calendar` · `/webhook/metrics`
- **Learn:** `POST /feedback`
- **Delivery:** automatic to Telegram (set `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`)
- **Ops:** `GET /health` · `GET /status` · `POST /telegram/test` · `POST /poll/email`

## Deploy & set up for Jim

Concierge model (you run it, Jim only sees Telegram). Step-by-step in
[`CONCIERGE_RUNBOOK.md`](CONCIERGE_RUNBOOK.md): deploy the Brain to Railway, set
env vars, create the Telegram bot, then a 15-minute setup session with Jim.

## Docs

- [`HERMES_BUILD_BRIEF.md`](HERMES_BUILD_BRIEF.md) — spec for the Hermes workhorse
- [`HERMES_SETUP.md`](HERMES_SETUP.md) — **hand this to Jim's Hermes Agent** and it self-installs the `brain-bridge` skill (files, config, cron jobs)
- [`PHASE_2_API.md`](PHASE_2_API.md) — the Brain's API contract
- [`CONCIERGE_RUNBOOK.md`](CONCIERGE_RUNBOOK.md) — deploy + onboard Jim
- [`email_to_jim.md`](email_to_jim.md) — the intro note to Jim
