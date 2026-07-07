# 🚂 Railway Deployment Guide

Deploy Brain to Railway for 24/7 uptime.

---

## ⚠️ Important: Local Files Problem

**Issue:** If Brain is on Railway (cloud) and Hermes is on your desktop (local), Brain can't read local files.

```
Hermes (Local Desktop)
    ↓ saves to
D:\Work\APPS\Brain\data\
    ↓ Brain can't reach from Railway ❌
Railway (Cloud)
```

**Solutions:**

1. **Keep Brain Local** (Recommended for now)
   - Brain and Hermes both on desktop
   - Direct file access ✅
   - No architecture changes needed
   - Later: Move both to cloud

2. **Cloud Storage** (Best for production)
   - Hermes uploads to AWS S3 / Google Cloud Storage
   - Brain downloads from cloud
   - Both on desktop OR in cloud ✅

3. **Webhook Integration** (Alternative)
   - Hermes sends data directly to Brain API
   - No files needed ✅
   - Requires code changes

4. **Hybrid** (Recommended)
   - Phase 1: Keep both local
   - Phase 2: Add cloud storage
   - Phase 3: Full cloud deployment

---

## 🎯 Recommended Approach

### Phase 1 (Now): Keep Local
```
Hermes (Desktop) → saves → data/ folder
Brain Dashboard (Desktop) → reads → data/ folder
Both accessible locally on http://localhost:8501
```

**Pros:**
- ✅ Works immediately
- ✅ No architecture changes
- ✅ Direct file access
- ✅ Hermes and Brain share filesystem

**Cons:**
- ❌ Only accessible on Jim's desktop
- ❌ Not 24/7 uptime
- ❌ Can't share link with team

### Phase 2 (Later): Add Cloud Storage
```
Hermes (Desktop) → uploads → AWS S3
Brain (Railway) → downloads → AWS S3
Brain Dashboard (Cloud) → http://brain-xxxxx.railway.app
```

**Pros:**
- ✅ Brain runs 24/7
- ✅ Accessible from anywhere
- ✅ Shareable URL
- ✅ Hermes still local

**Cons:**
- ⚠️ Requires S3 setup ($1-5/month)
- ⚠️ Code changes needed

---

## 📋 Option 1: Keep Brain Local (Recommended Now)

**Best if:** You want to deploy immediately without changes

### Don't Deploy to Railway Yet

Just keep running locally:

```bash
# On your desktop (daily)
streamlit run dashboard.py
```

**Advantage:** Works perfectly with your Hermes setup

**When to move to cloud:** After you've tested with Hermes for 2 weeks

---

## ☁️ Option 2: Deploy to Railway + Use Cloud Storage

**Best if:** You want Brain in cloud from the start

### Step 1: Set Up AWS S3 Bucket

1. Go to https://aws.amazon.com
2. Create S3 bucket (e.g., "brain-signals")
3. Get Access Key ID & Secret Access Key
4. (Or use free tier: 5GB storage free)

### Step 2: Update Brain to Read from S3

Add to `dashboard.py` (near top):

```python
import boto3
from io import BytesIO
import json

# S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

def read_digest_from_s3():
    """Read latest digest from S3 instead of local filesystem"""
    try:
        # List all digest files in S3
        response = s3_client.list_objects_v2(
            Bucket='brain-signals',
            Prefix='incoming/digest_'
        )
        
        if not response.get('Contents'):
            return None
        
        # Get latest file
        latest = sorted(
            response['Contents'],
            key=lambda x: x['LastModified'],
            reverse=True
        )[0]
        
        # Download and parse
        obj = s3_client.get_object(Bucket='brain-signals', Key=latest['Key'])
        digest_json = json.loads(obj['Body'].read())
        return HermesDigest(**digest_json)
    except Exception as e:
        st.error(f"Error reading from S3: {e}")
        return None
```

Then replace `hermes.read_latest_digest()` with `read_digest_from_s3()`

### Step 3: Update Hermes to Upload to S3

In Hermes, after saving JSON locally, also upload to S3:

```python
import boto3

s3_client = boto3.client('s3')

def upload_digest_to_s3(digest_json, filename):
    """Upload digest to S3 after saving locally"""
    s3_client.put_object(
        Bucket='brain-signals',
        Key=f'incoming/{filename}',
        Body=json.dumps(digest_json)
    )
```

### Step 4: Deploy to Railway

