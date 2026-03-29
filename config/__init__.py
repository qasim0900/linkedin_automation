import os
import logging
from dotenv import load_dotenv
from config.constants import GOOGLE_SEARCH_QUERIES

_dotenv_logger = logging.getLogger("dotenv.main")
_dotenv_logger.setLevel(logging.ERROR)
load_dotenv(override=False, verbose=False)


class Config:
    # -------------------------------------------------------------------------
    # :: MongoDB
    # -------------------------------------------------------------------------
    MONGO_CONNECTION = os.getenv("MONGO_CONNECTION", "mongodb://localhost:27017/")
    DATABASE_NAME = os.getenv("DB", os.getenv("DATABASE_NAME", "linked_connections"))

    # Four region-specific collections (from attached .env)
    USA_COLLECTION = os.getenv("USA_COLLECTION", "usa_google_connections")
    LAHORE_COLLECTION = os.getenv("LAHORE_COLLECTION", "lahore_google_connections")
    USA_MESSAGE_COLLECTION = os.getenv("USA_MESSAGE_COLLECTION", "usa_linkedin_connections")
    LAHORE_MESSAGE_COLLECTION = os.getenv("LAHORE_MESSAGE_COLLECTION", "lahore_linkedin_connections")

    # Legacy collection names mapped to new ones for backward compatibility
    PROFILES_COLLECTION = os.getenv("PROFILES_COLLECTION", "usa_google_connections")
    CONNECTIONS_COLLECTION = os.getenv("CONNECTIONS_COLLECTION", "usa_linkedin_connections")
    MESSAGES_COLLECTION = os.getenv("MESSAGES_COLLECTION", "usa_linkedin_connections")
    ACTIVITY_LOG_COLLECTION = os.getenv("ACTIVITY_LOG_COLLECTION", "activity_log")

    # -------------------------------------------------------------------------
    # :: LinkedIn Credentials
    # New env var names (IN_EMAIL / IN_PASSWORD) take priority;
    # LINKEDIN_EMAIL / LINKEDIN_PASSWORD kept for backward compatibility.
    # -------------------------------------------------------------------------
    LINKEDIN_EMAIL = os.getenv("IN_EMAIL") or os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD = os.getenv("IN_PASSWORD") or os.getenv("LINKEDIN_PASSWORD")

    # -------------------------------------------------------------------------
    # :: URLs
    # LOGIN_URL takes priority over the legacy LINKEDIN_LOGIN_URL key.
    # -------------------------------------------------------------------------
    LINKEDIN_LOGIN_URL = os.getenv("LOGIN_URL") or os.getenv(
        "LINKEDIN_LOGIN_URL", "https://www.linkedin.com/login"
    )

    # Full pre-built Google search URLs for each region
    USA_GOOGLE_URL = os.getenv("USA_GOOGLE", "")
    LAHORE_GOOGLE_URL = os.getenv("LAHORE_GOOGLE", "")

    # LinkedIn people-search URLs for each region
    USA_CONNECTION_URL = os.getenv("USA_CONECCTION_URL", "")
    LAHORE_CONNECTION_URL = os.getenv("LAHORE_CONECCTION_URL", "")

    # Legacy base URL (used as fallback when full regional URLs are not set)
    GOOGLE_SEARCH_URL = os.getenv("GOOGLE_SEARCH_URL", "https://www.google.com/search")

    # -------------------------------------------------------------------------
    # :: XPaths
    # New env var names take priority; old names used as fallbacks.
    # -------------------------------------------------------------------------
    XPATHS = {
        # Login form
        "email_input": os.getenv("EMAIL_INPUT") or os.getenv(
            "EMAIL_INPUT_XPATH", "//input[@id='username']"
        ),
        "password_input": os.getenv("PASSWORD_INPUT") or os.getenv(
            "PASSWORD_INPUT_XPATH", "//input[@id='password']"
        ),
        "login_button": os.getenv("SUBMIT_BUTTON") or os.getenv(
            "LOGIN_BUTTON_XPATH", "//button[@type='submit']"
        ),
        "loading_page": os.getenv(
            "LOADING_PAGE", "//div[@class='application-outlet']"
        ),
        # Profile actions
        "profile_name": os.getenv(
            "PROFILE_NAME_XPATH", "//h1[@class='text-heading-xlarge']"
        ),
        "connect_button": os.getenv(
            "CONNECT_BUTTON_XPATH", "//button[contains(., 'Connect')]"
        ),
        "follow_button": os.getenv(
            "FOLLOW_BUTTON_XPATH", "//button[contains(., 'Follow')]"
        ),
        "end_module": os.getenv(
            "END_MODULE",
            '//div[contains(@class,"ph5")]//button[span[text()="Got it"]]',
        ),
        # Messaging
        "message_button": os.getenv("MESSAGE_BUTTON") or os.getenv(
            "MESSAGE_BUTTON_XPATH",
            '//div[contains(@class,"ph5")]//button[span[text()="Message"]]',
        ),
        "message_textbox": os.getenv("MESSAGE_TEXTBOX") or os.getenv(
            "MESSAGE_TEXTBOX_XPATH",
            "//div[contains(@aria-label, 'Write a message')]",
        ),
        "send_message_button": os.getenv("MESSAGE_SEND_BUTTON") or os.getenv(
            "SEND_MESSAGE_BUTTON_XPATH",
            "//button[.//span[contains(@class,'artdeco-button__text') and text()='Message']]",
        ),
        "send_without_note": os.getenv(
            "SEND_WITHOUT_NOTE_XPATH",
            "//button[contains(., 'Send without a note')]",
        ),
        # Google scraping
        "google_profiles": os.getenv("GOOGLE_LINKEDIN_PROFILES") or os.getenv(
            "GOOGLE_PROFILES_XPATH",
            '//div[@class="dURPMd"]//a',
        ),
        "google_next_link": os.getenv("GOOGLE_NEXT_LINK") or os.getenv(
            "GOOGLE_NEXT_LINK_XPATH", '//*[@id="pnnext"]'
        ),
        # Connection list (LinkedIn people search)
        "connection_list": os.getenv("CONNECTION_LIST") or os.getenv(
            "CONNECTION_LIST_XPATH", '//div[@class="display-flex"]'
        ),
        "connection_next_button": os.getenv(
            "CONNECTION_NEXT_BUTTON", '//button[@aria-label="Next"]'
        ),
    }

    # -------------------------------------------------------------------------
    # :: Rate Limits
    # -------------------------------------------------------------------------
    MAX_CONNECTIONS_PER_DAY = int(os.getenv("MAX_CONNECTIONS_PER_DAY", "20"))
    MAX_MESSAGES_PER_DAY = int(os.getenv("MAX_MESSAGES_PER_DAY", "15"))
    MAX_PROFILE_VISITS_PER_DAY = int(os.getenv("MAX_PROFILE_VISITS_PER_DAY", "50"))

    # -------------------------------------------------------------------------
    # :: Human Behavior Delays
    # -------------------------------------------------------------------------
    MIN_DELAY_SECONDS = float(os.getenv("MIN_DELAY_SECONDS", "2.0"))
    MAX_DELAY_SECONDS = float(os.getenv("MAX_DELAY_SECONDS", "8.0"))
    MIN_TYPING_DELAY = float(os.getenv("MIN_TYPING_DELAY", "0.05"))
    MAX_TYPING_DELAY = float(os.getenv("MAX_TYPING_DELAY", "0.15"))

    # -------------------------------------------------------------------------
    # :: Browser
    # -------------------------------------------------------------------------
    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "true").lower() == "true"
    WINDOW_SIZE = (
        int(os.getenv("WINDOW_WIDTH", "1366")),
        int(os.getenv("WINDOW_HEIGHT", "768")),
    )

    # -------------------------------------------------------------------------
    # :: Logging
    # -------------------------------------------------------------------------
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

    # -------------------------------------------------------------------------
    # :: Session
    # -------------------------------------------------------------------------
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    COOKIE_FILE = os.getenv("COOKIE_FILE", "data/cookies.pkl")

    @classmethod
    def validate_config(cls):
        """Validate required environment variables are set."""
        missing = [
            var for var in ("LINKEDIN_EMAIL", "LINKEDIN_PASSWORD")
            if not getattr(cls, var)
        ]
        if missing:
            raise ValueError(
                f"Required environment variable(s) not set: {', '.join(missing)}"
            )
        return True

    @classmethod
    def get_google_search_url(cls, location="USA"):
        """
        Return the full Google search URL for the given location.
        Uses pre-built regional URLs from env when available;
        falls back to constructing a URL from the query constants.
        """
        if location == "USA" and cls.USA_GOOGLE_URL:
            return cls.USA_GOOGLE_URL
        if location == "Lahore" and cls.LAHORE_GOOGLE_URL:
            return cls.LAHORE_GOOGLE_URL
        # Fallback: build URL from query string constant
        query = GOOGLE_SEARCH_QUERIES.get(location, GOOGLE_SEARCH_QUERIES["USA"])
        return f"{cls.GOOGLE_SEARCH_URL}?q={query}"

    @classmethod
    def get_google_search_query(cls, location="USA"):
        """
        Return the Google search query string for the given location.
        Kept for backward compatibility with callers that build their own URL.
        """
        return GOOGLE_SEARCH_QUERIES.get(location, GOOGLE_SEARCH_QUERIES["USA"])

    @classmethod
    def get_collection_for_location(cls, location="USA"):
        """Return the MongoDB collection name for a given location."""
        mapping = {
            "USA": cls.USA_COLLECTION,
            "Lahore": cls.LAHORE_COLLECTION,
        }
        return mapping.get(location, cls.USA_COLLECTION)

    @classmethod
    def get_message_collection_for_location(cls, location="USA"):
        """Return the MongoDB message collection name for a given location."""
        mapping = {
            "USA": cls.USA_MESSAGE_COLLECTION,
            "Lahore": cls.LAHORE_MESSAGE_COLLECTION,
        }
        return mapping.get(location, cls.USA_MESSAGE_COLLECTION)


config = Config()
