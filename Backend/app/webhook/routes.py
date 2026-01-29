"""
Flask API routes for webhook handling

Endpoints:
- GET  /health   - Health check
- POST /webhook  - Receive GitHub webhooks
- GET  /events   - Get stored events
"""
import logging
# Fix imports when running directly
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from app.database import db
from app.webhook.parsers import parse_webhook

# Create a Blueprint
# Why Blueprint? Keeps webhook routes organized and separate
# Can register this blueprint in the main app
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
def receive_webhook():
    """
    Receive and process GitHub webhook
    
    Flow:
    1. Receive JSON payload from GitHub
    2. Validate payload structure
    3. Parse the webhook (PUSH/PR/MERGE)
    4. Save to MongoDB
    5. Return success/error response
    
    Returns:
        - 200: Webhook processed successfully
        - 400: Invalid payload or unsupported event
        - 500: Server error (database failure, etc.)
        - 503: Database unavailable
    
    Why different status codes?
    - GitHub uses these to know if webhook delivered successfully
    - 200 = success, don't retry
    - 400 = bad request, don't retry
    - 500/503 = server error, GitHub will retry later
    """
    try:
        # Get JSON payload from request
        # request.json automatically parses JSON from request body
        data = request.json
        
        # Validate payload exists
        # Why? Sometimes requests come with empty body
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Parse the webhook using our parser
        # Returns None if unsupported or invalid event
        event_data = parse_webhook(data)
        
        if not event_data:
            # Parsing failed or unsupported event type
            return jsonify({'error': 'Failed to parse webhook'}), 400
        
        # Check database connection before trying to save
        # Why? Better to check first than catch error after
        if not db.is_connected():
            logger.warning("Database not connected, attempting reconnect...")
            
            # Try to reconnect
            from app.config import Config
            db.connect(Config.MONGODB_URI, Config.DB_NAME, Config.COLLECTION_NAME)
            
            # Still not connected? Return 503 (service unavailable)
            if not db.is_connected():
                return jsonify({'error': 'Database unavailable'}), 503
        
        # Save event to MongoDB
        # insert_one() returns result with inserted_id
        result = db.collection.insert_one(event_data)
        logger.info(f"Saved to MongoDB: {result.inserted_id}")
        
        # Return success response with details
        # GitHub sees 200 = webhook delivered successfully
        return jsonify({
            'status': 'success',
            'action': event_data['action'],
            'author': event_data['author'],
            'id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        # Catch any unexpected errors
        # Log the error and return 500
        # Why 500? Tells GitHub "our server had a problem, retry later"
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@webhook_bp.route('/events', methods=['GET'])
def get_events():
    """
    Get recent events from MongoDB
    
    Returns last N events sorted by timestamp (newest first)
    
    Response format:
    [
        {
            "_id": "65b9e...",
            "request_id": "abc123",
            "author": "Vamshi",
            "action": "PUSH",
            "from_branch": "main",
            "to_branch": "main",
            "timestamp": "2026-01-29T06:30:00Z"
        },
        ...
    ]
    
    Returns:
        - 200: Events retrieved successfully
        - 503: Database unavailable
        - 500: Server error
    """
    try:
        # Check database connection
        if not db.is_connected():
            return jsonify({'error': 'Database unavailable'}), 503
        
        # Fetch events from MongoDB
        # find() = get all documents (empty filter = match all)
        # sort('timestamp', -1) = sort by timestamp descending (newest first)
        # limit(50) = only return 50 most recent
        events = list(
            db.collection
            .find()
            .sort('timestamp', -1)
            .limit(50)
        )
        
        # Convert ObjectId to string for JSON serialization
        # Why? MongoDB _id is ObjectId type, JSON can't serialize it
        # Must convert to string first
        for event in events:
            event['_id'] = str(event['_id'])
        
        logger.info(f"Returning {len(events)} events")
        
        # Return events as JSON array
        return jsonify(events), 200
        
    except Exception as e:
        # Catch any errors during database query
        logger.error(f"Error fetching events: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============ TEST CODE ============
# Only runs when you execute this file directly

if __name__ == '__main__':
    from app.config import Config
    from flask import Flask
    
    # Configure logging for tests
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    logger.info("=" * 60)
    logger.info("TESTING FLASK ROUTES")
    logger.info("=" * 60)
    
    # Validate config
    Config.validate()
    
    # Connect to database
    logger.info("Connecting to database...")
    if not db.connect(Config.MONGODB_URI, Config.DB_NAME, Config.COLLECTION_NAME):
        logger.error("Database connection failed - tests aborted")
        exit(1)
    
    # Create test Flask app
    app = Flask(__name__)
    app.register_blueprint(webhook_bp)
    
    # Test with Flask test client
    # Why test client? Can simulate HTTP requests without running server
    client = app.test_client()
    
    logger.info("=" * 60)
    logger.info("[TEST 1] GET /health")
    logger.info("=" * 60)
    response = client.get('/health')
    logger.info(f"Status: {response.status_code}")
    logger.info(f"Response: {response.json}")
    assert response.status_code == 200, "Health check should return 200"
    assert response.json['status'] == 'healthy', "Status should be healthy"
    logger.info("Health check passed")
    
    logger.info("=" * 60)
    logger.info("[TEST 2] POST /webhook - PUSH event")
    logger.info("=" * 60)
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
    
    logger.info("=" * 60)
    logger.info("[TEST 3] GET /events")
    logger.info("=" * 60)
    response = client.get('/events')
    logger.info(f"Status: {response.status_code}")
    logger.info(f"Events count: {len(response.json)}")
    assert response.status_code == 200, "Events endpoint should return 200"
    assert len(response.json) > 0, "Should have at least 1 event"
    logger.info(f"Events retrieval passed - {len(response.json)} events found")
    
    # Cleanup test data
    logger.info("Cleaning up test data...")
    db.collection.delete_many({'request_id': 'test123'})
    logger.info("Cleanup complete")
    
    logger.info("=" * 60)
    logger.info("ALL ROUTE TESTS PASSED")
    logger.info("=" * 60)
