# 🚀 Client Setup Guide — Operations Co-Founder Brain

For: Jim Harshaw Jr. and anyone running the Brain dashboard on Windows

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Get Your API Key
1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Click **Keys** in the left menu
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-`)
6. Keep it safe — don't share it!

### Step 2: Install the Brain
1. Download the Brain folder
2. Double-click **`INSTALL.bat`**
3. Wait for installation to complete
4. When prompted, edit `.env` file:
   - Open `.env` in Notepad
   - Paste your API key after `ANTHROPIC_API_KEY=`
   - Save and close
5. Close the installer window

### Step 3: Run the Dashboard
Double-click **`START_DASHBOARD.bat`**

The dashboard will open in your browser at: **http://localhost:8501**

---

## 📋 What Each File Does

| File | Purpose |
|------|---------|
| **INSTALL.bat** | One-time setup (installs Python packages) |
| **START_DASHBOARD.bat** | Launches the dashboard (run this every time) |
| **.env** | Config file with your API key |
| **dashboard.py** | The actual dashboard app |

---

## 🎯 Using the Dashboard

### Every Time You Start
1. Double-click **`START_DASHBOARD.bat`**
2. Wait for "Streamlit ready to go"
3. Your browser opens automatically
4. Use the dashboard (see instructions below)
5. Press **CTRL+C** to stop

### The 4 Pages

#### 📋 Briefing
- Generates morning/evening updates
- Shows signals from Hermes
- Displays key metrics
- Items requiring your attention

#### 📞 Analyze Call
- Upload call transcripts (from Zoom, Fathom, etc.)
- Extracts decisions and follow-ups
- Shows what can be automated
- Organized in 5 tabs

#### 🔍 Strategic Lens
- Pressure-test decisions
- See perspectives from different strategic thinkers
- Get synthesized recommendations
- Make better decisions faster

#### 📚 History
- Browse past briefings
- Review call analyses
- See previous strategic lenses
- Everything timestamped

---

## 🔗 Connecting with Hermes

### How It Works
```
Hermes (running on your desktop)
    ↓ (saves files)
data/incoming/ (signals, metrics)
    ↓ (Brain reads)
Brain Dashboard
    ↓ (processes with Claude)
Results (briefings, analyses)
    ↓ (displays in)
