# 🧠 Operations Co-Founder Brain

AI-powered operations assistant for your coaching business. Synthesizes signals from Hermes, analyzes calls, and pressure-tests decisions.

---

## ⚡ Quick Start

### Windows
```
1. Double-click: INSTALL.bat
2. Edit .env and add API key
3. Double-click: START_DASHBOARD.bat
```

### Mac or Linux
```bash
1. chmod +x install.sh start_dashboard.sh
2. ./install.sh
3. Edit .env and add API key
4. ./start_dashboard.sh
```

Opens at: **http://localhost:8501**

---

## 🎯 What It Does

### 📋 Generate Daily Briefings
- Morning and evening updates
- Synthesizes signals from Hermes
- Shows key metrics
- Flags items needing your attention

### 📞 Analyze Call Transcripts
- Upload calls (Zoom, Fathom, Meet)
- Extracts decisions made
- Lists follow-ups with owners
- Shows what can be automated
- Identifies key themes

### 🔍 Pressure-Test Decisions
- Ask a question or decision
- Get perspectives from strategic thinkers
- See potential blind spots
- Get synthesized recommendations

### 📚 Browse History
- Past briefings (morning/evening)
- Call analyses
- Strategic lens results
- Everything timestamped

---

## 🔗 Works with Hermes

The Brain reads signals that Hermes surfaces:
- **Emails** → Priority signals
- **Skool posts** → Community activity
- **Metrics** → Business KPIs
- **Transcripts** → Call recordings

---

## 📂 Files You Need to Know

| File | What | When |
|------|------|------|
| `INSTALL.bat` | Setup script | Run once |
| `START_DASHBOARD.bat` | Launch script | Run every time |
| `.env` | Config (API key) | Edit after INSTALL |
| `dashboard.py` | The app | Auto-starts |

---

## ❓ Troubleshooting

**"Python not found"**
- Install Python 3.10+ from python.org
- Make sure to check "Add to PATH"

**"API key error"**
- Edit `.env` file
- Add your key from console.anthropic.com
- Save and try again

**"Hermes data not showing"**
- Normal if Hermes isn't running
- Try the sample data included
- Works offline for testing

See `CLIENT_SETUP.md` for more help.

---

## 📖 Full Documentation

- **`CLIENT_SETUP.md`** ← Read this first (detailed setup guide)
- **`QUICK_START.md`** — How to use the dashboard
- **`VISUAL_GUIDE.md`** — Page-by-page walkthrough
- **`DASHBOARD_IMPROVEMENTS.md`** — Design & features

---

## 🎯 Typical Workflow

### Morning
1. Run START_DASHBOARD.bat
2. Go to 📋 Briefing
3. Review priorities for the day

### After Calls
1. Upload transcript
2. Go to 📞 Analyze Call
3. Review decisions & follow-ups

### Making Big Decisions
1. Go to 🔍 Strategic Lens
2. Enter your question
3. Get multiple perspectives

### Admin
1. Go to 📚 History
2. Review past work
3. Track patterns

---

## ⚙️ What You Need

- Windows 10+ (or Mac/Linux)
- Python 3.10+ (INSTALL.bat sets it up)
- Claude API key (free tier available)
- Hermes running (optional, sample data included)

---

## 🚀 First Time?

1. **Read:** `CLIENT_SETUP.md` (has full setup guide)
2. **Run:** `INSTALL.bat` (one-time installation)
3. **Launch:** `START_DASHBOARD.bat` (every time)
4. **Test:** Use sample data (Briefing, Call, Lens)

---

## 💡 Pro Tips

- Sample data included — test without Hermes
- Dashboard is responsive — works on phone too
- Real-time status shows if Hermes is connected
- All results saved automatically (in `data/` folder)

---

## 💻 Platform Support

- **Windows 10+** → Use `INSTALL.bat` and `START_DASHBOARD.bat`
- **Mac** → Use `install.sh` and `start_dashboard.sh` (see `MAC_LINUX_SETUP.md`)
- **Linux** → Use `install.sh` and `start_dashboard.sh` (see `MAC_LINUX_SETUP.md`)

---

## 📞 Support

- **Windows setup?** → See `CLIENT_SETUP.md`
- **Mac/Linux setup?** → See `MAC_LINUX_SETUP.md`
- **How to use?** → See `QUICK_START.md`
- **Visual walkthrough?** → See `VISUAL_GUIDE.md`

---

**Brain thinks. Hermes acts. You win. 🧠**
