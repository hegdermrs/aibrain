# 🚂 Deploy to Railway (Recommended - 10 Minutes)

Railway is the easiest way to host the Brain 24/7 in the cloud.

---

## ⚡ Quick Deploy (5 steps)

### 1. Create Railway Account
- Go to https://railway.app
- Click "Start for free"
- Sign up with GitHub (easiest)

### 2. Create New Project
- Click "New Project"
- Select "Deploy from GitHub"

### 3. Connect GitHub
- Authorize Railway to access your GitHub
- Select the Brain repository
- Click "Deploy"

**Railway auto-detects it's Python and starts building!**

### 4. Add Environment Variable
- In Railway dashboard, go to your project
- Click the app instance
- Go to "Variables" tab
- Click "Add Variable"
- Add these:
  ```
  ANTHROPIC_API_KEY = sk-ant-xxxxx
  BRAIN_MODEL = claude-sonnet-4-20250514
  ```
- Click "Add"

### 5. Done!
- Dashboard shows "Build Successful"
- Railway gives you URL: `https://brain-xxxxx.railway.app`
- Share this URL with Jim!

**Total time: ~10 minutes**

---

## 🌐 Access the Dashboard

Jim can now access the Brain from:
- **Computer:** https://brain-xxxxx.railway.app
- **Phone:** https://brain-xxxxx.railway.app (responsive!)
- **Anywhere:** Works from any device with internet

No need to run anything on his desktop!

---

## 🔄 Push Updates

Your code auto-deploys when you push to GitHub:

```bash
# Make changes to code
git add .
git commit -m "Update prompts or features"
git push origin main
```

Railway automatically:
1. Detects the push
2. Rebuilds the Docker image
3. Deploys the new version
4. Keeps the same URL

**Zero downtime updates!**

---

## 📊 Monitor Your Deployment

Railway dashboard shows:
- **Build logs** — See what's happening
- **Deployment history** — View all versions
- **Metrics** — CPU, memory, request count
- **Logs** — Real-time application logs

---

## 💰 Cost Breakdown

| Item | Cost |
|------|------|
| Build minutes (limited) | Free |
| App runtime | $5/month (first 100 hours free) |
| Additional compute | Pay-as-you-go |
| **Total** | **~$5/month** |

**Much cheaper than running a VPS!**

---

## 🔒 Security

### API Key Protection
Railway keeps your `ANTHROPIC_API_KEY` secret:
- ✅ Never logged
- ✅ Never exposed in logs
- ✅ Only sent to Claude API
- ✅ Encrypted at rest

### Adding Password Protection (Optional)

If you want Jim to be the only one accessing it, add basic auth:

**In `dashboard.py`, add at the top:**

```python
import streamlit as st

# Password protection
if 'authenticated' not in st.session_state:
    col1, col2 = st.columns(3)
    with col2:
        password = st.text_input("Enter password:", type="password")
        if password == "jim-secret-password-here":
            st.session_state.authenticated = True
        elif password:
            st.error("❌ Wrong password")
    if 'authenticated' not in st.session_state or not st.session_state.get('authenticated'):
        st.stop()

# Rest of dashboard code continues here...
```

Then push to GitHub and Railway auto-deploys with password protection!

---

## 🐛 Troubleshooting

### "Build Failed"
- Check logs in Railway dashboard
- Common issue: Missing `requirements.txt`
- Solution: Make sure requirements.txt exists in repo

### "App Crashing"
- Check "Logs" tab in Railway
- Look for errors
- Common issue: Missing environment variable
- Solution: Add `ANTHROPIC_API_KEY` in Variables

### "Dashboard is blank"
- Check browser console (F12) for errors
- Check Railway logs
- Common issue: API key invalid
- Solution: Verify key at console.anthropic.com

### "Very slow loading"
- First load may take 10-30 seconds
- Check metrics in Railway dashboard
- If consistently slow, may need higher tier

---

## 📞 Support

**Railroad Issues?**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

**Brain Issues?**
- Check logs in Railway dashboard
- Verify API key is correct
- Restart service (Railway admin panel)

---

## 🎯 What Jim Sees

Jim opens his browser and sees:

```
https://brain-xxxxx.railway.app

↓ (instant load)

┌────────────────────────────────────┐
│ 🧠 Operations Co-Founder Brain     │
│                                    │
│ [📋 Briefing] [📞 Analyze] ...    │
│                                    │
│ Ready to use! ✅                  │
└────────────────────────────────────┘
```

No setup needed on his end!

---

## ✅ Deployment Checklist

- [ ] Brain code pushed to GitHub
- [ ] Created Railway account
- [ ] Connected GitHub to Railway
- [ ] App built successfully (green checkmark)
- [ ] Added `ANTHROPIC_API_KEY` environment variable
- [ ] Tested URL in browser
- [ ] Shared URL with Jim
- [ ] Verified all 4 pages work
- [ ] Tested with sample data

---

## 🚀 You're Live!

**Your Brain is now running 24/7 in the cloud.**

- ✅ Always on
- ✅ Professional uptime
- ✅ Shareable link
- ✅ Auto-deploys on code push
- ✅ Only $5/month

**Done! 🎉**
