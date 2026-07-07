# ✅ Test Brain with Hermes — Quick Checklist

---

## 🚀 Quick Start (5 minutes)

### 1. Start Brain Dashboard
```bash
streamlit run dashboard.py
```
Opens at: http://localhost:8501

### 2. Start Hermes (if not already running)
Your Hermes instance should be saving files to:
- `data/incoming/digest_*.json`
- `data/transcripts/transcript_*.json`

### 3. Refresh Dashboard
Press F5 in browser to refresh

### 4. Check Sidebar Status
Look at **📊 System Status**:
- **Hermes:** Should show time (e.g., "23 min ago" with 🟢 Live)
- **Claude API:** Should show ✅ Ready

✅ **If both show green:** Hermes integration is working!

---

## 📋 Test Each Page

### Test 1: 📋 Briefing Page (2 min)
```
1. Go to "📋 Briefing" page
2. Check "📡 Incoming Signals"
3. Should show:
   - Total Signals: (number)
   - 🔴 High Priority: (number)
   - 💬 Need Response: (number)
   - List of recent signals
4. Click "🚀 Generate Briefing"
5. Should generate briefing using REAL Hermes signals
6. Check tabs: Content | Metrics | Action Items
```

**Success if:** Shows real Hermes signals and generates briefing ✅

---

### Test 2: 📞 Analyze Call (3 min)
```
1. Make sure Hermes has saved a call transcript
2. Go to "📞 Analyze Call" page
3. Click "📂 Recent Transcripts" tab
4. Should see your real call listed
5. Click "📊 Analyze" button
6. Should analyze the real transcript
7. Check 5 tabs for results
```

**Success if:** Real call appears and analyzes correctly ✅

---

### Test 3: 🔍 Strategic Lens (2 min)
```
1. Go to "🔍 Strategic Lens" page
2. Enter a real business question
3. Add context
4. Select personas (Hormozi, Musk)
5. Click "🚀 Run Lens Analysis"
6. Should analyze with real Claude API
7. Should show persona perspectives + synthesis
```

**Success if:** Gets real analysis from Claude ✅

---

### Test 4: 📚 History (1 min)
```
1. Go to "📚 History" page
2. Check all 3 tabs:
   - Briefings (should show ones you generated)
   - Call Analyses (should show analyzed calls)
   - Lens Results (should show past analyses)
3. Click "View" on any item
4. Should show full results
```

**Success if:** History shows all your work ✅

---

## 🔍 Verify Hermes Connection

### Check File Creation
```bash
# List digest files (signals from Hermes)
ls -lt data/incoming/digest_*.json | head -3

# List transcript files (calls from Hermes)
ls -lt data/transcripts/transcript_*.json | head -3

# List metrics files (business metrics from Hermes)
ls -lt data/incoming/metrics_*.json | head -3
```

### Check File Contents
```bash
# View latest digest (signals)
cat data/incoming/digest_*.json | python -m json.tool | head -30

# Verify it has signals array
cat data/incoming/digest_*.json | python -m json.tool | grep -A 2 "signals"
```

### Check File Timestamps
```bash
# Recent files show in status as "Live" (< 60 min)
# Older files show as "Stale" (60-180 min)
# Very old show as "Offline" (> 180 min)

ls -lh data/incoming/digest_*.json
```

---

## ⚠️ Troubleshooting

### Dashboard shows "Offline" but Hermes is running

**Check:**
1. Hermes is actually saving files?
```bash
ls -la data/incoming/
```

2. Files have correct format?
```bash
cat data/incoming/digest_*.json | python -m json.tool
```

3. Timestamp is recent?
```bash
# File modification time should be recent
ls -lh data/incoming/digest_*.json
```

**Fix:**
- Verify Hermes config is correct
- Check Hermes is actually running
- Restart Hermes
- Refresh Brain dashboard (F5)

---

### "No signals shown" but Hermes is connected

**Check:**
1. Digest file exists?
```bash
ls data/incoming/digest_*.json
```

2. Has signals array?
```bash
cat data/incoming/digest_*.json | grep -c '"signals"'
# Should output: 1
```

3. Signals array not empty?
```bash
cat data/incoming/digest_*.json | python -c "import sys, json; d=json.load(sys.stdin); print(f'Signals: {len(d.get(\"signals\", []))}')"
```

**Fix:**
- Check Hermes is capturing signals
- Verify signal format matches schema (see HERMES_INTEGRATION.md)
- Check signal timestamps are within time_window

---

### Analysis button disabled

**Means:** API key not configured or missing

**Check:**
1. .env file exists?
```bash
ls -la .env
```

2. ANTHROPIC_API_KEY is set?
```bash
grep ANTHROPIC_API_KEY .env
```

3. API key is valid?
- Go to console.anthropic.com
- Check key hasn't been deleted
- Generate new key if needed

**Fix:**
1. Add/update .env:
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
```
2. Restart dashboard (Ctrl+C, then streamlit run dashboard.py)
3. Try again

---

### Can't upload transcript

**Check:**
1. File is valid JSON?
```bash
python -m json.tool transcript_file.json
```

2. Has required fields?
```json
{
  "id": "...",
  "title": "...",
  "date": "...",
  "participants": [...],
  "full_text": "...",
  "duration_minutes": 45,
  "segments": [...]
}
```

3. full_text is not empty?

**Fix:**
- Use transcript from data/transcripts/ (guaranteed valid)
- Check Hermes transcript format
- See HERMES_INTEGRATION.md for schema

---

## ✅ Final Verification

Run this checklist:

- [ ] Brain dashboard running (streamlit run dashboard.py)
- [ ] No error messages in console
- [ ] Hermes creating files in data/incoming/
- [ ] Sidebar status shows Hermes connection
- [ ] Can generate briefing with real signals
- [ ] Can analyze real transcript
- [ ] Can run strategic lens
- [ ] History shows all results
- [ ] Sample data still works
- [ ] All 4 pages responsive and fast

**If all green:** Brain + Hermes integration is working perfectly! 🎉

---

## 🚀 Ready for Production

Once verified with Hermes:

1. **Keep running daily**
   - Generate morning + evening briefings
   - Analyze weekly calls
   - Use lens for decisions

2. **Gather feedback**
   - Does it help Jim?
   - What would make it better?
   - Any missing features?

3. **Plan Phase 2**
   - Auto-analyze transcripts on arrival
   - Scheduled briefings (no manual generation)
   - Telegram delivery
   - Hermes webhook integration

4. **Deploy to cloud** (optional)
   - Keep on desktop, OR
   - Move to Railway ($5/mo)
   - Both options work!

---

**Test it now! 🚀**
