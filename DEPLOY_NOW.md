# Quick Deployment Instructions

Your Smart Study Buddy app is ready to deploy! Follow these steps:

## Step 1: Push Latest Changes to GitHub

```bash
git push origin main
```

If you get a 403 error, you may need to update your git credentials or push manually through GitHub Desktop/web interface.

## Step 2: Deploy Backend to Railway

### Option A: Using Railway Dashboard (Recommended)

1. Go to **[railway.app](https://railway.app)** and sign in
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `smart-study-buddy-22` repository
4. Configure the service:
   - **Root Directory**: `backend`
   - **Start Command**: (will use Procfile automatically)

5. Add Environment Variables (click **Variables** tab):
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_service_role_key
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URI=your_mongodb_connection_string
   SENDGRID_API_KEY=your_sendgrid_api_key
   SENDGRID_FROM_EMAIL=your_verified_sender_email
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   USER_EMAIL=your_email@gmail.com
   FRONTEND_URL=https://your-app.vercel.app
   BACKEND_URL=https://your-app.railway.app
   ```

6. Click **"Deploy"**

7. Once deployed, note your Railway URL (e.g., `https://your-app.railway.app`)

### Add Worker Service (Agentic AI)

1. In same Railway project, click **"+ New"** → **"GitHub Repo"**
2. Select same repository
3. Configure:
   - **Root Directory**: `backend`
   - **Start Command**: `python agentic_service.py`
4. Add same environment variables as above
5. Deploy

## Step 3: Deploy Frontend to Vercel

### Option A: Using Vercel Dashboard (Recommended)

1. Go to **[vercel.com](https://vercel.com)** and sign in
2. Click **"New Project"**
3. Import your `smart-study-buddy-22` repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `./`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Add Environment Variables:
   ```
   VITE_SUPABASE_URL=your_supabase_project_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

6. Click **"Deploy"**

7. Once deployed, note your Vercel URL (e.g., `https://your-app.vercel.app`)

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

## Step 4: Update Environment Variables

Now that you have both URLs, update them:

### In Railway (Backend):
- Update `FRONTEND_URL` to your Vercel URL
- Update `BACKEND_URL` to your Railway URL

### In Your Frontend Code:
If you hardcoded any backend URLs, update them to your Railway URL.

## Step 5: Configure Supabase

1. Go to **Supabase Dashboard** → **Authentication** → **URL Configuration**
2. Set **Site URL**: `https://your-vercel-app.vercel.app`
3. Add **Redirect URLs**:
   - `https://your-vercel-app.vercel.app`
   - `https://your-vercel-app.vercel.app/auth`

## Step 6: Update CORS (if needed)

If you get CORS errors, update `backend/api.py`:

```python
from flask_cors import CORS

CORS(app, origins=[
    "https://your-vercel-app.vercel.app",
    "http://localhost:5173"  # For local development
])
```

Then redeploy backend.

## Step 7: Test Your Deployment

1. Visit your Vercel URL
2. Create an account
3. Test calendar sync
4. Create an assignment
5. Upload materials
6. Generate exercises
7. Check if email notifications work

## Troubleshooting

### Backend Not Starting
- Check Railway logs for errors
- Verify all environment variables are set
- Ensure MongoDB connection string is correct

### Frontend Can't Connect to Backend
- Check CORS configuration
- Verify `BACKEND_URL` in frontend
- Check Railway service is running

### Database Errors
- Ensure Supabase migrations are applied
- Check service role key (not anon key) is used in backend
- Verify MongoDB Atlas IP whitelist allows Railway

### Google Calendar Not Working
- Upload `credentials.json` to Railway
- May need to handle `token.json` via environment variable
- Check OAuth redirect URIs

## Quick Deploy Commands Reference

```bash
# Deploy Frontend
npm install -g vercel
vercel --prod

# Deploy Backend (if using Railway CLI)
npm install -g @railway/cli
railway login
cd backend
railway up
```

## Cost Estimate

- **Vercel**: Free (Hobby tier)
- **Railway**: ~$5-10/month
- **Supabase**: Free tier
- **MongoDB Atlas**: Free tier
- **OpenAI**: Usage-based (~$5-20/month)

**Total**: ~$10-30/month

---

## Next Steps After Deployment

1. Test all features
2. Monitor logs for errors
3. Set up custom domain (optional)
4. Configure SSL certificates (usually automatic)
5. Set up monitoring/alerts
6. Create backup strategy

---

**Your app is ready to deploy!** 🚀

For detailed instructions, see `DEPLOYMENT.md`
