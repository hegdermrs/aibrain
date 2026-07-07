# 🍎 Mac & Linux Setup Guide

The Operations Co-Founder Brain works great on Mac and Linux! Just use different setup scripts.

---

## ⚡ Quick Setup (Mac or Linux)

### Step 1: Get Your API Key
1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Click **Keys**
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-`)

### Step 2: Make Scripts Executable
Open Terminal and run:
```bash
chmod +x install.sh start_dashboard.sh
```

### Step 3: Install Everything
```bash
./install.sh
```
- Installs Python packages
- Creates `.env` file
- Asks you to add API key

### Step 4: Add Your API Key
1. Open `.env` file in your editor
2. Find: `ANTHROPIC_API_KEY=`
3. Add your key: `ANTHROPIC_API_KEY=sk-ant-xxxxx`
4. Save

### Step 5: Start Dashboard
```bash
./start_dashboard.sh
```

Opens at: **http://localhost:8501**

---

## 📋 Using the Dashboard

### Every Time
```bash
./start_dashboard.sh
```

### To Stop
Press **CTRL+C** in the terminal

---

## 🍎 Mac-Specific Notes

### If Python Isn't Installed
```bash
# Using Homebrew (easiest)
brew install python3

# Or download from python.org
```

### If Homebrew Isn't Installed
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Making Scripts Executable
```bash
chmod +x install.sh start_dashboard.sh
```

### Running from Finder
1. Open Terminal
2. Navigate to Brain folder: `cd ~/Downloads/Brain` (or wherever it is)
3. Run: `./start_dashboard.sh`

---

## 🐧 Linux-Specific Notes

### Install Python (if needed)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip
```

**Arch:**
```bash
sudo pacman -S python python-pip
```

### Make Scripts Executable
```bash
chmod +x install.sh start_dashboard.sh
```

### Run from Terminal
```bash
./start_dashboard.sh
```

---

## 📁 File Structure (Same on All Platforms)

```
Brain/
├── install.sh                     ← Run once (Mac/Linux)
├── install.bat                    ← Run once (Windows)
├── start_dashboard.sh             ← Run every time (Mac/Linux)
├── START_DASHBOARD.bat            ← Run every time (Windows)
├── .env.example                   → becomes .env
├── README.md
├── CLIENT_SETUP.md
├── dashboard.py
├── brain/
├── config/
└── data/
```

---

## 🔧 Environment Setup

### .env File (Same on All Platforms)

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

---

## 🐛 Troubleshooting

### "Python not found"
```bash
# Check if Python 3 is installed
python3 --version

# If not, install it
brew install python3        # Mac
sudo apt install python3    # Linux
```

### "Permission denied" when running scripts
```bash
# Make scripts executable
chmod +x install.sh start_dashboard.sh
```

### "ModuleNotFoundError" after install
```bash
# Reinstall packages
pip3 install -r requirements.txt
```

### "API key error"
1. Edit `.env` file
2. Make sure the line is exactly: `ANTHROPIC_API_KEY=sk-ant-xxxxx`
3. No spaces, no quotes, no extra characters
4. Save and try again

### Dashboard is slow
1. Close other browser tabs
2. Restart dashboard (CTRL+C, then `./start_dashboard.sh`)
3. Give it 10-15 seconds to load

---

## 🔗 Integration with Hermes

Same as Windows! Brain reads from:
```
data/incoming/digest_*.json       (signals)
data/incoming/metrics_*.json      (metrics)
data/transcripts/transcript_*.json (calls)
```

Hermes just needs to save files to these locations.

---

## 📖 Full Documentation

- **GETTING_STARTED.txt** — Visual setup guide
- **README.md** — Quick overview
- **CLIENT_SETUP.md** — Detailed setup & troubleshooting
- **QUICK_START.md** — How to use dashboard
- **VISUAL_GUIDE.md** — Page-by-page walkthrough

---

## ✅ Setup Checklist (Mac/Linux)

- [ ] Downloaded Python 3.10+
- [ ] Got API key from https://console.anthropic.com/
- [ ] Navigated to Brain folder in Terminal
- [ ] Ran `chmod +x install.sh start_dashboard.sh`
- [ ] Ran `./install.sh` successfully
- [ ] Added API key to .env file
- [ ] Ran `./start_dashboard.sh`
- [ ] Dashboard opened in browser
- [ ] Tested briefing generation
- [ ] Tested call analysis
- [ ] Tested strategic lens

---

## 🎉 You're All Set!

The Operations Co-Founder Brain works perfectly on Mac and Linux!

**Every time you want to use it:**
```bash
./start_dashboard.sh
```

That's it. Enjoy! 🧠
