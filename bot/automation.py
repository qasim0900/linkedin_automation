"""
LinkedIn automation module.
Handles profile visits, connections, and messaging.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException

from config import config
from database import db_manager
from bot import driver_manager
from bot.auth import linkedin_auth
from utils import get_human_behavior

logger = logging.getLogger(__name__)

class LinkedInAutomation:
    """Handles LinkedIn profile automation with human-like behavior."""
    
    def __init__(self):
        self.driver = None
        self.human_behavior = None
        self.actions_completed = 0
        self.session_active = False
    
    def _initialize_session(self) -> bool:
        """Initialize driver and ensure logged in."""
        if not self.driver:
            self.driver = driver_manager.get_driver()
            self.human_behavior = get_human_behavior(self.driver)
        
        # Verify login status
        if not linkedin_auth.verify_session():
            logger.info("Session expired, attempting re-login")
            if not linkedin_auth.refresh_session():
                logger.error("Failed to establish session")
                return False
        
        self.session_active = True
        return True
    
    def visit_profiles(self, max_profiles: int = 20) -> int:
        """Visit LinkedIn profiles with human-like behavior."""
        if not self._initialize_session():
            return 0
        
        # Check rate limits
        rate_limits = db_manager.check_rate_limits()
        if rate_limits["visits_reached"]:
            logger.warning("Daily profile visit limit reached")
            return 0
        
        visited_count = 0
        
        try:
            profiles = list(db_manager.get_unprocessed_profiles(max_profiles))
            logger.info(f"Starting profile visits for {len(profiles)} profiles")
            
            for profile in profiles:
                if visited_count >= max_profiles:
                    break
                
                profile_url = profile.get("href")
                if not profile_url:
                    continue
                
                try:
                    if self._visit_profile(profile_url):
                        visited_count += 1
                        self.actions_completed += 1
                        
                        # Mark as visited
                        db_manager.mark_profile_processed(profile_url, "visited")
                        db_manager.log_activity("visit", profile_url)
                        
                        # Check for breaks
                        if self.human_behavior.should_take_break(self.actions_completed):
                            self.human_behavior.break_session()
                        
                        # Random delay between visits
                        self.human_behavior.random_delay(3, 8)
                
                except Exception as e:
                    logger.error(f"Error visiting profile {profile_url}: {e}")
                    continue
            
            logger.info(f"Profile visits completed: {visited_count}")
            return visited_count
            
        except Exception as e:
            logger.error(f"Error in visit_profiles: {e}")
            return 0
    
    def _visit_profile(self, profile_url: str) -> bool:
        """Visit a single profile with human-like behavior."""
        try:
            # Navigate to profile
            self.human_behavior.human_like_navigation(profile_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Check for CAPTCHA
            if self.human_behavior.check_for_captcha():
                logger.warning("CAPTCHA detected, skipping profile")
                return False
            
            # Simulate reading the profile
            self.human_behavior.profile_interaction_sequence()
            
            # Random scroll and interaction
            self.human_behavior.random_scroll("down", random.randint(200, 500))
            self.human_behavior.random_delay(2, 4)
            
            # Maybe scroll back up
            if random.random() < 0.6:
                self.human_behavior.random_scroll("up", random.randint(100, 300))
            
            logger.debug(f"Successfully visited profile: {profile_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error visiting profile {profile_url}: {e}")
            return False
    
    def send_connection_requests(self, max_requests: int = 15) -> int:
        """Send connection requests with human-like behavior."""
        if not self._initialize_session():
            return 0
        
        # Check rate limits
        rate_limits = db_manager.check_rate_limits()
        if rate_limits["connections_reached"]:
            logger.warning("Daily connection limit reached")
            return 0
        
        connections_sent = 0
        
        try:
            profiles = list(db_manager.get_unprocessed_profiles(max_requests))
            logger.info(f"Starting connection requests for {len(profiles)} profiles")
            
            for profile in profiles:
                if connections_sent >= max_requests:
                    break
                
                profile_url = profile.get("href")
                if not profile_url:
                    continue
                
                try:
                    result = self._send_connection_request(profile_url)
                    if result["success"]:
                        connections_sent += 1
                        self.actions_completed += 1
                        
                        # Mark as connected
                        db_manager.mark_profile_processed(profile_url, "connected")
                        db_manager.log_activity("connection", profile_url, result)
                        
                        # Check for breaks
                        if self.human_behavior.should_take_break(self.actions_completed):
                            self.human_behavior.break_session()
                        
                        # Random delay between requests
                        self.human_behavior.random_delay(5, 12)
                
                except Exception as e:
                    logger.error(f"Error sending connection request to {profile_url}: {e}")
                    continue
            
            logger.info(f"Connection requests completed: {connections_sent}")
            return connections_sent
            
        except Exception as e:
            logger.error(f"Error in send_connection_requests: {e}")
            return 0
    
    def _send_connection_request(self, profile_url: str) -> Dict[str, Any]:
        """Send a single connection request."""
        result = {"success": False, "method": "", "note_sent": False}
        
        try:
            # Navigate to profile
            self.human_behavior.human_like_navigation(profile_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Check for CAPTCHA
            if self.human_behavior.check_for_captcha():
                return {**result, "error": "CAPTCHA detected"}
            
            # Check weekly limit
            if self.human_behavior.handle_weekly_limit():
                return {**result, "error": "Weekly limit reached"}
            
            # Look for Connect button
            connect_button = self._find_connect_button()
            if not connect_button:
                return {**result, "error": "No connect button found"}
            
            # Click connect button
            self.human_behavior.scroll_to_element(connect_button)
            self.human_behavior.random_delay(1, 2)
            
            if self.human_behavior.safe_click(connect_button):
                result["method"] = "connect_button"
                
                # Handle connection dialog
                dialog_result = self._handle_connection_dialog()
                if dialog_result["success"]:
                    result.update(dialog_result)
                    logger.info(f"Connection request sent to {profile_url}")
                else:
                    result.update(dialog_result)
                
                return result
            else:
                return {**result, "error": "Failed to click connect button"}
        
        except Exception as e:
            logger.error(f"Error sending connection request to {profile_url}: {e}")
            return {**result, "error": str(e)}
    
    def _find_connect_button(self) -> Optional:
        """Find the Connect button on a profile."""
        connect_selectors = [
            config.XPATHS["connect_button"],
            "//button[contains(., 'Connect')]",
            "//button[contains(@aria-label, 'Connect')]",
            "//span[contains(text(), 'Connect')]/parent::button"
        ]
        
        for selector in connect_selectors:
            try:
                button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                if button and button.is_displayed():
                    return button
            except TimeoutException:
                continue
        
        return None
    
    def _handle_connection_dialog(self) -> Dict[str, Any]:
        """Handle the connection dialog that appears after clicking Connect."""
        result = {"success": False, "note_sent": False}
        
        try:
            # Wait for dialog to appear
            time.sleep(2)
            
            # Look for "Send without note" button
            send_without_note_button = self._find_send_without_note_button()
            
            if send_without_note_button:
                # Click send without note
                self.human_behavior.random_delay(1, 2)
                if self.human_behavior.safe_click(send_without_note_button):
                    result["success"] = True
                    result["note_sent"] = False
                    logger.debug("Connection request sent without note")
                    return result
            
            # If no "Send without note", look for regular send button
            send_button_selectors = [
                config.XPATHS["send_message_button"],
                "//button[contains(., 'Send')]",
                "//button[contains(@aria-label, 'Send')]"
            ]
            
            for selector in send_button_selectors:
                try:
                    send_button = self.driver.find_element(By.XPATH, selector)
                    if send_button and send_button.is_displayed():
                        self.human_behavior.random_delay(1, 2)
                        if self.human_behavior.safe_click(send_button):
                            result["success"] = True
                            result["note_sent"] = True
                            logger.debug("Connection request sent with note")
                            return result
                except:
                    continue
            
            # Try to close dialog if neither option works
            self._close_connection_dialog()
            
            return {**result, "error": "No send button found in dialog"}
        
        except Exception as e:
            logger.error(f"Error handling connection dialog: {e}")
            return {**result, "error": str(e)}
    
    def _find_send_without_note_button(self) -> Optional:
        """Find the 'Send without note' button."""
        selectors = [
            config.XPATHS["send_without_note"],
            "//button[contains(., 'Send without a note')]",
            "//button[contains(., 'Send without note')]",
            "//span[contains(text(), 'Send without note')]/parent::button"
        ]
        
        for selector in selectors:
            try:
                button = self.driver.find_element(By.XPATH, selector)
                if button and button.is_displayed():
                    return button
            except:
                continue
        
        return None
    
    def _close_connection_dialog(self) -> None:
        """Close the connection dialog."""
        try:
            close_selectors = [
                "//button[@aria-label='Dismiss']",
                "//button[contains(@class, 'close')]",
                "//button[contains(text(), 'Cancel')]",
                "//li-icon[@type='cancel-icon']"
            ]
            
            for selector in close_selectors:
                try:
                    close_button = self.driver.find_element(By.XPATH, selector)
                    if close_button and close_button.is_displayed():
                        self.human_behavior.safe_click(close_button)
                        time.sleep(1)
                        return
                except:
                    continue
        except:
            pass
    
    def send_messages(self, max_messages: int = 10) -> int:
        """Send messages to profiles with human-like behavior."""
        if not self._initialize_session():
            return 0
        
        # Check rate limits
        rate_limits = db_manager.check_rate_limits()
        if rate_limits["messages_reached"]:
            logger.warning("Daily message limit reached")
            return 0
        
        messages_sent = 0
        
        try:
            # Get profiles that are connected but not messaged
            query = {
                "connected": True,
                "$or": [
                    {"messaged": {"$exists": False}},
                    {"messaged": False}
                ]
            }
            
            profiles = list(db_manager.profiles_collection.find(query).limit(max_messages))
            logger.info(f"Starting messaging for {len(profiles)} profiles")
            
            for profile in profiles:
                if messages_sent >= max_messages:
                    break
                
                profile_url = profile.get("href")
                if not profile_url:
                    continue
                
                try:
                    result = self._send_message(profile_url, profile)
                    if result["success"]:
                        messages_sent += 1
                        self.actions_completed += 1
                        
                        # Mark as messaged
                        db_manager.mark_profile_processed(profile_url, "messaged")
                        db_manager.log_activity("message", profile_url, result)
                        
                        # Check for breaks
                        if self.human_behavior.should_take_break(self.actions_completed):
                            self.human_behavior.break_session()
                        
                        # Random delay between messages
                        self.human_behavior.random_delay(8, 15)
                
                except Exception as e:
                    logger.error(f"Error sending message to {profile_url}: {e}")
                    continue
            
            logger.info(f"Messages sent: {messages_sent}")
            return messages_sent
            
        except Exception as e:
            logger.error(f"Error in send_messages: {e}")
            return 0
    
    def _send_message(self, profile_url: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to a profile."""
        result = {"success": False, "message_type": "", "message_length": 0}
        
        try:
            # Navigate to profile
            self.human_behavior.human_like_navigation(profile_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Check for CAPTCHA
            if self.human_behavior.check_for_captcha():
                return {**result, "error": "CAPTCHA detected"}
            
            # Find and click Message button
            message_button = self._find_message_button()
            if not message_button:
                return {**result, "error": "No message button found"}
            
            # Click message button
            self.human_behavior.scroll_to_element(message_button)
            self.human_behavior.random_delay(1, 2)
            
            if not self.human_behavior.safe_click(message_button):
                return {**result, "error": "Failed to click message button"}
            
            # Handle message dialog
            dialog_result = self._handle_message_dialog(profile_data)
            result.update(dialog_result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error sending message to {profile_url}: {e}")
            return {**result, "error": str(e)}
    
    def _find_message_button(self) -> Optional:
        """Find the Message button on a profile."""
        message_selectors = [
            config.XPATHS["message_button"],
            "//button[contains(., 'Message')]",
            "//button[contains(@aria-label, 'Message')]",
            "//span[contains(text(), 'Message')]/parent::button"
        ]
        
        for selector in message_selectors:
            try:
                button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                if button and button.is_displayed():
                    return button
            except TimeoutException:
                continue
        
        return None
    
    def _handle_message_dialog(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the message dialog."""
        result = {"success": False, "message_type": "", "message_length": 0}
        
        try:
            # Wait for message dialog
            time.sleep(2)
            
            # Find message textbox
            textbox = self._find_message_textbox()
            if not textbox:
                return {**result, "error": "No message textbox found"}
            
            # Generate message
            if random.random() < 0.7:  # 70% chance for personalized message
                message = self.human_behavior.get_personalized_message(profile_data)
                result["message_type"] = "personalized"
            else:
                message = self.human_behavior.get_random_message()
                result["message_type"] = "template"
            
            # Type message with human-like behavior
            self.human_behavior.human_typing(textbox, message)
            result["message_length"] = len(message)
            
            # Send message
            send_result = self._send_message_in_dialog()
            result.update(send_result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error handling message dialog: {e}")
            return {**result, "error": str(e)}
    
    def _find_message_textbox(self) -> Optional:
        """Find the message textbox."""
        textbox_selectors = [
            config.XPATHS["message_textbox"],
            "//div[@contenteditable='true']",
            "//textarea[contains(@placeholder, 'message')]",
            "//div[contains(@class, 'msg-form__contenteditable')]"
        ]
        
        for selector in textbox_selectors:
            try:
                textbox = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                if textbox and textbox.is_displayed():
                    return textbox
            except TimeoutException:
                continue
        
        return None
    
    def _send_message_in_dialog(self) -> Dict[str, Any]:
        """Send the message in the dialog."""
        result = {"success": False}
        
        try:
            # Look for send button
            send_selectors = [
                config.XPATHS["send_message_button"],
                "//button[contains(., 'Send')]",
                "//button[contains(@aria-label, 'Send')]"
            ]
            
            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.XPATH, selector)
                    if send_button and send_button.is_displayed():
                        self.human_behavior.random_delay(1, 2)
                        if self.human_behavior.safe_click(send_button):
                            result["success"] = True
                            logger.debug("Message sent successfully")
                            return result
                except:
                    continue
            
            return {**result, "error": "No send button found"}
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {**result, "error": str(e)}
    
    def get_automation_stats(self) -> Dict[str, Any]:
        """Get automation statistics."""
        try:
            daily_stats = db_manager.get_daily_stats()
            rate_limits = db_manager.check_rate_limits()
            
            return {
                "daily_stats": daily_stats,
                "rate_limits": rate_limits,
                "session_active": self.session_active,
                "actions_completed": self.actions_completed
            }
        
        except Exception as e:
            logger.error(f"Error getting automation stats: {e}")
            return {}

# Global automation instance
linkedin_automation = LinkedInAutomation()
