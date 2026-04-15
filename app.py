from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Track connected clients
connected_clients = set()
WATCH_ROOM = 'photo_watch_room'

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """API endpoint to check if anyone is watching"""
    return {
        'viewers': len(connected_clients),
        'active': len(connected_clients) > 0,
        'timestamp': datetime.now().isoformat()
    }

# SocketIO Events
@app.route('/api/upload-photo', methods=['POST'])
def api_upload_photo():
    data = request.get_json()
    if not data or 'photo_url' not in data:
        return {'status': 'error', 'message': 'Missing photo_url'}, 400
    
    # Broadcast to all connected Socket.IO clients
    socketio.emit('new_photo', {
        'photo_url': data['photo_url'],
        'timestamp': datetime.now().isoformat()
    }, room=WATCH_ROOM)
    
    return {'status': 'broadcasted', 'viewers': len(connected_clients)}

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients.add(client_id)
    join_room(WATCH_ROOM)
    
    print(f"✓ Client connected: {client_id}")
    print(f"  Total viewers: {len(connected_clients)}")
    
    # Notify all clients that viewer count changed
    emit('viewer_count', {'count': len(connected_clients)}, room=WATCH_ROOM)
    
    return True

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    connected_clients.discard(client_id)
    leave_room(WATCH_ROOM)
    
    print(f"✗ Client disconnected: {client_id}")
    print(f"  Total viewers: {len(connected_clients)}")
    
    # Notify all remaining clients that viewer count changed
    emit('viewer_count', {'count': len(connected_clients)}, room=WATCH_ROOM)

@socketio.on('upload_photo')
def handle_photo_upload(data):
    """Receive photo from uploader script and broadcast to viewers"""
    if len(connected_clients) > 0:
        # Broadcast to all connected browsers
        emit('new_photo', {
            'photo_url': data.get('photo_url'),
            'timestamp': datetime.now().isoformat()
        }, room=WATCH_ROOM)
        
        return {'status': 'broadcasted', 'viewers': len(connected_clients)}
    else:
        return {'status': 'no viewers', 'viewers': 0}

@socketio.on('ping')
def handle_ping():
    """Keep-alive ping from client"""
    emit('pong', {'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # For local development
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
