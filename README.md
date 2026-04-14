# 📸 Live Photo Stream - Flask + Vercel

A real-time photo streaming application where a Python uploader script sends screenshots only when someone is actively viewing the website.

## 🎯 How It Works

1. **Web Browser** opens the site → establishes a WebSocket connection
2. **Flask Server** detects an active viewer and broadcasts a "channel open" signal
3. **Python Uploader Script** monitors this signal:
   - If channel is **OPEN** (viewers online) → captures & uploads screenshots every N seconds
   - If channel is **CLOSED** (no viewers) → stops uploading, saves resources
4. **Browsers** receive photos in real-time via WebSocket

```
Browser ←→ [Flask Server] ←→ Uploader Script
           (WebSocket)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env and change SECRET_KEY to something random
```

### 3. Run Flask Server Locally

```bash
python app.py
```

Server will start on `http://localhost:5000`

### 4. In Another Terminal, Run Uploader Script

```bash
python uploader.py --url http://localhost:5000 --interval 5
```

- `--url`: Flask server URL
- `--interval`: Seconds between screenshots (when viewers are online)

### 5. Open the Website

Visit `http://localhost:5000` in your browser → you'll see photos appear!

## 📁 Project Structure

```
photowebsite/
├── app.py                 # Flask server with WebSocket
├── uploader.py            # Screenshot uploader script
├── templates/
│   └── index.html         # Web frontend (HTML + JavaScript)
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment config
├── .env.example          # Environment variables template
└── screenshots/          # Local screenshots folder (created at runtime)
```

## 🛠️ Customization

### Change Upload Interval

```bash
# Upload a new screenshot every 10 seconds
python uploader.py --interval 10
```

### Use Real Screenshots

The default uploader creates dummy test images. For real screenshots:

1. Ensure Pillow is installed (it is, in requirements.txt)
2. Uploader will automatically use `ImageGrab` for real screenshots
3. Works on Windows, Mac, and Linux

### Upload to Cloud Storage

For production, store screenshots in cloud storage (AWS S3, Google Cloud Storage, etc.) instead of data URLs:

```python
# In uploader.py, replace create_dummy_photo_url() with:
photo_url = upload_to_s3(screenshot)  # Your implementation
```

## 🌐 Deployment to Vercel

### Option 1: Direct Vercel Deployment

```bash
npm i -g vercel
vercel
```

### Option 2: Deploy with Git (GitHub)

1. Push to GitHub
2. Connect to Vercel
3. Vercel automatically deploys on push

### Option 3: Environment Variables on Vercel

1. Go to Vercel Dashboard → Settings → Environment Variables
2. Add `SECRET_KEY` with a random value
3. Add `FLASK_URL` with your Vercel domain

## 📋 API Endpoints

### REST API

- **GET** `/` - Serves the main page
- **GET** `/api/status` - Returns `{viewers: int, active: bool, timestamp: string}`

### WebSocket Events

#### Client Events (sent from browser)
- `connect` - Browser connects (automatic)
- `disconnect` - Browser leaves (automatic)
- `ping` - Keep-alive signal

#### Server Events (sent to browser)
- `viewer_count` - `{count: int}` - Viewer count updated
- `new_photo` - `{photo_url: string, timestamp: string}` - New photo arrived

#### Uploader Events
- `upload_photo` - `{photo_url: string, timestamp: string}` - Upload photo from script

## 🔒 Security Notes

- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Consider adding authentication for uploader script
- Use HTTPS in production

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Connection refused to localhost:5000
- Make sure Flask server is running: `python app.py`
- Check that port 5000 is not in use

### No photos appearing
1. Check uploader script is running
2. Verify Flask URL in uploader matches your server
3. Check browser console for errors (F12)

### WebSocket connection failed on Vercel
- Vercel requires special configuration for WebSockets
- Alternative: Use Server-Sent Events (SSE) instead
- See `app-sse.py` for SSE version

## 📚 Documentation

- [Flask-SocketIO Docs](https://flask-socketio.readthedocs.io/)
- [Socket.IO Client Docs](https://socket.io/docs/client-api/)
- [Vercel Python Guide](https://vercel.com/docs/functions/serverless-functions/python)

## 📝 License

MIT License - feel free to use and modify!

## 💡 Future Enhancements

- [ ] Add authentication for uploader
- [ ] Store photos in cloud storage
- [ ] Add photo viewer with zoom
- [ ] Support multiple channels
- [ ] Add history/archive of photos
- [ ] Performance dashboards
- [ ] Automated screenshot scheduling
