# 📋 Instructions for Hermes — Copy & Paste

Give these to whoever is implementing Hermes.

---

## 🎯 Quick Summary

Hermes watches Jim's digital life and saves signals to JSON files:

```
Watch:          Save:                                    Brain reads:
Skool    ──┐    ─→ data/incoming/digest_*.json    ──┐
Email    ──┼──→                                      ├──→ Generates briefings
Telegram ──┘    ─→ data/incoming/metrics_*.json   ──┤
Calls    ──────→ data/transcripts/transcript_*.json──┘
```

---

## 📂 Two Files to Read

**For implementers:**
1. `HERMES_INSTRUCTIONS.md` — Full specifications (all details)
2. `HERMES_QUICK_REFERENCE.md` — Quick checklist (TL;DR)

**Copy the JSON schemas from HERMES_INSTRUCTIONS.md**

---

## ⚡ Quick Start

### What to Capture
- **Email:** Client inquiries, urgent messages, decisions needed
- **Skool:** New members, engagement, milestones
- **Telegram:** Messages from Sarah (assistant), status updates
- **Calls:** Transcripts from Zoom/Fathom/Google Meet

### Where to Save
```
D:\Work\APPS\Brain\data\incoming\digest_YYYYMMDD_HHMM.json
D:\Work\APPS\Brain\data\incoming\metrics_YYYYMMDD_HHMM.json
D:\Work\APPS\Brain\data\transcripts\transcript_YYYYMMDD_HHMM.json
```

### When to Save (Cron Schedule)
```
8:30 AM  - Signals (overnight + morning)
6:30 PM  - Signals (rest of day)
7:00 PM  - Metrics
9:00 PM  - Transcripts (or real-time after calls)
```

### How to Save (JSON Format)
See JSON schemas in `HERMES_INSTRUCTIONS.md`

**Key rules:**
- Valid JSON (no syntax errors)
- Timestamps in ISO 8601 format (2024-06-30T14:30:00Z)
- Priorities: HIGH, MEDIUM, LOW
- Full content in `raw_text` (not truncated)
- Recent timestamps (< 180 min old)

---

## 📝 Document Reference

| Task | Read This |
|------|-----------|
| Understand requirements | `HERMES_INSTRUCTIONS.md` (full details) |
| Quick checklist | `HERMES_QUICK_REFERENCE.md` (TL;DR) |
| Email collection | HERMES_INSTRUCTIONS.md → "Email Collection" |
| Skool collection | HERMES_INSTRUCTIONS.md → "Skool Collection" |
| Telegram integration | HERMES_INSTRUCTIONS.md → "Telegram Collection" |
| Call transcripts | HERMES_INSTRUCTIONS.md → "Call Transcription" |
| Metrics tracking | HERMES_INSTRUCTIONS.md → "Metrics Collection" |
| JSON schemas | HERMES_INSTRUCTIONS.md → "File Format" |
| Cron setup | HERMES_INSTRUCTIONS.md → "Cron Schedule" |
| Debugging | HERMES_INSTRUCTIONS.md → "Debug Commands" |

---

## ✅ Verification

Once implemented, Hermes should:

```bash
# Files exist and are recent
ls -lh data/incoming/digest_*.json
ls -lh data/transcripts/transcript_*.json

# JSON is valid
python -m json.tool data/incoming/digest_*.json

# Brain can read it
streamlit run dashboard.py
# Sidebar shows: Hermes: [time] ago ✅
```

---

## 🚀 Integration Test

1. Hermes running (saving files)
2. Brain dashboard running (`streamlit run dashboard.py`)
3. Check sidebar: Hermes status should show ✅ Live
4. Go to 📋 Briefing
5. Click "Generate Briefing"
6. Should use real Hermes signals!

---

## 📞 If Stuck

1. Check `HERMES_QUICK_REFERENCE.md` for quick fixes
2. Read `HERMES_INSTRUCTIONS.md` for detailed specs
3. Verify file format matches JSON schema
4. Validate JSON with: `python -m json.tool file.json`
5. Check timestamps are recent
6. Check file locations are correct

---

## 💡 Key Points

- Signals = notifications/events from email/Skool/Telegram
- Metrics = business numbers (clients, revenue, etc.)
- Transcripts = call recordings with full text
- Priority = HIGH/MEDIUM/LOW (determines importance)
- Format = JSON (exact schema in HERMES_INSTRUCTIONS.md)
- Schedule = Cron jobs 2x daily for signals, as-needed for calls
- Location = Exact paths in `data/` folder
- Timestamps = ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)

---

## ✨ That's All Hermes Needs to Do

Everything else is Brain's job!

Brain will:
- ✅ Generate daily briefings
- ✅ Analyze call transcripts
- ✅ Synthesize decisions
- ✅ Pressure-test plans
- ✅ Show everything in dashboard

Hermes just needs to:
- ✅ Watch (email, Skool, Telegram, calls)
- ✅ Save (as JSON)
- ✅ Keep it fresh (recent timestamps)
- ✅ Follow the format (use schemas)

---

**Give `HERMES_INSTRUCTIONS.md` to the implementer. That's everything they need! 🚀**
