"""
Alternative Flask app using Server-Sent Events (SSE) instead of WebSockets
This is more Vercel-friendly as it doesn't require special WebSocket support.

To use instead of app.py:
  1. Rename this file from app-sse.py to app.py
  2. Keep the original as app-socketio.py for reference
"""

from flask import Flask, render_template, Response, jsonify, request
from datetime import datetime
import os
import json
import time
from dotenv import load_dotenv
from threading import Lock

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Track connected clients and state
clients = []
clients_lock = Lock()
last_photo = None
last_photo_lock = Lock()

# Track clients for keeping them alive
CHECK_INTERVAL = 5  # seconds

class Client:
    """Represents a connected client"""
    def __init__(self, client_id):
        self.id = client_id
        self.connected_at = datetime.now()
        self.last_heartbeat = datetime.now()
    
    def update_heartbeat(self):
        self.last_heartbeat = datetime.now()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index-sse.html')

@app.route('/api/status')
def status():
    """API endpoint to check if anyone is watching"""
    with clients_lock:
        viewer_count = len(clients)
    
    return {
        'viewers': viewer_count,
        'active': viewer_count > 0,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/photo')
def get_latest_photo():
    """Get the latest photo"""
    with last_photo_lock:
        if last_photo:
            return jsonify(last_photo)
    
    return jsonify({'photo_url': None, 'timestamp': None})

@app.route('/api/upload-photo', methods=['POST'])
def upload_photo():
    """Receive photo from uploader script"""
    data = request.get_json()
    
    if not data or 'photo_url' not in data:
        return {'error': 'Missing photo_url'}, 400
    
    with clients_lock:
        viewer_count = len(clients)
    
    if viewer_count > 0:
        # Store the latest photo
        with last_photo_lock:
            global last_photo
            last_photo = {
                'photo_url': data['photo_url'],
                'timestamp': data.get('timestamp', datetime.now().isoformat())
            }
        
        return {
            'status': 'broadcasted',
            'viewers': viewer_count,
            'timestamp': datetime.now().isoformat()
        }, 200
    else:
        return {
            'status': 'no viewers',
            'viewers': 0,
            'timestamp': datetime.now().isoformat()
        }, 200

@app.route('/api/subscribe')
def subscribe():
    """Server-Sent Events endpoint for real-time updates"""
    client_id = request.args.get('client_id', f"client_{int(time.time())}")
    client = Client(client_id)
    
    with clients_lock:
        clients.append(client)
        viewer_count = len(clients)
    
    print(f"✓ Client connected: {client_id}")
    print(f"  Total viewers: {viewer_count}")
    
    def event_stream():
        last_sent_photo = None
        
        try:
            while True:
                # Check if client is still connected
                client.update_heartbeat()
                
                # Get current photo
                with last_photo_lock:
                    current_photo = last_photo
                
                # Send photo if new
                if current_photo and current_photo != last_sent_photo:
                    yield f"data: {json.dumps({
                        'type': 'photo',
                        'data': current_photo
                    })}\n\n"
                    last_sent_photo = current_photo
                
                # Send viewer count periodically
                with clients_lock:
                    viewer_count = len(clients)
                
                yield f"data: {json.dumps({
                    'type': 'viewer_count',
                    'viewers': viewer_count
                })}\n\n"
                
                # Wait before sending next heartbeat
                time.sleep(CHECK_INTERVAL)
                
        except GeneratorExit:
            # Client disconnected
            with clients_lock:
                if client in clients:
                    clients.remove(client)
                new_viewer_count = len(clients)
            
            print(f"✗ Client disconnected: {client_id}")
            print(f"  Total viewers: {new_viewer_count}")
    
    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