Dashboard (http://localhost:8501)
```

### What Hermes Should Save

**Signals Digest** → `data/incoming/digest_*.json`
```json
{
  "signals": [...],
  "time_window_start": "2024-06-30T10:00:00Z",
  "time_window_end": "2024-06-30T18:00:00Z"
}
```

**Metrics** → `data/incoming/metrics_*.json`
```json
{
  "metrics": [
    {"name": "Clients", "value": 42, "unit": ""},
    ...
  ]
}
```

**Transcripts** → `data/transcripts/transcript_*.json`
```json
{
  "id": "call_001",
  "title": "Weekly Call",
  "participants": ["You", "Assistant"],
  "full_text": "...",
  ...
}
```

### Testing Without Hermes

Sample data is included! Open the dashboard and:
- **📋 Briefing** — generates from sample signals
- **📞 Analyze Call** — use sample transcript
- **🔍 Lens** — test with any decision

No Hermes needed to try it out!

---

## ⚙️ Configuration

### .env File Explained

```env
# Required: Your Claude API key
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Optional: Which Claude model to use
BRAIN_MODEL=claude-sonnet-4-20250514

# Optional: Where Hermes saves signals
HERMES_DIGEST_DIR=./data/incoming

# Optional: Where Hermes saves transcripts
HERMES_TRANSCRIPT_DIR=./data/transcripts
```

You only **need** to set `ANTHROPIC_API_KEY`. The others have good defaults.

---

## 🐛 Troubleshooting

### "Python is not installed"
1. Download Python 3.10+ from python.org
2. Run the installer
3. **IMPORTANT:** Check "Add Python to PATH"
4. Restart your computer
5. Try INSTALL.bat again

### "Failed to install dependencies"
1. Open Command Prompt (Win+R, type `cmd`)
2. Run: `pip install --upgrade pip`
3. Run: `pip install -r requirements.txt`
4. Try START_DASHBOARD.bat again

### "ANTHROPIC_API_KEY not configured"
1. Edit `.env` file (open with Notepad)
2. Find the line: `ANTHROPIC_API_KEY=`
3. Add your key: `ANTHROPIC_API_KEY=sk-ant-xxxxx`
4. Save the file
5. Try START_DASHBOARD.bat again

### "Streamlit not found"
1. Make sure INSTALL.bat completed without errors
2. Try running it again
3. If still failing, open Command Prompt and run:
   ```
   pip install streamlit anthropic pyyaml pydantic click python-dotenv
   ```

### Dashboard is slow
1. Close other browser tabs
2. Restart the dashboard (CTRL+C, then START_DASHBOARD.bat)
3. Give it 10-15 seconds to load

### "No data from Hermes"
This is normal! Hermes needs to be running and saving files to `data/incoming/`.

**Quick test:** Use the sample data that's already included (no Hermes needed)

---

## 📱 Accessing from Another Computer

### On Your Network
If you want to access the dashboard from another computer on the same network:

1. Find your computer's IP address:
   - Open Command Prompt
   - Type: `ipconfig`
   - Look for "IPv4 Address" (e.g., 192.168.1.100)

2. Open browser on other computer:
   - Go to: `http://192.168.1.100:8501`

**Note:** Only works if both computers are on same network.

### Via Internet
Not recommended for this version (no authentication). For remote access, we'd need to add security.

---

## 🔄 Keeping It Running

### Option 1: Manual (Simplest)
Double-click START_DASHBOARD.bat whenever you want to use it.

### Option 2: Startup Shortcut
Create a Windows shortcut that runs on startup:
1. Right-click on START_DASHBOARD.bat
2. Send to → Desktop (creates shortcut)
3. Windows+R, type `shell:startup`
4. Move shortcut to that folder
5. Dashboard starts when computer boots

### Option 3: Task Scheduler
Create a Windows scheduled task:
1. Windows+R, type `taskschd.msc`
2. Create Basic Task
3. Trigger: On startup (or time of day)
4. Action: Start program → START_DASHBOARD.bat
5. Check "Run whether user is logged in or not"

---

## 📞 Getting Help

### Common Questions

**Q: Can I run this on Mac/Linux?**
A: Yes! The Python code works everywhere. Skip the .bat files and run:
```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

**Q: Is my API key safe?**
A: Your key only leaves your computer to talk to Claude's API. Never shared elsewhere. Don't push .env to GitHub!

**Q: Can multiple people use it?**
A: Yes, if they're on the same network (see "Accessing from Another Computer" above).

**Q: What if I lose my API key?**
A: Create a new one at console.anthropic.com and update .env.

**Q: Do I need to install this every time?**
A: No! INSTALL.bat is one-time only. After that, just use START_DASHBOARD.bat.

---

## 📚 Learn More

- **How to Use Dashboard** → See `QUICK_START.md`
- **Visual Walkthrough** → See `VISUAL_GUIDE.md`
- **Design Details** → See `DASHBOARD_IMPROVEMENTS.md`

---

## ✅ Setup Checklist

- [ ] Downloaded Python 3.10+ and added to PATH
- [ ] Got API key from https://console.anthropic.com/
- [ ] Ran INSTALL.bat successfully
- [ ] Added API key to .env file
- [ ] Ran START_DASHBOARD.bat
- [ ] Dashboard opened in browser
- [ ] Tested briefing generation (uses sample data)
- [ ] Tested call analysis (uses sample transcript)
- [ ] Tested strategic lens (uses sample decision)

---

## 🎉 You're All Set!

**The Operations Co-Founder Brain is ready to use.**

Every morning:
1. Double-click START_DASHBOARD.bat
2. Go to 📋 Briefing
3. Review your morning briefing
4. Get clear on priorities for the day

When you have calls:
1. Upload the transcript
2. Go to 📞 Analyze Call
3. See decisions, follow-ups, what to delegate
4. Hand off tasks to your assistant

When making big decisions:
1. Go to 🔍 Strategic Lens
2. Enter your question
3. Get multiple perspectives
4. Synthesized recommendation

---

**Support your business. Amplify your thinking. The Brain is ready! 🚀**
