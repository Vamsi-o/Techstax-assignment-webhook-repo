"""
Application entry point

Run the Flask development server:
    python3 run.py

Production deployment uses gunicorn instead:
    gunicorn run:app
"""

from app import create_app
from app.config import Config

# Create Flask app using factory
app = create_app()

if __name__ == '__main__':
    """
    Only runs when executing this file directly
    (not when imported by gunicorn)
    """
    print("=" * 60)
    print(f"🚀 Flask server starting on http://localhost:{Config.PORT}")
    print(f"📝 Debug mode: {Config.DEBUG}")
    print("=" * 60)
    print("\nAvailable endpoints:")
    print(f"  GET  http://localhost:{Config.PORT}/health")
    print(f"  POST http://localhost:{Config.PORT}/webhook")
    print(f"  GET  http://localhost:{Config.PORT}/events")
    print("\nPress CTRL+C to stop")
    print("=" * 60)
    
    # Run Flask development server
    # host='0.0.0.0' = listen on all network interfaces
    # port = from Config (default 5000)
    # debug = enables hot reload and better error messages
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )
