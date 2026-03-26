"""
Utilities module for LinkedIn automation system.
Contains human behavior simulation and helper functions.
"""

import random
import time
import logging
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from config import config

logger = logging.getLogger(__name__)

class HumanBehavior:
    """Simulates human-like behavior for LinkedIn automation."""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.action_chains = ActionChains(driver)
    
    def random_delay(self, min_seconds: float = None, max_seconds: float = None) -> None:
        """Add random delay between actions."""
        min_delay = min_seconds if min_seconds is not None else config.MIN_DELAY_SECONDS
        max_delay = max_seconds if max_seconds is not None else config.MAX_DELAY_SECONDS
        
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Random delay: {delay:.2f} seconds")
        time.sleep(delay)
    
    def human_typing(self, element, text: str) -> None:
        """Type text like a human with random delays between characters."""
        if not element:
            return
        
        element.click()
        element.clear()
        
        for char in text:
            delay = random.uniform(config.MIN_TYPING_DELAY, config.MAX_TYPING_DELAY)
            element.send_keys(char)
            time.sleep(delay)
        
        # Random pause after typing
        self.random_delay(0.5, 1.5)
    
    def random_scroll(self, direction: str = "down", amount: int = None) -> None:
        """Scroll randomly like a human would."""
        if amount is None:
            amount = random.randint(200, 800)
        
        if direction == "down":
            self.driver.execute_script(f"window.scrollBy(0, {amount});")
        elif direction == "up":
            self.driver.execute_script(f"window.scrollBy(0, -{amount});")
        
        self.random_delay(0.5, 2.0)
    
    def random_mouse_movement(self) -> None:
        """Move mouse randomly to simulate human behavior."""
        try:
            width = self.driver.execute_script("return window.innerWidth")
            height = self.driver.execute_script("return window.innerHeight")
            
            # Random coordinates
            x = random.randint(0, width)
            y = random.randint(0, height)
            
            self.action_chains.move_by_offset(x, y).perform()
            self.random_delay(0.1, 0.5)
            
        except Exception as e:
            logger.warning(f"Failed to move mouse: {e}")
    
    def hover_element(self, element) -> None:
        """Hover over an element like a human would."""
        try:
            self.action_chains.move_to_element(element).perform()
            self.random_delay(0.5, 1.5)
        except Exception as e:
            logger.warning(f"Failed to hover element: {e}")
    
    def random_click_position(self, element) -> None:
        """Click on random position within element."""
        try:
            # Get element size and position
            size = element.size
            location = element.location
            
            # Random offset within element
            x_offset = random.randint(-size['width']//4, size['width']//4)
            y_offset = random.randint(-size['height']//4, size['height']//4)
            
            self.action_chains.move_to_element_with_offset(element, x_offset, y_offset).click().perform()
            self.random_delay(0.5, 2.0)
            
        except Exception as e:
            logger.warning(f"Failed to click random position: {e}")
            # Fallback to normal click
            element.click()
    
    def natural_page_navigation(self) -> None:
        """Simulate natural page navigation behavior."""
        # Random scroll
        if random.random() < 0.7:  # 70% chance to scroll
            self.random_scroll()
        
        # Random mouse movement
        if random.random() < 0.3:  # 30% chance to move mouse
            self.random_mouse_movement()
        
        # Small delay
        self.random_delay(1.0, 3.0)
    
    def break_session(self, min_break: int = 30, max_break: int = 180) -> None:
        """Take a break to simulate human work patterns."""
        break_duration = random.randint(min_break, max_break)
        logger.info(f"Taking a break for {break_duration} seconds")
        time.sleep(break_duration)
    
    def check_for_captcha(self) -> bool:
        """Check if CAPTCHA is present on the page."""
        captcha_indicators = [
            "//div[contains(@class, 'captcha')]",
            "//iframe[contains(@src, 'recaptcha')]",
            "//div[contains(text(), 'CAPTCHA')]",
            "//div[contains(text(), 'verify')]"
        ]
        
        for xpath in captcha_indicators:
            if self.driver.find_elements(By.XPATH, xpath):
                logger.warning("CAPTCHA detected!")
                return True
        
        return False
    
    def handle_weekly_limit(self) -> bool:
        """Handle LinkedIn weekly connection limit."""
        limit_indicators = [
            "//h2[contains(text(), 'weekly limit')]",
            "//div[contains(text(), 'reached your weekly limit')]",
            "//span[contains(text(), 'weekly connection limit')]"
        ]
        
        for xpath in limit_indicators:
            elements = self.driver.find_elements(By.XPATH, xpath)
            if elements:
                logger.error("LinkedIn weekly limit reached!")
                # Try to dismiss the dialog
                dismiss_buttons = [
                    "//button[@aria-label='Dismiss']",
                    "//button[contains(text(), 'Close')]",
                    "//button[contains(text(), 'Got it')]"
                ]
                
                for btn_xpath in dismiss_buttons:
                    button = self.driver.find_elements(By.XPATH, btn_xpath)
                    if button:
                        button[0].click()
                        logger.info("Dismissed weekly limit dialog")
                        return True
                
                return True
        
        return False
    
    def simulate_reading_time(self, min_seconds: int = 3, max_seconds: int = 8) -> None:
        """Simulate time spent reading a profile."""
        reading_time = random.randint(min_seconds, max_seconds)
        logger.debug(f"Simulating reading for {reading_time} seconds")
        
        # During reading, occasionally scroll or move mouse
        for _ in range(reading_time):
            time.sleep(1)
            if random.random() < 0.1:  # 10% chance per second
                self.random_scroll("down", random.randint(100, 300))
            elif random.random() < 0.05:  # 5% chance per second
                self.random_mouse_movement()
    
    def random_tab_switch(self) -> None:
        """Randomly switch to a different tab and back."""
        if random.random() < 0.1:  # 10% chance
            try:
                # Open new tab
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[1])
                
                # Spend some time in new tab
                time.sleep(random.uniform(1, 3))
                
                # Switch back
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                
                logger.debug("Random tab switch completed")
                
            except Exception as e:
                logger.warning(f"Failed to switch tabs: {e}")
    
    def human_like_navigation(self, target_url: str) -> None:
        """Navigate to URL with human-like behavior."""
        try:
            # Sometimes type URL directly, sometimes click
            if random.random() < 0.3:  # 30% chance to type URL
                self.driver.get("about:blank")
                time.sleep(0.5)
                
                # Type URL in address bar
                address_bar = self.driver.switch_to.active_element
                self.human_typing(address_bar, target_url)
                address_bar.send_keys(Keys.RETURN)
            else:
                # Direct navigation
                self.driver.get(target_url)
            
            # Wait for page load with natural behavior
            self.random_delay(2, 4)
            
            # Natural page interaction
            self.natural_page_navigation()
            
        except Exception as e:
            logger.error(f"Failed human-like navigation: {e}")
            # Fallback to direct navigation
            self.driver.get(target_url)
    
    def profile_interaction_sequence(self) -> None:
        """Execute a realistic profile interaction sequence."""
        # 1. Initial scroll down to see more content
        self.random_scroll("down", random.randint(300, 600))
        self.random_delay(1, 3)
        
        # 2. Scroll up a bit
        if random.random() < 0.6:  # 60% chance
            self.random_scroll("up", random.randint(100, 300))
            self.random_delay(0.5, 2)
        
        # 3. Scroll down again
        self.random_scroll("down", random.randint(200, 500))
        
        # 4. Simulate reading
        self.simulate_reading_time()
        
        # 5. Maybe hover over some elements
        if random.random() < 0.4:  # 40% chance
            interactive_elements = self.driver.find_elements(By.XPATH, "//button | //a")
            if interactive_elements:
                random_element = random.choice(interactive_elements[:5])  # First 5 elements
                self.hover_element(random_element)
    
    def should_take_break(self, actions_completed: int) -> bool:
        """Determine if it's time to take a break based on actions completed."""
        # Take breaks after certain number of actions
        break_points = [10, 20, 35, 50]
        
        for break_point in break_points:
            if actions_completed == break_point:
                return True
        
        return False
    
    def get_random_message(self) -> str:
        """Get a random personalized message template."""
        messages = [
            "Hello! I came across your profile and was impressed by your background. Would love to connect and learn more about your work.",
            "Hi there! I see we share similar interests in the industry. I'd be great to connect and potentially collaborate in the future.",
            "Good day! Your experience really stood out to me. I'm always looking to connect with talented professionals like yourself.",
            "Hello! I've been following your work and I'm very impressed. Would be great to connect and share insights.",
            "Hi! I believe we could have some interesting conversations given our backgrounds. Looking forward to connecting!",
            "Hello! Your professional journey is inspiring. I'd love to connect and learn from your experiences.",
            "Hi there! I think we could benefit from being connected. Looking forward to potential future collaborations.",
            "Hello! Came across your profile and was really impressed. Would be great to connect and stay in touch.",
            "Hi! I admire your work in the field. I'd love to connect and potentially share ideas.",
            "Hello! Your profile caught my attention. I believe we could have valuable professional discussions."
        ]
        
        return random.choice(messages)
    
    def get_personalized_message(self, profile_data: dict) -> str:
        """Generate a personalized message based on profile data."""
        base_messages = [
            "Hello {name}! I noticed your work at {company} and was really impressed by your experience as {title}.",
            "Hi {name}! Your background in {industry} caught my attention, especially your work at {company}.",
            "Hello {name}! I came across your profile and was impressed by your journey as a {title}."
        ]
        
        # Extract available information
        name = profile_data.get("name", "there")
        company = profile_data.get("company", "your company")
        title = profile_data.get("title", "professional")
        industry = profile_data.get("industry", "your field")
        
        # Select random base message
        message = random.choice(base_messages)
        
        # Format with available data
        try:
            message = message.format(
                name=name,
                company=company,
                title=title,
                industry=industry
            )
        except KeyError:
            # Fallback if formatting fails
            message = f"Hello {name}! I came across your profile and was impressed by your background."
        
        # Add closing
        message += " Would love to connect and learn more about your work."
        
        return message

# Global human behavior instance
def get_human_behavior(driver: webdriver.Chrome) -> HumanBehavior:
    """Get a human behavior instance for the given driver."""
    return HumanBehavior(driver)