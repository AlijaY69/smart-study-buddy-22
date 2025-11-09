# Deployment Guide

This guide will walk you through deploying Smart Study Buddy to Railway (backend) and Cloudflare Pages (frontend).

## Prerequisites

- GitHub account (for both deployments)
- Railway account ([sign up](https://railway.app/))
- Cloudflare account ([sign up](https://dash.cloudflare.com/sign-up))
- Your project pushed to a GitHub repository

## Part 1: Deploy Backend to Railway

### Step 1: Prepare Your Repository

Make sure your code is pushed to GitHub:
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Create Railway Project

1. Go to [Railway.app](https://railway.app/) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select your `smart-study-buddy-22` repository

### Step 3: Configure Railway Service

1. After the project is created, Railway will detect it's a Python app
2. Click on the service that was created
3. Go to **Settings** tab
4. Set **Root Directory** to: `backend`
5. Under **Deploy**, set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api.py`

### Step 4: Add Environment Variables

In Railway, go to the **Variables** tab and add these:

```env
# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# MongoDB
MONGODB_URI=your_mongodb_connection_string

# SendGrid (optional)
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_verified_sender_email

# User Email
USER_EMAIL=your.email@example.com

# Google Calendar - Important!
# You'll need to handle credentials.json and token.json separately
# For now, we'll set this up after initial deployment
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json

# Application URLs - Update these after deployment
FRONTEND_URL=https://your-app.pages.dev
BACKEND_URL=${{RAILWAY_PUBLIC_DOMAIN}}

# Python Environment
PYTHONUNBUFFERED=1
```

### Step 5: Generate a Domain

1. In Railway, go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy your Railway domain (e.g., `your-app.up.railway.app`)
4. Update the `BACKEND_URL` variable to use this domain

### Step 6: Deploy!

Railway will automatically deploy your backend. Monitor the deployment in the **Deployments** tab.

### Step 7: Set Up Background Worker (Optional)

For the agentic service that syncs calendar every 60 seconds:

**Option A: Add as a Second Service**
1. In your Railway project, click **"+ New"**
2. Select **"Empty Service"**
3. Configure it:
   - Root Directory: `backend`
   - Start Command: `python agentic_service.py`
4. Share all environment variables with this service

**Option B: Use External Cron (Simpler)**
1. Use [cron-job.org](https://cron-job.org/) (free)
2. Set up a job to call `POST https://your-app.up.railway.app/api/calendar/sync` every minute

### Step 8: Handle Google Calendar Credentials

Google credentials are files, not environment variables. Here's how to handle them:

**Option 1: Base64 Encode (Recommended)**
```bash
# In your backend directory
cat credentials.json | base64 > credentials.base64.txt
cat token.json | base64 > token.base64.txt
```

Add to Railway variables:
```env
GOOGLE_CREDENTIALS_BASE64=<paste contents of credentials.base64.txt>
GOOGLE_TOKEN_BASE64=<paste contents of token.base64.txt>
```

Then update `backend/google_calendar.py` to decode these on startup.

**Option 2: Use Railway Volumes**
Upload the files directly to Railway's persistent storage.

---

## Part 2: Deploy Frontend to Cloudflare Pages

### Step 1: Update Frontend Environment

First, update your `.env` file with the Railway backend URL:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_BACKEND_URL=https://your-app.up.railway.app
```

Commit and push:
```bash
git add .env
git commit -m "Update backend URL for production"
git push origin main
```

### Step 2: Deploy via Cloudflare Dashboard

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **Workers & Pages** → **Pages**
3. Click **"Create a project"**
4. Select **"Connect to Git"**
5. Authorize Cloudflare to access your GitHub
6. Select your `smart-study-buddy-22` repository

### Step 3: Configure Build Settings

Set these build configurations:

- **Production branch**: `main`
- **Framework preset**: `Vite`
- **Build command**: `npm run build`
- **Build output directory**: `dist`
- **Root directory**: `/` (leave as project root)
- **Node version**: `18` or higher

### Step 4: Add Environment Variables

In the **Environment Variables** section, add:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_BACKEND_URL=https://your-app.up.railway.app
```

⚠️ **Important**: Add these variables to **both** Production and Preview environments.

### Step 5: Deploy!

Click **"Save and Deploy"**. Cloudflare will:
1. Clone your repository
2. Install dependencies
3. Build your Vite app
4. Deploy to their global CDN

### Step 6: Get Your Cloudflare URL

After deployment completes, you'll get a URL like:
- `https://smart-study-buddy-22.pages.dev`

### Step 7: Update Railway Backend

Go back to Railway and update the `FRONTEND_URL` variable:
```env
FRONTEND_URL=https://smart-study-buddy-22.pages.dev
```

This ensures CORS is properly configured.

---

## Part 3: Test Your Deployment

### Backend Health Check
```bash
curl https://your-app.up.railway.app/api/health
```

Should return: `{"status": "ok"}`

### Frontend Check
1. Visit your Cloudflare Pages URL
2. Try to sign in with Supabase authentication
3. Check browser console for any errors

### API Connection Test
Open browser console on your frontend and run:
```javascript
fetch('https://your-app.up.railway.app/api/calendar/stats')
  .then(r => r.json())
  .then(console.log)
```

---

## Part 4: Set Up Continuous Deployment

Both Railway and Cloudflare Pages are now set up for automatic deployments:

- **Push to `main` branch** → Automatically deploys to both services
- Railway redeploys the backend
- Cloudflare redeploys the frontend

---

## Troubleshooting

### Backend Issues

**Problem**: Backend won't start
- Check Railway logs: Click on service → **Deployments** → Click latest deployment → **View Logs**
- Common issues:
  - Missing environment variables
  - Python version mismatch
  - Import errors

**Problem**: Google Calendar not working
- Check that credentials are properly set up
- Verify token.json is accessible
- Check Railway logs for authentication errors

### Frontend Issues

**Problem**: Build fails on Cloudflare
- Check build logs in Cloudflare Pages dashboard
- Verify all environment variables start with `VITE_`
- Ensure Node version is 18+

**Problem**: Can't connect to backend
- Verify `VITE_BACKEND_URL` is set correctly
- Check CORS settings in backend/api.py
- Ensure Railway backend is running

### CORS Issues

If you get CORS errors, update `backend/api.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    'http://localhost:5173',  # Local development
    'https://smart-study-buddy-22.pages.dev',  # Production
    'https://*.pages.dev'  # All Cloudflare preview deployments
])
```

---

## Cost Breakdown

### Railway (Backend)
- **Free Tier**: $5 credit per month, ~500 hours
- **Hobby Plan**: $5/month for hobby projects
- **Pro Plan**: Starting at $20/month

For this project, the free tier should be sufficient for development/testing.

### Cloudflare Pages (Frontend)
- **Free Tier**: Unlimited bandwidth, unlimited requests
- **Paid Plans**: Only needed for advanced features

Completely free for your use case!

### Total Monthly Cost
- **Development**: $0 (use Railway free credits)
- **Production**: $0-5 depending on Railway usage

---

## Next Steps

After deployment:

1. ✅ Test all functionality
2. ✅ Set up custom domain (optional)
3. ✅ Configure production Google OAuth credentials
4. ✅ Set up monitoring/logging
5. ✅ Enable Railway backups
6. ✅ Set up status monitoring (e.g., UptimeRobot)

---

## Custom Domains (Optional)

### Cloudflare Pages Custom Domain
1. In Cloudflare Pages, go to **Custom domains**
2. Add your domain (e.g., `studybuddy.com`)
3. Follow DNS configuration instructions

### Railway Custom Domain
1. In Railway Settings → **Networking**
2. Add custom domain
3. Configure DNS CNAME record

---

## Support

- **Railway Docs**: https://docs.railway.app/
- **Cloudflare Pages Docs**: https://developers.cloudflare.com/pages/
- **Issues**: Create an issue in your GitHub repository

---

## Quick Reference

### Useful Commands

**Check Railway Logs**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# View logs
railway logs
```

**Rebuild Cloudflare Pages**
```bash
# Install Wrangler CLI
npm i -g wrangler

# Deploy manually
npm run build
wrangler pages deploy dist --project-name=smart-study-buddy-22
```

### Important URLs
- Railway Dashboard: https://railway.app/dashboard
- Cloudflare Dashboard: https://dash.cloudflare.com/
- Backend URL: `https://your-app.up.railway.app`
- Frontend URL: `https://smart-study-buddy-22.pages.dev`
