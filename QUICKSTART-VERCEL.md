# 🚀 QUICK START - Vercel Format

## Local Development (2 Minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create .env File
```bash
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux
```

### Step 3: Start Flask Server
```bash
python api/index.py
```

URL: **http://localhost:5000**

### Step 4: Open Website
Visit **http://localhost:5000** in your browser

You should see:
- ✓ Live Photo Stream interface
- ✓ "Connecting..." status
- ✓ "👥 Connecting..." viewer count

### Step 5: Start Uploader (New Terminal)
```bash
python uploader_vercel.py --url http://localhost:5000 --interval 5
```

You should see:
```
✓ Server is reachable
✓ Ready! Monitoring channel...

🟢 ACTIVE | Viewers: 1
📸 Capturing screenshot... Saved ✓
🔄 Converting to data URL... Done (...)
📤 Uploading... ✓ Success! (Viewers: 1)
```

✅ **Photos appear instantly in your browser!**

---

## Deploy to Vercel (2 Minutes)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Deploy
```bash
vercel
```

Answer the prompts:
- Set up and deploy? → `y`
- Which scope? → (Your account)
- Link to existing project? → `n`
- Project name? → `photowebsite` (or your choice)
- Production? → `y`

### Step 3: Get Your URL
Vercel shows you the URL:
```
✅ Production: https://photowebsite-abc123.vercel.app
```

Copy this URL!

### Step 4: Set Environment Variables

On Vercel Dashboard:
1. Go to your project
2. Settings → Environment Variables
3. Add:
   - **Name**: `SECRET_KEY`
     **Value**: `any-random-string`
   - **Name**: `FLASK_URL`
     **Value**: `https://photowebsite-abc123.vercel.app`
4. Click "Save"

### Step 5: Test It
Visit your Vercel URL → you should see the Live Photo Stream

### Step 6: Run Uploader
```bash
python uploader_vercel.py --url https://photowebsite-abc123.vercel.app --interval 5
```

Photos upload to your live site! 🎉

---

## Usage

### Keep Website Open
- Every 5 seconds: new screenshot uploaded
- Close tab: uploader stops
- Reopen tab: uploader resumes

### Change Upload Speed
```bash
# Every 10 seconds
python uploader_vercel.py --url YOUR_URL --interval 10

# Every 2 seconds
python uploader_vercel.py --url YOUR_URL --interval 2
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Make sure `python api/index.py` is running |
| No photos appearing | Check uploader shows "🟢 ACTIVE" |
| "502 Bad Gateway" on Vercel | Check deployment logs: `vercel logs` |
| Uploader won't connect to Vercel | Use full HTTPS URL, check firewall |

---

## Files Explained

| File | Purpose |
|------|---------|
| `api/index.py` | Flask server (runs on Vercel) |
| `templates/vercel.html` | Website frontend |
| `uploader_vercel.py` | Screenshot uploader (runs on your PC) |
| `vercel.json` | Vercel configuration |
| `requirements.txt` | Python packages |

---

## Next Steps

📚 See **VERCEL_DEPLOY.md** for full deployment guide  
📚 See **README.md** for advanced features  
💬 See **Troubleshooting** section above

**You're done! Your site is live! 🚀**
