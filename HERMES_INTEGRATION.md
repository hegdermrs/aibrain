# 🔗 Hermes Integration Guide

Test the Brain with your actual Hermes instance running on your desktop.

---

## 🎯 How It Works

```
Hermes (running on desktop)
    ↓ (watches browser, saves files)
data/incoming/
    ├── digest_*.json      (signals from email, Skool, Telegram)
    └── metrics_*.json     (business metrics)
data/transcripts/
    └── transcript_*.json  (call recordings)
    ↓ (Brain reads)
Brain Dashboard
    ↓ (processes with Claude)
Results on http://localhost:8501
```

---

## 📋 What Hermes Should Save

### 1. Signal Digests → `data/incoming/digest_*.json`

**File format:**
```json
{
  "signals": [
    {
      "id": "unique_id",
      "source": "email|skool|telegram|transcript",
      "title": "Signal title",
      "summary": "Brief summary (1-2 sentences)",
      "priority": "high|medium|low",
      "timestamp": "2024-06-30T14:30:00Z",
      "raw_text": "Full content of the signal",
      "sender": "who sent it (optional)",
      "thread_id": "email thread ID (optional)",
      "requires_response": true/false
    }
  ],
  "generated_at": "2024-06-30T14:35:00Z",
  "time_window_start": "2024-06-30T08:00:00Z",
  "time_window_end": "2024-06-30T14:35:00Z"
}
```

**Filename:** `digest_20240630_0835.json` (any timestamp pattern)

**What signals to capture:**
- 📧 **Email** → New messages to Jim
- 🎯 **Skool** → Community posts, new members, engagement
- 📱 **Telegram** → Messages from Jim's assistant
- 🎤 **Transcript** → If saving call transcripts here

---

### 2. Business Metrics → `data/incoming/metrics_*.json`

**File format:**
```json
{
  "metrics": [
    {
      "name": "Active Clients",
      "value": 42,
      "previous_value": 40,
      "unit": "",
      "trend": "up|down|flat",
      "note": "Details about the metric (optional)"
    },
    {
      "name": "Monthly Revenue",
      "value": 21000,
      "previous_value": 20000,
      "unit": "$",
      "trend": "up"
    }
  ],
  "timestamp": "2024-06-30T14:35:00Z"
}
```

**Filename:** `metrics_20240630_0835.json`

**What metrics to track:**
- 💰 Revenue (MRR, daily, weekly)
- 👥 Active clients/members
- 📊 Engagement rates
- 🎯 Conversion metrics
- 📈 Growth indicators

---

### 3. Call Transcripts → `data/transcripts/transcript_*.json`

**File format:**
```json
{
  "id": "unique_call_id",
  "title": "Call title (e.g., 'Weekly Strategy Call')",
  "date": "2024-06-30T10:00:00Z",
  "participants": ["Jim Harshaw", "Sarah (Assistant)", "Coach"],
  "duration_minutes": 45,
  "segments": [
    {
      "speaker": "Jim Harshaw",
      "text": "What we discussed...",
      "start_time": 0,
      "end_time": 120
    },
    {
      "speaker": "Sarah",
      "text": "Response...",
      "start_time": 120,
      "end_time": 240
    }
  ],
  "full_text": "Complete transcript as one string",
  "source": "zoom|fathom|meet|other"
}
```

**Filename:** `transcript_20240630_1000.json`

---

## 📁 Directory Structure

Brain expects this structure:

```
D:\Work\APPS\Brain\
└── data/
    ├── incoming/              (Hermes saves here)
    │   ├── digest_*.json     (multiple files, latest is used)
    │   └── metrics_*.json    (multiple files, latest is used)
    ├── transcripts/          (Hermes saves here)
    │   └── transcript_*.json (multiple files)
    ├── briefings/            (Brain creates)
    │   ├── morning_*.json
    │   └── evening_*.json
    └── analysis/             (Brain creates)
        ├── call_*.json
        └── lens_*.json
```

**Hermes only needs to create files in:**
- `data/incoming/`
- `data/transcripts/`

**Brain auto-creates the other folders.**

---

## 🧪 Testing Integration

### Step 1: Start Brain Dashboard
```bash
streamlit run dashboard.py
```
Opens at: http://localhost:8501

### Step 2: Check Sidebar Status
- Go to **🧠 Operations Co-Founder Brain**
- Look at **📊 System Status**
- Should show:
  - Hermes: ⏱️ Stale or ❌ Offline (normal at first)
  - Claude API: ✅ Ready

### Step 3: Run Hermes
Start your Hermes instance to create signal files.

### Step 4: Refresh Dashboard
- Refresh browser (F5)
- Check System Status again
- Hermes should now show: 🟢 Live (if data is fresh)

### Step 5: Test Briefing Generation
1. Go to **📋 Briefing** page
2. Should see "Incoming Signals" dashboard
3. Click **🚀 Generate Briefing**
4. Should work with real Hermes data!

### Step 6: Test Call Analysis
1. Have Hermes capture a call transcript
2. Save to `data/transcripts/`
3. Go to **📞 Analyze Call** page
4. Click "Recent Transcripts" tab
5. Should see your real call
6. Click **📊 Analyze**

### Step 7: Test Strategic Lens
1. Go to **🔍 Strategic Lens**
2. Enter a real business question
3. Click **🚀 Run Lens Analysis**
4. Should work with live Claude API

---

## 🔍 Debugging Checklist

### "Hermes: Offline" in Status
**Means:** No digest file found in `data/incoming/`

**Check:**
- [ ] Hermes is running
- [ ] Hermes created `data/incoming/digest_*.json`
- [ ] File has valid JSON
- [ ] File has `generated_at` timestamp
- [ ] Timestamp is recent (< 180 min old)

