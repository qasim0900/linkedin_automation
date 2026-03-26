import os
from dotenv import load_dotenv
from dataclasses import dataclass, field


load_dotenv()


# --------------------------------
# :: Env Int Helper Function
# --------------------------------

""" 
Helper function to read an integer environment variable with a default fallback.
"""


def _env_int(key, default):
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return default


# --------------------------------
# :: Env Float Helper Function
# --------------------------------

""" 
Helper function to read a float environment variable with a default fallback.
"""


def _env_float(key, default):
    try:
        return float(os.getenv(key, default))
    except (ValueError, TypeError):
        return default


# --------------------------------
# :: Env Bool Helper Function
# --------------------------------

""" 
Helper function to read a boolean environment variable with a default fallback.
"""


def _env_bool(key, default):
    val = os.getenv(key, "").lower()
    if val in ("1", "true", "yes"):
        return True
    if val in ("0", "false", "no"):
        return False
    return default


# -----------------------------------
# :: Rate Limit Settings Data Class
# -----------------------------------

""" 
Data class to hold all rate limit related settings for the bot. This includes limits on connections, messages, 
and profile visits, as well as cooldown periods and warning thresholds.
"""


@dataclass(frozen=True)
class RateLimitSettings:
    max_connections_per_day = field(
        default_factory=lambda: _env_int("MAX_CONNECTIONS_PER_DAY", 20)
    )
    max_messages_per_day = field(
        default_factory=lambda: _env_int("MAX_MESSAGES_PER_DAY", 15)
    )
    max_visits_per_day = field(
        default_factory=lambda: _env_int("MAX_PROFILE_VISITS_PER_DAY", 50)
    )
    max_connections_per_hour = 5
    max_messages_per_hour = 3
    max_visits_per_hour = 12

    connection_cooldown_seconds = 300
    message_cooldown_seconds = 600
    visit_cooldown_seconds = 60
    weekly_connection_warning = 95
    pending_request_cap = 500


# --------------------------------
# :: Dataclass for Delays
# --------------------------------

""" 
Data class to hold all delay related settings for the bot. This includes typing delays, action delays,
and navigation delays.
"""


@dataclass(frozen=True)
class DelaySettings:
    typing_min_ms = 50.0
    typing_max_ms = 180.0

    action_min_seconds = 3.0
    action_max_seconds = 10.0

    navigation_min_seconds = 2.0
    navigation_max_seconds = 6.0

    reading_min_seconds = 1.5
    reading_max_seconds = 5.0

    micro_break_min_seconds = 30.0
    micro_break_max_seconds = 120.0

    session_break_min_seconds = 300.0
    session_break_max_seconds = 900.0

    between_connections_min = 5.0
    between_connections_max = 12.0

    between_messages_min = 8.0
    between_messages_max = 15.0


# --------------------------------
# :: Browser Settings Data Class
# --------------------------------

""" 
Data class to hold all browser-related settings for the bot.
"""


@dataclass(frozen=True)
class BrowserSettings:
    headless = field(default_factory=lambda: _env_bool("HEADLESS_MODE", False))
    window_width = field(default_factory=lambda: _env_int("BROWSER_WIDTH", 1366))
    window_height = field(default_factory=lambda: _env_int("BROWSER_HEIGHT", 768))
    page_load_timeout = field(
        default_factory=lambda: _env_int("PAGE_LOAD_TIMEOUT", 30)
    )
    implicit_wait = field(default_factory=lambda: _env_int("IMPLICIT_WAIT", 10))
    element_wait_timeout = 15

    disable_images = field(
        default_factory=lambda: _env_bool("DISABLE_IMAGES", False)
    )
    disable_notifications = True
    disable_infobars = True
    use_undetected_driver = True
    randomise_fingerprint = True


# --------------------------------
# :: Scheduler Settings Data Class
# --------------------------------

""" 
Data class to hold all scheduler-related settings for the bot. This includes the hours during which automation should run,
session durations, and intervals for scraping and scheduling tasks.
"""


