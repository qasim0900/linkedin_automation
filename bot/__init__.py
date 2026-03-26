import logging
import pickle
import os
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException
import undetected_chromedriver as uc
from config import config

logger = logging.getLogger(__name__)

class DriverManager:
    """Manages Chrome WebDriver with anti-detection features."""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.session_active = False
    
    def create_driver(self, headless: bool = None) -> webdriver.Chrome:
        """Create and configure Chrome WebDriver with anti-detection."""
        if self.driver:
            logger.warning("Driver already exists. Closing existing driver.")
            self.close_driver()
        
        headless = headless if headless is not None else config.HEADLESS_MODE
        
        try:
            # Chrome options for anti-detection
            options = uc.ChromeOptions()
            
            # Stealth arguments
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
                "--disable-renderer-backgrounding"
            ]
            
            for arg in stealth_args:
                options.add_argument(arg)
            
            # Window size
            options.add_argument(f"--window-size={config.WINDOW_SIZE[0]},{config.WINDOW_SIZE[1]}")
            
            # Headless mode
            if headless:
                options.add_argument("--headless=new")
            else:
                options.add_argument("--start-maximized")
            
            # User agent
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            options.add_argument(f"--user-agent={user_agent}")
            
            # Experimental options
            options.add_experimental_option("prefs", {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            })
            
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Create undetected driver
            self.driver = uc.Chrome(version_main=144, options=options)
            
            # Anti-detection scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
            
            # Maximize window if not headless
            if not headless:
                self.driver.maximize_window()
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            # Load cookies if they exist
            self._load_cookies()
            
            self.session_active = True
            logger.info("Chrome driver created successfully with anti-detection")
            
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise
    
    def _load_cookies(self) -> None:
        """Load saved cookies for session persistence."""
        try:
            if os.path.exists(config.COOKIE_FILE):
                with open(config.COOKIE_FILE, 'rb') as file:
                    cookies = pickle.load(file)
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
                logger.info("Cookies loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load cookies: {e}")
    
    def _save_cookies(self) -> None:
        """Save current cookies for session persistence."""
        try:
            os.makedirs(os.path.dirname(config.COOKIE_FILE), exist_ok=True)
            with open(config.COOKIE_FILE, 'wb') as file:
                pickle.dump(self.driver.get_cookies(), file)
            logger.info("Cookies saved successfully")
        except Exception as e:
            logger.warning(f"Failed to save cookies: {e}")
    
    def get_driver(self) -> webdriver.Chrome:
        """Get the current driver instance."""
        if not self.driver or not self.session_active:
            logger.info("No active driver found. Creating new driver.")
            return self.create_driver()
        return self.driver
    
    def close_driver(self) -> None:
        """Close the driver and save cookies."""
        try:
            if self.driver:
                self._save_cookies()
                self.driver.quit()
                self.driver = None
                self.session_active = False
                logger.info("Driver closed successfully")
        except Exception as e:
            logger.error(f"Error closing driver: {e}")
    
    def restart_driver(self) -> webdriver.Chrome:
        """Restart the driver."""
        logger.info("Restarting driver...")
        self.close_driver()
        return self.create_driver()
    
    def is_session_active(self) -> bool:
        """Check if the driver session is active."""
        if not self.driver:
            return False
        
        try:
            self.driver.current_url
            return True
        except WebDriverException:
            return False
    
    def wait_for_element(self, locator: tuple, timeout: int = 10) -> bool:
        """Wait for element to be present and return True if found."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            logger.warning(f"Element not found within {timeout} seconds: {locator}")
            return False
    
    def wait_for_clickable(self, locator: tuple, timeout: int = 10) -> bool:
        """Wait for element to be clickable and return True if found."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return True
        except TimeoutException:
            logger.warning(f"Element not clickable within {timeout} seconds: {locator}")
            return False
    
    def safe_click(self, element) -> bool:
        """Safely click an element with JavaScript fallback."""
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
    
    def scroll_to_element(self, element) -> None:
        """Scroll element into view smoothly."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        except Exception as e:
            logger.warning(f"Failed to scroll to element: {e}")
    
    def check_page_load_complete(self) -> bool:
        """Check if page has finished loading."""
        try:
            return self.driver.execute_script("return document.readyState") == "complete"
        except Exception:
            return False
    
    def get_element_by_xpath(self, xpath: str, timeout: int = 10):
        """Get element by XPath with wait."""
        try:
            locator = (By.XPATH, xpath)
            if self.wait_for_element(locator, timeout):
                return self.driver.find_element(By.XPATH, xpath)
        except Exception as e:
            logger.warning(f"Failed to find element by XPath '{xpath}': {e}")
        return None
    
    def get_elements_by_xpath(self, xpath: str, timeout: int = 10):
        """Get multiple elements by XPath with wait."""
        try:
            locator = (By.XPATH, xpath)
            if self.wait_for_element(locator, timeout):
                return self.driver.find_elements(By.XPATH, xpath)
        except Exception as e:
            logger.warning(f"Failed to find elements by XPath '{xpath}': {e}")
        return []

# Global driver manager instance
driver_manager = DriverManager()