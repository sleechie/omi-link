import os
from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv
import db
import transcript_processor

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize database on startup
try:
    db.init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")

# Start transcript processor thread
transcript_processor.start_processor()

@app.route('/', methods=['GET', 'POST'])
def health_check():
    """Health check endpoint for Railway - also handles webhook if posted to root"""
    # If it's a POST request, treat it as a webhook
    if request.method == 'POST':
        return webhook()
    
    # Otherwise, return health check
    return jsonify({
        'status': 'healthy',
        'message': 'Omi Webhook Receiver is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/conversation', methods=['GET'])
def get_conversation():
    """Get conversation history"""
    try:
        messages = db.get_all_messages()
        return jsonify({
            'status': 'success',
            'count': len(messages),
            'messages': messages
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive and process Omi device webhooks"""
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        if not data:
            print("Warning: Received empty webhook data")
            return jsonify({'status': 'error', 'message': 'No data received'}), 400
        
        # Print the full webhook data for debugging
        print("\n" + "="*60)
        print(f"NEW WEBHOOK RECEIVED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Check for segments (can be 'transcript_segments' or 'segments')
        segments = data.get('transcript_segments') or data.get('segments', [])
        
        if segments:
            print(f"\nTranscript Segments: {len(segments)} segment(s)")
            print("-"*60)
            
            # Save each segment to database
            session_id = data.get('session_id', 'unknown')
            
            for i, segment in enumerate(segments, 1):
                speaker_id = segment.get('speaker_id', 'Unknown')
                text = segment.get('text', '')
                start_time = segment.get('start', 0)
                end_time = segment.get('end', 0)
                
                print(f"\nSegment {i}:")
                print(f"  Speaker: {speaker_id}")
                print(f"  Time: {start_time:.2f}s - {end_time:.2f}s")
                print(f"  Text: {text}")
                
                # Add session_id to segment data
                segment['session_id'] = session_id
                
                # Save to database
                db.save_transcript_segment(segment)
        
        # Check for session information
        if 'session_id' in data:
            print(f"\nSession ID: {data['session_id']}")
        
        # Check for structured data (memory/conversation)
        if 'structured' in data:
            structured = data['structured']
            print("\nStructured Data:")
            if 'title' in structured:
                print(f"  Title: {structured['title']}")
            if 'overview' in structured:
                print(f"  Overview: {structured['overview']}")
            if 'category' in structured:
                print(f"  Category: {structured['category']}")
            if 'action_items' in structured:
                action_items = structured['action_items']
                if action_items:
                    print(f"  Action Items: {len(action_items)}")
                    for item in action_items:
                        print(f"    - {item.get('description', 'No description')}")
        
        # Print any other interesting fields
        for key in ['language', 'source', 'created_at', 'started_at', 'finished_at']:
            if key in data:
                print(f"\n{key.replace('_', ' ').title()}: {data[key]}")
        
        print("\n" + "="*60)
        print("Raw JSON Data:")
        print("-"*60)
        import json
        print(json.dumps(data, indent=2))
        print("="*60 + "\n")
        
        # Return success response
        return jsonify({
            'status': 'success',
            'message': 'Webhook received and processed',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"\nERROR processing webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Use PORT from environment (Railway) or default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    
    # Check if running locally (no PORT env var = local)
    is_local = 'PORT' not in os.environ
    
    print("\n" + "="*60)
    print("OMI WEBHOOK RECEIVER STARTING")
    print("="*60)
    print(f"Server running on port {port}")
    print(f"Webhook endpoint: http://localhost:{port}/webhook")
    print(f"Health check: http://localhost:{port}/")
    if is_local:
        print(f"Auto-reload: ENABLED (debug mode)")
    print("="*60 + "\n")
    
    # Enable debug mode for local development (auto-reloads on file changes)
    # Disabled on Railway to avoid issues in production
    app.run(host='0.0.0.0', port=port, debug=is_local, use_reloader=is_local)

