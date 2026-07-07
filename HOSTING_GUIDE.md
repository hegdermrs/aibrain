# 🌐 Hosting Guide — Run Brain 24/7 in the Cloud

Yes! You can host the Brain remotely so it's always available. No more double-clicking on Jim's desktop.

---

## 🎯 Why Host Remotely?

- ✅ **Always On** — Access from anywhere, anytime
- ✅ **No Desktop Required** — Doesn't need Jim's computer to run
- ✅ **Shareable** — Can share link with team members
- ✅ **Reliable** — Professional uptime (99.9%+)
- ✅ **Scalable** — Grows with Jim's needs

---

## 🚀 Hosting Options (Easiest to Hardest)

### Option 1: Railway (Recommended - Easiest)

**Cost:** Free tier ($5 credit/month), then $5+/month  
**Setup Time:** 10 minutes  
**Difficulty:** ⭐ Very Easy  

**What You Get:**
- Always-on dashboard
- Automatic deployments
- Free SSL certificate (HTTPS)
- Professional uptime

**How to Deploy:**

1. **Create Railway account:**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Deploy the Brain:**
   - Click "New Project"
   - Select "Deploy from GitHub"
   - Connect your GitHub repo
   - Select the Brain repo
   - Railway auto-detects Python
   - Adds `requirements.txt` to deploy config

3. **Set Environment Variables:**
   - In Railway dashboard, go to "Variables"
   - Add: `ANTHROPIC_API_KEY=sk-ant-xxxxx`
   - Add: `BRAIN_MODEL=claude-sonnet-4-20250514`

4. **Done!**
   - Railway gives you a URL: `https://brain-xxxxx.railway.app`
   - Dashboard is live 24/7

**Access:** Anyone with the URL can use it (optional: add password)

---

### Option 2: Render (Also Very Easy)

**Cost:** Free tier (limited), then $7+/month  
**Setup Time:** 10 minutes  
**Difficulty:** ⭐ Very Easy  

**How to Deploy:**

1. **Create Render account:**
   - Go to https://render.com
   - Sign up

2. **Deploy:**
   - Click "New +"
   - Select "Web Service"
   - Connect GitHub
   - Select Brain repo
   - Render auto-detects Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run dashboard.py --server.port=8501`

3. **Set Environment Variables:**
   - Add: `ANTHROPIC_API_KEY=sk-ant-xxxxx`

4. **Done!**
   - Render gives you a URL
   - Dashboard is live 24/7

**Note:** Free tier sleeps after 15 min of inactivity. Pay $7/month for always-on.

---

### Option 3: Streamlit Cloud (Simplest)

**Cost:** Free  
**Setup Time:** 5 minutes  
**Difficulty:** ⭐ Super Easy  

**Limitations:**
- 1 GB storage
- Limited computational resources
- Community cloud (no privacy controls)

**How to Deploy:**

1. **Fork repo to GitHub:**
   - Add Brain to your GitHub

2. **Go to Streamlit Cloud:**
   - https://share.streamlit.io

3. **Deploy:**
   - Click "Deploy an app"
   - Select your GitHub repo
   - Select branch & file (`dashboard.py`)
   - Click "Deploy"

4. **Set Secrets:**
   - In "Settings" → "Secrets"
   - Add: `ANTHROPIC_API_KEY = sk-ant-xxxxx`

5. **Done!**
   - Your app is live at: `https://share.streamlit.io/yourname/Brain/main/dashboard.py`

**Note:** Free tier goes dormant after inactivity, but wakes up when accessed.

---

### Option 4: PythonAnywhere (Good for Simple Apps)

**Cost:** Free tier (limited), then $5+/month  
**Setup Time:** 15 minutes  
**Difficulty:** ⭐⭐ Easy  

**How to Deploy:**

1. **Create PythonAnywhere account:**
   - Go to https://www.pythonanywhere.com

2. **Upload Code:**
   - Upload Brain files to PythonAnywhere
   - Or clone from GitHub

3. **Create Web App:**
   - "New web app" → "Streamlit"
   - Point to `dashboard.py`
   - Set environment variables

4. **Set API Key:**
   - In "Web" tab → "WSGI configuration"
   - Add: `os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-xxxxx'`

5. **Done!**
   - Your app is live

---

### Option 5: Docker + Self-Hosted (Maximum Control)

**Cost:** $5-20/month (DigitalOcean, Linode, etc.)  
**Setup Time:** 30 minutes  
**Difficulty:** ⭐⭐⭐ Advanced  

**Benefits:**
- Full control
- No vendor lock-in
- Can add authentication
- Can customize deployment

**How to Deploy:**

1. **Create Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Push to Docker Hub:**
```bash
docker build -t yourusername/brain:latest .
docker push yourusername/brain:latest
```

3. **Deploy to DigitalOcean/Linode:**
   - Create VM (Ubuntu, 1GB RAM minimum)
   - Install Docker
   - Run: `docker run -e ANTHROPIC_API_KEY=sk-ant-xxxxx -p 80:8501 yourusername/brain:latest`

4. **Optional: Add nginx for reverse proxy**

---

## 🔒 Security Considerations

### API Key Management
**Never commit API key to GitHub!** Use environment variables:

```bash
# In Railway/Render/Streamlit dashboard
ANTHROPIC_API_KEY = sk-ant-xxxxx
```

### Authentication
Consider adding password protection for remote version:

**Option 1: Streamlit Secrets (easiest)**
```python
# In dashboard.py
import streamlit as st

if 'authenticated' not in st.session_state:
    password = st.text_input("Enter password:", type="password")
    if password == "jim's-secret-password":
        st.session_state.authenticated = True
    else:
        st.stop()
```

**Option 2: Basic Auth (nginx reverse proxy)**
```nginx
location / {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8501;
}
```

---

## 🎯 Recommended Setup for Jim

### Best Option: Railway

**Why?**
- ✅ Super easy setup (10 minutes)
- ✅ Always on (no sleeping)
- ✅ Professional infrastructure
- ✅ $5/month (very cheap)
- ✅ Automatic deployments

**Setup Steps:**
1. Create Railway account (GitHub login)
2. Connect Brain GitHub repo
3. Add `ANTHROPIC_API_KEY` environment variable
4. Done! Get URL and share with Jim

**Cost:** Free (trial), then $5/month

---

## 📊 Comparison

| Platform | Cost | Setup | Uptime | Ease |
|----------|------|-------|--------|------|
| **Railway** | $5/mo | 10min | 99.9% | ⭐ |
| **Render** | $7/mo | 10min | 99.9% | ⭐ |
| **Streamlit Cloud** | Free | 5min | 99% | ⭐ |
| **PythonAnywhere** | $5/mo | 15min | 99% | ⭐⭐ |
| **Docker + VPS** | $5-20/mo | 30min | Variable | ⭐⭐⭐ |

---

## 🚀 Quick Start: Railway (Recommended)

### 1. Prepare GitHub
```bash
# Make sure Brain repo is on GitHub
git add .
git commit -m "Brain ready for deployment"
git push origin main
```

### 2. Deploy to Railway
- Go to https://railway.app
- Sign up with GitHub
- Click "New Project"
- Select "Deploy from GitHub"
- Choose Brain repo
- Railway auto-deploys!

### 3. Configure
- In Railway dashboard: Settings → Variables
- Add: `ANTHROPIC_API_KEY=sk-ant-xxxxx`
- Add: `BRAIN_MODEL=claude-sonnet-4-20250514`

### 4. Share
- Railway gives you URL: `https://brain-xxxxx.railway.app`
- Share with Jim
- He opens in browser, no installation needed!

**Total time: 15 minutes**

---

## 💡 After Deployment

### Updates
Push to GitHub and Railway auto-deploys:
```bash
git add .
git commit -m "Update prompts"
git push origin main
# Railroad auto-deploys within minutes
```

### Monitoring
Railway dashboard shows:
- CPU/memory usage
- Logs
- Deployment history
- Uptime

### Backups
- GitHub = source code backup
- Railway = automatic backups
- Your `data/` folder = local backups

---

## 📞 Migration Path

### Today
Jim runs locally:
```
Desktop → Double-click START_DASHBOARD.bat → http://localhost:8501
```

### Tomorrow (Remote)
```
Railway (Cloud) → https://brain-xxxxx.railway.app → Accessible from anywhere
```

**Both work with the same code! No changes needed.**

---

## 🎯 Summary

**Yes, you can host it 24/7 in the cloud.**

**Best option:** Railway ($5/month, 10 minutes to setup)

**What Jim gets:**
- Always-on dashboard
- No need to run on his desktop
- Shareable with team
- Professional uptime
- Can access from phone, anywhere

---

## 📚 Next Steps

1. **Choose platform** (Railway recommended)
2. **Push code to GitHub** (if not already)
3. **Deploy** (10 minutes)
4. **Test** (works like localhost)
5. **Share URL** with Jim

---

**Want me to create the Railway/Docker deployment files? Just say the word! 🚀**
