from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# In-memory storage (for Vercel, consider using Vercel KV instead)
# This will reset on each deployment/redeploy
state = {
    'active_clients': set(),
    'last_photo': None,
    'last_updated': None,
    'viewer_count': 0
}

# For production, use a database or Vercel KV
# pip install vercel-kv for persistent storage

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('vercel.html')

@app.route('/status', methods=['GET'])
def api_status():
    """Check if anyone is watching"""
    # Get client IP as unique identifier
    client_ip = request.remote_addr
    
    # Optional: track viewers by IP (session-based)
    # For simplicity, just return current viewer count
    
    return jsonify({
        'viewers': state['viewer_count'],
        'active': state['viewer_count'] > 0,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/photo', methods=['GET'])
def api_get_photo():
    """Get the latest photo"""
    if state['last_photo']:
        return jsonify({
            'photo_url': state['last_photo'],
            'timestamp': state['last_updated'],
            'success': True
        })
    return jsonify({
        'photo_url': None,
        'timestamp': None,
        'success': False,
        'message': 'No photos yet'
    })

@app.route('/subscribe', methods=['GET'])
def api_subscribe():
    """
    Polling endpoint - client polls this to get new photos
    Returns new photo if available, or empty if nothing new
    """
    last_timestamp = request.args.get('last_timestamp', None)
    
    response = {
        'viewers': state['viewer_count'],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    # If we have a new photo since client's last request
    if state['last_photo'] and state['last_updated']:
        if last_timestamp is None or last_timestamp < state['last_updated']:
            response['photo'] = {
                'photo_url': state['last_photo'],
                'timestamp': state['last_updated']
            }
    
    return jsonify(response)

@app.route('/viewer/connect', methods=['POST'])
def api_viewer_connect():
    """Client connects to view stream"""
    client_id = request.args.get('client_id', request.remote_addr)
    
    state['active_clients'].add(client_id)
    state['viewer_count'] = len(state['active_clients'])
    
    print(f"✓ Viewer connected: {client_id} (Total: {state['viewer_count']})")
    
    return jsonify({
        'client_id': client_id,
        'viewers': state['viewer_count'],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/viewer/disconnect', methods=['POST'])
def api_viewer_disconnect():
    """Client disconnects from stream"""
    client_id = request.args.get('client_id', request.remote_addr)
    
    state['active_clients'].discard(client_id)
    state['viewer_count'] = len(state['active_clients'])
    
    print(f"✗ Viewer disconnected: {client_id} (Total: {state['viewer_count']})")
    
    return jsonify({
        'viewers': state['viewer_count'],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/upload-photo', methods=['POST'])
def api_upload_photo():
    """Upload a new photo"""
    data = request.get_json()
    
    if not data or 'photo_url' not in data:
        return jsonify({'error': 'Missing photo_url', 'success': False}), 400
    
    # Store the photo
    state['last_photo'] = data['photo_url']
    state['last_updated'] = data.get('timestamp', datetime.utcnow().isoformat() + 'Z')
    
    viewer_count = state['viewer_count']
    
    print(f"📸 Photo uploaded ({len(data['photo_url'])} bytes) - Viewers: {viewer_count}")
    
    return jsonify({
        'success': True,
        'status': 'uploaded',
        'viewers': viewer_count,
        'timestamp': state['last_updated']
    })

@app.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'viewers': state['viewer_count']
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Local development only
    app.run(debug=True, host='0.0.0.0', port=5000)
