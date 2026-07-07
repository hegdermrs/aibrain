# ✅ Cross-Platform Support — Yes, It Works on Mac!

## TL;DR

**Yes, the Operations Co-Founder Brain works on Mac and Linux.**

Just use different setup scripts instead of the `.bat` files.

---

## 🖥️ Platform Support

| OS | Status | Setup Script | Run Script |
|----|--------|--------------|-----------|
| **Windows** | ✅ Full Support | `INSTALL.bat` | `START_DASHBOARD.bat` |
| **Mac** | ✅ Full Support | `install.sh` | `start_dashboard.sh` |
| **Linux** | ✅ Full Support | `install.sh` | `start_dashboard.sh` |

---

## 📋 Quick Setup by Platform

### Windows (Easiest)
```
1. Double-click: INSTALL.bat
2. Edit .env with API key
3. Double-click: START_DASHBOARD.bat
```

### Mac
```bash
1. chmod +x install.sh start_dashboard.sh
2. ./install.sh
3. Edit .env with API key
4. ./start_dashboard.sh
```

### Linux (Ubuntu/Debian)
```bash
1. sudo apt install python3 python3-pip
2. chmod +x install.sh start_dashboard.sh
3. ./install.sh
4. Edit .env with API key
5. ./start_dashboard.sh
```

---

## 🚀 What Works on All Platforms

✅ Dashboard (same design)  
✅ All 4 pages (briefing, call analysis, lens, history)  
✅ Sample data (included)  
✅ Real-time status indicators  
✅ Integration with Hermes  
✅ API key configuration  
✅ Browser-based interface  

---

## 📦 Files You Get

### Windows Only
- `INSTALL.bat` — Batch installer
- `START_DASHBOARD.bat` — Batch launcher
- `run.bat` — Old/optional

### Mac/Linux Only
- `install.sh` — Shell installer
- `start_dashboard.sh` — Shell launcher

### All Platforms
- Everything else (Python code, config, data, docs)

---

## 🎯 For Mac Users

### Prerequisites
- **Python 3.10+** (free, open source)
- **API key** from https://console.anthropic.com/
- **Terminal** (built into Mac)
- **Text editor** (built-in, or use VS Code)

### Installation (4 steps)
```bash
# 1. Make scripts executable (one time)
chmod +x install.sh start_dashboard.sh

# 2. Install everything (one time)
./install.sh

# 3. Edit .env with API key
# (opens in your default editor)

# 4. Start dashboard (every time)
./start_dashboard.sh
```

### That's It!
Browser opens to http://localhost:8501

---

## 🐧 For Linux Users

### Prerequisites
- **Python 3.10+** (usually pre-installed)
- **pip** (Python package manager)
- **API key** from https://console.anthropic.com/
- **Terminal**
- **Text editor** (nano, vim, VS Code, etc.)

### Installation (4 steps)
```bash
# 1. Install Python if needed (Ubuntu/Debian)
sudo apt install python3 python3-pip

# 2. Make scripts executable (one time)
chmod +x install.sh start_dashboard.sh

# 3. Install everything (one time)
./install.sh

# 4. Edit .env with API key
nano .env
# (or use your preferred editor)

# 5. Start dashboard (every time)
./start_dashboard.sh
```

### That's It!
Browser opens to http://localhost:8501

---

## 📚 Documentation by Platform

| Need | Windows | Mac/Linux |
|------|---------|-----------|
| Setup | `CLIENT_SETUP.md` | `MAC_LINUX_SETUP.md` |
| Overview | `README.md` | `README.md` |
| Usage | `QUICK_START.md` | `QUICK_START.md` |
| Visual | `VISUAL_GUIDE.md` | `VISUAL_GUIDE.md` |
| Design | `DASHBOARD_IMPROVEMENTS.md` | `DASHBOARD_IMPROVEMENTS.md` |

---

## 🔄 Cross-Platform Details

### Python Code
- Pure Python (no Windows-only libraries)
- Works identically on all platforms
- Streamlit handles all UI rendering

### Configuration Files
- `.env` works on all platforms
- `config/personas.yaml` works on all platforms
- `config/prompts.yaml` works on all platforms

### Data Storage
- `data/` directory works on all platforms
- Same file format (JSON)
- Same directory structure

### Hermes Integration
- Same file-based integration on all platforms
- Hermes can run on any OS
- Brain reads same JSON format everywhere

### API Connection
- Same Claude API on all platforms
- Same request/response format
- Same pricing

---

## ✅ Testing Checklist

### Windows
- [x] Batch files tested
- [x] Python installation automated
- [x] Dashboard launches from .bat
- [x] Sample data works
- [x] API key validation works

### Mac
- [x] Shell scripts tested
- [x] Python detection works
- [x] Dashboard launches from .sh
- [x] Sample data works
- [x] API key validation works

### Linux
- [x] Shell scripts tested
- [x] Package detection works
- [x] Dashboard launches from .sh
- [x] Sample data works
- [x] API key validation works

---

## 🎯 Summary

**The Operations Co-Founder Brain is truly cross-platform.**

- **Same code** runs everywhere
- **Same UI** looks the same
- **Same features** work identically
- **Same integration** with Hermes
- **Same sample data** for testing

Just different setup scripts for different operating systems.

**Choose your platform, run the setup script, add your API key, and you're done!**

---

## 📞 Support

**Setup Issues?**
- Windows → See `CLIENT_SETUP.md`
- Mac/Linux → See `MAC_LINUX_SETUP.md`

**General Questions?**
- See `QUICK_START.md`

**Visual Walkthrough?**
- See `VISUAL_GUIDE.md`

---

**The Brain works everywhere. Pick your OS and run! 🧠**
