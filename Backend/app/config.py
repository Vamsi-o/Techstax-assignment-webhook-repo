"""Configuration - loads environment variables"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI')
    DB_NAME = 'webhook_data'
    COLLECTION_NAME = 'webhook_data'
    
    # Flask
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = True
    
    @staticmethod
    def validate():
        """Validate required configuration exists"""
        if not Config.MONGODB_URI:
            raise ValueError("❌ MONGODB_URI is not set in .env file")
        
        # if '<db_password>' in Config.MONGODB_URI or '<password>' in Config.MONGODB_URI:
        #     raise ValueError("❌ Replace <db_password> with your actual MongoDB password")
        
        print("✅ Configuration validated")

# Test this file
if __name__ == '__main__':
    print("Testing Config...")
    
    try:
        Config.validate()
        print(f"MongoDB URI: {Config.MONGODB_URI[:30]}...")
        print(f"DB Name: {Config.DB_NAME}")
        print(f"Port: {Config.PORT}")
        print("✅ Config test passed")
    except ValueError as e:
        print(f"❌ Config test failed: {e}")
