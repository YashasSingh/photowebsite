"""
Screenshot Uploader Script for Vercel API
===========================================
This script monitors the live photo stream channel via REST API
and uploads screenshots when someone is viewing the website.

Usage:
    python uploader_vercel.py --url https://yoursite.vercel.app --interval 5
    
Or with environment variables:
    FLASK_URL=https://yoursite.vercel.app python uploader_vercel.py --interval 5

How it works:
1. Checks /api/status to see if anyone is viewing
2. If yes: capture a screenshot and POST to /api/upload-photo
3. If no: wait and check again
4. Repeat until stopped
"""

import requests
import time
import argparse
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import base64
from io import BytesIO

# Try to import screenshot library
try:
    from PIL import Image, ImageDraw, ImageGrab
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    print("⚠️  Warning: Pillow not installed. Using dummy images.")

load_dotenv()

# Configuration
FLASK_URL = os.getenv('FLASK_URL', 'http://localhost:5000').rstrip('/')
UPLOAD_INTERVAL = 5  # seconds between uploads when channel is active
CHECK_INTERVAL = 2   # seconds between checking if anyone is viewing

# Create screenshots directory
SCREENSHOTS_DIR = Path('screenshots')
SCREENSHOTS_DIR.mkdir(exist_ok=True)

class UploaderState:
    """Track uploader state"""
    is_ready = False
    viewers_online = 0
    last_upload_time = 0
    upload_count = 0
    failed_uploads = 0
    last_error = None

state = UploaderState()

def check_server_status():
    """Check if server is online and get viewer count"""
    try:
        response = requests.get(f'{FLASK_URL}/api/status', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            state.viewers_online = data.get('viewers', 0)
            state.is_ready = True
            return True
        else:
            state.is_ready = False
            state.last_error = f"HTTP {response.status_code}"
            return False
            
    except requests.exceptions.ConnectionError:
        state.is_ready = False
        state.last_error = "Connection refused"
        return False
    except requests.exceptions.Timeout:
        state.is_ready = False
        state.last_error = "Timeout"
        return False
    except Exception as e:
        state.is_ready = False
        state.last_error = str(e)
        return False

def capture_screenshot():
    """Capture a screenshot from the screen"""
    try:
        if SCREENSHOT_AVAILABLE:
            try:
                # Try to capture actual screenshot
                screenshot = ImageGrab.grab()
                return screenshot
            except:
                # Fallback to dummy image
                return create_dummy_image()
        else:
            return create_dummy_image()
    except Exception as e:
        print(f"❌ Error capturing screenshot: {e}")
        return None

def create_dummy_image():
    """Create a dummy image for testing"""
    try:
        img = Image.new('RGB', (800, 600), color=(100, 150, 200))
        draw = ImageDraw.Draw(img)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        viewers = state.viewers_online
        
        try:
            draw.text((20, 20), f"Screenshot: {timestamp}", fill=(255, 255, 255))
            draw.text((20, 60), f"Viewers: {viewers}", fill=(255, 255, 255))
            draw.text((20, 100), f"Uploads: {state.upload_count}", fill=(255, 255, 255))
        except:
            # Font not available, that's ok
            pass
        
        return img
    except Exception as e:
        print(f"❌ Error creating dummy image: {e}")
        return None

def screenshot_to_data_url(screenshot):
    """Convert PIL Image to data URL"""
    try:
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode()
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f"❌ Error converting to data URL: {e}")
        return None

def save_screenshot_locally(screenshot, filename=None):
    """Save screenshot to disk for reference"""
    try:
        if filename is None:
            filename = f"screenshot_{int(time.time())}.png"
        
        filepath = SCREENSHOTS_DIR / filename
        screenshot.save(str(filepath))
        return str(filepath)
    except Exception as e:
        print(f"⚠️  Error saving screenshot: {e}")
        return None

