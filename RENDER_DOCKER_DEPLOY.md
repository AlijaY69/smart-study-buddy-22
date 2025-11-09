# Deploy Smart Study Buddy to Render using Docker

This guide will walk you through deploying your application to Render using the Docker containers that are already configured in your repository.

## What's Included

Your repository already has:
- ✅ `backend/Dockerfile` - Backend API Docker container
- ✅ `frontend.Dockerfile` - Frontend Docker container with Nginx
- ✅ `docker-compose.yml` - Local development setup
- ✅ `render.yaml` - Render Blueprint configuration
- ✅ `nginx/default.conf` - Nginx configuration for frontend

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│                   Render Cloud                   │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────────────┐  ┌──────────────────┐  │
│  │   Frontend Web     │  │   Backend Web    │  │
│  │   (Nginx+React)    │  │   (Flask API)    │  │
│  │   Port: 80         │  │   Port: 5001     │  │
│  └────────────────────┘  └──────────────────┘  │
│                                                  │
│  ┌────────────────────┐                         │
│  │  Worker Service    │                         │
│  │  (Agentic AI)      │                         │
│  └────────────────────┘                         │
│                                                  │
└─────────────────────────────────────────────────┘
         ↓              ↓              ↓
    Supabase       MongoDB        OpenAI
   (Database)      (Events)        (AI)
```

## Prerequisites

1. **GitHub Account** - Repository must be pushed to GitHub
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Environment Variables Ready** - Have all your credentials ready

## Step 1: Prepare Your Repository

Make sure all Docker files are committed and pushed to GitHub:

```bash
git status
git add .
git commit -m "Ready for Render Docker deployment"
git push origin main
```

## Step 2: Deploy Using Render Blueprint (Recommended)

### Option A: Deploy via render.yaml (Easiest)

1. Go to **[Render Dashboard](https://dashboard.render.com/)**
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub account if not already connected
4. Select your `smart-study-buddy-22` repository
5. Render will automatically detect the `render.yaml` file
6. Click **"Apply"**

Render will create 3 services:
- `smart-study-buddy-backend` (Web Service - Flask API)
- `smart-study-buddy-worker` (Background Worker - Agentic AI)
- `smart-study-buddy-frontend` (Web Service - React + Nginx)

7. **Add Environment Variables** for each service (see below)

### Option B: Manual Service Creation

If blueprint doesn't work, create services manually:

#### 2.1 Create Backend Service

1. Click **"New"** → **"Web Service"**
2. Connect GitHub repo: `smart-study-buddy-22`
3. Configure:
   - **Name**: `smart-study-buddy-backend`
   - **Region**: Frankfurt (or your preference)
   - **Branch**: `main`
   - **Runtime**: Docker
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `.`
   - **Docker Command**: (leave empty, uses CMD from Dockerfile)
4. **Instance Type**: Free
5. Click **"Create Web Service"**

#### 2.2 Create Worker Service

1. Click **"New"** → **Background Worker"**
2. Connect GitHub repo: `smart-study-buddy-22`
3. Configure:
   - **Name**: `smart-study-buddy-worker`
   - **Region**: Frankfurt
   - **Branch**: `main`
   - **Runtime**: Docker
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `.`
   - **Docker Command**: `python agentic_service.py`
4. **Instance Type**: Free
5. Click **"Create Background Worker"**

#### 2.3 Create Frontend Service

1. Click **"New"** → **"Web Service"**
2. Connect GitHub repo: `smart-study-buddy-22`
3. Configure:
   - **Name**: `smart-study-buddy-frontend`
   - **Region**: Frankfurt
   - **Branch**: `main`
   - **Runtime**: Docker
   - **Dockerfile Path**: `./frontend.Dockerfile`
   - **Docker Context**: `.`
   - **Docker Command**: (leave empty, uses CMD from Dockerfile)
4. **Instance Type**: Free
5. Click **"Create Web Service"**

## Step 3: Configure Environment Variables

### Backend Service Environment Variables

Go to **Backend Service** → **Environment** → Add:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here

# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here

# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/

# Email (SendGrid)
SENDGRID_API_KEY=SG.your-sendgrid-key
SENDGRID_FROM_EMAIL=your-verified@email.com

# SMTP (Gmail App Password)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password

# User
USER_EMAIL=your-email@gmail.com

# URLs (update after deployment)
FRONTEND_URL=https://your-frontend.onrender.com
PORT=5001
```

### Worker Service Environment Variables

Add the **same environment variables** as backend service.

### Frontend Service Environment Variables

Go to **Frontend Service** → **Environment** → Add:

```bash
# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here
```

## Step 4: Handle Google Calendar Credentials

Google Calendar requires `credentials.json` and `token.json` files. Since these can't be committed to git:

### Option A: Environment Variables (Recommended)

1. Convert credentials to base64:
```bash
cd backend
cat credentials.json | base64 > credentials_base64.txt
cat token.json | base64 > token_base64.txt
```

2. Add to Render environment variables:
```bash
GOOGLE_CREDENTIALS_BASE64=<paste base64 content>
GOOGLE_TOKEN_BASE64=<paste base64 content>
```

3. Update `google_calendar.py` to decode from env vars (see code below)

### Option B: Persistent Disk (Paid Plan)

If using Render's paid plan, you can mount a persistent disk and upload the files there.

### Code to Decode Credentials (Add to google_calendar.py)

