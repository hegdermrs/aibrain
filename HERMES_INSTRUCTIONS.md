# 📋 Hermes Instructions — What to Capture & How

Instructions for Hermes to feed data to the Brain.

---

## 🎯 Hermes' Job

Hermes watches Jim's digital life and surfaces signals to the Brain:

```
Hermes (the Hands - 24/7 automation)
    ├── Watches Skool (community platform)
    ├── Monitors Email (Gmail)
    ├── Tracks Telegram (messages)
    └── Captures Transcripts (calls)
         ↓ (saves as JSON files)
Brain (the Thinks - synthesizes daily)
    ├── Generates briefings
    ├── Analyzes calls
    └── Pressure-tests decisions
```

---

## 📁 Save Locations

Hermes must save files to:

```
D:\Work\APPS\Brain\data\
├── incoming/
│   ├── digest_YYYYMMDD_HHMM.json      (signals summary)
│   └── metrics_YYYYMMDD_HHMM.json     (business metrics)
└── transcripts/
    └── transcript_YYYYMMDD_HHMM.json  (call transcripts)
```

---

## 📊 What to Capture

### 1. SIGNALS (from Skool, Email, Telegram)

**From Skool:**
- New community posts (high engagement)
- New member signups
- Comments on Jim's posts
- Member milestones (100th member, etc.)
- High engagement content
- Questions requiring Jim's response

**From Email:**
- New client inquiries
- Important client messages
- Vendor/partner updates
- Time-sensitive emails
- Emails with "decision needed" in subject
- Calendar invites (meetings, deadlines)

**From Telegram:**
- Messages from Jim's assistant (Sarah)
- Questions that need response
- Status updates from automation
- Alerts/notifications

**What counts as HIGH PRIORITY:**
- Client inquiries or issues
- Urgent responses needed
- Revenue-related (invoices, payments, deals)
- New high-value opportunities
- Milestones (member count, revenue records)
- Questions requiring Jim's decision

**What counts as MEDIUM PRIORITY:**
- Regular engagement updates
- Non-urgent follow-ups
- General community activity
- Administrative updates
- Routine reports

**What counts as LOW PRIORITY:**
- Minor community activity
- Informational only
- No action needed
- Background context

---

## 📝 File Format: Digest (Signals)

