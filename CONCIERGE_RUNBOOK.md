# Concierge Runbook — Getting Jim Live

Scope: one client (Jim), you set everything up. Jim's only surface is a
Telegram chat. Everything below is done by **you**, once.

---

## A. Operator prep (before Jim is involved)

1. **Deploy the Brain to Railway** (from `github.com/hegdermrs/aibrain`):
   - New Project → Deploy from GitHub → this repo.
   - Variables: `ANTHROPIC_API_KEY`, `BRAIN_MODEL=claude-sonnet-5`.
   - Add a **Volume mounted at `/app/data`** (so the outbox/data survive restarts).
   - Note the URL, e.g. `https://aibrain-production.up.railway.app`.
   - Test: open `<url>/health` → `{"status":"ok"}`.

2. **Create the Telegram bot:**
   - In Telegram, message **@BotFather** → `/newbot` → name it → save the **bot token**.
   - This is the bot Jim will talk to. Hermes uses the token to message him.

3. **Hermes** (the AI agent on Jim's desktop): have it ready, and give it the
   Brain URL + Telegram bot token. It will get Jim's chat id the moment Jim
   taps Start (step B1).

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
4. **Ask Jim these 5 questions**, type answers into the business profile
   (`hermes/state/business_profile.json` per the build brief):
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

Ship this before briefings — it needs nothing from Jim (Fathom already
records his calls). Give Hermes this prompt:

> You connect to the Brain at `<railway-url>`. Do two things continuously:
>
> **Deliver:** every ~2 minutes, GET `<railway-url>/outgoing/pending`. For each
> message, send its `text` to Jim on Telegram exactly as written, then POST
> `<railway-url>/outgoing/{id}/ack` with body `{}`.
>
> **Ingest calls:** whenever a Fathom transcript arrives in Jim's email, POST
> it to `<railway-url>/webhook/transcript` as JSON with fields: `id`, `title`,
> `date`, `participants` (list), `duration_minutes`, `segments` (use `[]`),
> `full_text` (the transcript), `source": "fathom"`. The Brain analyzes it and
> queues the summary — your deliver loop sends it to Jim.
>
> **Feedback:** when Jim reacts to a delivered message (👍/👎 or a reply), POST
> `<railway-url>/feedback` with `{target_kind, target_ref: <that message id>,
> rating, note, tags}`. This is what makes it improve.

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
