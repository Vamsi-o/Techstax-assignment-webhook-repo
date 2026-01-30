# """
# Application entry point

# Run the Flask development server:
#     python3 run.py

# Production deployment uses gunicorn instead:
    # gunicorn run:app
# """

# from app import create_app
# from app.config import Config

# # Create Flask app using factory
# app = create_app()

# if __name__ == '__main__':
#     """
#     Only runs when executing this file directly
#     (not when imported by gunicorn)
#     """
#     print("=" * 60)
#     print(f"🚀 Flask server starting on http://localhost:{Config.PORT}")
#     print(f"📝 Debug mode: {Config.DEBUG}")
#     print("=" * 60)
#     print("\nAvailable endpoints:")
#     print(f"  GET  http://localhost:{Config.PORT}/health")
#     print(f"  POST http://localhost:{Config.PORT}/webhook")
#     print(f"  GET  http://localhost:{Config.PORT}/events")
#     print("\nPress CTRL+C to stop")
#     print("=" * 60)
    
#     # Run Flask development server
#     # host='0.0.0.0' = listen on all network interfaces
#     # port = from Config (default 5000)
#     # debug = enables hot reload and better error messages
#     app.run(
#         host='0.0.0.0',
#         port=Config.PORT,
#         debug=Config.DEBUG
#     )

import logging
import os
from app.config import Config
from app import create_app

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Validate configuration and create app at module level for gunicorn
Config.validate()
app = create_app()

if __name__ == '__main__':
    try:
        # Get port from environment (Railway sets this)
        port = int(os.getenv('PORT', Config.PORT))
        
        logger.info("=" * 60)
        logger.info(f"🚀 Flask server starting on port {port}")
        logger.info(f"📝 Debug mode: {Config.DEBUG}")
        logger.info("=" * 60)
        logger.info("\nAvailable endpoints:")
        logger.info(f"  GET  /health")
        logger.info(f"  POST /webhook")
        logger.info(f"  GET  /events")
        logger.info("\n" + "=" * 60)
        
        # Run the app
        app.run(
            host='0.0.0.0',  # Important for Railway!
            port=port,
            debug=Config.DEBUG
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

