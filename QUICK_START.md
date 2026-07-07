# 🚀 Quick Start Guide — Brain Dashboard

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run the Dashboard
```bash
streamlit run dashboard.py
```

The dashboard will open at **http://localhost:8501**

---

## 📋 How to Use

### Generate a Briefing
1. Go to **📋 Briefing** page
2. Select **Morning ☀️** or **Evening 🌙**
3. The dashboard shows incoming signals from Hermes
4. Click **🚀 Generate Briefing**
5. Review results in tabs (Content | Metrics | Action Items)

**Note:** Requires Hermes to have dropped signal data in `data/incoming/digest_*.json`

### Analyze a Call
1. Go to **📞 Analyze Call** page
2. Upload a transcript JSON file
3. Review the transcript summary card
4. Click **📊 Analyze**
5. Browse results in tabs

**Transcript format:**
```json
{
  "id": "call_001",
  "title": "Weekly Assistant Call",
  "date": "2024-06-30T10:00:00Z",
  "participants": ["Jim", "Assistant"],
  "duration_minutes": 45,
  "segments": [
    {
      "speaker": "Jim",
      "text": "Let's talk about Q3 strategy...",
      "start_time": 0,
      "end_time": 120
    }
  ],
  "full_text": "Jim: Let's talk about...",
  "source": "zoom"
}
```

### Strategic Lens
1. Go to **🔍 Strategic Lens** page
2. Enter your decision/question
3. Add context (optional)
4. Select personas (Hormozi, Musk)
5. Add constraints (optional)
6. Click **🚀 Run Lens Analysis**
7. Review individual personas + synthesis

### Browse History
Go to **📚 History** to see all past:
- Briefings (with timestamps)
- Call analyses (with summaries)
- Strategic lens results (with personas used)

---

## 📁 Directory Structure

```
data/
├── incoming/              # Hermes drops digests here
│   ├── digest_*.json     # Signal collections
│   └── metrics_*.json    # Business metrics
├── transcripts/          # Call transcripts
│   └── transcript_*.json
├── briefings/            # Generated briefings
│   └── morning_*.json
│   └── evening_*.json
└── analysis/             # Generated analyses
    ├── call_*.json
    └── lens_*.json
```

---

## 🧪 Testing Without Hermes

Create sample data files to test:

### Test Digest (`data/incoming/digest_sample.json`)
```json
{
  "signals": [
    {
      "id": "sig_001",
      "source": "email",
      "title": "New client inquiry",
      "summary": "Potential enterprise client asking about Q3 programs",
      "priority": "high",
      "timestamp": "2024-06-30T09:00:00Z",
      "raw_text": "Hi Jim, I'm interested in your enterprise coaching...",
      "sender": "prospect@company.com",
      "requires_response": true
    },
    {
      "id": "sig_002",
      "source": "skool",
      "title": "Community engagement update",
      "summary": "2 new posts in Skool community, high engagement",
      "priority": "medium",
      "timestamp": "2024-06-30T08:30:00Z",
      "raw_text": "Post about summer coaching season...",
      "requires_response": false
    }
  ],
  "generated_at": "2024-06-30T10:00:00Z",
  "time_window_start": "2024-06-29T18:00:00Z",
  "time_window_end": "2024-06-30T10:00:00Z"
}
```

### Test Metrics (`data/incoming/metrics_sample.json`)
```json
{
  "metrics": [
    {
      "name": "Active Clients",
      "value": 42,
      "previous_value": 40,
      "unit": "",
      "trend": "up"
    },
    {
      "name": "Monthly Revenue",
      "value": 21000,
      "previous_value": 20000,
      "unit": "$",
      "trend": "up"
    },
    {
      "name": "Engagement Rate",
      "value": 87.5,
      "previous_value": 85,
      "unit": "%",
      "trend": "up"
    }
  ],
  "timestamp": "2024-06-30T10:00:00Z"
}
```

