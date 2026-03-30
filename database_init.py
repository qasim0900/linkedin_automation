import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    def __init__(self):
        self.client = None
        self.db = None
        
    def connect_to_mongodb(self):
        try:
            self.client = MongoClient(
                config.MONGO_CONNECTION,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=30000,
            )
            # Test connection
            self.client.admin.command("ping")
            logger.info("✅ MongoDB से successfully connected!")
            return True
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
        except ServerSelectionTimeoutError as e:
            logger.error(f"❌ MongoDB server timeout: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
            return False
    
    def check_database_exists(self):
        """Check करें कि database exist करता है या नहीं"""
        try:
            database_list = self.client.list_database_names()
            if config.DATABASE_NAME in database_list:
                logger.info(f"✅ Database '{config.DATABASE_NAME}' पहले से exist करता है")
                return True
            else:
                logger.info(f"ℹ️  Database '{config.DATABASE_NAME}' exist नहीं करता")
                return False
        except Exception as e:
            logger.error(f"❌ Database check में error: {e}")
            return False
    
    def create_database_and_collections(self):
        """Database और collections create करें"""
        try:
            self.db = self.client[config.DATABASE_NAME]
            
            # Collections create करें (पहले document insert करने पर automatically create हो जाते हैं)
            collections = [
                config.USA_COLLECTION,
                config.LAHORE_COLLECTION,
                config.USA_MESSAGE_COLLECTION,
                config.LAHORE_MESSAGE_COLLECTION,
                config.ACTIVITY_LOG_COLLECTION
            ]
            
            for collection_name in collections:
                # Empty document insert करके collection create करें, फिर delete कर दें
                collection = self.db[collection_name]
                temp_doc = {"temp": True}
                result = collection.insert_one(temp_doc)
                collection.delete_one({"_id": result.inserted_id})
                logger.info(f"✅ Collection '{collection_name}' created successfully")
            
            logger.info(f"✅ Database '{config.DATABASE_NAME}' और सभी collections successfully created!")
            return True
        except Exception as e:
            logger.error(f"❌ Database या collections create करने में error: {e}")
            return False
    
    def insert_sample_data(self):
        """Sample data insert करें"""
        try:
            if not self.db:
                self.db = self.client[config.DATABASE_NAME]
            
            # Sample profiles data
            sample_profiles = [
                {
                    "name": "John Doe",
                    "href": "https://www.linkedin.com/in/johndoe",
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "location": "USA",
                    "processed": False,
                    "connected": False,
                    "messaged": False,
                    "scraped_at": datetime.utcnow()
                },
                {
                    "name": "Jane Smith",
                    "href": "https://www.linkedin.com/in/janesmith",
                    "title": "Product Manager",
                    "company": "Startup Inc",
                    "location": "USA",
                    "processed": False,
                    "connected": False,
                    "messaged": False,
                    "scraped_at": datetime.utcnow()
                },
                {
                    "name": "Ahmed Khan",
                    "href": "https://www.linkedin.com/in/ahmedkhan",
                    "title": "Data Scientist",
                    "company": "Data Solutions",
                    "location": "Lahore",
                    "processed": False,
                    "connected": False,
                    "messaged": False,
                    "scraped_at": datetime.utcnow()
                }
            ]
            
            # USA profiles में data insert करें
            usa_collection = self.db[config.USA_COLLECTION]
            usa_result = usa_collection.insert_many(sample_profiles[:2])
            logger.info(f"✅ USA collection में {len(usa_result.inserted_ids)} profiles inserted")
            
            # Lahore profiles में data insert करें
            lahore_collection = self.db[config.LAHORE_COLLECTION]
            lahore_result = lahore_collection.insert_many([sample_profiles[2]])
            logger.info(f"✅ Lahore collection में {len(lahore_result.inserted_ids)} profiles inserted")
            
            # Sample activity log
            sample_activity = {
                "action_type": "visit",
                "profile_href": "https://www.linkedin.com/in/johndoe",
                "timestamp": datetime.utcnow(),
                "details": {"source": "google_search", "location": "USA"}
            }
            
            activity_collection = self.db[config.ACTIVITY_LOG_COLLECTION]
            activity_result = activity_collection.insert_one(sample_activity)
            logger.info(f"✅ Activity log में 1 record inserted")
            
            return True
        except Exception as e:
            logger.error(f"❌ Sample data insert करने में error: {e}")
            return False
    
    def create_indexes(self):
        """Important indexes create करें"""
        try:
            if not self.db:
                self.db = self.client[config.DATABASE_NAME]
            
            # Profile collections के लिए indexes
            profile_collections = [
                self.db[config.USA_COLLECTION],
                self.db[config.LAHORE_COLLECTION]
            ]
            
            for collection in profile_collections:
                # href के लिए unique index
                collection.create_index("href", unique=True)
                # processed status के लिए index
                collection.create_index("processed")
                # location के लिए index
                collection.create_index("location")
                logger.info(f"✅ Indexes created for {collection.name}")
            
            # Activity log के लिए indexes
            activity_collection = self.db[config.ACTIVITY_LOG_COLLECTION]
            activity_collection.create_index("timestamp")
            activity_collection.create_index("action_type")
            activity_collection.create_index([("profile_href", 1), ("timestamp", -1)])
            logger.info("✅ Indexes created for activity log collection")
            
            return True
        except Exception as e:
            logger.error(f"❌ Indexes create करने में error: {e}")
            return False
    
    def initialize_database(self):
        """Complete database initialization"""
        logger.info("🚀 MongoDB Database Initialization Started...")
        
        # Step 1: Connect to MongoDB
        if not self.connect_to_mongodb():
            logger.error("❌ Database initialization failed - Connection error")
            return False
        
        # Step 2: Check if database exists
        db_exists = self.check_database_exists()
        
        # Step 3: Create database और collections (अगर exist नहीं करता)
        if not db_exists:
            logger.info("📝 Creating new database और collections...")
            if not self.create_database_and_collections():
                logger.error("❌ Database initialization failed - Creation error")
                return False
        else:
            logger.info("📝 Using existing database...")
            self.db = self.client[config.DATABASE_NAME]
        
        # Step 4: Create indexes
        if not self.create_indexes():
            logger.error("❌ Database initialization failed - Index creation error")
            return False
        
        # Step 5: Insert sample data (सिर्फ नए database के लिए)
        if not db_exists:
            logger.info("📝 Inserting sample data...")
            if not self.insert_sample_data():
                logger.error("❌ Database initialization failed - Data insertion error")
                return False
        else:
            logger.info("📝 Database already contains data, skipping sample data insertion")
        
        logger.info("🎉 Database initialization completed successfully!")
        return True
    
    def close_connection(self):
        """MongoDB connection close करें"""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB connection closed")


def main():
    """Main function"""
    initializer = DatabaseInitializer()
    
    try:
        success = initializer.initialize_database()
        if success:
            print("\n" + "="*60)
            print("🎉 MongoDB Database Successfully Initialized!")
            print("="*60)
            print(f"Database Name: {config.DATABASE_NAME}")
            print(f"Collections Created:")
            print(f"  - {config.USA_COLLECTION}")
            print(f"  - {config.LAHORE_COLLECTION}")
            print(f"  - {config.USA_MESSAGE_COLLECTION}")
            print(f"  - {config.LAHORE_MESSAGE_COLLECTION}")
            print(f"  - {config.ACTIVITY_LOG_COLLECTION}")
            print("="*60)
        else:
            print("\n❌ Database initialization failed!")
            return 1
    except KeyboardInterrupt:
        logger.info("⚠️  Initialization interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1
    finally:
        initializer.close_connection()
    
    return 0


if __name__ == "__main__":
    exit(main())
