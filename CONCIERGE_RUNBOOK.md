# Concierge Runbook — Getting Jim Live

Scope: one client (Jim), you set everything up. Jim's only surface is a
Telegram chat. Everything below is done by **you**, once.

---

## A. Operator prep (before Jim is involved)

1. **Deploy the Brain to Railway** (from `github.com/hegdermrs/aibrain`):
   - New Project → Deploy from GitHub → this repo.
   - Variables (minimum): `ANTHROPIC_API_KEY`, `BRAIN_MODEL=claude-sonnet-5`.
   - For direct Telegram delivery, also: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
   - Optional email fallback (Fathom-via-email, no Mac needed): `EMAIL_ADDRESS`,
     `EMAIL_APP_PASSWORD` (Gmail app password), `EMAIL_POLL_MINUTES`.
   - Add a **Volume mounted at `/app/data`** (so the outbox/data survive restarts).
   - Note the URL, e.g. `https://aibrain-production.up.railway.app`.
   - Test: open `<url>/health` → `{"status":"ok"}`.

2. **Create the Telegram bot:**
   - In Telegram, message **@BotFather** → `/newbot` → name it → save the **bot token**.
   - Set it as `TELEGRAM_BOT_TOKEN` on Railway. Jim's `TELEGRAM_CHAT_ID` is
     captured when he taps Start (step B1) — set it and redeploy.
   - Verify with `POST <url>/telegram/test` → Jim's phone should buzz.

3. **Hermes** — this is Jim's existing
   [Hermes Agent](https://hermes-agent.nousresearch.com/) install on his
   Mac, already connected to his Telegram/email. **On the call with Jim,
   paste him [`HERMES_SETUP.md`](HERMES_SETUP.md) and ask him to give it to
   his Hermes Agent** ("please set this up for me") — it self-installs the
   `brain-bridge` skill (writes its own files, asks him for the Brain's URL
   + the Telegram bot token from step 2, wires the `hermes cron create`
   jobs, and reports back what it did). You shouldn't need to touch his Mac
   directly. It'll flag if Skool/Calendar need a browser login only he can
   click through — that's expected, not a failure.

---

## B. Setup day with Jim (~15 min, you drive a screen-share)

1. **Jim taps Start** on the bot (send him the link, or add him). Hermes now
   knows his chat id.
2. **Jim logs into Google and Fathom** in the browser Hermes uses (he just
   signs in / clicks "allow"). This is what lets Hermes read his email and
   pick up call transcripts — no API keys, uses his own logins.
3. **In Fathom:** turn on **auto-share transcript to email** (Settings →
   sharing/notifications). Now every recorded call emails a transcript into
   the Gmail Hermes already watches.
4. **Ask Jim these 5 questions out loud** — no file to type them into; his
   Hermes Agent has its own persistent memory/user-modeling and will absorb
   the context from the conversation itself:
   1. What are your main offers and prices?
   2. Who's on your team, and who handles what (especially your assistant)?
   3. What should I always flag as urgent / interrupt you for?
   4. What does your week look like — calls, standing meetings, cadence?
   5. How do you want updates — how brief, and what times morning/evening?
5. **Live test:** you POST a briefing, Hermes delivers it, Jim watches it
   land on his phone:
   ```
   curl.exe -X POST <railway-url>/briefing/run -H "Content-Type: application/json" -d "{\"type\":\"morning\"}"
   ```
   Jim sees a morning briefing in Telegram → done. Setup complete.

That's Jim's entire involvement. From here he only receives and replies.

---

## C. First value: the call-summary loop

Ship this before briefings — it needs nothing from Jim beyond Fathom
auto-share (already on from step A3). The `brain-bridge` skill covers this
loop already — you're wiring cron jobs, not hand-writing it:

- The "brain-transcripts" cron job (agent-driven, every 15 min per the
  skill's "Scheduled Runs" section) checks email for a new Fathom
  transcript and runs `scripts/push_transcript.py`, which `POST`s to
  `<railway-url>/webhook/transcript`. The Brain analyzes it and delivers
  the summary straight to Jim's Telegram.
- Feedback (👍/👎 or a reply) is captured by the "brain-feedback" cron job
  (`--no-agent`, every ~2 min) running `scripts/poll_feedback.py`, which
  long-polls the Brain's bot token for Jim's reactions and `POST`s
  `/feedback`, resolving which message he means via `GET /outgoing/recent`.
- `GET /outgoing/pending` → send → ack only matters as a fallback if direct
  Telegram delivery is ever unconfigured on the Brain — not part of this
  skill's normal operation.

Result: Jim finishes a call → minutes later gets decisions + follow-ups texted
to him. That alone justifies the whole system.

---

## D. Then add briefings

Point Hermes at Jim's Gmail/Skool to build signals and push a fresh digest a
couple times a day (`POST /webhook/digest`). The Brain generates morning +
evening briefings on its schedule; your deliver loop already handles them.
(Full source/cadence details are in `HERMES_BUILD_BRIEF.md`.)

---

## E. Keeping it running (your job, not Jim's)

- Brain on Railway is always-on; check `<url>/status` occasionally (digest
  age, pending count, lessons learned).
- Hermes on Jim's desktop should **auto-start on boot** so a reboot doesn't
  break it.
- If something fails, you fix it — Jim should never see an error or restart
  anything. His experience is only ever "the assistant texts me."

---

## What Jim never touches

No dashboard, no logins after setup day, no API keys, no servers, no installs.
The Streamlit dashboard and all the deploy/hosting docs in this repo are for
**you**, the operator — not him.
