"""
Database module for LinkedIn automation system.
Provides MongoDB singleton connection and data operations.
"""

import logging
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime, timedelta
from config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Singleton MongoDB connection manager."""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._connect()
    
    def _connect(self) -> None:
        """Establish MongoDB connection."""
        try:
            self._client = MongoClient(
                config.MONGO_CONNECTION,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=30000
            )
            # Test connection
            self._client.admin.command('ping')
            self._db = self._client[config.DATABASE_NAME]
            self._create_indexes()
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    def _create_indexes(self) -> None:
        """Create necessary database indexes."""
        try:
            # Profiles collection indexes
            profiles_collection = self._db[config.PROFILES_COLLECTION]
            profiles_collection.create_index("href", unique=True)
            profiles_collection.create_index("processed")
            profiles_collection.create_index("location")
            profiles_collection.create_index("date_added")
            
            # Connections collection indexes
            connections_collection = self._db[config.CONNECTIONS_COLLECTION]
            connections_collection.create_index("href", unique=True)
            connections_collection.create_index("connected")
            connections_collection.create_index("connection_date")
            
            # Messages collection indexes
            messages_collection = self._db[config.MESSAGES_COLLECTION]
            messages_collection.create_index("href", unique=True)
            messages_collection.create_index("messaged")
            messages_collection.create_index("message_date")
            
            # Activity log collection indexes
            activity_collection = self._db[config.ACTIVITY_LOG_COLLECTION]
            activity_collection.create_index("timestamp")
            activity_collection.create_index("action_type")
            activity_collection.create_index("profile_href")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    @property
    def db(self) -> pymongo.database.Database:
        """Get database instance."""
        return self._db
    
    @property
    def profiles_collection(self) -> pymongo.collection.Collection:
        """Get profiles collection."""
        return self._db[config.PROFILES_COLLECTION]
    
    @property
    def connections_collection(self) -> pymongo.collection.Collection:
        """Get connections collection."""
        return self._db[config.CONNECTIONS_COLLECTION]
    
    @property
    def messages_collection(self) -> pymongo.collection.Collection:
        """Get messages collection."""
        return self._db[config.MESSAGES_COLLECTION]
    
    @property
    def activity_log_collection(self) -> pymongo.collection.Collection:
        """Get activity log collection."""
        return self._db[config.ACTIVITY_LOG_COLLECTION]
    
    def bulk_insert_profiles(self, profiles: List[Dict[str, Any]]) -> int:
        """Bulk insert profiles with deduplication."""
        if not profiles:
            return 0
        
        try:
            operations = []
            for profile in profiles:
                operations.append(
                    pymongo.UpdateOne(
                        {"href": profile["href"]},
                        {
                            "$setOnInsert": {
                                **profile,
                                "date_added": datetime.utcnow(),
                                "processed": False,
                                "connected": False,
                                "messaged": False
                            }
                        },
                        upsert=True
                    )
                )
            
            result = self.profiles_collection.bulk_write(operations, ordered=False)
            logger.info(f"Inserted {result.upserted_count} new profiles")
            return result.upserted_count
            
        except Exception as e:
            logger.error(f"Error in bulk insert profiles: {e}")
            return 0
    
    def get_unprocessed_profiles(self, limit: int = 100) -> Generator[Dict[str, Any], None, None]:
        """Get profiles that haven't been processed yet."""
        try:
            query = {
                "$or": [
                    {"processed": {"$exists": False}},
                    {"processed": False}
                ]
            }
            
            cursor = self.profiles_collection.find(query).limit(limit)
            for profile in cursor:
                yield profile
                
        except Exception as e:
            logger.error(f"Error getting unprocessed profiles: {e}")
    
    def mark_profile_processed(self, profile_href: str, action: str = "processed") -> bool:
        """Mark a profile as processed with timestamp."""
        try:
            update_data = {
                "processed": True,
                "processed_at": datetime.utcnow(),
                "last_action": action
            }
            
            if action == "connected":
                update_data["connected"] = True
                update_data["connection_date"] = datetime.utcnow()
            elif action == "messaged":
                update_data["messaged"] = True
                update_data["message_date"] = datetime.utcnow()
            
            result = self.profiles_collection.update_one(
                {"href": profile_href},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error marking profile processed: {e}")
            return False
    
    def log_activity(self, action_type: str, profile_href: str, details: Dict[str, Any] = None) -> bool:
        """Log an activity for tracking and analytics."""
        try:
            activity = {
                "action_type": action_type,
                "profile_href": profile_href,
                "timestamp": datetime.utcnow(),
                "details": details or {}
            }
            
            result = self.activity_log_collection.insert_one(activity)
            return bool(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False
    
    def get_daily_stats(self) -> Dict[str, int]:
        """Get daily activity statistics."""
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": today}}},
                {"$group": {
                    "_id": "$action_type",
                    "count": {"$sum": 1}
                }}
            ]
            
            results = list(self.activity_log_collection.aggregate(pipeline))
            stats = {item["_id"]: item["count"] for item in results}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}
    
    def check_rate_limits(self) -> Dict[str, bool]:
        """Check if daily rate limits have been reached."""
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            stats = self.get_daily_stats()
            
            return {
                "connections_reached": stats.get("connection", 0) >= config.MAX_CONNECTIONS_PER_DAY,
                "messages_reached": stats.get("message", 0) >= config.MAX_MESSAGES_PER_DAY,
                "visits_reached": stats.get("visit", 0) >= config.MAX_PROFILE_VISITS_PER_DAY
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return {"connections_reached": False, "messages_reached": False, "visits_reached": False}
    
    def close(self) -> None:
        """Close database connection."""
        if self._client:
            self._client.close()
            logger.info("Database connection closed")

# Global database instance
db_manager = DatabaseManager()