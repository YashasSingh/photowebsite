# 🚀 QUICK START GUIDE

## Local Development (Windows, Mac, Linux)

### Step 1: Install Python Packages
```bash
pip install -r requirements.txt
```

### Step 2: Create .env File
```bash
# Copy example to .env
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux

# Edit .env and change SECRET_KEY to something random
# Example: SECRET_KEY=abc123xyz789random
```

### Step 3: Start Flask Server
```bash
python app.py
```
You should see:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Step 4: Open Browser
Visit: **http://localhost:5000**

You should see the Live Photo Stream interface with "Channel Active" status.

### Step 5: Start Uploader (New Terminal)
```bash
python uploader.py --url http://localhost:5000 --interval 5
```

You should see:
```
✓ Connected to http://localhost:5000
✓ Ready! Monitoring channel...

🟢 ACTIVE | Viewers: 1
📸 Capturing screenshot... Saved to screenshots/screenshot_1234567890.png
📤 Uploading... Success! (broadcasted, viewers: 1)
```

✅ **Photos should now appear in your browser!**

---

## 📱 Usage

### Keep the Website Open
- Every 5 seconds (default), a screenshot is captured and uploaded
- Close the page? → Uploader stops sending screenshots
- Reopen the page? → Uploader resumes automatically

### Adjust Upload Frequency
```bash
# Every 10 seconds instead of 5
python uploader.py --url http://localhost:5000 --interval 10

# Every 2 seconds (fast!)
python uploader.py --url http://localhost:5000 --interval 2
```

### Custom Server URL
```bash
# For testing on different machine
python uploader.py --url http://192.168.1.100:5000 --interval 5
```

---

## 🌐 Deploy to Vercel

### Prerequisites
- GitHub account
- Vercel account (free tier works!)
- Git installed

### Option A: Deploy via CLI (Fastest)
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy
vercel

# 3. Follow prompts and answer:
#    - Link to existing project? No
#    - Set project name? (press enter for default)
#    - Deploy anyway? Yes
```

### Option B: Deploy via GitHub
```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/photowebsite.git
git push -u origin main

# 2. Go to https://vercel.com/new
# 3. Import your GitHub repo
# 4. Click "Deploy"
```

### After Deployment
1. Get your Vercel URL (e.g., `photowebsite-abc123.vercel.app`)
2. Set environment variable on Vercel Dashboard:
   - Go to Settings → Environment Variables
   - Add: `SECRET_KEY` = (generate random string)
   - Add: `FLASK_URL` = `https://photowebsite-abc123.vercel.app`

3. Run uploader with Vercel URL:
```bash
python uploader.py --url https://photowebsite-abc123.vercel.app --interval 5
```

---

## ❓ Troubleshooting

### "Address already in use" error?
Port 5000 is taken. Kill it:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5000 | xargs kill -9
```

### No photos showing up?
1. Check uploader is running (should show "🟢 ACTIVE")
2. Check Flask server is running (http://localhost:5000 loads)
3. Check browser console: Press F12 → Console tab → Look for errors

### "Connection refused" error?
- Make sure Flask server is running on correct URL
- If running on different machine: use that machine's IP
  ```bash
  # Get your IP on Windows
  ipconfig | find "IPv4"
  
  # Then run uploader with that IP
  python uploader.py --url http://192.168.1.100:5000 --interval 5
  ```

### "ModuleNotFoundError"?
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## 🎯 Next Steps

- **Customize upload logic**: Edit `uploader.py`
- **Change website design**: Edit `templates/index.html`
- **Add authentication**: See `README.md`
- **Use cloud storage**: See `README.md` for AWS S3 integration

---

## 🎓 Learn More

- See **README.md** for detailed documentation
- See **app.py** for Flask server code
- See **uploader.py** for screenshot logic
- See **templates/index.html** for web interface

---

**Need help?** Check the README.md file or modify the code to suit your needs! 🚀
