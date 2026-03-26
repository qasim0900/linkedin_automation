import os
import logging
from dotenv import load_dotenv
from dataclasses import dataclass, field

load_dotenv()

# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: Collection Names
# --------------------------------

""" 
Constants for MongoDB collection names. These are used throughout the codebase to ensure consistency when referencing collections in the database. If needed, these can be overridden
by environment variables or by passing different values to the DatabaseConfig dataclass.
"""

COLLECTION_PROFILES = "profiles"
COLLECTION_ACTIVITY_LOG = "activity_log"
COLLECTION_RATE_LIMITS = "rate_limits"
COLLECTION_SESSIONS = "sessions"
COLLECTION_MESSAGES = "messages"


# --------------------------------
# :: Default Database Settings
# --------------------------------

""" 
Default values for MongoDB connection settings. These are used as fallbacks if environment variables are not set. 
They include timeouts and pool size settings that help ensure the application can handle database connections efficiently and robustly.
"""

_DEFAULT_SERVER_SELECTION_TIMEOUT_MS = 5_000
_DEFAULT_CONNECT_TIMEOUT_MS = 5_000
_DEFAULT_SOCKET_TIMEOUT_MS = 5_000
_DEFAULT_MAX_POOL_SIZE = 10
_DEFAULT_MIN_POOL_SIZE = 1
_DEFAULT_WAIT_QUEUE_TIMEOUT_MS = 10_000


# --------------------------------
# :: DatabaseConfig Dataclass
# --------------------------------

""" 
The DatabaseConfig dataclass encapsulates all configuration settings related to the MongoDB connection. 
It reads values from environment variables with sensible defaults, and provides helper methods for building connection URIs and validating connectivity. This structured approach allows for easy management of database settings and promotes clean code throughout the application.
"""


@dataclass
class DatabaseConfig:
    uri = field(
        default_factory=lambda: os.getenv(
            "MONGO_CONNECTION", "mongodb://localhost:27017/"
        )
    )
    database_name = field(
        default_factory=lambda: os.getenv("DATABASE_NAME", "linkedin_automation")
    )
    max_pool_size = field(
        default_factory=lambda: int(
            os.getenv("MONGO_MAX_POOL_SIZE", _DEFAULT_MAX_POOL_SIZE)
        )
    )
    min_pool_size = field(
        default_factory=lambda: int(
            os.getenv("MONGO_MIN_POOL_SIZE", _DEFAULT_MIN_POOL_SIZE)
        )
    )
    server_selection_timeout_ms = _DEFAULT_SERVER_SELECTION_TIMEOUT_MS
    connect_timeout_ms = _DEFAULT_CONNECT_TIMEOUT_MS
    socket_timeout_ms = _DEFAULT_SOCKET_TIMEOUT_MS
    wait_queue_timeout_ms = _DEFAULT_WAIT_QUEUE_TIMEOUT_MS
    retry_writes = True
    retry_reads = True

    col_profiles = COLLECTION_PROFILES
    col_activity_log = COLLECTION_ACTIVITY_LOG
    col_rate_limits = COLLECTION_RATE_LIMITS
    col_sessions = COLLECTION_SESSIONS
    col_messages = COLLECTION_MESSAGES

    # --------------------------------
    # :: Get Client Kwargs Method
    # --------------------------------

    """ 
    Get a dictionary of keyword arguments for initializing a MongoDB client. This method consolidates all the 
    connection settings into a single dictionary that can be easily passed to the MongoClient constructor. It ensures that all relevant settings are included and can be maintained in one place.
    """

    def get_client_kwargs(self):
        return {
            "host": self.uri,
            "maxPoolSize": self.max_pool_size,
            "minPoolSize": self.min_pool_size,
            "serverSelectionTimeoutMS": self.server_selection_timeout_ms,
            "connectTimeoutMS": self.connect_timeout_ms,
            "socketTimeoutMS": self.socket_timeout_ms,
            "waitQueueTimeoutMS": self.wait_queue_timeout_ms,
            "retryWrites": self.retry_writes,
            "retryReads": self.retry_reads,
        }

    # ----------------------------------------
    # :: Build URI with Credentials Method
    # ----------------------------------------

    """ 
    Build a MongoDB URI that includes credentials if they are provided. This method checks for the presence of username and password either
    as parameters or in environment variables, and constructs a URI that includes these credentials. If no credentials are found, it returns the original URI. This allows for flexible configuration while maintaining security by not hardcoding credentials in the codebase.
    """

    def build_uri_with_credentials(
        self,
        username=None,
        password=None,
    ):
        _user = username or os.getenv("MONGO_USERNAME", "")
        _pass = password or os.getenv("MONGO_PASSWORD", "")

        if not _user or not _pass:
            return self.uri

        from urllib.parse import quote_plus, urlparse, urlunparse

        parsed = urlparse(self.uri)
        netloc = f"{quote_plus(_user)}:{quote_plus(_pass)}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"

        new_uri = urlunparse(parsed._replace(netloc=netloc))
        return new_uri

    # -----------------------------------
    # :: Is Local Method
    # -----------------------------------

    """ 
    Determine if the database URI points to a local instance.
    """

    def is_local(self):
        return "localhost" in self.uri or "127.0.0.1" in self.uri

    # --------------------------------
    # :: Validate Method
    # --------------------------------

    """ 
    Validate the database connection by attempting a ping command. This method tries to connect to the MongoDB 
    server using the provided URI and connection settings
    """

    def validate(self):
        try:
            import pymongo

            client = pymongo.MongoClient(**self.get_client_kwargs())
            client.admin.command("ping")
            client.close()
            logger.info(f"MongoDB connection validated: {self.uri}")
            return True
        except Exception as exc:
            logger.warning(f"MongoDB validation failed: {exc}")
            return False

    # --------------------------------
    # :: Summary Method
    # --------------------------------

    """ 
    Return a loggable summary of the database configuration, excluding sensitive information like credentials. 
    This method provides a way to log the current database settings without exposing any sensitive data, which is useful for debugging and monitoring purposes.
    """

    def summary(self):
        uri_safe = self.uri.split("@")[-1] if "@" in self.uri else self.uri
        return {
            "uri": uri_safe,
            "database": self.database_name,
            "max_pool_size": self.max_pool_size,
            "collections": {
                "profiles": self.col_profiles,
                "activity_log": self.col_activity_log,
                "sessions": self.col_sessions,
            },
        }


# ----------------------------------------
# :: Initialize DatabaseConfig Instance
# ----------------------------------------

""" 
Initialize a global instance of the DatabaseConfig dataclass. This instance will be used throughout the application to access database configuration settings. By creating a single instance, we ensure that all parts of the application are using consistent settings and can easily access the configuration when needed.
"""

db_config = DatabaseConfig()