**Filename:** `digest_YYYYMMDD_HHMM.json`  
**Save to:** `D:\Work\APPS\Brain\data\incoming\`  
**Frequency:** 2x daily (morning + evening) or whenever significant signals appear

**JSON Schema:**

```json
{
  "signals": [
    {
      "id": "sig_001",
      "source": "email|skool|telegram|transcript",
      "title": "Brief title (< 80 chars)",
      "summary": "1-2 sentence summary of what this is",
      "priority": "high|medium|low",
      "timestamp": "2024-06-30T14:30:00Z",
      "raw_text": "Full content of the signal (email body, post text, etc.)",
      "sender": "person@email.com or @username (optional)",
      "thread_id": "email_thread_id or skool_post_id (optional)",
      "requires_response": true/false
    }
  ],
  "generated_at": "2024-06-30T14:35:00Z",
  "time_window_start": "2024-06-30T08:00:00Z",
  "time_window_end": "2024-06-30T14:35:00Z"
}
```

**Example Signal (Email):**
```json
{
  "id": "sig_email_001",
  "source": "email",
  "title": "Enterprise client inquiry - $50K opportunity",
  "summary": "Fortune 500 company inquiring about executive coaching program for Q3. Contact: Sarah@acme.com",
  "priority": "high",
  "timestamp": "2024-06-30T09:15:00Z",
  "raw_text": "Hi Jim,\n\nWe've heard great things about your coaching approach...",
  "sender": "sarah@acme.com",
  "thread_id": "thread_abc123",
  "requires_response": true
}
```

**Example Signal (Skool):**
```json
{
  "id": "sig_skool_001",
  "source": "skool",
  "title": "Community milestone: 500 active members",
  "summary": "Skool community hit 500 active members. Engagement up 22% this week.",
  "priority": "high",
  "timestamp": "2024-06-30T08:45:00Z",
  "raw_text": "🎉 Community Milestone\n\nWe just crossed 500 active members...",
  "sender": "skool_bot",
  "requires_response": false
}
```

**Key Rules:**
- `timestamp`: When the signal happened (ISO 8601 format)
- `priority`: HIGH for urgent/revenue/important, MEDIUM for routine, LOW for FYI
- `requires_response`: true if Jim needs to reply or take action
- `raw_text`: Full content, not truncated
- `sender`: Who sent it (email, Telegram user, Skool username)
- `thread_id`: For grouping related signals together

---

## 💰 Metrics (Business Data)

**Filename:** `metrics_YYYYMMDD_HHMM.json`  
**Save to:** `D:\Work\APPS\Brain\data\incoming\`  
**Frequency:** Daily (or whenever metrics change significantly)

**JSON Schema:**

```json
{
  "metrics": [
    {
      "name": "Metric Name",
      "value": 42,
      "previous_value": 40,
      "unit": "clients|$|%|hours|etc",
      "trend": "up|down|flat",
      "note": "Additional context (optional)"
    }
  ],
  "timestamp": "2024-06-30T14:35:00Z"
}
```

**Example Metrics:**

```json
{
  "metrics": [
    {
      "name": "Active Clients",
      "value": 42,
      "previous_value": 40,
      "unit": "",
      "trend": "up",
      "note": "2 new onboardings this week"
    },
    {
      "name": "Monthly Recurring Revenue",
      "value": 21000,
      "previous_value": 20000,
      "unit": "$",
      "trend": "up",
      "note": "Up from price optimization"
    },
    {
      "name": "Skool Community Engagement",
      "value": 87.5,
      "previous_value": 85,
      "unit": "%",
      "trend": "up",
      "note": "500-member milestone reached"
    },
    {
      "name": "Average Client Satisfaction",
      "value": 9.2,
      "previous_value": 9.1,
      "unit": "/10",
      "trend": "up"
    },
    {
      "name": "Waitlist",
      "value": 12,
      "previous_value": 9,
      "unit": " people",
      "trend": "up"
    }
  ],
  "timestamp": "2024-06-30T14:35:00Z"
}
```

**Key Metrics to Track:**
- Active clients / members
- Monthly recurring revenue (MRR)
- Engagement rates (Skool, email, etc.)
- Conversion rates (inquiries → clients)
- Client satisfaction scores
- Waitlist size
- Program completion rates

---

## 🎤 Call Transcripts

**Filename:** `transcript_YYYYMMDD_HHMM.json`  
**Save to:** `D:\Work\APPS\Brain\data\transcripts\`  
**Frequency:** After each call (real-time or batched)

**JSON Schema:**

```json
{
  "id": "call_20240630_100000",
  "title": "Weekly Strategy Call - Jim & Sarah",
  "date": "2024-06-30T10:00:00Z",
  "participants": ["Jim Harshaw", "Sarah (Assistant)"],
  "duration_minutes": 45,
  "segments": [
    {
      "speaker": "Jim Harshaw",
      "text": "Let's start with what we saw this week.",
      "start_time": 0,
      "end_time": 30
    },
    {
      "speaker": "Sarah",
      "text": "Really strong week. Community hit 500 members...",
      "start_time": 30,
      "end_time": 120
    }
  ],
  "full_text": "Complete transcript as one continuous string. Jim: Let's start... Sarah: Really strong week...",
  "source": "zoom|fathom|meet|other"
}
```

**Key Rules:**
- `id`: Unique identifier (use timestamp pattern)
- `date`: When call happened (ISO 8601)
- `participants`: List of people on the call
- `duration_minutes`: Total call length
- `segments`: Array of speaker/text with timestamps
- `full_text`: Complete transcript (single string, not array)
- `source`: Where transcript came from (Zoom, Fathom, Google Meet)

**Example Transcript:**

```json
{
  "id": "call_20240627_100000",
  "title": "Weekly Strategy Call with Sarah — Jun 27",
  "date": "2024-06-27T10:00:00Z",
  "participants": ["Jim Harshaw", "Sarah (Operations Assistant)"],
  "duration_minutes": 45,
  "segments": [
    {
      "speaker": "Jim",
      "text": "Hey Sarah, let's kick off. How's the Skool community?",
      "start_time": 0,
      "end_time": 30
    },
    {
      "speaker": "Sarah",
      "text": "500 active members, engagement up 22%. People are fired up.",
      "start_time": 30,
      "end_time": 60
    },
    {
      "speaker": "Jim",
      "text": "Excellent. We need a group coaching option. Can you research platforms?",
      "start_time": 60,
      "end_time": 120
    }
  ],
  "full_text": "Jim: Hey Sarah, let's kick off. How's the Skool community? Sarah: 500 active members...",
  "source": "zoom"
}
```

---

## ⏰ Cron Schedule

### Recommended Schedule

```cron
# Morning digest (8:30 AM)
30 8 * * * hermes collect-signals && hermes save-digest morning

