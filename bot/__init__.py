import os
import pickle
import logging
from config import config
from typing import Optional
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: Driver Manager Class
# --------------------------------

""" 
DriverManager is responsible for managing the lifecycle of the Selenium WebDriver instance.
"""


class DriverManager:

    # --------------------------------
    # :: Init Method
    # --------------------------------

    """
    init method initializes the DriverManager instance. It sets up the driver variable and
    """

    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.session_active = False

    # --------------------------------
    # :: Create Driver Method
    # --------------------------------

    """ 
    create_driver method creates a new instance of the Chrome WebDriver with anti-detection measures.
    """

    def create_driver(self, headless=None):
        if self.driver:
            logger.warning("Driver already exists. Closing existing driver.")
            self.close_driver()
        headless = headless if headless is not None else config.HEADLESS_MODE
        try:
            options = uc.ChromeOptions()
            stealth_args = [
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

            for arg in stealth_args:
                options.add_argument(arg)
            options.add_argument(
                f"--window-size={config.WINDOW_SIZE[0]},{config.WINDOW_SIZE[1]}"
            )
            if headless:
                options.add_argument("--headless=new")
            else:
                options.add_argument("--start-maximized")
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            options.add_argument(f"--user-agent={user_agent}")
            options.add_experimental_option(
                "prefs",
                {
                    "credentials_enable_service": False,
                    "profile.password_manager_enabled": False,
                    "profile.default_content_setting_values.notifications": 2,
                    "profile.default_content_settings.popups": 0,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True,
                },
            )
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            self.driver = uc.Chrome(version_main=144, options=options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            self.driver.execute_cdp_cmd(
                "Network.setUserAgentOverride", {"userAgent": user_agent}
            )
            if not headless:
                self.driver.maximize_window()
            self.driver.set_page_load_timeout(30)
            self._load_cookies()
            self.session_active = True
            logger.info("Chrome driver created successfully with anti-detection")
            return self.driver
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise

    # --------------------------------
    # :: Load Cookies Method
    # --------------------------------

    """ 
    load_cookies method loads cookies from a file and adds them to the WebDriver instance.
    """

    def _load_cookies(self):
        try:
            if os.path.exists(config.COOKIE_FILE):
                with open(config.COOKIE_FILE, "rb") as file:
                    cookies = pickle.load(file)
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
                logger.info("Cookies loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load cookies: {e}")

    # --------------------------------
    # :: Save Cookies Method
    # --------------------------------

    """ 
    save_cookies method saves the current cookies from the WebDriver instance to a file.
    """

    def _save_cookies(self):
        try:
            os.makedirs(os.path.dirname(config.COOKIE_FILE), exist_ok=True)
            with open(config.COOKIE_FILE, "wb") as file:
                pickle.dump(self.driver.get_cookies(), file)
            logger.info("Cookies saved successfully")
        except Exception as e:
            logger.warning(f"Failed to save cookies: {e}")

    # --------------------------------
    # :: Get Driver Method
    # --------------------------------

    """ 
    get_driver method returns the current WebDriver instance. If there is no active driver, it creates a new one.
    """

    def get_driver(self):
        if not self.driver or not self.session_active:
            logger.info("No active driver found. Creating new driver.")
            return self.create_driver()
        return self.driver

    # --------------------------------
    # :: Close Driver Method
    # --------------------------------

    """ 
    close_driver method closes the WebDriver instance and saves cookies before quitting.
    """

    def close_driver(self):
        try:
            if self.driver:
                self._save_cookies()
                self.driver.quit()
                self.driver = None
                self.session_active = False
                logger.info("Driver closed successfully")
        except Exception as e:
            logger.error(f"Error closing driver: {e}")

    # --------------------------------
    # :: Restart Driver Method
    # --------------------------------

    """ 
    restart_driver method restarts the WebDriver instance by closing the existing driver and creating a new one.
    """

    def restart_driver(self):
        logger.info("Restarting driver...")
        self.close_driver()
        return self.create_driver()

    # --------------------------------
    # :: Is Session Active Method
    # --------------------------------

    """ 
    is_session_active method checks if the WebDriver session is still active by trying to access the current URL. 
    If it throws a WebDriverException, it means the session is not active.
    """

    def is_session_active(self):
        if not self.driver:
            return False
        try:
            self.driver.current_url
            return True
        except WebDriverException:
            return False

    # --------------------------------
    # :: Wait For Element Method
    # --------------------------------

    """ 
    wait_for_element method waits for an element to be present on the page using the specified locator and timeout.
    """

    def wait_for_element(self, locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            logger.warning(f"Element not found within {timeout} seconds: {locator}")
            return False

    # --------------------------------
    # :: Wait For Clickable Method
    # --------------------------------

    """ 
    wait_for_clickable method waits for an element to be clickable on the page using the specified locator and timeout.
    """

    def wait_for_clickable(self, locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return True
        except TimeoutException:
            logger.warning(f"Element not clickable within {timeout} seconds: {locator}")
            return False

    # --------------------------------
    # :: Safe Click Method
    # --------------------------------

    """ 
    safe_click method attempts to click an element using a normal click first. If that fails, 
    it falls back to using JavaScript to click the element.
    """

    def safe_click(self, element):
        try:
            if element.is_enabled() and element.is_displayed():
                element.click()
                return True
        except Exception as e:
            logger.warning(f"Normal click failed: {e}")
        try:
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            logger.error(f"JavaScript click failed: {e}")
            return False

    # --------------------------------
    # :: Scroll To Element Method
    # --------------------------------

    """ 
    scroll_to_element method scrolls the page to bring the specified element into view using JavaScript.
    """

    def scroll_to_element(self, element):
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                element,
            )
        except Exception as e:
            logger.warning(f"Failed to scroll to element: {e}")

    # ------------------------------------
    # :: Check Page Load Complete Method
    # ------------------------------------

    """ 
    check_page_load_complete method checks if the page has fully loaded by checking the document.readyState property.
    """

    def check_page_load_complete(self):
        try:
            return (
                self.driver.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            return False

    # --------------------------------
    # :: Get Element By XPath Method
    # --------------------------------

    """ 
    get_element_by_xpath method attempts to find an element using the specified XPath. 
    It first waits for the element to be present before trying to find it.
    """

    def get_element_by_xpath(self, xpath, timeout=10):
        try:
            locator = (By.XPATH, xpath)
            if self.wait_for_element(locator, timeout):
                return self.driver.find_element(By.XPATH, xpath)
        except Exception as e:
            logger.warning(f"Failed to find element by XPath '{xpath}': {e}")
        return None

    # --------------------------------
    # :: Get Elements By XPath Method
    # --------------------------------

    """ 
    get_elements_by_xpath method attempts to find multiple elements using the specified XPath.
    """

    def get_elements_by_xpath(self, xpath, timeout=10):
        try:
            locator = (By.XPATH, xpath)
            if self.wait_for_element(locator, timeout):
                return self.driver.find_elements(By.XPATH, xpath)
        except Exception as e:
            logger.warning(f"Failed to find elements by XPath '{xpath}': {e}")
        return []


# -----------------------------------
# :: Global Driver Manager Instance
# -----------------------------------

""" 
DriverManager is instantiated globally to be used across the bot module. 
This allows for centralized management of the WebDriver instance
"""

driver_manager = DriverManager()
