# --------------------------------
# :: LinkedIn Bot Constants
# --------------------------------

"""
Defines all constants used across the LinkedIn Bot application, including
URLs, browser settings, rate limits, human behavior parameters, scheduler
settings, scraper configurations, and logging parameters.
"""

LINKEDIN_BASE_URL = "https://www.linkedin.com"
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"
LINKEDIN_MY_NETWORK_URL = "https://www.linkedin.com/mynetwork/"
LINKEDIN_INVITATIONS_URL = "https://www.linkedin.com/mynetwork/invitation-manager/"
LINKEDIN_MESSAGING_URL = "https://www.linkedin.com/messaging/"
LINKEDIN_LOGOUT_URL = "https://www.linkedin.com/logout"


# --------------------------------
# :: Browser Settings
# --------------------------------

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

CHROME_STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-notifications",
    "--ignore-certificate-errors",
    "--disable-popup-blocking",
    "--disable-extensions",
    "--log-level=3",
    "--disable-features=VizDisplayCompositor",
    "--no-first-run",
    "--password-store=basic",
    "--disable-web-security",
    "--allow-running-insecure-content",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
]

# --------------------------------
# :: Rate Limits
# --------------------------------

DEFAULT_MAX_CONNECTIONS_PER_DAY = 20
DEFAULT_MAX_MESSAGES_PER_DAY = 15
DEFAULT_MAX_VISITS_PER_DAY = 50

CONNECTIONS_PER_HOUR = 5
MESSAGES_PER_HOUR = 3
VISITS_PER_HOUR = 10

MIN_CONNECTION_COOLDOWN = 120
MIN_MESSAGE_COOLDOWN = 180
MIN_VISIT_COOLDOWN = 30


# --------------------------------
# :: Human Behavior Parameters
# --------------------------------

DEFAULT_MIN_DELAY = 2.0
DEFAULT_MAX_DELAY = 8.0
DEFAULT_MIN_TYPING_DELAY = 0.05
DEFAULT_MAX_TYPING_DELAY = 0.15

ACTIONS_BEFORE_BREAK = 15
SESSION_BREAK_MIN = 30
SESSION_BREAK_MAX = 120


# --------------------------------
# :: Scheduler Settings
# --------------------------------

DEFAULT_AUTOMATION_START_HOUR = 9
DEFAULT_AUTOMATION_END_HOUR = 18


# --------------------------------
# :: Scraper Settings
# --------------------------------

"""
Fallback Google search query strings used when full regional URLs are not
provided via environment variables. The Config.get_google_search_url()
method prefers the env-provided full URLs (USA_GOOGLE / LAHORE_GOOGLE)
over these query strings.
"""

GOOGLE_SEARCH_QUERIES = {
    "USA": (
        'site:linkedin.com/in ("HR Manager" OR "Talent Acquisition") '
        '("CEO" OR "FinTech" OR "CTO") "USA"'
    ),
    "Lahore": (
        'site:linkedin.com/in ("HR Manager" OR "Talent Acquisition") '
        '("CEO" OR "FinTech" OR "CTO") "Lahore" "Pakistan"'
    ),
    "UK": "site:linkedin.com/in software developer United Kingdom",
    "Canada": "site:linkedin.com/in software engineer Canada",
    "Australia": "site:linkedin.com/in software engineer Australia",
}

MAX_GOOGLE_PAGES = 10
MIN_PAGE_DELAY = 3.0
MAX_PAGE_DELAY = 7.0

# --------------------------------
# :: Logging Parameters
# --------------------------------

LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 5