# Evening digest (6:30 PM)
30 18 * * * hermes collect-signals && hermes save-digest evening

# Metrics snapshot (Daily at 7 PM)
0 19 * * * hermes collect-metrics && hermes save-metrics

# Call transcripts (Real-time, or batch at 9 PM)
0 21 * * * hermes collect-transcripts && hermes save-transcripts
```

**Or if running as daemon:**
```python
# Every 4 hours
hermes collect-signals && hermes save-digest
# Every 6 hours
hermes collect-metrics && hermes save-metrics
# Every time a call ends
hermes detect-call-end && hermes save-transcript
```

---

## 🔄 Digest Timing

### Option A: Daily Digests (Recommended)
- **Morning (8:30 AM):** Signals from overnight + yesterday
- **Evening (6:30 PM):** Signals from today

**Use for:** Jim checks in twice daily (morning priorities, evening recap)

### Option B: Continuous Digests
- **Every 2-4 hours:** New digest with latest signals
- **Real-time:** Brain dashboard auto-updates

**Use for:** Always-on monitoring, more granular updates

### Option C: On-Demand
- **Only when significant event occurs:** New client, milestone, urgent issue
- **Plus daily summary:** Batch smaller signals

**Use for:** Minimal notification fatigue, focus on urgent only

---

## 📋 Checklist for Hermes Implementation

### Email Collection
- [ ] Connect to Gmail API
- [ ] Filter by sender priority (known clients, partners)
- [ ] Detect urgent flags (HIGH, URGENT, etc.)
- [ ] Extract sender, subject, body
- [ ] Identify requires_response (action items, questions)
- [ ] Format as signals with high/medium/low priority

### Skool Collection
- [ ] Connect to Skool API or scrape
- [ ] Track new members
- [ ] Monitor engagement (reactions, comments, posts)
- [ ] Identify trending posts
- [ ] Track community health metrics
- [ ] Format as signals with appropriate priority

### Telegram Collection
- [ ] Connect to Telegram Bot API
- [ ] Listen for messages from Sarah (assistant)
- [ ] Filter noise (don't capture bot spam)
- [ ] Extract questions requiring response
- [ ] Flag action items
- [ ] Format as signals

### Call Transcription
- [ ] Connect to Zoom/Fathom/Meet API
- [ ] Auto-detect when calls end
- [ ] Fetch transcript
- [ ] Format segments with speaker + time
- [ ] Combine into full_text
- [ ] Save within 1 hour of call end

### Metrics Collection
- [ ] Query client database (active clients count)
- [ ] Calculate MRR (revenue data)
- [ ] Pull engagement metrics (Skool, email)
- [ ] Satisfaction scores (if available)
- [ ] Waitlist size
- [ ] Compare to previous day/week

### File Management
- [ ] Create data/incoming/ if doesn't exist
- [ ] Create data/transcripts/ if doesn't exist
- [ ] Use correct filename format (digest_YYYYMMDD_HHMM.json)
- [ ] Validate JSON before saving
- [ ] Keep latest 10 digests, archive old ones

---

## 🔍 Quality Checks

Before Hermes saves a digest, it should verify:

```python
# Check 1: Valid JSON
try:
    json.loads(digest_json)
