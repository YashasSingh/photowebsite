# 🚀 Vercel Deployment Guide

## Overview

This project is now set up for **Vercel serverless deployment**. The REST API approach works perfectly with Vercel's serverless functions.

## Project Structure (Vercel Format)

```
photowebsite/
├── api/
│   └── index.py              # Flask app (serverless function)
├── templates/
│   └── vercel.html           # Web frontend with polling
├── uploader_vercel.py        # REST API uploader script
├── vercel.json              # Vercel configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # Documentation
```

## Key Differences from WebSocket Version

✅ **REST API** instead of WebSockets (Vercel-compatible)  
✅ **Polling-based** client (every 2 seconds)  
✅ **Stateless** serverless functions  
✅ **No long-running connections** (Vercel limitation)  
✅ **Better scalability** - can handle many concurrent requests

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env File
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux
```

Edit `.env`:
```
SECRET_KEY=your-random-secret-key-here
FLASK_URL=http://localhost:5000
```

### 3. Run Flask Locally
```bash
python api/index.py
```

Server will start on `http://localhost:5000`

### 4. Run Uploader
In another terminal:
```bash
python uploader_vercel.py --url http://localhost:5000 --interval 5
```

## Deploy to Vercel

### Option 1: CLI Deployment (Fastest)

#### Prerequisites
- Node.js installed (for Vercel CLI)
- GitHub/GitLab/Bitbucket account (or email)

#### Steps

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy (from project folder)
vercel

# 3. Answer prompts:
#    Set up and deploy "~/pathtoproject"? > y
#    Which scope? (your account)
#    Link to existing project? > n
#    Project name? > photowebsite (or your choice)
#    Production? > y
```

Vercel will:
- Build the project
- Deploy to `https://photowebsite-xxx.vercel.app`
- Show you the deployment URL

### Option 2: GitHub Integration (Recommended)

#### Steps

```bash
# 1. Initialize git repo
git init
git add .
git commit -m "Initial commit"

# 2. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/photowebsite.git
git branch -M main
git push -u origin main
```

Then:
1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your GitHub repo
4. Click "Deploy"

Vercel will auto-deploy on every push to main!

## After Deployment

### 1. Set Environment Variables

On Vercel Dashboard:
1. Go to your project → Settings → Environment Variables
2. Add these variables:
   - `SECRET_KEY`: Generate a random string
   - `FLASK_URL`: Your Vercel URL (e.g., `https://photowebsite-abc.vercel.app`)

### 2. Test the Deployment

1. Visit your Vercel URL (e.g., `https://photowebsite-abc.vercel.app`)
2. You should see the Live Photo Stream interface
3. Status should show "Connecting..." then "Connected"

### 3. Run Uploader Against Vercel

```bash
python uploader_vercel.py --url https://photowebsite-abc.vercel.app --interval 5
```

Photos should now appear on your live site!

## API Endpoints

### Status & Info
- `GET /api/status` - Get viewer count and channel status
- `GET /api/health` - Health check
- `GET /api/photo` - Get latest photo

### Viewer Management
- `POST /api/viewer/connect?client_id=xxx` - Register viewer
- `POST /api/viewer/disconnect?client_id=xxx` - Unregister viewer

### Upload
- `POST /api/upload-photo` - Upload new photo (from uploader script)

### Polling
- `GET /api/subscribe?last_timestamp=xxx` - Poll for new photos

## Monitoring & Debugging

### View Logs
```bash
# View deployment logs
vercel logs

# View real-time logs
vercel logs --follow
```

### Check Status
```bash
# Test health endpoint
curl https://photowebsite-abc.vercel.app/api/health
```

## Troubleshooting

### "502 Bad Gateway" Error
- Check that `api/index.py` is properly formatted
- Verify `vercel.json` exists and is valid
- Check deployment logs: `vercel logs`

### Uploader Can't Connect
- Verify Vercel deployment URL is correct
- Check network (firewall might block)
- Check `FLASK_URL` in `.env` on Vercel Dashboard

### Photos Not Appearing
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests
4. Verify uploader is running and shows "🟢 ACTIVE"

### Cold Start Delays
Vercel serverless functions have ~5 second cold start:
- First request after deployment will be slow
- Subsequent requests are instant
- This is normal and expected

## Production Best Practices

### 1. Change Secret Key
Generate a random string:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Add to Vercel Environment Variables:
- `SECRET_KEY`: Your generated value

### 2. Add Custom Domain
On Vercel Dashboard:
1. Project Settings → Domains
2. Add your custom domain
3. Update DNS records (instructions provided)

### 3. Enable Analytics
On Vercel Dashboard:
1. Project Settings → Analytics
2. Enable Web Analytics
3. Monitor usage and performance

### 4. Set Up Alerts
On Vercel Dashboard:
1. Notifications → Alert Rules
2. Alert on deployment failures
3. Alert on high error rates

## Scaling & Performance

### Limits
- **Max function duration**: 60 seconds (set in vercel.json)
- **Max response size**: 4.5 MB
- **Max request body**: 4.5 MB
- **Concurrent requests**: Unlimited on Pro plan

### Optimization
- Data URLs work for small images
- For large images: use cloud storage (AWS S3, Cloudinary)
- Images over 1MB should be compressed

## Upgrading to Pro

For production use:
- **Free Tier**: Limited to 100 serverless function invocations/day
- **Pro**: $20/month, unlimited invocations
- Upgrade on Vercel Dashboard → Billing

## Backup & Version Control

Always keep your code in Git:
```bash
# Create local backup
git archive --format=zip --output=backup.zip HEAD

# Tag releases
git tag -a v1.0 -m "First production release"
git push origin v1.0
```

## Support Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Flask on Vercel](https://vercel.com/docs/frameworks/flask)
- [Python Serverless Functions](https://vercel.com/docs/functions/serverless-functions/python)

---

**Your site is ready for production! 🎉**