@dataclass(frozen=True)
class SchedulerSettings:
    automation_start_hour = field(
        default_factory=lambda: _env_int("AUTOMATION_START_HOUR", 9)
    )
    automation_end_hour = field(
        default_factory=lambda: _env_int("AUTOMATION_END_HOUR", 18)
    )
    session_duration_minutes = 120
    scheduler_tick_seconds = 60
    max_actions_per_session = 50
    scrape_interval_hours = 24


# --------------------------------
# :: Logging Settings Data Class
# --------------------------------

""" 
Data class to hold all logging-related settings for the bot. This includes log file location, log level, and log rotation settings.
"""


@dataclass(frozen=True)
class LoggingSettings:
    log_file = field(default_factory=lambda: os.getenv("LOG_FILE", "logs/app.log"))
    log_level = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper()
    )
    max_bytes = 10 * 1024 * 1024
    backup_count = 5


# --------------------------------
# :: Feature Flags Data Class
# --------------------------------

""" 
Data class to hold all feature flags for the bot. This allows for easy toggling of features like connection requests, 
messaging, profile visits, Google scraping, and scheduler functionality.
"""


@dataclass(frozen=True)
class FeatureFlags:
    enable_connection_requests = field(
        default_factory=lambda: _env_bool("ENABLE_CONNECTIONS", True)
    )
    enable_messaging = field(
        default_factory=lambda: _env_bool("ENABLE_MESSAGING", True)
    )
    enable_profile_visits = field(
        default_factory=lambda: _env_bool("ENABLE_VISITS", True)
    )
    enable_accept_requests = field(
        default_factory=lambda: _env_bool("ENABLE_ACCEPT", True)
    )
    enable_google_scraping = field(
        default_factory=lambda: _env_bool("ENABLE_SCRAPING", True)
    )
    enable_cookie_session = field(
        default_factory=lambda: _env_bool("ENABLE_COOKIE_SESSION", True)
    )
    enable_scheduler = field(
        default_factory=lambda: _env_bool("ENABLE_SCHEDULER", True)
    )
    enable_human_breaks = True
    strict_rate_limits = True


# --------------------------------
# :: App Settings Data Class
# --------------------------------

""" 
Data class to hold all application settings for the bot. This includes rate limits, delays, browser settings, scheduler settings, logging settings, and feature flags.
"""


@dataclass(frozen=True)
class AppSettings:
    rate_limits: RateLimitSettings = field(default_factory=RateLimitSettings)
    delays: DelaySettings = field(default_factory=DelaySettings)
    browser: BrowserSettings = field(default_factory=BrowserSettings)
    scheduler: SchedulerSettings = field(default_factory=SchedulerSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    features: FeatureFlags = field(default_factory=FeatureFlags)

    # --------------------------------
    # :: Summer Method
    # --------------------------------

    """ 
    Summary method to provide a concise overview of the current settings. This can be useful for logging or debugging purposes,
    allowing developers to quickly see the key configuration values without having to inspect each setting individually.
    """

    def summary(self):
        return {
            "rate_limits": {
                "connections/day": self.rate_limits.max_connections_per_day,
                "messages/day": self.rate_limits.max_messages_per_day,
                "visits/day": self.rate_limits.max_visits_per_day,
            },
            "browser": {
                "headless": self.browser.headless,
                "size": f"{self.browser.window_width}x{self.browser.window_height}",
            },
            "scheduler": {
                "hours": (
                    f"{self.scheduler.automation_start_hour}:00 - "
                    f"{self.scheduler.automation_end_hour}:00 UTC"
                ),
            },
            "features": {
                "connections": self.features.enable_connection_requests,
                "messaging": self.features.enable_messaging,
                "visits": self.features.enable_profile_visits,
                "scraping": self.features.enable_google_scraping,
                "scheduler": self.features.enable_scheduler,
            },
        }


# --------------------------------
# :: App Settings Instance
# --------------------------------

""" 
Create a single instance of the AppSettings data class that can be imported and used throughout the application. 
This instance will hold all the configuration settings for the bot, allowing for easy access and consistency across different modules.
"""

app_settings = AppSettings()
