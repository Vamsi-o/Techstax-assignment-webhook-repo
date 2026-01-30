import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger(__name__)

class Config:
    """Application configuration"""
    
    MONGODB_URI = os.getenv('MONGODB_URI')
    DB_NAME = os.getenv('DB_NAME', 'webhook_data')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'webhook_data')
    
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.MONGODB_URI:
            logger.error("MONGODB_URI not found in environment variables")
            raise ValueError("MONGODB_URI is required")
        logger.info("✅ Configuration validated successfully")