def upload_photo():
    """Capture and upload a photo via REST API"""
    if not state.is_ready:
        print("❌ Server not ready")
        return False
    
    if state.viewers_online == 0:
        print("⏸️  No viewers online")
        return False
    
    try:
        # Capture screenshot
        print("📸 Capturing screenshot...", end=" ", flush=True)
        screenshot = capture_screenshot()
        
        if screenshot is None:
            print("Failed!")
            return False
        
        # Save locally for reference
        save_screenshot_locally(screenshot)
        print("Saved ✓")
        
        # Convert to data URL
        print("🔄 Converting to data URL...", end=" ", flush=True)
        photo_url = screenshot_to_data_url(screenshot)
        
        if not photo_url:
            print("Failed!")
            return False
        print(f"Done ({len(photo_url)} bytes)")
        
        # Upload via REST API
        print("📤 Uploading...", end=" ", flush=True)
        
        payload = {
            'photo_url': photo_url,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        response = requests.post(
            f'{FLASK_URL}/api/upload-photo',
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            state.upload_count += 1
            viewers = data.get('viewers', 0)
            print(f"✓ Success! (Viewers: {viewers})")
            return True
        else:
            print(f"Failed (HTTP {response.status_code})")
            state.failed_uploads += 1
            state.last_error = f"HTTP {response.status_code}"
            return False
            
    except requests.exceptions.Timeout:
        print("Failed (Timeout)")
        state.failed_uploads += 1
        state.last_error = "Upload timeout"
        return False
    except Exception as e:
        print(f"Failed ({str(e)})")
        state.failed_uploads += 1
        state.last_error = str(e)
        return False

def show_banner():
    """Display startup banner"""
    print(f"""
╔════════════════════════════════════════╗
║   Live Photo Stream Uploader            ║
║       (Vercel API Version)              ║
╚════════════════════════════════════════╝

📍 Server: {FLASK_URL}
⏱️  Upload Interval: {UPLOAD_INTERVAL}s
🔄 Check Interval: {CHECK_INTERVAL}s

Checking server...
    """)

def show_status(reason=""):
    """Display current status with emoji"""
    status = ""
    
    if state.is_ready:
        if state.viewers_online > 0:
            status = f"🟢 ACTIVE | Viewers: {state.viewers_online}"
        else:
            status = "⚫ IDLE   | Waiting for viewers"
    else:
        status = f"⛔ ERROR  | {state.last_error}"
    
    if reason:
        status += f" ({reason})"
    
    print(status)

def main():
    """Main uploader loop"""
    parser = argparse.ArgumentParser(
        description='Upload screenshots via REST API to live photo stream'
    )
    parser.add_argument(
        '--url',
        default=FLASK_URL,
        help='Flask/Vercel server URL'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=UPLOAD_INTERVAL,
        help='Upload interval in seconds'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=CHECK_INTERVAL,
        help='Server check interval in seconds'
    )
    
    args = parser.parse_args()
    
    global FLASK_URL
    FLASK_URL = args.url.rstrip('/')
    UPLOAD_INTERVAL = args.interval
    CHECK_INTERVAL = args.check_interval
    
    show_banner()
    
    try:
        # Check server connectivity
        for attempt in range(3):
            if check_server_status():
                print("✓ Server is reachable\n")
                break
            else:
                print(f"❌ Attempt {attempt + 1}/3 failed: {state.last_error}")
                if attempt < 2:
                    time.sleep(2)
        
        if not state.is_ready:
            print("\n❌ Cannot connect to server. Exiting.")
            return
        
        last_upload = 0
        last_status_check = 0
        
        print("✓ Ready! Monitoring channel...\n")
        
        # Main loop
        while True:
            current_time = time.time()
            
            # Check server status periodically
            if current_time - last_status_check >= CHECK_INTERVAL:
                check_server_status()
                show_status()
                last_status_check = current_time
            
            # If viewers are online and enough time has passed, upload
            if state.is_ready and state.viewers_online > 0:
                if current_time - last_upload >= UPLOAD_INTERVAL:
                    upload_photo()
                    last_upload = current_time
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping uploader...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if state.is_ready:
            print(f"""
╔════════════════════════════════════════╗
║        Uploader Stopped                 ║
╚════════════════════════════════════════╝

📊 Statistics:
   Total uploads: {state.upload_count}
   Failed uploads: {state.failed_uploads}
   Screenshots saved: {len(list(SCREENSHOTS_DIR.glob('*.png')))}
   Last error: {state.last_error or 'None'}
        """)

if __name__ == '__main__':
    main()
