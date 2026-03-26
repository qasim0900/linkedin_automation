import os
from dotenv import load_dotenv
from config.constants import (
    GOOGLE_SEARCH_QUERIES,
)


load_dotenv()

# --------------------------------
# :: Config Class
# --------------------------------

""" 
The Config class is responsible for loading and managing all configuration settings for the LinkedIn automation application. It retrieves values from environment variables,
 provides default values where necessary, and includes methods for validating the configuration and generating Google search queries based on location.
"""


class Config:
    MONGO_CONNECTION = os.getenv("MONGO_CONNECTION", "mongodb://localhost:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "linkedin_automation")

    PROFILES_COLLECTION = os.getenv("PROFILES_COLLECTION", "profiles")
    CONNECTIONS_COLLECTION = os.getenv("CONNECTIONS_COLLECTION", "connections")
    MESSAGES_COLLECTION = os.getenv("MESSAGES_COLLECTION", "messages")
    ACTIVITY_LOG_COLLECTION = os.getenv("ACTIVITY_LOG_COLLECTION", "activity_log")

    LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

    LINKEDIN_LOGIN_URL = os.getenv(
        "LINKEDIN_LOGIN_URL", "https://www.linkedin.com/login"
    )
    GOOGLE_SEARCH_URL = os.getenv("GOOGLE_SEARCH_URL", "https://www.google.com/search")

    XPATHS = {
        "email_input": os.getenv("EMAIL_INPUT_XPATH", "//input[@id='username']"),
        "password_input": os.getenv("PASSWORD_INPUT_XPATH", "//input[@id='password']"),
        "login_button": os.getenv("LOGIN_BUTTON_XPATH", "//button[@type='submit']"),
        "profile_name": os.getenv(
            "PROFILE_NAME_XPATH", "//h1[@class='text-heading-xlarge']"
        ),
        "connect_button": os.getenv(
            "CONNECT_BUTTON_XPATH", "//button[contains(., 'Connect')]"
        ),
        "follow_button": os.getenv(
            "FOLLOW_BUTTON_XPATH", "//button[contains(., 'Follow')]"
        ),
        "message_button": os.getenv(
            "MESSAGE_BUTTON_XPATH", "//button[contains(., 'Message')]"
        ),
        "message_textbox": os.getenv(
            "MESSAGE_TEXTBOX_XPATH", "//div[@contenteditable='true']"
        ),
        "send_message_button": os.getenv(
            "SEND_MESSAGE_BUTTON_XPATH", "//button[contains(., 'Send')]"
        ),
        "send_without_note": os.getenv(
            "SEND_WITHOUT_NOTE_XPATH", "//button[contains(., 'Send without a note')]"
        ),
        "google_profiles": os.getenv(
            "GOOGLE_PROFILES_XPATH",
            "//div[@class='g']//a[contains(@href, 'linkedin.com/in')]/ancestor::div[@class='g']",
        ),
        "google_next_link": os.getenv("GOOGLE_NEXT_LINK_XPATH", "//a[@id='pnnext']"),
        "connection_list": os.getenv(
            "CONNECTION_LIST_XPATH",
            "//div[contains(@class, 'mn-connections')]//a[contains(@href, 'linkedin.com/in')]",
        ),
    }

    MAX_CONNECTIONS_PER_DAY = int(os.getenv("MAX_CONNECTIONS_PER_DAY", "20"))
    MAX_MESSAGES_PER_DAY = int(os.getenv("MAX_MESSAGES_PER_DAY", "15"))
    MAX_PROFILE_VISITS_PER_DAY = int(os.getenv("MAX_PROFILE_VISITS_PER_DAY", "50"))

    MIN_DELAY_SECONDS = float(os.getenv("MIN_DELAY_SECONDS", "2.0"))
    MAX_DELAY_SECONDS = float(os.getenv("MAX_DELAY_SECONDS", "8.0"))
    MIN_TYPING_DELAY = float(os.getenv("MIN_TYPING_DELAY", "0.05"))
    MAX_TYPING_DELAY = float(os.getenv("MAX_TYPING_DELAY", "0.15"))

    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "false").lower() == "true"
    WINDOW_SIZE = (
        int(os.getenv("WINDOW_WIDTH", "1600")),
        int(os.getenv("WINDOW_HEIGHT", "900")),
    )

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    COOKIE_FILE = os.getenv("COOKIE_FILE", "data/cookies.pkl")

    # --------------------------------
    # :: Validate Config Method
    # --------------------------------

    """
    Validates that all required environment variables are set. Raises a ValueError if any required variable is missing.
    """

    @classmethod
    def validate_config(cls):
        required_vars = ["LINKEDIN_EMAIL", "LINKEDIN_PASSWORD"]

        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"Required environment variable {var} is not set")

        return True

    # ------------------------------------
    # :: Get Google Search Query Method
    # ------------------------------------

    """
    Returns the appropriate Google search query based on the specified location. If the location is not found in the 
    predefined queries, it defaults to the USA query.
    """

    @classmethod
    def get_google_search_query(cls, location = "USA"):
        return GOOGLE_SEARCH_QUERIES.get(location, GOOGLE_SEARCH_QUERIES["USA"])


# --------------------------------
# :: Config Instance
# --------------------------------

""" 
Creates a global instance of the Config class that can be imported and used throughout the application.
"""

config = Config()