### Test Transcript (`data/transcripts/transcript_sample.json`)
```json
{
  "id": "call_001",
  "title": "Weekly Strategy Call — Jun 30",
  "date": "2024-06-30T10:00:00Z",
  "participants": ["Jim Harshaw", "Sarah (Assistant)"],
  "duration_minutes": 45,
  "segments": [
    {
      "speaker": "Jim",
      "text": "Let's start with the Skool community. How's engagement looking?",
      "start_time": 0,
      "end_time": 30
    },
    {
      "speaker": "Sarah",
      "text": "Really strong this week. We got 200+ new members and engagement is up 15%.",
      "start_time": 30,
      "end_time": 60
    },
    {
      "speaker": "Jim",
      "text": "Excellent. Let's capitalize on this. I want to launch a group coaching pilot.",
      "start_time": 60,
      "end_time": 90
    },
    {
      "speaker": "Sarah",
      "text": "I'll start researching group coaching platforms and send options by Friday.",
      "start_time": 90,
      "end_time": 120
    }
  ],
  "full_text": "Jim: Let's start with the Skool community. Sarah: Really strong this week. We got 200+ new members...",
  "source": "zoom"
}
```

**To test:** Place these JSON files in the `data/` directories, then upload or generate briefings through the dashboard.

---

## 🔧 Environment Variables

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional (defaults shown)
BRAIN_MODEL=claude-sonnet-4-20250514
HERMES_DIGEST_DIR=./data/incoming
HERMES_TRANSCRIPT_DIR=./data/transcripts
```

---

## 📊 Status Indicators Explained

### Hermes Connection
- 🟢 **Live** (✅) — Data received in last 60 minutes
- 🟡 **Stale** (⏱️) — Data is 60-180 minutes old
- 🔴 **Offline** (❌) — No data in 3+ hours or missing

### Claude API
- 🟢 **Ready** (✅) — API key configured, ready to go
- 🔴 **Error** (❌) — API key missing or invalid

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `r` | Rerun page |
| `c` | Clear cache |
| `CTRL+R` | Hard refresh |

---

## 🐛 Troubleshooting

### "No data from Hermes yet"
- Check that Hermes is running and dropping files to `data/incoming/`
- Check file permissions
- Verify `HERMES_DIGEST_DIR` path in `.env`

### "No API key found"
- Add `ANTHROPIC_API_KEY` to `.env`
- Verify key is valid on platform.anthropic.com

### "Analysis failed"
- Check Claude API status
- Ensure transcript/digest JSON is valid
- Check console for detailed error

### Dashboard is slow
- Check available RAM
- Close other browser tabs
- Restart Streamlit: `CTRL+C` then `streamlit run dashboard.py`

---

## 📚 Architecture Reminder

```
┌─────────────────────────────────────────┐
│        Hermes (The Hands)               │
│  - Runs 24/7                            │
│  - Owns browser (Skool, Gmail)          │
│  - Surfaces signals via JSON files      │
└──────────────────┬──────────────────────┘
                   │
        (file-based integration)
                   │
                   ▼
┌─────────────────────────────────────────┐
│      Brain (This Project)               │
│  - Pure synthesis & strategy            │
│  - Reads Hermes signals                 │
│  - Uses Claude for analysis             │
│  - Generates briefings & insights       │
└──────────────────┬──────────────────────┘
                   │
        (JSON outputs to disk)
                   │
                   ▼
        ┌──────────────────┐
        │  CLI or Dashboard│
        │  (for Jim)       │
        └──────────────────┘
```

---

## 🎯 Next: Phase 2 Autonomy

Once Phase 1 is working well, Phase 2 will add:
- 🔄 File watchers (auto-analyze transcripts)
- ⏰ Scheduled briefings (7am & 6pm daily)
- 🔗 Hermes webhook (real-time updates)
- 📱 Direct Telegram delivery
- 🚀 One-click automation setup

---

## 💬 Questions?

- Check `DASHBOARD_IMPROVEMENTS.md` for design details
- See `main.py` for CLI commands
- Review `brain/` for architecture
- Check `.env.example` for config reference
