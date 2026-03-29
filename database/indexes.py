import logging
from pymongo import ASCENDING, DESCENDING


logger = logging.getLogger(__name__)


def ensure_indexes(db, cfg):
    """
    Create or verify all required MongoDB indexes.
    Covers both the legacy single-collection layout and the four
    region-specific collections introduced in the updated configuration.
    """
    # --- Region-specific Google-scraped profile collections -----------
    _profiles_indexes(db[cfg.USA_COLLECTION])
    _profiles_indexes(db[cfg.LAHORE_COLLECTION])

    # --- Region-specific LinkedIn connection/message collections ------
    _connections_indexes(db[cfg.USA_MESSAGE_COLLECTION])
    _connections_indexes(db[cfg.LAHORE_MESSAGE_COLLECTION])

    # --- Shared activity log ------------------------------------------
    _activity_indexes(db[cfg.ACTIVITY_LOG_COLLECTION])

    logger.info("All database indexes verified / created")


def _profiles_indexes(col):
    """Indexes for Google-scraped profile collections."""
    col.create_index([("href", ASCENDING)], unique=True, name="href_unique")
    col.create_index([("processed", ASCENDING)], name="idx_processed")
    col.create_index([("connected", ASCENDING)], name="idx_connected")
    col.create_index([("messaged", ASCENDING)], name="idx_messaged")
    col.create_index([("location", ASCENDING)], name="idx_location")
    col.create_index([("date_added", DESCENDING)], name="idx_date_added")
    col.create_index([("source", ASCENDING)], name="idx_source")


def _connections_indexes(col):
    """Indexes for LinkedIn connection/message target collections."""
    col.create_index([("href", ASCENDING)], unique=True, name="href_unique")
    col.create_index([("connected", ASCENDING)], name="idx_connected")
    col.create_index([("connection_date", DESCENDING)], name="idx_connection_date")
    col.create_index([("messaged", ASCENDING)], name="idx_messaged")
    col.create_index([("message_date", DESCENDING)], name="idx_message_date")


def _activity_indexes(col):
    """Indexes for the shared activity log collection."""
    col.create_index([("timestamp", DESCENDING)], name="idx_timestamp")
    col.create_index([("action_type", ASCENDING)], name="idx_action_type")
    col.create_index([("profile_href", ASCENDING)], name="idx_profile_href")
    col.create_index(
        [("timestamp", DESCENDING), ("action_type", ASCENDING)],
        name="idx_daily_stats",
    )
