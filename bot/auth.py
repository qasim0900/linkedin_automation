import time
import logging
from config import config
from bot import driver_manager
from utils import get_human_behavior
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bot.session import save_cookies, load_cookies, delete_cookies


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: LinkedInAuth Class
# --------------------------------

""" 
LinkedInAuth is responsible for managing authentication sessions with LinkedIn. It handles logging in, logging out,
"""


class LinkedInAuth:

    # --------------------------------
    # :: Init Method
    # --------------------------------

    """
    Initializes the LinkedInAuth class with default values for the driver, human behavior simulator, login status,
    """

    def __init__(self):
        self.driver = None
        self.human_behavior = None
        self.is_logged_in = False
        self.login_attempts = 0
        self.max_login_attempts = 3

    # --------------------------------
    # :: initialize Method
    # --------------------------------

    """
    Initializes the Selenium WebDriver and the human behavior simulator. This method is called before any login
    """

    def _initialize_driver(self):
        if not self.driver:
            self.driver = driver_manager.get_driver()
            self.human_behavior = get_human_behavior(self.driver)

    # --------------------------------
    # :: Iogin Method
    # --------------------------------

    """
    Performs the login process. It first tries to restore a session from saved cookies. If that fails, it performs
    """

    def login(self, force_new_session=False):
        self._initialize_driver()
        if force_new_session:
            delete_cookies()
            self.driver = driver_manager.restart_driver()
            self.human_behavior = get_human_behavior(self.driver)
        if not force_new_session:
            if self._restore_session_from_cookies():
                self.is_logged_in = True
                return True
        try:
            logger.info("Attempting credential-based login to LinkedIn…")
            self.login_attempts += 1
            self.human_behavior.human_like_navigation(config.LINKEDIN_LOGIN_URL)
            if not self._wait_for_login_form():
                logger.error("Login form not found")
                return False
            if not self._fill_credentials():
                logger.error("Failed to fill credentials")
                return False
            if not self._submit_login():
                logger.error("Failed to submit login form")
                return False
            if self._wait_for_login_completion():
                self.is_logged_in = True
                self.login_attempts = 0
                logger.info("Successfully logged in to LinkedIn")
                save_cookies(self.driver)
                from database import db_manager

                db_manager.log_activity("login", "linkedin.com", {"success": True})
                return True
            else:
                logger.error("Login completion check failed")
                return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    # -----------------------------------------
    # :: restore_session_from_cookies Method
    # -----------------------------------------

    """
    Attempts to restore a login session using previously saved cookies. It loads the cookies into the browser and checks
    if the session is still valid by navigating to the LinkedIn feed page and looking for indicators of a logged-in state.
    """

    def _restore_session_from_cookies(self):
        try:
            self.driver.get("https://www.linkedin.com")
            self.human_behavior.random_delay(1, 2)

            if not load_cookies(self.driver):
                return False
            self.driver.get("https://www.linkedin.com/feed/")
            self.human_behavior.random_delay(2, 4)

            if self._check_login_status():
                logger.info("Session restored from saved cookies")
                return True
            else:
                logger.info("Saved cookies are expired — will perform fresh login")
                delete_cookies()
                return False
        except Exception as e:
            logger.warning(f"Cookie session restore failed: {e}")
            return False

    # ------------------------------------
    # :: Accept Pending Requests Method
    # ------------------------------------

    """
    Accepts pending connection requests up to a specified maximum. Navigates to the invitation manager,
    """

    def _check_login_status(self):
        try:
            login_indicators = [
                "//div[contains(@class, 'global-nav__primary-link')]",
                "//img[contains(@alt, 'profile photo')]",
                "//div[contains(@class, 'feed-identity-module')]",
                "//a[contains(@href, '/feed')]",
            ]
            for indicator in login_indicators:
                if self.driver.find_elements(By.XPATH, indicator):
                    logger.debug("Login status indicator found")
                    return True
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            if "login" in self.driver.current_url.lower():
                return False
            feed_indicators = [
                "//div[contains(@class, 'feed-shared-update')]",
                "//div[contains(@class, 'feed-identity-module')]",
            ]
            for indicator in feed_indicators:
                if self.driver.find_elements(By.XPATH, indicator):
                    return True
            return False
        except Exception as e:
            logger.debug(f"Error checking login status: {e}")
            return False

    # --------------------------------
    # :: wait_for_login_form Method
    # --------------------------------

    """
    Waits for the login form to be present on the page. It looks for the email input field as an indicator that the form
    """

    def _wait_for_login_form(self):
        try:
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, config.XPATHS["email_input"]))
            )
            if email_input and email_input.is_displayed():
                logger.debug("Login form found")
                self.human_behavior.random_delay(1, 2)
                return True
            return False
        except TimeoutException:
            logger.error("Login form not found within timeout")
            return False

    # --------------------------------
    # :: Fill Credentials Method
    # --------------------------------

    """
    Fills in the login credentials (email and password) into the login form. It uses the human behavior simulator to
    type the credentials in a human-like manner, with random delays between keystrokes.
    """

    def _fill_credentials(self):
        try:
            email_input = self.driver.find_element(
                By.XPATH, config.XPATHS["email_input"]
            )
            self.human_behavior.human_typing(email_input, config.LINKEDIN_EMAIL)
            self.human_behavior.random_delay(0.5, 1.5)
            password_input = self.driver.find_element(
                By.XPATH, config.XPATHS["password_input"]
            )
            self.human_behavior.human_typing(password_input, config.LINKEDIN_PASSWORD)
            self.human_behavior.random_delay(0.5, 1.5)
            logger.debug("Credentials filled successfully")
            return True
        except Exception as e:
            logger.error(f"Error filling credentials: {e}")
            return False

    # --------------------------------
    # :: Submit Login Method
    # --------------------------------

    """
    Submits the login form by clicking the login button. It waits for the button to be clickable and uses the human
    behavior simulator to click it in a human-like manner
    """

    def _submit_login(self):
        try:
            login_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, config.XPATHS["login_button"]))
            )
            self.human_behavior.random_click_position(login_button)
            logger.debug("Login form submitted")
            return True
        except Exception as e:
            logger.error(f"Error submitting login: {e}")
            return False

    # --------------------------------------
    # :: Wait for Login Completion Method
    # --------------------------------------

    """
    Waits for the login process to complete by checking for indicators of a successful login or error messages.
    """

    def _wait_for_login_completion(self):
        try:
            time.sleep(3)
            error_indicators = [
                "//div[contains(@class, 'alert-error')]",
                "//span[contains(text(), 'wrong')]",
                "//span[contains(text(), 'invalid')]",
                "//div[contains(text(), 'incorrect')]",
            ]
            for indicator in error_indicators:
                error_elements = self.driver.find_elements(By.XPATH, indicator)
                if error_elements:
                    error_text = error_elements[0].text.lower()
                    logger.error(f"Login error detected: {error_text}")
                    from database import db_manager

                    db_manager.log_activity(
                        "login_failed",
                        "linkedin.com",
                        {"error": error_text, "attempt": self.login_attempts},
                    )
                    return False
            success_indicators = [
                "//div[contains(@class, 'feed-identity-module')]",
                "//div[contains(@class, 'global-nav__primary-link')]",
                "//a[contains(@href, '/mynetwork')]",
                "//img[contains(@alt, 'profile photo')]",
            ]
            for indicator in success_indicators:
                try:
                    element = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, indicator))
                    )
                    if element and element.is_displayed():
                        logger.debug("Login success indicator found")
                        self.human_behavior.random_delay(2, 4)
                        self.human_behavior.natural_page_navigation()
                        return True
                except TimeoutException:
                    continue
            current_url = self.driver.current_url
            if "login" not in current_url.lower() and "feed" in current_url.lower():
                logger.info("Login successful (URL based)")
                return True
            logger.error("No login success indicators found")
            return False
        except Exception as e:
            logger.error(f"Error waiting for login completion: {e}")
            return False

    # --------------------------------
    # :: Logout Method
    # --------------------------------

    """
    Logs out of the LinkedIn session. It first checks if the user is currently logged in. If so, it attempts to log out
    """

    def logout(self):
        try:
            if not self.is_logged_in:
                logger.info("Not logged in, skipping logout")
                return True
            logout_methods = [self._logout_via_url, self._logout_via_menu]
            for method in logout_methods:
                try:
                    if method():
                        self.is_logged_in = False
                        logger.info("Successfully logged out")
                        from database import db_manager

                        db_manager.log_activity(
                            "logout", "linkedin.com", {"success": True}
                        )
                        return True
                except Exception:
                    continue
            logger.error("All logout methods failed")
            return False
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False

    # --------------------------------
    # :: logout via URL Method
    # --------------------------------

    """
    Logs out of the LinkedIn session by navigating directly to the logout URL. 
    It checks if the logout was successful by looking for indicators of a logged-out state.
    """

    def _logout_via_url(self):
        try:
            self.driver.get("https://www.linkedin.com/logout")
            time.sleep(3)
            if "login" in self.driver.current_url.lower():
                return True
            return False
        except Exception:
            return False

    # --------------------------------
    # :: logout via Menu Method
    # --------------------------------

    """
    Logs out of the LinkedIn session by navigating through the user menu. It looks for common profile menu selectors,
    """

    def _logout_via_menu(self):
        try:
            profile_selectors = [
                "//button[contains(@class, 'global-nav__primary-link')]",
                "//div[contains(@class, 'profile-rail-card')]",
                "//img[contains(@alt, 'profile photo')]",
            ]
            for selector in profile_selectors:
                menu_button = self.driver.find_elements(By.XPATH, selector)
                if menu_button:
                    self.human_behavior.random_click_position(menu_button[0])
                    time.sleep(2)
                    logout_selectors = [
                        "//a[contains(@href, 'logout')]",
                        "//button[contains(text(), 'Sign out')]",
                        "//span[contains(text(), 'Sign out')]",
                    ]

                    for logout_selector in logout_selectors:
                        logout_button = self.driver.find_elements(
                            By.XPATH, logout_selector
                        )
                        if logout_button:
                            self.human_behavior.random_click_position(logout_button[0])
                            time.sleep(3)
                            return True
            return False
        except Exception:
            return False

    # --------------------------------
    # :: Verify Session Method
    # --------------------------------

    """
    Verifies if the current session is still valid by navigating to the LinkedIn feed page and checking for indicators of a logged-in state.
    """

    def verify_session(self):
        try:
            if not self.driver:
                return False
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            return self._check_login_status()
        except Exception as e:
            logger.error(f"Error verifying session: {e}")
            return False

    # --------------------------------
    # :: Refresh Session Method
    # --------------------------------

    """
    Refreshes the session by checking if the user is currently logged in and if the session is still valid. 
    If the session has expired, it attempts to log in again.
    """

    def refresh_session(self):
        try:
            if not self.is_logged_in:
                return self.login()
            if self.verify_session():
                logger.info("Session is still valid")
                return True
            else:
                logger.info("Session expired, attempting re-login")
                return self.login(force_new_session=True)
        except Exception as e:
            logger.error(f"Error refreshing session: {e}")
            return False

    # --------------------------------
    # :: Get Session Info Method
    # --------------------------------

    """
    Retrieves information about the current session, such as login status, profile name, current URL, and login attempts.
     This can be used for debugging and monitoring the bot's activity.
    """

    def get_session_info(self):
        try:
            if not self.is_logged_in or not self.driver:
                return {"logged_in": False}
            profile_info = {}
            try:
                name_element = self.driver.find_element(
                    By.XPATH, config.XPATHS["profile_name"]
                )
                profile_info["name"] = name_element.text.strip()
            except:
                profile_info["name"] = "Unknown"
            try:
                profile_info["current_url"] = self.driver.current_url
            except:
                profile_info["current_url"] = "Unknown"
            profile_info["logged_in"] = True
            profile_info["login_attempts"] = self.login_attempts
            profile_info["session_active"] = driver_manager.is_session_active()
            return profile_info
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return {"logged_in": False, "error": str(e)}


# --------------------------------------
# :: Initialize LinkedInAuth Instance
# --------------------------------------

"""
Initialize a global instance of LinkedInAuth that can be imported and used by other modules in the bot.
"""

linkedin_auth = LinkedInAuth()
