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

# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: Database Manager Class
# --------------------------------

""" 
DatabaseManager is a singleton class responsible for managing the MongoDB connection and providing methods to interact with the database.
"""


class DatabaseManager:
    _instance = None
    _client = None
    _db = None

    # --------------------------------
    # :: New Method
    # --------------------------------

    """
    Implements the singleton pattern to ensure only one instance of DatabaseManager exists.
    """

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    # --------------------------------
    # :: Init Method
    # --------------------------------

    """
    Initializes the DatabaseManager class with default values for the MongoDB client and database.
    """

    def __init__(self):
        if self._client is None:
            self._connect()

    # --------------------------------
    # :: Connect Method
    # --------------------------------

    """
    Establishes a connection to the MongoDB database using the connection string from the configuration.
    """

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
            logger.info("Successfully connected to MongoDB")
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

    # --------------------------------
    # :: Ensure Connected Method
    # --------------------------------

    """
    Ensures that the database connection is established before performing any operations. If the connection is lost, it will attempt to reconnect.
    """

    def _ensure_connected(self):
        if self._db is not None:
            return True
        self._connect()
        return self._db is not None

    # --------------------------------
    # :: Create Indexes Method
    # --------------------------------

    """
    Creates necessary indexes on the MongoDB collections to optimize query performance. This method is called after establishing a connection to the database.
    """

    def _create_indexes(self):
        try:
            from database.indexes import ensure_indexes

            ensure_indexes(self._db, config)
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    # --------------------------------
    # :: Database Property
    # --------------------------------

    """
    Provides access to the MongoDB database instance. Ensures that the connection is established before returning the database object. 
    If the connection is not available, it will raise a ConnectionFailure exception.
    """

    @property
    def db(self):
        self._ensure_connected()
        return self._db

    # --------------------------------
    # :: Profiles Collection Property
    # --------------------------------

    """
    Provides access to the profiles collection in the MongoDB database. Ensures that the connection is established before returning the collection object. 
    If the connection is not available, it will raise a ConnectionFailure exception.
    """

    @property
    def profiles_collection(self):
        if not self._ensure_connected():
            raise ConnectionFailure("MongoDB is not connected")
        return self._db[config.PROFILES_COLLECTION]

    # ------------------------------------
    # :: Connections Collection Property
    # ------------------------------------

    """
    Provides access to the connections collection in the MongoDB database. Ensures that the connection is established before returning the collection object. 
    If the connection is not available, it will raise a ConnectionFailure exception.
    """

    @property
    def connections_collection(self):
        if not self._ensure_connected():
            raise ConnectionFailure("MongoDB is not connected")
        return self._db[config.CONNECTIONS_COLLECTION]

    # --------------------------------
    # :: Messages Collection Property
    # --------------------------------

    """
    Provides access to the messages collection in the MongoDB database. Ensures that the connection is established before returning the collection object. 
    If the connection is not available, it will raise a ConnectionFailure exception.
    """

    @property
    def messages_collection(self):
        if not self._ensure_connected():
            raise ConnectionFailure("MongoDB is not connected")
        return self._db[config.MESSAGES_COLLECTION]

    # -------------------------------------
    # :: Activity Log Collection Property
    # -------------------------------------

    """
    Provides access to the activity log collection in the MongoDB database. Ensures that the connection is established before returning the collection object. 
    If the connection is not available, it will raise a ConnectionFailure exception.
    """

    @property
    def activity_log_collection(self):
        if not self._ensure_connected():
            raise ConnectionFailure("MongoDB is not connected")
        return self._db[config.ACTIVITY_LOG_COLLECTION]

    # --------------------------------
    # :: Bulk Insert Profiles Method
    # --------------------------------

    """
    Inserts multiple LinkedIn profiles into the database in bulk. This method takes a list of profile dictionaries, creates upsert operations for each profile, and executes them in a single bulk write operation. It returns the number of new profiles that were inserted. If any errors occur during the process, it logs the error and returns 0.
    """

    def bulk_insert_profiles(self, profiles):
        if not profiles:
            return 0
        try:
            operations = [
                upsert_profile_operation(p) for p in profiles if p.get("href")
            ]
            if not operations:
                return 0
            result = self.profiles_collection.bulk_write(operations, ordered=False)
            logger.info(f"Inserted {result.upserted_count} new profiles")
            return result.upserted_count
        except Exception as e:
            logger.error(f"Error in bulk insert profiles: {e}")
            return 0

    # ------------------------------------
    # :: Get Unprocessed Profiles Method
    # ------------------------------------

    """
    Retrieves unprocessed LinkedIn profiles from the database. This method executes a query to find profiles that have not been marked as processed, and yields each profile one at a time. The number of profiles returned can be limited by the `limit` parameter. If any errors occur during the retrieval process, it logs the error and continues yielding any successfully retrieved profiles.
    """

    def get_unprocessed_profiles(self, limit=100):
        try:
            cursor = self.profiles_collection.find(unprocessed_profiles_query()).limit(
                limit
            )
            for profile in cursor:
                yield profile
        except Exception as e:
            logger.error(f"Error getting unprocessed profiles: {e}")

    # ----------------------------------------
    # :: Get Profiles for Connection Method
    # ----------------------------------------

    """
    Retrieves LinkedIn profiles that need to be connected to from the database. This method executes a query to find profiles that meet the criteria for connection, and yields each profile one at a time. The number of profiles returned can be limited by the `limit` parameter. If any errors occur during the retrieval process, it logs the error and continues yielding any successfully retrieved profiles.
    """

    def get_profiles_for_connection(self, limit=20):
        try:
            cursor = self.profiles_collection.find(needs_connection_query()).limit(
                limit
            )
            for profile in cursor:
                yield profile
        except Exception as e:
            logger.error(f"Error getting profiles for connection: {e}")

    # ---------------------------------------
    # :: Get Profiles for Messaging Method
    # ---------------------------------------

    """
    Retrieves LinkedIn profiles that need to be messaged from the database. This method executes a query to find profiles that meet the criteria for messaging, and yields each profile one at a time. The number of profiles returned can be limited by the `limit` parameter. If any errors occur during the retrieval process, it logs the error and continues yielding any successfully retrieved profiles.
    """

    def get_profiles_for_messaging(self, limit=15):
        try:
            cursor = self.profiles_collection.find(needs_message_query()).limit(limit)
            for profile in cursor:
                yield profile
        except Exception as e:
            logger.error(f"Error getting profiles for messaging: {e}")

    # ----------------------------------
    # :: Mark Profile Processed Method
    # ----------------------------------

    """
    Marks a LinkedIn profile as processed in the database. This method updates the profile document with the current timestamp and the specified action (e.g., "processed", "connected", "messaged"). If the action is "connected" or "messaged", it also updates additional fields to indicate that the profile has been connected to or messaged, along with the respective timestamps. The method returns True if the profile was successfully updated, and False if any errors occur during the update process.
    """

    def mark_profile_processed(self, profile_href, action="processed"):
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
            result = self.profiles_collection.update_one(
                {"href": profile_href}, {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error marking profile processed: {e}")
            return False

    # --------------------------------
    # :: Log Activity Method
    # --------------------------------

    """
    Logs an activity in the activity log collection. This method takes the action type (e.g., "connection", "message", "visit"), the profile href associated with the activity, and any additional details as a dictionary. It creates an activity document with the provided information and the current timestamp, and inserts it into the activity log collection. The method returns True if the activity was successfully logged, and False if any errors occur during the logging process.
    """

    def log_activity(self, action_type, profile_href, details=None):
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

    # --------------------------------
    # :: IGet Daily Stats Method
    # --------------------------------

    """
    Retrieves daily activity statistics from the activity log collection. This method executes an aggregation pipeline to group activities by their action type and count the number of occurrences for each type. It returns a dictionary where the keys are the action types and the values are the respective counts. If any errors occur during the retrieval process, it logs the error and returns an empty dictionary.
    """

    def get_daily_stats(self):
        try:
            results = list(
                self.activity_log_collection.aggregate(daily_activity_pipeline())
            )
            return {item["_id"]: item["count"] for item in results}
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}

    # --------------------------------
    # :: Check Rate Limits Method
    # --------------------------------

    """
    Checks if the rate limits for connections, messages, and profile visits have been reached. This method retrieves daily activity statistics and compares them to the configured maximum limits for each activity type. It returns a dictionary indicating whether each limit has been reached.
    """

    def check_rate_limits(self):
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            stats = self.get_daily_stats()

            return {
                "connections_reached": stats.get("connection", 0)
                >= config.MAX_CONNECTIONS_PER_DAY,
                "messages_reached": stats.get("message", 0)
                >= config.MAX_MESSAGES_PER_DAY,
                "visits_reached": stats.get("visit", 0)
                >= config.MAX_PROFILE_VISITS_PER_DAY,
            }
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return {
                "connections_reached": False,
                "messages_reached": False,
                "visits_reached": False,
            }

    # --------------------------------
    # :: Close Method
    # --------------------------------

    """
    Closes the MongoDB connection when the DatabaseManager instance is deleted. This ensures that resources are properly released when the application is shutting down or when the DatabaseManager is no longer needed.
    """

    def close(self):
        if self._client:
            self._client.close()
            logger.info("Database connection closed")


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

db_manager = DatabaseManager()
