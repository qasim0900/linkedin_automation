import logging
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
# :: Unprocessed Profiles Query
# --------------------------------

""" 
Returns a MongoDB query to find profiles that have not been processed yet. 
This includes profiles where the 'processed' field is either missing or explicitly set to False.
"""


def unprocessed_profiles_query():
    return {
        "$or": [
            {"processed": {"$exists": False}},
            {"processed": False},
        ]
    }


# --------------------------------
# :: Need Connection Query
# --------------------------------

""" 
Returns a MongoDB query to find profiles that need to be connected with. 
This includes profiles that have not been processed and are not yet connected.
"""


def needs_connection_query():
    return {
        "processed": False,
        "$or": [
            {"connected": {"$exists": False}},
            {"connected": False},
        ],
    }


# --------------------------------
# :: Need Message Query
# --------------------------------

""" 
Returns a MongoDB query to find profiles that need to be messaged. 
This includes profiles that are connected but have not been messaged yet.
"""


def needs_message_query():
    return {
        "connected": True,
        "$or": [
            {"messaged": {"$exists": False}},
            {"messaged": False},
        ],
    }


# --------------------------------
# :: Need Visit Query
# --------------------------------

""" 
Returns a MongoDB query to find profiles that need to be visited. 
This includes profiles that have not been visited today.
"""


def needs_visit_query():
    today = _start_of_today()
    return {
        "$or": [
            {"last_visited": {"$exists": False}},
            {"last_visited": {"$lt": today}},
        ]
    }


# --------------------------------
# :: Old Unprocessed Profiles Query
# --------------------------------

""" 
Returns a MongoDB query to find profiles that have been unprocessed for a long time (e.g., 30 days).
This can be used for cleanup or reprocessing of old profiles.
"""


def old_unprocessed_profiles_query(days = 30):
    cutoff = datetime.utcnow() - timedelta(days=days)
    return {
        "processed": False,
        "date_added": {"$lt": cutoff},
    }


# --------------------------------
# :: Daily Activity Pipeline
# --------------------------------

""" 
Returns a MongoDB aggregation pipeline to count the number of actions taken today, grouped by action type.
This can be used to track daily activity and ensure that the bot is operating within expected limits.
"""


def daily_activity_pipeline():
    today = _start_of_today()
    return [
        {"$match": {"timestamp": {"$gte": today}}},
        {"$group": {"_id": "$action_type", "count": {"$sum": 1}}},
    ]


# --------------------------------
# :: Recent Activity Count Query
# --------------------------------

""" 
Returns a MongoDB query to count the number of actions taken in the last N minutes. 
This can be used for rate limit tracking to ensure that the bot does not exceed allowed limits.
"""


def recent_activity_count_query(minutes = 30):
    since = datetime.utcnow() - timedelta(minutes=minutes)
    return {"timestamp": {"$gte": since}}


# --------------------------------
# :: Profile Upsert Operation
# --------------------------------

""" 
Returns a MongoDB UpdateOne operation to upsert a profile document. 
This operation will insert the profile if it does not exist, or do nothing if it already exists
"""


def upsert_profile_operation(profile):
    import pymongo

    return pymongo.UpdateOne(
        {"href": profile["href"]},
        {
            "$setOnInsert": {
                **profile,
                "date_added": datetime.utcnow(),
                "processed": False,
                "connected": False,
                "messaged": False,
                "visited": False,
            }
        },
        upsert=True,
    )


# --------------------------------
# :: Stale Profile Query
# --------------------------------

""" 
Returns a MongoDB query to find profiles that have not been processed for a long time (e.g., 30 days).
This can be used to identify profiles that may need to be reprocessed or removed from the database
"""


def _start_of_today():
    now = datetime.utcnow()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)