```python
import os
import base64
import json

def load_credentials():
    """Load Google credentials from environment or file"""
    if os.getenv('GOOGLE_CREDENTIALS_BASE64'):
        # Decode from environment variable
        creds_json = base64.b64decode(os.getenv('GOOGLE_CREDENTIALS_BASE64'))
        return json.loads(creds_json)
    elif os.path.exists('credentials.json'):
        # Load from file
        with open('credentials.json', 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError("Google credentials not found")

def load_token():
    """Load Google token from environment or file"""
    if os.getenv('GOOGLE_TOKEN_BASE64'):
        token_json = base64.b64decode(os.getenv('GOOGLE_TOKEN_BASE64'))
        return json.loads(token_json)
    elif os.path.exists('token.json'):
        with open('token.json', 'r') as f:
            return json.load(f)
    return None
```

## Step 5: Update CORS and URLs

### Update Backend CORS

After deployment, note your frontend URL and update `backend/api.py`:

```python
from flask_cors import CORS

CORS(app, origins=[
    "https://your-frontend.onrender.com",  # Your Render frontend URL
    "http://localhost:5173"  # For local development
])
```

### Update Environment Variables

Go back to both Backend and Worker services and update:

```bash
FRONTEND_URL=https://your-frontend.onrender.com
```

## Step 6: Update Supabase Auth URLs

1. Go to **Supabase Dashboard** → **Authentication** → **URL Configuration**
2. Set **Site URL**: `https://your-frontend.onrender.com`
3. Add **Redirect URLs**:
   - `https://your-frontend.onrender.com`
   - `https://your-frontend.onrender.com/auth`

## Step 7: Update Frontend API URLs

If you have hardcoded backend URLs in your frontend, update them to point to your Render backend:

```typescript
// Update any fetch calls or API configuration
const BACKEND_URL = 'https://your-backend.onrender.com';
```

## Step 8: Deploy and Monitor

### Initial Deployment

Render will automatically build and deploy all services. Monitor the logs:

1. Go to each service in Render dashboard
2. Click **"Logs"** tab
3. Watch for any errors during build/deploy

### Health Checks

Render automatically checks if your services are healthy:
- Frontend: Expects 200 response on `/`
- Backend: Expects 200 response on `/` (health check endpoint)

### View Your Live App

Once deployed, you'll get URLs like:
- Frontend: `https://smart-study-buddy-frontend.onrender.com`
- Backend: `https://smart-study-buddy-backend.onrender.com`

## Step 9: Test Your Deployment

1. Visit your frontend URL
2. Sign up / Log in
3. Test calendar sync
4. Create an assignment
5. Upload materials
6. Generate exercises
7. Check if emails are sent
8. Verify agentic AI is running (check worker logs)

## Troubleshooting

### Build Fails

**Error**: "Dockerfile not found"
- **Solution**: Check `dockerfilePath` and `dockerContext` in render.yaml

**Error**: "COPY failed"
- **Solution**: Ensure all files referenced in Dockerfile exist

### Backend Can't Connect to Database

**Error**: "Connection refused" or "Timeout"
- **Solution**: Check MongoDB Atlas IP whitelist (allow 0.0.0.0/0)
- Verify Supabase service role key (not anon key)

### Frontend Can't Reach Backend

**Error**: CORS errors or "Network Error"
- **Solution**: Update CORS in `backend/api.py` with frontend URL
- Verify backend is running (check logs)

### Google Calendar Not Working

**Error**: "Credentials not found"
- **Solution**: Add credentials as environment variables (see Step 4)
- Make sure to decode base64 in code

### Worker Service Not Running

**Error**: Worker shows as "Failed"
- **Solution**: Check worker logs for errors
- Verify all environment variables are set
- Ensure `dockerCommand` is correct: `python agentic_service.py`

### Free Tier Limitations

**Issue**: Services go to sleep after 15 min of inactivity
- **Solution**: Upgrade to paid tier ($7/month per service)
- Or: Use a cron job to ping your services every 10 minutes

## Cost Estimates

### Free Tier
- 3 services: **Free**
- Limitations:
  - Services sleep after 15 min inactivity
  - 750 hours/month per service
  - Shared CPU/memory

### Paid Tier
- **Starter Plan**: $7/month per service
  - 3 services = $21/month
  - Always on (no sleep)
  - 0.5 GB RAM
  - Shared CPU

- **Standard Plan**: $25/month per service
  - 3 services = $75/month
  - 2 GB RAM
  - 1 CPU

### External Services
- Supabase: Free tier
- MongoDB Atlas: Free tier (512MB)
- OpenAI: Usage-based (~$5-20/month)

**Total Free Tier**: $0-20/month (only OpenAI)
**Total Paid Tier**: $21-75/month + OpenAI

## Maintenance

### Update Deployment

When you push to GitHub, Render will auto-deploy:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

### Manual Deploy

In Render dashboard:
1. Go to service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

### View Logs

Monitor application logs in real-time:
1. Select service
2. Click **"Logs"** tab
3. Filter by level (Info, Warning, Error)

### Restart Service

If service is misbehaving:
1. Go to service
2. Click **"Manual Deploy"** → **"Clear build cache & deploy"**

## Next Steps

1. ✅ Set up custom domain (optional)
2. ✅ Configure SSL (automatic on Render)
3. ✅ Set up monitoring and alerts
4. ✅ Configure auto-scaling (paid tier)
5. ✅ Set up backup strategy

## Resources

- [Render Docker Documentation](https://render.com/docs/docker)
- [Render Blueprint Docs](https://render.com/docs/blueprint-spec)
- [Render Environment Variables](https://render.com/docs/environment-variables)

---

**Your app is ready to deploy on Render with Docker!** 🚀

Follow this guide step by step, and you'll have your Smart Study Buddy application running in production.
