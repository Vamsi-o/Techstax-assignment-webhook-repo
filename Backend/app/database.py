"""
MongoDB database connection manager with error handling

This file handles:
1. Connecting to MongoDB
2. Testing the connection
3. Providing a global db instance for the app to use
"""

# Fix imports when running directly
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# MongoDB client and error types
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


class Database:
    """
    MongoDB connection manager
    
    Why a class?
    - Keeps all database logic in one place
    - Can reconnect if connection drops
    - Easy to test
    """
    
    def __init__(self):
        """
        Initialize empty database connection
        
        We don't connect in __init__ because:
        - Connection might fail (error handling)
        - We want to control WHEN we connect
        - Makes testing easier
        """
        self.client = None          # MongoDB client (main connection)
        self.db = None              # Database object (webhook_data)
        self.collection = None      # Collection object (webhook_data.webhook_data)
        self._connected = False     # Connection status flag
    
    def connect(self, uri, db_name, collection_name):
        """
        Connect to MongoDB with timeout and error handling
        
        Args:
            uri: MongoDB connection string from .env
            db_name: Database name ("webhook_data")
            collection_name: Collection name ("webhook_data")
        
        Returns:
            True if connection successful
            False if connection failed
        
        Why return bool instead of raising error?
        - Lets calling code decide what to do on failure
        - Can retry connection without crashing app
        """
        try:
            print(f"🔌 Connecting to MongoDB...")
            
            # Create MongoDB client
            # serverSelectionTimeoutMS = how long to wait for server (5 seconds)
            # connectTimeoutMS = how long to wait for connection (10 seconds)
            # Why timeouts? If MongoDB is down, don't wait forever
            self.client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            
            # Test connection with ping command
            # Why? MongoClient() doesn't actually connect immediately
            # It's "lazy" - only connects when you use it
            # ping forces an actual connection attempt
            self.client.admin.command('ping')
            
            # Get database object
            # In MongoDB: server > databases > collections > documents
            # This gets the "webhook_data" database
            self.db = self.client[db_name]
            
            # Get collection object
            # This gets the "webhook_data" collection inside the database
            # This is where we'll store webhook events
            self.collection = self.db[collection_name]
            
            # Mark as connected
            self._connected = True
            print(f"✅ Connected to MongoDB: {db_name}.{collection_name}")
            return True
            
        except ConnectionFailure as e:
            """
            ConnectionFailure = couldn't reach MongoDB server
            Reasons: wrong URI, server down, network issue
            """
            print(f"❌ MongoDB connection failed: {e}")
            self._connected = False
            return False
            
        except ServerSelectionTimeoutError:
            """
            Timeout = took too long to connect
            Common causes:
            - IP not whitelisted in MongoDB Atlas
            - Firewall blocking connection
            - Wrong URI
            """
            print(f"❌ MongoDB timeout - check your connection and IP whitelist")
            self._connected = False
            return False
            
        except Exception as e:
            """
            Catch any other unexpected errors
            Why? Better to handle gracefully than crash
            """
            print(f"❌ Unexpected database error: {e}")
            self._connected = False
            return False
    
    def is_connected(self):
        """
        Check if database is connected
        
        Why this method?
        - Routes can check before trying to save data
        - Avoids crash if connection drops
        - Can trigger reconnect if needed
        """
        return self._connected and self.collection is not None
    
    def test_operations(self):
        """
        Test basic database operations
        
        Tests:
        1. Count documents (read operation)
        2. Insert document (write operation)
        3. Delete document (cleanup)
        
        Why test?
        - Verify permissions work
        - Catch issues before production
        """
        if not self.is_connected():
            print("❌ Not connected to database")
            return False
        
        try:
            # Count how many documents exist
            # count_documents({}) = count all (empty filter = match everything)
            count = self.collection.count_documents({})
            print(f"📊 Current documents: {count}")
            
            # Insert a test document
            # insert_one() returns result with inserted_id
            test_doc = {
                'test': True,
                'message': 'Database connection test'
            }
            result = self.collection.insert_one(test_doc)
            print(f"✅ Test insert successful: {result.inserted_id}")
            
            # Delete the test document (cleanup)
            # delete_one({'_id': ...}) = delete by ID
            self.collection.delete_one({'_id': result.inserted_id})
            print(f"✅ Test delete successful")
            
            return True
            
        except Exception as e:
            """
            Any error during operations = something wrong with permissions or connection
            """
            print(f"❌ Database operation failed: {e}")
            return False


# Create a global database instance
# Why global?
# - Flask routes need to access the same connection
# - Creating multiple connections = waste of resources
# - This is called the "singleton pattern"
db = Database()


# Test code - only runs when you execute this file directly
# Doesn't run when you import this file in other code
if __name__ == '__main__':
    """
    Test the database connection
    
    Flow:
    1. Import config
    2. Validate config
    3. Connect to database
    4. Test operations
    """
    from app.config import Config
    
    print("Testing Database connection...\n")
    
    # Validate config first
    # If config is wrong, no point trying to connect
    try:
        Config.validate()
    except ValueError as e:
        print(e)
        exit(1)  # Exit with error code
    
    # Try to connect
    if db.connect(Config.MONGODB_URI, Config.DB_NAME, Config.COLLECTION_NAME):
        # Connection successful
        print(f"\n✅ Connection test passed")
        print(f"Database: {db.db.name}")
        print(f"Collection: {db.collection.name}")
        
        # Test database operations
        print("\nTesting database operations...")
        if db.test_operations():
            print("\n✅ All database tests passed")
        else:
            print("\n❌ Database operations test failed")
    else:
        # Connection failed
        print("\n❌ Connection test failed")
