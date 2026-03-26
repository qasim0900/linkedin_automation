"""
LinkedIn authentication module.
Handles secure login and session management.
"""

import logging
import time
from typing import Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from config import config
from bot import driver_manager
from utils import get_human_behavior

logger = logging.getLogger(__name__)

class LinkedInAuth:
    """Handles LinkedIn authentication and session management."""
    
    def __init__(self):
        self.driver = None
        self.human_behavior = None
        self.is_logged_in = False
        self.login_attempts = 0
        self.max_login_attempts = 3
    
    def _initialize_driver(self) -> None:
        """Initialize WebDriver and human behavior."""
        if not self.driver:
            self.driver = driver_manager.get_driver()
            self.human_behavior = get_human_behavior(self.driver)
    
    def login(self, force_new_session: bool = False) -> bool:
        """Login to LinkedIn with human-like behavior."""
        self._initialize_driver()
        
        if force_new_session:
            self.driver = driver_manager.restart_driver()
            self.human_behavior = get_human_behavior(self.driver)
        
        # Check if already logged in
        if self._check_login_status() and not force_new_session:
            logger.info("Already logged in to LinkedIn")
            self.is_logged_in = True
            return True
        
        try:
            logger.info("Attempting to login to LinkedIn...")
            self.login_attempts += 1
            
            # Navigate to login page
            self.human_behavior.human_like_navigation(config.LINKEDIN_LOGIN_URL)
            
            # Wait for login form to load
            if not self._wait_for_login_form():
                logger.error("Login form not found")
                return False
            
            # Fill login credentials
            if not self._fill_credentials():
                logger.error("Failed to fill credentials")
                return False
            
            # Submit login
            if not self._submit_login():
                logger.error("Failed to submit login")
                return False
            
            # Wait for login completion
            if self._wait_for_login_completion():
                self.is_logged_in = True
                self.login_attempts = 0
                logger.info("Successfully logged in to LinkedIn")
                
                # Log activity
                from database import db_manager
                db_manager.log_activity("login", "linkedin.com", {"success": True})
                
                return True
            else:
                logger.error("Login completion failed")
                return False
        
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def _check_login_status(self) -> bool:
        """Check if already logged in to LinkedIn."""
        try:
            # Check for login indicators
            login_indicators = [
                "//div[contains(@class, 'global-nav__primary-link')]",
                "//img[contains(@alt, 'profile photo')]",
                "//div[contains(@class, 'feed-identity-module')]",
                "//a[contains(@href, '/feed')]"
            ]
            
            for indicator in login_indicators:
                if self.driver.find_elements(By.XPATH, indicator):
                    logger.debug("Login status indicator found")
                    return True
            
            # Try to navigate to feed and check
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Check if redirected to login page
            if "login" in self.driver.current_url.lower():
                return False
            
            # Check for feed elements
            feed_indicators = [
                "//div[contains(@class, 'feed-shared-update')]",
                "//div[contains(@class, 'feed-identity-module')]"
            ]
            
            for indicator in feed_indicators:
                if self.driver.find_elements(By.XPATH, indicator):
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking login status: {e}")
            return False
    
    def _wait_for_login_form(self) -> bool:
        """Wait for login form to be ready."""
        try:
            # Wait for email input
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
    
    def _fill_credentials(self) -> bool:
        """Fill email and password with human-like typing."""
        try:
            # Fill email
            email_input = self.driver.find_element(By.XPATH, config.XPATHS["email_input"])
            self.human_behavior.human_typing(email_input, config.LINKEDIN_EMAIL)
            
            self.human_behavior.random_delay(0.5, 1.5)
            
            # Fill password
            password_input = self.driver.find_element(By.XPATH, config.XPATHS["password_input"])
            self.human_behavior.human_typing(password_input, config.LINKEDIN_PASSWORD)
            
            self.human_behavior.random_delay(0.5, 1.5)
            
            logger.debug("Credentials filled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error filling credentials: {e}")
            return False
    
    def _submit_login(self) -> bool:
        """Submit the login form."""
        try:
            # Find and click login button
            login_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, config.XPATHS["login_button"]))
            )
            
            # Human-like click
            self.human_behavior.random_click_position(login_button)
            
            logger.debug("Login form submitted")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting login: {e}")
            return False
    
    def _wait_for_login_completion(self) -> bool:
        """Wait for login to complete and check for success."""
        try:
            # Wait for page to load after login
            time.sleep(3)
            
            # Check for login error indicators
            error_indicators = [
                "//div[contains(@class, 'alert-error')]",
                "//span[contains(text(), 'wrong')]",
                "//span[contains(text(), 'invalid')]",
                "//div[contains(text(), 'incorrect')]"
            ]
            
            for indicator in error_indicators:
                error_elements = self.driver.find_elements(By.XPATH, indicator)
                if error_elements:
                    error_text = error_elements[0].text.lower()
                    logger.error(f"Login error detected: {error_text}")
                    
                    # Log failed login attempt
                    from database import db_manager
                    db_manager.log_activity("login_failed", "linkedin.com", {
                        "error": error_text,
                        "attempt": self.login_attempts
                    })
                    
                    return False
            
            # Wait for successful login indicators
            success_indicators = [
                "//div[contains(@class, 'feed-identity-module')]",
                "//div[contains(@class, 'global-nav__primary-link')]",
                "//a[contains(@href, '/mynetwork')]",
                "//img[contains(@alt, 'profile photo')]"
            ]
            
            for indicator in success_indicators:
                try:
                    element = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, indicator))
                    )
                    if element and element.is_displayed():
                        logger.debug("Login success indicator found")
                        
                        # Additional human-like behavior after login
                        self.human_behavior.random_delay(2, 4)
                        self.human_behavior.natural_page_navigation()
                        
                        return True
                except TimeoutException:
                    continue
            
            # Check URL as fallback
            current_url = self.driver.current_url
            if "login" not in current_url.lower() and "feed" in current_url.lower():
                logger.info("Login successful (URL based)")
                return True
            
            logger.error("No login success indicators found")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for login completion: {e}")
            return False
    
    def logout(self) -> bool:
        """Logout from LinkedIn."""
        try:
            if not self.is_logged_in:
                logger.info("Not logged in, skipping logout")
                return True
            
            # Navigate to logout URL or use menu
            logout_methods = [
                self._logout_via_url,
                self._logout_via_menu
            ]
            
            for method in logout_methods:
                try:
                    if method():
                        self.is_logged_in = False
                        logger.info("Successfully logged out")
                        
                        # Log activity
                        from database import db_manager
                        db_manager.log_activity("logout", "linkedin.com", {"success": True})
                        
                        return True
                except Exception:
                    continue
            
            logger.error("All logout methods failed")
            return False
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    def _logout_via_url(self) -> bool:
        """Logout using direct URL."""
        try:
            self.driver.get("https://www.linkedin.com/logout")
            time.sleep(3)
            
            # Check if logged out
            if "login" in self.driver.current_url.lower():
                return True
            
            return False
            
        except Exception:
            return False
    
    def _logout_via_menu(self) -> bool:
        """Logout using navigation menu."""
        try:
            # Click profile menu
            profile_selectors = [
                "//button[contains(@class, 'global-nav__primary-link')]",
                "//div[contains(@class, 'profile-rail-card')]",
                "//img[contains(@alt, 'profile photo')]"
            ]
            
            for selector in profile_selectors:
                menu_button = self.driver.find_elements(By.XPATH, selector)
                if menu_button:
                    self.human_behavior.random_click_position(menu_button[0])
                    time.sleep(2)
                    
                    # Look for logout option
                    logout_selectors = [
                        "//a[contains(@href, 'logout')]",
                        "//button[contains(text(), 'Sign out')]",
                        "//span[contains(text(), 'Sign out')]"
                    ]
                    
                    for logout_selector in logout_selectors:
                        logout_button = self.driver.find_elements(By.XPATH, logout_selector)
                        if logout_button:
                            self.human_behavior.random_click_position(logout_button[0])
                            time.sleep(3)
                            return True
            
            return False
            
        except Exception:
            return False
    
    def verify_session(self) -> bool:
        """Verify that the current session is still valid."""
        try:
            if not self.driver:
                return False
            
            # Try to access feed
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Check if still logged in
            return self._check_login_status()
            
        except Exception as e:
            logger.error(f"Error verifying session: {e}")
            return False
    
    def refresh_session(self) -> bool:
        """Refresh the current session."""
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
    
    def get_session_info(self) -> dict:
        """Get information about the current session."""
        try:
            if not self.is_logged_in or not self.driver:
                return {"logged_in": False}
            
            # Try to get profile information
            profile_info = {}
            
            try:
                # Get profile name
                name_element = self.driver.find_element(By.XPATH, config.XPATHS["profile_name"])
                profile_info["name"] = name_element.text.strip()
            except:
                profile_info["name"] = "Unknown"
            
            try:
                # Get current URL
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

# Global auth instance
linkedin_auth = LinkedInAuth()
