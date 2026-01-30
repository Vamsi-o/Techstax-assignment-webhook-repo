
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


class Database:
    
    def __init__(self):
        self.client = None         
        self.db = None             
        self.collection = None     
        self._connected = False     
    
    def connect(self, uri, db_name, collection_name):
   
        try:
            print(f"🔌 Connecting to MongoDB...")
         
            self.client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            
        
            self.client.admin.command('ping')
            
           
            self.db = self.client[db_name]
            

            self.collection = self.db[collection_name]
            
            self._connected = True
            print(f"✅ Connected to MongoDB: {db_name}.{collection_name}")
            return True
            
        except ConnectionFailure as e:
          
            print(f"❌ MongoDB connection failed: {e}")
            self._connected = False
            return False
            
        except ServerSelectionTimeoutError:
            
            print(f"❌ MongoDB timeout - check your connection and IP whitelist")
            self._connected = False
            return False
            
        except Exception as e:
          
            print(f"❌ Unexpected database error: {e}")
            self._connected = False
            return False
    
    def is_connected(self):
     
        return self._connected and self.collection is not None
    
    def test_operations(self):
      
        if not self.is_connected():
            print("❌ Not connected to database")
            return False
        
        try:
       
            count = self.collection.count_documents({})
            print(f"📊 Current documents: {count}")
        
            test_doc = {
                'test': True,
                'message': 'Database connection test'
            }
            result = self.collection.insert_one(test_doc)
            print(f"✅ Test insert successful: {result.inserted_id}")
            
      
            self.collection.delete_one({'_id': result.inserted_id})
            print(f"✅ Test delete successful")
            
            return True
            
        except Exception as e:
            """
            Any error during operations = something wrong with permissions or connection
            """
            print(f"❌ Database operation failed: {e}")
            return False



db = Database()



if __name__ == '__main__':
 
    from app.config import Config
    
    print("Testing Database connection...\n")
    

    try:
        Config.validate()
    except ValueError as e:
        print(e)
        exit(1)  
    
    if db.connect(Config.MONGODB_URI, Config.DB_NAME, Config.COLLECTION_NAME):
        print(f"\n✅ Connection test passed")
        print(f"Database: {db.db.name}")
        print(f"Collection: {db.collection.name}")
        
        print("\nTesting database operations...")
        if db.test_operations():
            print("\n✅ All database tests passed")
        else:
            print("\n❌ Database operations test failed")
    else:
        print("\n❌ Connection test failed")
