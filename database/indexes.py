import logging
from pymongo import ASCENDING, DESCENDING

# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: Ensure Indexes Function
# --------------------------------

""" 
Function to ensure that all necessary indexes are created on the MongoDB collections.
"""


def ensure_indexes(db, cfg):
    _profiles_indexes(db[cfg.PROFILES_COLLECTION])
    _connections_indexes(db[cfg.CONNECTIONS_COLLECTION])
    _messages_indexes(db[cfg.MESSAGES_COLLECTION])
    _activity_indexes(db[cfg.ACTIVITY_LOG_COLLECTION])
    logger.info("All database indexes verified / created")


# --------------------------------
# :: Profile Indexes Function
# --------------------------------

""" 
Function to create indexes for the profiles collection. This function will be called by the ensure_indexes 
function to set up the necessary indexes for efficient querying of profile data.
"""


def _profiles_indexes(col):
    col.create_index([("href", ASCENDING)], unique=True, name="href_unique")
    col.create_index([("processed", ASCENDING)], name="idx_processed")
    col.create_index([("connected", ASCENDING)], name="idx_connected")
    col.create_index([("messaged", ASCENDING)], name="idx_messaged")
    col.create_index([("location", ASCENDING)], name="idx_location")
    col.create_index([("date_added", DESCENDING)], name="idx_date_added")
    col.create_index([("source", ASCENDING)], name="idx_source")


# --------------------------------
# :: Connections Indexes Function
# --------------------------------

""" 
Function to create indexes for the connections collection. This function will be called by the ensure_indexes 
function to set up the necessary indexes for efficient querying of connection data.
"""


def _connections_indexes(col):
    col.create_index([("href", ASCENDING)], unique=True, name="href_unique")
    col.create_index([("connected", ASCENDING)], name="idx_connected")
    col.create_index([("connection_date", DESCENDING)], name="idx_connection_date")


# --------------------------------
# :: Messages Indexes Function
# --------------------------------

""" 
Function to create indexes for the messages collection. This function will be called by the ensure_indexes 
function to set up the necessary indexes for efficient querying of message data.
"""


def _messages_indexes(col):
    col.create_index([("href", ASCENDING)], unique=True, name="href_unique")
    col.create_index([("messaged", ASCENDING)], name="idx_messaged")
    col.create_index([("message_date", DESCENDING)], name="idx_message_date")


# --------------------------------
# :: Activity Log Indexes Function
# --------------------------------

""" 
Function to create indexes for the activity log collection. This function will be called by the ensure_indexes 
function to set up the necessary indexes for efficient querying of activity log data.
"""


def _activity_indexes(col):
    col.create_index([("timestamp", DESCENDING)], name="idx_timestamp")
    col.create_index([("action_type", ASCENDING)], name="idx_action_type")
    col.create_index([("profile_href", ASCENDING)], name="idx_profile_href")
    col.create_index(
        [("timestamp", DESCENDING), ("action_type", ASCENDING)],
        name="idx_daily_stats",
    )
