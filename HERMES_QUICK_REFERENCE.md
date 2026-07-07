# 🎯 Hermes Quick Reference — TL;DR

What Hermes needs to do. Copy and use.

---

## 📍 Save Locations

```
D:\Work\APPS\Brain\data\incoming\digest_YYYYMMDD_HHMM.json
D:\Work\APPS\Brain\data\incoming\metrics_YYYYMMDD_HHMM.json
D:\Work\APPS\Brain\data\transcripts\transcript_YYYYMMDD_HHMM.json
```

---

## 📊 What to Capture

### Signals (Email, Skool, Telegram)

| Source | What | Priority | Example |
|--------|------|----------|---------|
| Email | Client inquiries | HIGH | "New $50K opportunity" |
| Email | Urgent questions | HIGH | "Decision needed by EOD" |
| Email | Vendor/partner updates | MEDIUM | "Invoice received" |
| Skool | Community milestones | HIGH | "500 members!" |
| Skool | High engagement posts | MEDIUM | "New member introduction" |
| Skool | Regular activity | LOW | "Jane posted in community" |
| Telegram | From Sarah (assistant) | MEDIUM-HIGH | Questions, status updates |
| Telegram | Notifications | LOW | "Invoice sent" |

### Metrics

- Active clients
- Monthly revenue
- Community engagement %
- Client satisfaction
- Waitlist size
- Any other KPIs Jim tracks

---

## 💾 File Format (Copy This)

### Digest (Signals)
```json
{
  "signals": [
    {
      "id": "sig_001",
      "source": "email|skool|telegram",
      "title": "Brief title",
      "summary": "1-2 sentences",
      "priority": "high|medium|low",
      "timestamp": "2024-06-30T14:30:00Z",
      "raw_text": "Full content here",
      "sender": "person@email.com",
      "requires_response": true/false
    }
  ],
  "generated_at": "2024-06-30T14:35:00Z",
  "time_window_start": "2024-06-30T08:00:00Z",
  "time_window_end": "2024-06-30T14:35:00Z"
}
```

### Metrics
```json
{
  "metrics": [
    {
      "name": "Active Clients",
      "value": 42,
      "previous_value": 40,
      "unit": "",
      "trend": "up"
    }
  ],
  "timestamp": "2024-06-30T14:35:00Z"
}
```

### Transcript
```json
{
  "id": "call_20240630_100000",
  "title": "Weekly Strategy Call",
  "date": "2024-06-30T10:00:00Z",
  "participants": ["Jim Harshaw", "Sarah"],
  "duration_minutes": 45,
  "segments": [
    {
      "speaker": "Jim",
      "text": "What Jim said",
      "start_time": 0,
      "end_time": 30
    }
  ],
  "full_text": "Complete transcript as one string",
  "source": "zoom|fathom|meet"
}
```

---

## ⏰ Cron Jobs

```cron
# Morning signals (8:30 AM)
30 8 * * * /path/to/hermes collect-signals morning

# Evening signals (6:30 PM)
30 18 * * * /path/to/hermes collect-signals evening

# Daily metrics (7 PM)
0 19 * * * /path/to/hermes collect-metrics

# Transcripts (after calls, or 9 PM batch)
0 21 * * * /path/to/hermes collect-transcripts
```

---

## ✅ Priority Rules

### HIGH Priority
- Client inquiries
- Revenue-related
- Urgent response needed
- Milestones/records
- "Decision needed" in subject

### MEDIUM Priority
- Regular updates
- Community activity
- Status reports
- Questions (not urgent)

### LOW Priority
- FYI only
- No action needed
- Background info
- Routine notifications

---

## 🔍 Quick Checks

Before saving, verify:

- [ ] Valid JSON (no syntax errors)
- [ ] Has all required fields
- [ ] Timestamps are ISO 8601 format
- [ ] `generated_at` is recent (within last hour)
- [ ] Signals are in correct time window
- [ ] Priorities are accurate (high/medium/low)
- [ ] `raw_text` is not empty
- [ ] IDs are unique

---

## 📁 File Naming

```
digest_20240630_0830.json    ✓ Correct
digest_20240630.json         ✗ Missing time
metrics_20240630_1900.json   ✓ Correct
transcript_20240627_1000.json ✓ Correct
```

**Pattern:** `{type}_{YYYYMMDD}_{HHMM}.json`

---

## 🚀 Testing

```bash
# Check files exist
ls data/incoming/digest_*.json
ls data/transcripts/transcript_*.json

# Validate JSON
python -m json.tool data/incoming/digest_*.json

# Check in Brain
streamlit run dashboard.py
# Sidebar should show: Hermes: [time] ago ✅
```

---

## 💡 Common Issues

| Issue | Fix |
|-------|-----|
| "Hermes: Offline" | Files not created or too old |
| "No signals shown" | Digest exists but empty signals array |
| "Invalid JSON" | Syntax error in file (extra comma, quote, etc.) |
| "Timestamp error" | Use ISO 8601 format: `2024-06-30T14:30:00Z` |
| "File not found" | Save to correct path with correct filename |

---

## 🎯 One Page Summary

Hermes **watches** Jim's:
- Email (Gmail) → clients, partners
- Skool (community) → members, engagement
- Telegram (assistant) → messages, status
- Calls (Zoom/Fathom) → transcripts

Hermes **saves** as JSON:
- Signals → `data/incoming/digest_*.json`
- Metrics → `data/incoming/metrics_*.json`
- Transcripts → `data/transcripts/transcript_*.json`

Brain **reads** these files and:
- Generates briefings from signals
- Analyzes transcripts
- Synthesizes into decisions

---

## 📞 Questions?

See `HERMES_INSTRUCTIONS.md` for full details.

Key sections:
- Signals schema (detailed)
- Metrics schema (detailed)
- Transcript schema (detailed)
- Priority logic (how to decide HIGH/MEDIUM/LOW)
- Quality checks (validation)
- Cron scheduling (timing)

---

**That's it! Save files in the right format to the right location on the right schedule. Brain does the rest. 🚀**
