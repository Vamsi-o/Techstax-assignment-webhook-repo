
"""
Flask application factory

Creates and configures the Flask application with:
- CORS enabled
- Database connection
- Blueprint registration
"""

from flask import Flask
from flask_cors import CORS

def create_app():
    """
    Application factory pattern
    
    Why factory pattern?
    - Can create multiple app instances (testing, production)
    - Configuration happens in one place
    - Easy to test and maintain
    
    Returns:
        Flask app instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Enable CORS (Cross-Origin Resource Sharing)
    # Why? Frontend (Next.js) will run on different port/domain
    # Without CORS, browser blocks the requests
    CORS(app, resources={
        r"/*": {
            "origins": "*",              # Allow all origins (for development)
            "methods": ["GET", "POST"],  # Allowed HTTP methods
            "allow_headers": ["Content-Type"]  # Allowed headers
        }
    })
    
    # Connect to MongoDB
    from app.config import Config
    from app.database import db
    
    # Validate config first
    Config.validate()
    
    # Connect to database
    db.connect(Config.MONGODB_URI, Config.DB_NAME, Config.COLLECTION_NAME)
    
    # Register blueprints
    # Blueprint = group of routes
    # We register the webhook blueprint which has /health, /webhook, /events
    from app.webhook.routes import webhook_bp
    app.register_blueprint(webhook_bp)
    
    print("✅ Flask app created successfully")
    
    return app
