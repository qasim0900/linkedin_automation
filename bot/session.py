import os
import pickle
import logging
from config import config


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)

COOKIE_FILE = config.COOKIE_FILE


# --------------------------------
# :: Save Cookies Function
# --------------------------------

""" 
Function to save the current session cookies from the Selenium WebDriver to a file. 
This allows the bot to maintain a logged-in state across sessions without needing to log in again, as long as 
the cookies are still valid. The function handles exceptions and logs the outcome of the save operation.
"""


def save_cookies(driver, filepath=COOKIE_FILE):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        cookies = driver.get_cookies()
        with open(filepath, "wb") as f:
            pickle.dump(cookies, f)
        logger.info(f"Session cookies saved ({len(cookies)} cookies)")
        return True
    except Exception as e:
        logger.error(f"Failed to save cookies: {e}")
        return False


# --------------------------------
# :: Load Cookies Function
# --------------------------------

""" 
Function to load previously saved cookies into the browser. This allows the bot to maintain a logged-in state across sessions without needing to log in again, as long as the cookies are still valid. 
The function handles exceptions and logs the outcome of the load operation.
"""


def load_cookies(driver, filepath=COOKIE_FILE):
    if not os.path.exists(filepath):
        logger.info("No saved session found — fresh login required")
        return False
    try:
        with open(filepath, "rb") as f:
            cookies = pickle.load(f)
        if "linkedin.com" not in driver.current_url:
            driver.get("https://www.linkedin.com")
        for cookie in cookies:
            cookie.pop("expiry", None)
            cookie.pop("sameSite", None)
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass
        logger.info(f"Session cookies loaded ({len(cookies)} cookies)")
        return True
    except Exception as e:
        logger.error(f"Failed to load cookies: {e}")
        return False


# --------------------------------
# :: Delete Cookies Function
# --------------------------------

""" 
Function to delete the saved cookie file. This can be used to clear the session and force a fresh login on the next run. The function handles exceptions and logs the outcome of the delete operation.
"""


def delete_cookies(filepath=COOKIE_FILE):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info("Saved session cookies deleted")
        return True
    except Exception as e:
        logger.error(f"Failed to delete cookie file: {e}")
        return False
