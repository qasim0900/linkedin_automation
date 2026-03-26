import random
import logging
from config import config
from string import Template
from database import db_manager
from datetime import datetime, timedelta

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

_DEFAULT_TEMPLATES = [
    (
        "Hi $first_name, I noticed your profile and was impressed by your work "
        "in $field. I'd love to connect and explore potential synergies. "
        "Looking forward to staying in touch!"
    ),
    (
        "Hello $first_name! Your background in $field caught my eye. "
        "I'm always keen to connect with professionals who share similar interests. "
        "Hope we can exchange insights sometime!"
    ),
    (
        "Hi $first_name — great to be connected! I came across your profile and "
        "found your expertise in $field really interesting. "
        "Would love to keep in touch."
    ),
    (
        "Hey $first_name, thanks for connecting! I've been following interesting "
        "work happening in $field and would love to learn more about your journey. "
        "Feel free to reach out anytime."
    ),
    (
        "Hi $first_name! Excited to be connected. Your experience in $field is "
        "exactly the kind of background I enjoy learning from. "
        "Looking forward to exchanging ideas!"
    ),
]


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

_GENERIC_FALLBACK = (
    "Hi there! Great to be connected. I'm always looking to expand my network "
    "with talented professionals. Looking forward to staying in touch!"
)


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def _extract_first_name(profile):
    name = profile.get("name", "")
    return name.split()[0] if name.strip() else "there"


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def _extract_field(profile):
    for key in ("title", "headline", "company"):
        value = profile.get(key, "").strip()
        if value:
            return " ".join(value.split()[:3])
    return "your field"


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


class MessagingService:

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def __init__(self):
        self._templates = _DEFAULT_TEMPLATES
        self._sent_cache: set = set()

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def add_template(self, template_text):
        self._templates.append(template_text)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def remove_template(self, index):
        if 0 <= index < len(self._templates):
            self._templates.pop(index)
            return True
        return False

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def list_templates(self):
        return self._templates

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def personalise_message(self, profile):
        if not self._templates:
            return _GENERIC_FALLBACK
        template_str = random.choice(self._templates)
        first_name = _extract_first_name(profile)
        field = _extract_field(profile)
        try:
            return Template(template_str).safe_substitute(
                first_name=first_name,
                field=field,
            )
        except Exception as exc:
            logger.warning(f"Template substitution failed: {exc}")
            return _GENERIC_FALLBACK

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def get_message_candidates(self, limit=15):
        try:
            query = {
                "connected": True,
                "$or": [
                    {"messaged": {"$exists": False}},
                    {"messaged": False},
                ],
            }
            profiles = list(
                db_manager.profiles_collection.find(query)
                .sort("connection_date", -1)
                .limit(limit * 2)
            )
            candidates = []
            for p in profiles:
                href = p.get("href", "")
                if href and href not in self._sent_cache:
                    candidates.append(p)
                if len(candidates) >= limit:
                    break
            logger.info(f"MessagingService: {len(candidates)} message candidates")
            return candidates
        except Exception as exc:
            logger.error(f"MessagingService.get_message_candidates: {exc}")
            return []

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
            used = daily_stats.get("messages", 0)
            return max(0, config.MAX_MESSAGES_PER_DAY - used)
        except Exception as exc:
            logger.error(f"MessagingService.get_remaining_budget: {exc}")
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

    def is_on_cooldown(self, profile_url):
        try:
            cutoff = datetime.utcnow() - timedelta(hours=24)
            return db_manager.activity_log_collection.find_one(
                {
                    "action_type": "messages",
                    "profile_url": profile_url,
                    "timestamp": {"$gte": cutoff},
                }
            )

        except Exception:
            return False

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def record_message_sent(self, profile_url, message, success):
        try:
            self._sent_cache.add(profile_url)

            if success:
                db_manager.profiles_collection.update_one(
                    {"href": profile_url},
                    {
                        "$set": {
                            "messaged": True,
                            "messaged_at": datetime.utcnow(),
                            "last_message": message[:200],
                        }
                    },
                )

            db_manager.log_activity(
                "messages",
                profile_url,
                {
                    "success": success,
                    "message_preview": message[:80],
                    "timestamp": datetime.utcnow(),
                },
            )

        except Exception as exc:
            logger.error(f"MessagingService.record_message_sent: {exc}")

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
            total_messaged = db_manager.profiles_collection.count_documents(
                {"messaged": True}
            )
            return {
                "daily_sent": daily_stats.get("messages", 0),
                "daily_limit": config.MAX_MESSAGES_PER_DAY,
                "remaining_budget": self.get_remaining_budget(),
                "total_messaged_all_time": total_messaged,
                "templates_available": len(self._templates),
                "session_cache_size": len(self._sent_cache),
            }
        except Exception as exc:
            logger.error(f"MessagingService.get_status_summary: {exc}")
            return {}


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""
messaging_service = MessagingService()
