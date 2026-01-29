"""Configuration - loads environment variables"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('webhook.log')  # File output
    ]
)

logger = logging.getLogger(__name__)

class Config:
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI')
    DB_NAME = 'webhook_data'
    COLLECTION_NAME = 'webhook_data'
    
    # Flask
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = True
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.MONGODB_URI:
            logger.error("MONGODB_URI not found in environment variables")
            raise ValueError("MONGODB_URI is required")
        logger.info("Configuration validated successfully")

# Test this file
if __name__ == '__main__':
    logger.info("Testing Config...")
    
    try:
        Config.validate()
        logger.info(f"MongoDB URI: {Config.MONGODB_URI[:30]}...")
        logger.info(f"DB Name: {Config.DB_NAME}")
        logger.info(f"Port: {Config.PORT}")
        logger.info("✅ Config test passed")
    except ValueError as e:
        logger.error(f"❌ Config test failed: {e}")