**Test:**
```bash
# Check if file exists
ls -la data/incoming/digest_*.json

# Check file content
cat data/incoming/digest_*.json | python -m json.tool
```

### "No signals shown" in Briefing Page
**Means:** Digest exists but has no signals

**Check:**
- [ ] Digest JSON has `signals` array
- [ ] Array is not empty
- [ ] Each signal has required fields (id, source, title, summary)

**Expected structure:**
```json
{
  "signals": [
    {
      "id": "sig_001",
      "source": "email",
      "title": "...",
      "summary": "..."
    }
  ]
}
```

### "Generate Briefing" button disabled
**Means:** Either no API key or no digest data

**Check:**
- [ ] ANTHROPIC_API_KEY is set in `.env`
- [ ] API key is valid (from console.anthropic.com)
- [ ] Digest file exists (not offline)

### Analysis not working
**Means:** Transcript format issue

**Check:**
- [ ] Transcript JSON is valid
- [ ] Has required fields: id, title, date, participants, full_text
- [ ] `full_text` has meaningful content (not empty)

---

## 📊 Monitoring Hermes Integration

### Dashboard Status Indicators

**Hermes Connection:**
- 🟢 **Live** — Data received in last 60 minutes ✅
- 🟡 **Stale** — Data is 60-180 minutes old ⚠️
- 🔴 **Offline** — No data in 3+ hours ❌

**Claude API:**
- ✅ **Ready** — API key configured and valid
- ❌ **Error** — API key missing or invalid

### Logs to Check

**Streamlit console (where you ran `streamlit run dashboard.py`):**
```
# Should see:
- Streamlit version
- Dashboard loaded
- No errors
```

**File timestamps:**
```bash
# Should show recent files (< 180 min old)
ls -lt data/incoming/ | head
ls -lt data/transcripts/ | head
```

---

## 🔄 Real-Time Workflow

### Morning Briefing
```
1. Hermes runs overnight, saves signals
2. You start dashboard at 7am
3. Go to 📋 Briefing
4. Click "Generate Briefing"
5. Get morning priorities
```

### After Call
```
1. Jim has call
2. Hermes records & transcribes (Fathom/Zoom)
3. Hermes saves transcript to data/transcripts/
4. You upload to Brain
5. Go to 📞 Analyze Call
6. See decisions, follow-ups, delegates
```

### Before Decision
```
1. Jim has big decision
2. You go to 🔍 Strategic Lens
3. Enter decision question
4. Get multi-perspective analysis
5. Help Jim decide
```

---

## 📞 Testing with Hermes

### Test 1: Live Signal Flow
1. Check if Hermes is creating digest files
2. Open Brain dashboard
3. Status should show "Live" or recent timestamp
4. Generate briefing
5. Should use real signals

### Test 2: Real Call Analysis
1. Have Hermes save actual call transcript
2. Go to Brain → 📞 Analyze Call
3. Upload the transcript
4. Analyze
5. Should extract real decisions/follow-ups

### Test 3: End-to-End
1. Hermes running 24/7
2. Brain dashboard accessible
3. Generate briefing (uses real signals)
4. Analyze call (uses real transcript)
5. Test strategic lens (uses real question)
6. All pages working with live data

---

## 🎯 Integration Verification

### Checklist

- [ ] Hermes is running on desktop
- [ ] Brain dashboard is running (streamlit run dashboard.py)
- [ ] Hermes creating files in `data/incoming/`
- [ ] Dashboard status shows "Live" (not offline)
- [ ] Generate Briefing button is enabled
- [ ] Generated briefing shows real signals
- [ ] Hermes saving transcripts to `data/transcripts/`
- [ ] Can upload and analyze real calls
- [ ] Strategic Lens working with Claude API
- [ ] Sample data test still works
- [ ] All 4 pages functioning

---

## 🚀 Next Steps

### If Everything Works:
1. Keep Brain running
2. Let Hermes collect real data for a week
3. Generate daily briefings
4. Analyze real calls
5. Use strategic lens for decisions
6. Gather feedback

### If Issues Occur:
1. Check Hermes file output (see debugging section)
2. Verify JSON format (use `python -m json.tool`)
3. Check timestamps (must be recent)
4. Review console logs
5. Restart dashboard if needed

### For Production:
1. Deploy to cloud (Railway, Streamlit Cloud)
2. Configure Hermes to save to cloud storage (if needed)
3. Set up scheduled briefings
4. Add webhook integration
5. Connect Telegram delivery

---

## 💡 Pro Tips

**Real-time Status:**
- Dashboard sidebar shows Hermes connection age
- Refresh browser to see latest digest

**File Organization:**
- Hermes can save multiple digest files
- Brain uses the latest one
- Older files are ignored (clean up monthly)

**Testing Without Hermes:**
- Sample data is in `data/` folders
- Works even if Hermes is offline
- Good for testing dashboard functionality

**Performance:**
- Dashboard loads in ~2-5 seconds
- Generating briefings takes 15-30 seconds
- Analyzing calls takes 20-40 seconds

---

## 📚 Reference

**Hermes should create:**
- `data/incoming/digest_YYYYMMDD_HHMM.json` (signals)
- `data/incoming/metrics_YYYYMMDD_HHMM.json` (metrics)
- `data/transcripts/transcript_YYYYMMDD_HHMM.json` (calls)

**Brain reads from:**
- `data/incoming/` (latest digest + metrics)
- `data/transcripts/` (all transcripts)
- `data/briefings/` (saves results)
- `data/analysis/` (saves results)

---

**Ready to test with live Hermes data? Start the dashboard and let Hermes start feeding it! 🚀**
