import re
import logging
from selenium.webdriver.common.by import By


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: Ex
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def extract_linkedin_username(url):
    if not url:
        return None
    match = re.search(r"linkedin\.com/in/([^/?#]+)", url)
    return match.group(1).rstrip("/") if match else None


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def normalize_profile_url(url):
    username = extract_linkedin_username(url)
    if not username:
        return None
    return f"https://www.linkedin.com/in/{username}"


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def get_page_title(driver):
    try:
        return driver.title or ""
    except Exception:
        return ""


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def is_on_linkedin(driver):
    try:
        return "linkedin.com" in driver.current_url
    except Exception:
        return False


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def get_profile_name(driver, name_xpath):
    try:
        elements = driver.find_elements(By.XPATH, name_xpath)
        if elements:
            return elements[0].text.strip() or None
    except Exception as exc:
        logger.debug(f"Could not read profile name: {exc}")
    return None


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def is_rate_limit_error(driver):
    keywords = [
        "rate limit",
        "too many requests",
        "temporarily restricted",
        "slow down",
    ]
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        return any(kw in body_text for kw in keywords)
    except Exception:
        return False
