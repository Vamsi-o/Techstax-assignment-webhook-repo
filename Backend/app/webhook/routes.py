
import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from app.database import db
from app.webhook.parsers import parse_webhook

webhook_bp = Blueprint('webhook', __name__)

logger = logging.getLogger(__name__)
@webhook_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    
    Returns:
        - 200 OK if server is running
        - Includes database connection status
    
    Why this endpoint?
    - Monitoring: Check if server is alive
    - Deployment: Health checks before routing traffic
    - Debugging: Quick way to test if app is running
    """
    # Check if database is connected
    db_status = "connected" if db.is_connected() else "disconnected"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'database': db_status
    }), 200


@webhook_bp.route('/webhook', methods=['POST'])


@webhook_bp.route('/webhook', methods=['POST'])
def receive_webhook():
    try:
        data = request.get_json(silent=True)
        
        if not data:
            logger.warning("Received empty or invalid webhook payload")
            return jsonify({'error': 'No data received'}), 400
        
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        logger.info(f"📥 Received GitHub event: {event_type}")
        
        if 'pull_request' in data:
            pr_action = data.get('action', 'unknown')
            logger.info(f"PR action: {pr_action}")
        
        event_data = parse_webhook(data)
        
        if not event_data:
            logger.info(f"⏭️  Event skipped or not relevant: {event_type}")
            return jsonify({
                'status': 'skipped',
                'message': 'Event type not supported or not relevant',
                'event_type': event_type
            }), 200  
        
        logger.info(f"✅ Parsed event data: {event_data}")
        
        if not db.is_connected():
            logger.error("❌ Database not connected")
            return jsonify({'error': 'Database unavailable'}), 503
        
        try:
            result = db.collection.insert_one(event_data)
            logger.info(f"💾 Saved to MongoDB: {result.inserted_id}")
        except Exception as db_error:
            logger.error(f"❌ Database insert failed: {db_error}", exc_info=True)
            return jsonify({'error': 'Database insert failed'}), 500
        
        return jsonify({
            'status': 'success',
            'action': event_data['action'],
            'author': event_data['author'],
            'id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@webhook_bp.route('/events', methods=['GET'])
def get_events():
    """Get recent events from MongoDB - sorted newest first"""
    try:
        if not db.is_connected():
            logger.error("Database not connected")
            return jsonify({'error': 'Database unavailable'}), 503
        
        events = list(
            db.collection
            .find()
            .sort([('timestamp', -1), ('_id', -1)])  
            .limit(50)
        )
        for event in events:
            event['_id'] = str(event['_id'])
        
        logger.info(f"Returning {len(events)} events")
        return jsonify(events), 200
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
if __name__ == '__main__':
    from app.config import Config
    from flask import Flask
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    logger.info("=" * 60)
    logger.info("TESTING FLASK ROUTES")
    logger.info("=" * 60)
    
    Config.validate()
    
    logger.info("Connecting to database...")
    if not db.connect(Config.MONGODB_URI, Config.DB_NAME, Config.COLLECTION_NAME):
        logger.error("Database connection failed - tests aborted")
        exit(1)
    
    app = Flask(__name__)
    app.register_blueprint(webhook_bp)
    client = app.test_client()
    
 
    response = client.get('/health')
    logger.info(f"Status: {response.status_code}")
    logger.info(f"Response: {response.json}")
    assert response.status_code == 200, "Health check should return 200"
    assert response.json['status'] == 'healthy', "Status should be healthy"
    logger.info("Health check passed")
    
 
    push_payload = {
        'ref': 'refs/heads/test-branch',
        'commits': [{
            'id': 'test123',
            'author': {'name': 'Test User'},
            'timestamp': '2026-01-29T12:00:00Z'
        }]
    }
    response = client.post('/webhook', json=push_payload)
    logger.info(f"Status: {response.status_code}")
    logger.info(f"Response: {response.json}")
    assert response.status_code == 200, "PUSH webhook should return 200"
    assert response.json['status'] == 'success', "Status should be success"
    assert response.json['action'] == 'PUSH', "Action should be PUSH"
    logger.info("PUSH webhook test passed")
    
 
    response = client.get('/events')
    logger.info(f"Status: {response.status_code}")
    assert response.status_code == 200, "Events endpoint should return 200"
    assert len(response.json) > 0, "Should have at least 1 event"
    logger.info(f"Events retrieval passed - {len(response.json)} events found")
    
    db.collection.delete_many({'request_id': 'test123'})
    
    logger.info("ALL ROUTE TESTS PASSED")
