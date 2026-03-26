import logging
from config import config
from datetime import datetime
from database import db_manager

# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

_ALREADY_CONNECTED_STATUSES = {"connected", "pending", "declined"}
_MAX_PENDING_ALLOWED = 500


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


class ConnectionService:

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def __init__(self):
        self._blacklist: set = set()
        self._whitelist: set = set()

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def get_connection_candidates(self, limit=20, location_filter=None):
        try:
            query = {
                "processed": {"$ne": True},
                "status": {"$nin": _ALREADY_CONNECTED_STATUSES},
            }
            if location_filter:
                query["location"] = {"$regex": location_filter, "$options": "i"}
            raw = list(
                db_manager.profiles_collection.find(query)
                .sort("scraped_at", 1)
                .limit(limit * 3)
            )
            candidates = []
            for profile in raw:
                href = profile.get("href", "")
                if href in self._blacklist:
                    continue
                if not self._is_eligible(profile):
                    continue
                candidates.append(profile)
                if len(candidates) >= limit:
                    break
            logger.info(
                f"ConnectionService: {len(candidates)} candidates "
                f"(limit={limit}, location={location_filter})"
            )
            return candidates
        except Exception as exc:
            logger.error(f"ConnectionService.get_connection_candidates: {exc}")
            return []

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def get_pending_count(self):
        try:
            return db_manager.profiles_collection.count_documents({"status": "pending"})
        except Exception as exc:
            logger.error(f"ConnectionService.get_pending_count: {exc}")
            return 0

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def get_remaining_budget(self):
        try:
            daily_stats = db_manager.get_daily_stats()
            used = daily_stats.get("connections", 0)
            cap = config.MAX_CONNECTIONS_PER_DAY
            return max(0, cap - used)
        except Exception as exc:
            logger.error(f"ConnectionService.get_remaining_budget: {exc}")
            return 0

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def has_budget(self):
        return self.get_remaining_budget() > 0

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def record_connection_sent(self, profile_url, success) -> None:
        try:
            status = "pending" if success else "connection_failed"
            db_manager.mark_profile_processed(profile_url, status)
            db_manager.log_activity(
                "connections",
                profile_url,
                {"success": success, "timestamp": datetime.utcnow()},
            )
        except Exception as exc:
            logger.error(f"ConnectionService.record_connection_sent: {exc}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def add_to_blacklist(self, href):
        self._blacklist.add(href)
        logger.debug(f"Blacklisted: {href}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def remove_from_blacklist(self, href):
        self._blacklist.discard(href)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def add_to_whitelist(self, href):
        self._whitelist.add(href)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def load_blacklist_from_db(self):
        try:
            docs = db_manager.profiles_collection.find(
                {"status": "declined"},
                {"href": 1},
            )
            for doc in docs:
                self._blacklist.add(doc["href"])
            logger.info(f"Loaded {len(self._blacklist)} blacklisted profiles")
            return len(self._blacklist)
        except Exception as exc:
            logger.error(f"ConnectionService.load_blacklist_from_db: {exc}")
            return 0

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def get_status_summary(self):
        try:
            daily_stats = db_manager.get_daily_stats()
            return {
                "daily_sent": daily_stats.get("connections", 0),
                "daily_limit": config.MAX_CONNECTIONS_PER_DAY,
                "remaining_budget": self.get_remaining_budget(),
                "pending_requests": self.get_pending_count(),
                "blacklist_size": len(self._blacklist),
                "has_budget": self.has_budget(),
            }
        except Exception as exc:
            logger.error(f"ConnectionService.get_status_summary: {exc}")
            return {}

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _is_eligible(self, profile):
        href = profile.get("href", "")
        if not href or "linkedin.com/in/" not in href:
            return False
        status = profile.get("status", "")
        if status in _ALREADY_CONNECTED_STATUSES and href not in self._whitelist:
            return False
        if status == "pending" and self.get_pending_count() >= _MAX_PENDING_ALLOWED:
            return False
        return True


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

connection_service = ConnectionService()