1. Push code to GitHub (with S3 changes)
2. Go to Railway (https://railway.app)
3. Deploy as normal (see Railway deployment below)
4. Add environment variables:
   - `AWS_ACCESS_KEY_ID=`
   - `AWS_SECRET_ACCESS_KEY=`
   - `AWS_BUCKET_NAME=brain-signals`

### Step 5: Test

- Hermes saves locally AND uploads to S3
- Brain on Railway reads from S3
- Brain accessible at: https://brain-xxxxx.railway.app

---

## 🚂 Deploy to Railway (Step by Step)

### If Keeping Local (No S3)

**Don't deploy yet.** Just run locally:
```bash
streamlit run dashboard.py
```

Later, deploy with cloud storage integration.

### If Using S3 (Cloud Storage)

#### 1. Push to GitHub

```bash
git add .
git commit -m "Add S3 support for Railway deployment"
git push origin main
```

#### 2. Deploy to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Authorize GitHub
5. Select your Brain repo
6. Click "Deploy"

Railway auto-detects Python and starts building!

#### 3. Add Environment Variables

In Railway dashboard:
1. Go to your project
2. Click the Brain app
3. Go to "Variables" tab
4. Add:

```
ANTHROPIC_API_KEY = sk-ant-xxxxx
AWS_ACCESS_KEY_ID = your_aws_key_id
AWS_SECRET_ACCESS_KEY = your_aws_secret_key
AWS_BUCKET_NAME = brain-signals
AWS_REGION = us-east-1
```

#### 4. Done!

Railway gives you URL: `https://brain-xxxxx.railway.app`

Brain now reads from S3 instead of local files!

---

## 📊 Architecture Comparison

### Setup 1: Local Only (Now)
```
Hermes (Desktop) → saves → data/
Brain (Desktop) → reads → data/
Access: http://localhost:8501 (local only)
Cost: $0/month
Always-on: ❌ (only when computer runs)
```

### Setup 2: Cloud Brain + Local Hermes + S3
```
Hermes (Desktop) → saves → data/ + S3
Brain (Railway) → reads → S3
Access: https://brain-xxxxx.railway.app (anywhere)
Cost: $5/month (Railway) + $1-5/month (S3)
Always-on: ✅ (24/7 cloud)
```

### Setup 3: Both Cloud + S3 (Phase 2+)
```
Hermes (Cloud/Scheduled) → uploads → S3
Brain (Railway) → reads → S3
Access: https://brain-xxxxx.railway.app (anywhere)
Cost: $5/month (Railway) + $1-5/month (S3) + $5/month (Hermes cloud if needed)
Always-on: ✅ (fully automated)
```

---

## ✅ My Recommendation

### Right Now (Today)
✅ Keep Brain running locally  
✅ Deploy Hermes locally  
✅ Test integration together  

### In 2 Weeks (After Testing)
- ✅ Switch to cloud storage (S3 or similar)
- ✅ Deploy Brain to Railway
- ✅ Keep Hermes local (or cloud)
- ✅ Share cloud URL with team

### In 2 Months (Full Automation)
- ✅ Auto-transcribe calls
- ✅ Scheduled briefings
- ✅ Telegram delivery
- ✅ Full 24/7 automation

---

## 🎯 Quick Decision Tree

**Do you need it on the internet right now?**
- **No** → Keep local, test with Hermes first
- **Yes** → Use S3 + Railway (see deployment below)

**Is S3 cost ($1-5/month) acceptable?**
- **No** → Keep local (free)
- **Yes** → Deploy to Railway + S3

**Can you wait 2 weeks?**
- **Yes** → Test locally first, THEN cloud
- **No** → Deploy to Railway now (with S3)

---

## 📁 File Structure with S3

If you use S3, Hermes should still save locally too:

```
D:\Work\APPS\Brain\data\
├── incoming/
│   ├── digest_*.json        ← Hermes saves locally
│   └── metrics_*.json       ↓ Hermes also uploads to S3
└── transcripts/
    └── transcript_*.json
```

Brain reads from S3 (not local files).

---

## 🔐 Security Note

**Never commit AWS keys to GitHub!**

Use Railway environment variables:
- Set in Railway dashboard
- Never in code
- Secrets are encrypted

---

## 🚀 Summary

| Option | Setup Time | Cost | Always-On | Team Access |
|--------|-----------|------|-----------|------------|
| **Local Only** | Now | $0 | ❌ | ❌ |
| **Local + S3** | 1 hour | $1-10/mo | ❌ | ❌ |
| **Railway + S3** | 1 hour | $5-10/mo | ✅ | ✅ |

**Recommendation:** Start with Local Only, move to Railway + S3 after testing

---

## 📞 Need Help?

**To keep local (now):**
- No changes needed
- Just run `streamlit run dashboard.py`
- See `TEST_WITH_HERMES.md`

**To deploy to Railway (later):**
- Add S3 integration first
- Push to GitHub
- Deploy via Railway UI
- See deployment guide below

**To use S3:**
- Create AWS account
- Get access keys
- Add code (see above)
- Set Railway environment variables

---

**My recommendation: Keep it local for now, deploy to Railway after 2 weeks of testing! 🚀**
