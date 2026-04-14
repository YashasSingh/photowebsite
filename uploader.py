"""
Screenshot Uploader Script
==========================
This script monitors the live photo stream channel and uploads screenshots 
when someone is viewing the website.

Usage:
    python uploader.py --url http://localhost:5000 --interval 5
    
Or with environment variables:
    FLASK_URL=http://yoururl.com python uploader.py --interval 5

The script will:
1. Check if anyone is viewing the website
2. If yes: capture a screenshot and upload it
3. If no: wait and check again
4. Repeat until stopped
"""

import socketio
import time
import argparse
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Try to import screenshot libraries (optional)
try:
    from PIL import ImageGrab
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    print("Warning: Pillow not installed. Using dummy images.")

load_dotenv()

# Configuration
FLASK_URL = os.getenv('FLASK_URL', 'http://localhost:5000')
UPLOAD_INTERVAL = 5  # seconds between uploads when channel is active
CHECK_INTERVAL = 2   # seconds between checking if anyone is viewing

# Create screenshots directory
SCREENSHOTS_DIR = Path('screenshots')
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Initialize SocketIO client
sio = socketio.Client()

class UploaderState:
    """Track uploader state"""
    is_connected = False
    viewers_online = 0
    last_upload_time = 0
    upload_count = 0

state = UploaderState()

@sio.event
def connect():
    """Handle successful connection to Flask server"""
    print(f"✓ Connected to {FLASK_URL}")
    state.is_connected = True

@sio.event
def disconnect():
    """Handle disconnection from Flask server"""
    print("✗ Disconnected from server")
    state.is_connected = False

@sio.on('viewer_count')
def on_viewer_count(data):
    """Receive viewer count updates"""
    state.viewers_online = data['count']
    status = "🟢 ACTIVE" if state.viewers_online > 0 else "🔴 IDLE"
    print(f"{status} | Viewers: {state.viewers_online}")

def capture_screenshot():
    """Capture a screenshot from the screen"""
    try:
        if SCREENSHOT_AVAILABLE:
            # Capture screenshot (works on Windows, Mac, Linux)
            screenshot = ImageGrab.grab()
            return screenshot
        else:
            # Dummy image for testing
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), f"Dummy Screenshot - {datetime.now()}", fill='black')
            return img
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None

def save_screenshot(screenshot, filename=None):
    """Save screenshot to disk"""
    try:
        if filename is None:
            filename = f"screenshot_{int(time.time())}.png"
        
        filepath = SCREENSHOTS_DIR / filename
        screenshot.save(str(filepath))
        return str(filepath)
    except Exception as e:
        print(f"Error saving screenshot: {e}")
        return None

def create_dummy_photo_url():
    """Create a data URL for dummy photo (for testing without real screenshots)"""
    import base64
    from io import BytesIO
    from PIL import Image, ImageDraw
    
    # Create a simple test image
    img = Image.new('RGB', (400, 300), color=(100, 150, 200))
    draw = ImageDraw.Draw(img)
    
    # Add current time as text
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((20, 20), f"Screenshot: {timestamp}", fill=(255, 255, 255))
    draw.text((20, 60), f"Viewers: {state.viewers_online}", fill=(255, 255, 255))
    
    # Convert to base64 data URL
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def upload_photo():
    """Capture and upload a photo"""
    if not state.is_connected:
        print("Not connected to server, skipping upload")
        return False
    
    if state.viewers_online == 0:
        print("No viewers online, skipping upload")
        return False
    
    try:
        # Capture screenshot
        print("📸 Capturing screenshot...", end=" ", flush=True)
        screenshot = capture_screenshot()
        
        if screenshot is None:
            print("Failed!")
            return False
        
        # Save locally
        filepath = save_screenshot(screenshot)
        print(f"Saved to {filepath}")
        
        # Create photo URL (using data URL for demo, or you can upload to cloud storage)
        # For production, you'd upload to AWS S3, Google Cloud Storage, etc.
        photo_url = create_dummy_photo_url()
        
        # Upload via SocketIO
        print("📤 Uploading...", end=" ", flush=True)
        response = sio.call('upload_photo', {
            'photo_url': photo_url,
            'timestamp': datetime.now().isoformat()
        })
        
        if response:
            state.upload_count += 1
            print(f"Success! ({response['status']}, viewers: {response['viewers']})")
            return True
        else:
            print("No response")
            return False
            
    except Exception as e:
        print(f"Error uploading photo: {e}")
        return False

def main():
    """Main uploader loop"""
    parser = argparse.ArgumentParser(description='Upload screenshots to live photo stream')
    parser.add_argument('--url', default=FLASK_URL, help='Flask server URL')
    parser.add_argument('--interval', type=int, default=UPLOAD_INTERVAL, help='Upload interval in seconds')
    parser.add_argument('--check-interval', type=int, default=CHECK_INTERVAL, help='Viewer check interval')
    
    args = parser.parse_args()
    
    global FLASK_URL
    FLASK_URL = args.url
    UPLOAD_INTERVAL = args.interval
    CHECK_INTERVAL = args.check_interval
    
    print(f"""
╔════════════════════════════════════════╗
║   Live Photo Stream Uploader            ║
╚════════════════════════════════════════╝

📍 Server: {FLASK_URL}
⏱️  Upload Interval: {UPLOAD_INTERVAL}s
🔄 Check Interval: {CHECK_INTERVAL}s

Connecting...
    """)
    
    try:
        # Connect to Flask server
        sio.connect(FLASK_URL, wait_timeout=10)
        
        last_upload = 0
        
        print("\n✓ Ready! Monitoring channel...\n")
        
        # Main loop
        while True:
            time.sleep(CHECK_INTERVAL)
            
            current_time = time.time()
            
            # If viewers are online and enough time has passed, upload
            if state.viewers_online > 0 and (current_time - last_upload >= UPLOAD_INTERVAL):
                upload_photo()
                last_upload = current_time
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping uploader...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if state.is_connected:
            sio.disconnect()
        
        print(f"""
╔════════════════════════════════════════╗
║        Uploader Stopped                 ║
╚════════════════════════════════════════╝

📊 Statistics:
   Total uploads: {state.upload_count}
   Screenshots taken: {len(list(SCREENSHOTS_DIR.glob('*.png')))}
        """)

if __name__ == '__main__':
    main()
