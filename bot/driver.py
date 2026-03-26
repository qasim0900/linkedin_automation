import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    WebDriverException,
)


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10


# --------------------------------
# :: Wait for Element Function
# --------------------------------

""" 
Wait functions for the bot module. These functions will be used to wait for certain conditions to be met before proceeding with actions. 
They help ensure that the bot interacts with the web page
"""


def wait_for_element(driver, xpath, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
    except TimeoutException:
        logger.debug(f"Element not visible within {timeout}s: {xpath}")
        return None


# --------------------------------
# :: Wait For Clickable Function
# --------------------------------

""" 
Wait functions for the bot module. These functions will be used to wait for certain conditions to be met before proceeding with actions. 
They help ensure that the bot interacts with the web page
"""


def wait_for_clickable(driver, xpath, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
    except TimeoutException:
        logger.debug(f"Element not clickable within {timeout}s: {xpath}")
        return None


# --------------------------------
# :: Find Element Function
# --------------------------------

""" 
Find element functions for the bot module. These functions will be used to find elements on the web page using XPath. 
They will return the element if found, or None if not found within the specified timeout.
"""


def find_element(driver, xpath, timeout=DEFAULT_TIMEOUT):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    except TimeoutException:
        return None


# --------------------------------
# :: Find Elements Function
# --------------------------------

""" 
Find element functions for the bot module. These functions will be used to find elements on the web page using XPath. 
They will return a list of elements if found, or an empty list if not found within the specified timeout.
"""


def find_elements(driver, xpath, timeout=DEFAULT_TIMEOUT):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return driver.find_elements(By.XPATH, xpath)
    except TimeoutException:
        return []
    except Exception:
        return []


# --------------------------------
# :: Safe Click Function
# --------------------------------

""" 
Safe click function for the bot module. This function will attempt to click an element using the normal click method, and if that fails (e.g., due to an intercepting element), it will attempt to click using JavaScript. 
This helps ensure that the bot can interact with elements even if there are unexpected overlays or popups
"""


def safe_click(driver, element):
    try:
        element.click()
        return True
    except (ElementClickInterceptedException, WebDriverException) as exc:
        logger.debug(f"Normal click blocked ({exc}), trying JS click")
    try:
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as exc:
        logger.error(f"JS click also failed: {exc}")
        return False


# --------------------------------
# :: Scroll To Element Function
# --------------------------------

""" 
Scroll to element function for the bot module. This function will scroll the web page to bring a specific element into view. 
This is useful for ensuring that the bot can interact with elements that may be off-screen or hidden
"""


def scroll_to(driver, element):
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});",
            element,
        )
    except Exception as exc:
        logger.debug(f"scroll_to failed: {exc}")


# --------------------------------
# :: Page Loaded Function
# --------------------------------

""" 
Page loaded function for the bot module. This function will check if the web page has fully loaded by checking the document.readyState property. 
This helps ensure that the bot does not attempt to interact with the page before it is ready,
"""


def page_loaded(driver):
    try:
        return driver.execute_script("return document.readyState") == "complete"
    except Exception:
        return False


# --------------------------------
# :: Dismiss Dialog Function
# --------------------------------

""" 
Dismiss dialog function for the bot module. This function will attempt to find and click on common "dismiss" buttons that may appear as popups or dialogs on the LinkedIn website. 
This helps ensure that the bot can continue operating even if unexpected dialogs appear, such as notifications,
"""


def dismiss_dialog(driver, dismiss_xpaths=None):
    defaults = [
        "//button[@aria-label='Dismiss']",
        "//button[contains(@aria-label,'Close')]",
        "//button[contains(text(),'Close')]",
        "//button[contains(text(),'Got it')]",
        "//button[contains(text(),'Cancel')]",
    ]
    xpaths = dismiss_xpaths or defaults
    for xpath in xpaths:
        el = find_element(driver, xpath, timeout=3)
        if el:
            safe_click(driver, el)
            logger.debug(f"Dismissed dialog via: {xpath}")
            return True
    return False


# --------------------------------
# :: Check Weekly Limit Function
# --------------------------------

""" 
Check weekly limit function for the bot module. This function will check for indicators on the LinkedIn website that suggest the user has reached a weekly connection limit. 
If such indicators are found, it will log a warning and attempt to dismiss any related dialogs,
"""


def check_weekly_limit(driver):
    indicators = [
        "//*[contains(text(),'weekly limit')]",
        "//*[contains(text(),'reached your weekly')]",
        "//*[contains(text(),'connection limit')]",
    ]
    for xpath in indicators:
        if driver.find_elements(By.XPATH, xpath):
            logger.warning("LinkedIn weekly connection limit detected")
            dismiss_dialog(driver)
            return True
    return False


# --------------------------------
# :: Check CAPTCHA Function
# --------------------------------

""" 
Check CAPTCHA function for the bot module. This function will check for indicators on the LinkedIn website that suggest a CAPTCHA challenge has been triggered. 
If such indicators are found, it will log a warning that manual intervention is required, as CAPTCHA challenges cannot be bypassed by automation, and will return True to indicate that a CAPTCHA was detected.
"""


def check_captcha(driver):
    indicators = [
        "//iframe[contains(@src,'recaptcha')]",
        "//*[contains(@class,'captcha')]",
        "//*[contains(text(),'CAPTCHA')]",
        "//*[contains(text(),'security check')]",
    ]
    for xpath in indicators:
        if driver.find_elements(By.XPATH, xpath):
            logger.warning("CAPTCHA detected — manual intervention required")
            return True
    return False
