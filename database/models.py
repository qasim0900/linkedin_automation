from datetime import datetime
from dataclasses import dataclass, field, asdict


# --------------------------------
# :: Profile Model
# --------------------------------

""" 
Represents a LinkedIn profile in the system.
"""


@dataclass
class Profile:
    href = ""
    name = ""
    headline = ""
    title = ""
    company = ""
    location = ""
    snippet = ""
    source = "google_search"

    processed = False
    connected = False
    messaged = False
    visited = False

    date_added = field(default_factory=datetime.utcnow)
    processed_at = None
    connection_date = None
    message_date = None
    last_visited = None
    last_action = ""

    # --------------------------------
    # :: TO DICT METHOD
    # --------------------------------

    """ 
    Convert the Profile dataclass instance to a dictionary for MongoDB storage.
    """

    def to_dict(self):
        d = asdict(self)
        return d


# --------------------------------
# :: Activity Log Model
# --------------------------------

""" 
Represents an action taken on a profile, used for logging and rate limit tracking.
"""


@dataclass
class ActivityLog:
    action_type = ""
    profile_href = ""
    timestamp = field(default_factory=datetime.utcnow)
    details = field(default_factory=dict)
    success = True

    # --------------------------------
    # :: To Dict Method
    # --------------------------------

    """ 
    Convert the ActivityLog dataclass instance to a dictionary for MongoDB storage.
    """

    def to_dict(self):
        return asdict(self)


# --------------------------------
# :: Rate Limit State Model
# --------------------------------

""" 
Represents the current state of rate limit consumption for connections, messages, and visits.
Not stored in MongoDB — derived from ActivityLog aggregation.
"""


@dataclass
class RateLimitState:
    connections_today = 0
    messages_today = 0
    visits_today = 0

    connections_limit = 20
    messages_limit = 15
    visits_limit = 50

    # --------------------------------
    # :: Properties and Methods
    # --------------------------------

    """ 
    Properties to check if we can perform more actions today based on the limits.
    """

    @property
    def can_connect(self):
        return self.connections_today < self.connections_limit

    # --------------------------------
    # :: Can Message Method
    # --------------------------------

    """ 
    Check if we can send more messages today based on the limit.
    """

    @property
    def can_message(self):
        return self.messages_today < self.messages_limit

    # --------------------------------
    # :: Can Visit Method
    # --------------------------------

    """ 
    Check if we can visit more profiles today based on the limit.
    """

    @property
    def can_visit(self):
        return self.visits_today < self.visits_limit

    # --------------------------------
    # :: TO DICT METHOD
    # --------------------------------

    """ 
    Convert the RateLimitState dataclass instance to a dictionary for reporting or API responses.
    """

    def to_dict(self):
        return {
            "connections": {
                "used": self.connections_today,
                "limit": self.connections_limit,
                "can_perform": self.can_connect,
                "daily_used": self.connections_today,
                "daily_limit": self.connections_limit,
            },
            "messages": {
                "used": self.messages_today,
                "limit": self.messages_limit,
                "can_perform": self.can_message,
                "daily_used": self.messages_today,
                "daily_limit": self.messages_limit,
            },
            "visits": {
                "used": self.visits_today,
                "limit": self.visits_limit,
                "can_perform": self.can_visit,
                "daily_used": self.visits_today,
                "daily_limit": self.visits_limit,
            },
        }