except:
    log_error("Invalid JSON")

# Check 2: Required fields
required = ["signals", "generated_at", "time_window_start", "time_window_end"]
for field in required:
    if field not in digest:
        log_error(f"Missing {field}")

# Check 3: Timestamp is recent
generated_at = parse_timestamp(digest["generated_at"])
if (now - generated_at).seconds > 3600:
    log_warning("Digest is stale")

# Check 4: At least one signal
if len(digest["signals"]) == 0:
    log_info("No signals captured (OK for low-activity periods)")

# Check 5: Signal timestamps are in time_window
for signal in digest["signals"]:
    if not (start < signal["timestamp"] < end):
        log_warning(f"Signal timestamp outside window: {signal['id']}")
```

---

## 💡 Pro Tips for Hermes

### Priority Logic
Use this to determine if a signal is HIGH priority:

```python
is_high_priority = any([
    "URGENT" in email_subject,
    email_sender in VIP_CLIENTS,
    "decision needed" in email_body,
    "revenue" in email_body.lower(),
    new_client_inquiry,
    community_milestone,
    urgent_skool_post,
    message_from_assistant,
])
```

### Response Detection
Use this to flag requires_response:

```python
requires_response = any([
    "?" in subject or body,  # Question
    "RSVP" in body,          # Needs confirmation
    "reply" in body.lower(), # Explicitly asks
    from_known_contact,      # Important person
    urgent_priority,         # High priority = likely needs response
    "Jim" mentioned in body, # Directly addressing Jim
])
```

### Batch vs Real-Time
- **Important signals** (client, revenue, decision): Save immediately
- **Routine signals** (engagement, updates): Batch into scheduled digest
- **Low-priority signals** (FYI only): Include in evening digest only

---

## 🚀 Next Steps

Once Hermes is saving correctly:

1. **Verify files exist:**
   ```bash
   ls -la data/incoming/digest_*.json
   ls -la data/transcripts/transcript_*.json
   ```

2. **Test with Brain:**
   ```bash
   streamlit run dashboard.py
   # Check sidebar status
   # Generate briefing
   # Analyze transcript
   ```

3. **Monitor for 1 week:**
   - Check digest quality
   - Verify all signals captured
   - Adjust priorities if needed
   - Refine filters

4. **Plan Phase 2:**
   - Auto-analysis of calls
   - Scheduled briefings
   - Telegram delivery
   - Webhook integration

---

## 📞 Debug Commands

### Check Digest Format
```bash
python -m json.tool data/incoming/digest_*.json | head -50
```

### Check Signal Count
```bash
python -c "import json; d=json.load(open('data/incoming/digest_*.json')); print(f'Signals: {len(d[\"signals\"])}')"
```

### Check File Age
```bash
ls -lh data/incoming/digest_*.json
# Should be recent (< 180 minutes old)
```

### Validate All Digests
```bash
for f in data/incoming/digest_*.json; do
    python -m json.tool "$f" > /dev/null && echo "✓ $f" || echo "✗ $f"
done
```

---

## 🎯 Summary

**Hermes should:**
1. ✅ Watch Skool, Email, Telegram for signals
2. ✅ Save signals as JSON to `data/incoming/digest_*.json`
3. ✅ Save business metrics to `data/incoming/metrics_*.json`
4. ✅ Save transcripts to `data/transcripts/transcript_*.json`
5. ✅ Run on cron schedule (2x daily for digests, as-needed for transcripts)
6. ✅ Use correct JSON format (see schemas above)
7. ✅ Mark priorities accurately (HIGH/MEDIUM/LOW)
8. ✅ Keep timestamps recent

**Brain will:**
1. ✅ Read latest digest files
2. ✅ Generate briefings from signals
3. ✅ Analyze transcripts
4. ✅ Show status in sidebar

---

**Give these instructions to Hermes and you're ready to test! 🚀**
