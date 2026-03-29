import logging
from config import config
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from database.queries import (
    unprocessed_profiles_query,
    needs_connection_query,
    needs_message_query,
    daily_activity_pipeline,
    upsert_profile_operation,
)


logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Singleton manager for MongoDB connections and CRUD operations.

    Supports four region-specific collections:
      - usa_google_connections    (USA Google-scraped profiles)
      - lahore_google_connections (Lahore Google-scraped profiles)
      - usa_linkedin_connections  (USA LinkedIn connection targets)
      - lahore_linkedin_connections (Lahore LinkedIn connection targets)

    Legacy single-collection access is preserved via the
    `profiles_collection` property for backward compatibility.
    """

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

    # ------------------------------------------------------------------
    # :: Connection Lifecycle
    # ------------------------------------------------------------------

    def _connect(self):
        try:
            self._client = MongoClient(
                config.MONGO_CONNECTION,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=30000,
            )
            self._client.admin.command("ping")
            self._db = self._client[config.DATABASE_NAME]
            self._create_indexes()
            logger.info(
                f"Successfully connected to MongoDB — database: '{config.DATABASE_NAME}'"
            )
        except ConnectionFailure as e:
            logger.error(
                f"MongoDB connection failed: {e}. "
                "Database operations will be unavailable until MongoDB is reachable."
            )
            self._client = None
            self._db = None
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            self._client = None
            self._db = None

    def _ensure_connected(self):
        if self._db is not None:
            return True
        self._connect()
        return self._db is not None

    def _create_indexes(self):
        try:
            from database.indexes import ensure_indexes
            ensure_indexes(self._db, config)
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    # ------------------------------------------------------------------
    # :: Database & Collection Properties
    # ------------------------------------------------------------------

    @property
    def db(self):
        self._ensure_connected()
        return self._db

    def _get_collection(self, name):
        if not self._ensure_connected():
            raise ConnectionFailure("MongoDB is not connected")
        return self._db[name]

    # --- Region-specific Google-scraped profile collections -----------

    @property
    def usa_profiles_collection(self):
        return self._get_collection(config.USA_COLLECTION)

    @property
    def lahore_profiles_collection(self):
        return self._get_collection(config.LAHORE_COLLECTION)

    # --- Region-specific LinkedIn connection collections --------------

    @property
    def usa_message_collection(self):
        return self._get_collection(config.USA_MESSAGE_COLLECTION)

    @property
    def lahore_message_collection(self):
        return self._get_collection(config.LAHORE_MESSAGE_COLLECTION)

    # --- Legacy single-collection access (backward compatible) --------

    @property
    def profiles_collection(self):
        """Default to the USA Google collection for backward compatibility."""
        return self._get_collection(config.PROFILES_COLLECTION)

    @property
    def connections_collection(self):
        return self._get_collection(config.CONNECTIONS_COLLECTION)

    @property
    def messages_collection(self):
        return self._get_collection(config.MESSAGES_COLLECTION)

    @property
    def activity_log_collection(self):
        return self._get_collection(config.ACTIVITY_LOG_COLLECTION)

    # ------------------------------------------------------------------
    # :: Helper: resolve collection by location
    # ------------------------------------------------------------------

    def _resolve_profiles_collection(self, location=None):
        """
        Return the correct profiles collection for the given location string.
        Falls back to the default profiles collection when location is unknown.
        """
        if location == "Lahore":
            return self.lahore_profiles_collection
        return self.usa_profiles_collection

    # ------------------------------------------------------------------
    # :: Profile Operations
    # ------------------------------------------------------------------

    def bulk_insert_profiles(self, profiles, location=None):
        """
        Insert multiple profiles in bulk using upsert-on-href.
        When `location` is specified the matching regional collection is used;
        otherwise the default (USA) collection is used.

        Returns the count of newly inserted profiles.
        """
        if not profiles:
            return 0
        try:
            collection = self._resolve_profiles_collection(location)
            operations = [
                upsert_profile_operation(p) for p in profiles if p.get("href")
            ]
            if not operations:
                return 0
            result = collection.bulk_write(operations, ordered=False)
            logger.info(
                f"Bulk insert into '{collection.name}': "
                f"{result.upserted_count} new profiles"
            )
            return result.upserted_count
        except Exception as e:
            logger.error(f"Error in bulk_insert_profiles: {e}")
            return 0

    def get_unprocessed_profiles(self, limit=100, location=None):
        """Yield unprocessed profiles from the appropriate regional collection."""
        try:
            collection = self._resolve_profiles_collection(location)
            cursor = collection.find(unprocessed_profiles_query()).limit(limit)
            for profile in cursor:
                yield profile
        except Exception as e:
            logger.error(f"Error getting unprocessed profiles: {e}")

    def get_profiles_for_connection(self, limit=20, location=None):
        """Yield profiles that are ready to receive a connection request."""
        try:
            collection = self._resolve_profiles_collection(location)
            cursor = collection.find(needs_connection_query()).limit(limit)
            for profile in cursor:
                yield profile
        except Exception as e:
            logger.error(f"Error getting profiles for connection: {e}")

    def get_profiles_for_messaging(self, limit=15, location=None):
        """Yield connected profiles that have not yet been messaged."""
        try:
            collection = self._resolve_profiles_collection(location)
            cursor = collection.find(needs_message_query()).limit(limit)
            for profile in cursor:
                yield profile
        except Exception as e:
            logger.error(f"Error getting profiles for messaging: {e}")

    def mark_profile_processed(self, profile_href, action="processed", location=None):
        """
        Mark a profile as processed with the given action label.
        Writes to the appropriate regional collection.
        """
        try:
            update_data = {
                "processed": True,
                "processed_at": datetime.utcnow(),
                "last_action": action,
            }
            if action == "connected":
                update_data["connected"] = True
                update_data["connection_date"] = datetime.utcnow()
            elif action == "messaged":
                update_data["messaged"] = True
                update_data["message_date"] = datetime.utcnow()

            collection = self._resolve_profiles_collection(location)
            result = collection.update_one(
                {"href": profile_href}, {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error marking profile processed: {e}")
            return False

    # ------------------------------------------------------------------
    # :: Activity Logging
    # ------------------------------------------------------------------

    def log_activity(self, action_type, profile_href, details=None):
        """Insert an activity record into the activity log collection."""
        try:
            activity = {
                "action_type": action_type,
                "profile_href": profile_href,
                "timestamp": datetime.utcnow(),
                "details": details or {},
            }
            result = self.activity_log_collection.insert_one(activity)
            return bool(result.inserted_id)
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False

    # ------------------------------------------------------------------
    # :: Stats & Rate Limit Checks
    # ------------------------------------------------------------------

    def get_daily_stats(self):
        """Return today's action counts keyed by action_type."""
        try:
            results = list(
                self.activity_log_collection.aggregate(daily_activity_pipeline())
            )
            return {item["_id"]: item["count"] for item in results}
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}

    def check_rate_limits(self):
        """Return a dict indicating which daily action limits have been reached."""
        try:
            stats = self.get_daily_stats()
            return {
                "connections_reached": (
                    stats.get("connection", 0) >= config.MAX_CONNECTIONS_PER_DAY
                ),
                "messages_reached": (
                    stats.get("message", 0) >= config.MAX_MESSAGES_PER_DAY
                ),
                "visits_reached": (
                    stats.get("visit", 0) >= config.MAX_PROFILE_VISITS_PER_DAY
                ),
            }
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return {
                "connections_reached": False,
                "messages_reached": False,
                "visits_reached": False,
            }

    # ------------------------------------------------------------------
    # :: Cleanup
    # ------------------------------------------------------------------

    def close(self):
        if self._client:
            self._client.close()
            logger.info("Database connection closed")


db_manager = DatabaseManager()
