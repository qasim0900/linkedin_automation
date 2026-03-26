import logging
from config import config
from selenium.webdriver.common.by import By
from bot.driver import (
    wait_for_element,
    wait_for_clickable,
    safe_click,
    scroll_to,
    check_captcha,
)


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: MessageSender Class
# --------------------------------

""" 
MessageSender is a class responsible for sending messages to LinkedIn profiles. It uses Selenium WebDriver to interact
 with the LinkedIn web interface and a human behavior module to mimic natural user interactions. The class provides methods to check if messaging is available, open the message dialog, type the message, and send it. It also handles various edge cases and logs important events throughout the process.
"""


class MessageSender:
    MESSAGE_BUTTON_XPATHS = [
        "//button[contains(@aria-label,'Message')]",
        "//button[.//span[text()='Message']]",
        config.XPATHS.get("message_button", "//button[contains(., 'Message')]"),
    ]

    TEXTBOX_XPATHS = [
        "//div[@role='textbox']",
        "//div[@contenteditable='true']",
        "//div[contains(@class,'msg-form__contenteditable')]",
        config.XPATHS.get("message_textbox", "//div[@contenteditable='true']"),
    ]

    SEND_BUTTON_XPATHS = [
        "//button[contains(@class,'msg-form__send-button')]",
        "//button[contains(@aria-label,'Send')]",
        "//button[.//span[text()='Send']]",
        config.XPATHS.get("send_message_button", "//button[contains(., 'Send')]"),
    ]

    # --------------------------------
    # :: Init Method
    # --------------------------------

    """ 
    Initialize the MessageSender with the Selenium WebDriver and a human behavior module. The driver is used to interact with the web page,
    """

    def __init__(self, driver, human_behavior):
        self.driver = driver
        self.human = human_behavior

    # --------------------------------
    # :: Send Message Method
    # --------------------------------

    """ 
    send a message to a LinkedIn profile. This method takes the profile URL and the message text as input
    """

    def send_message(self, profile_url, message):
        result= {"success": False}
        if not message or not message.strip():
            return {**result, "error": "Empty message"}
        try:
            self.human.human_like_navigation(profile_url)
            self.human.random_delay(1.5, 3.0)
            if check_captcha(self.driver):
                return {**result, "error": "CAPTCHA detected"}
            if not self._is_message_available():
                return {
                    **result,
                    "error": "Not connected — cannot message this profile",
                }
            if not self._open_message_dialog():
                return {**result, "error": "Could not open message dialog"}
            self.human.random_delay(0.8, 2.0)
            if not self._type_message(message):
                return {**result, "error": "Could not type message"}
            self.human.random_delay(1.0, 2.5)
            if not self._send_message():
                return {**result, "error": "Could not click Send"}
            result["success"] = True
            logger.info(f"Message sent to {profile_url}")
            return result
        except Exception as exc:
            logger.error(f"Error messaging {profile_url}: {exc}")
            return {**result, "error": str(exc)}

    # --------------------------------
    # :: Is Message Available Method
    # --------------------------------

    """ 
    Check if the message button is available on the profile page. This method tries multiple XPaths to find the message button,
    which indicates that the user can be messaged. If any of the XPaths match, it returns True, otherwise it returns False.
    """

    def _is_message_available(self):
        for xpath in self.MESSAGE_BUTTON_XPATHS:
            if self.driver.find_elements(By.XPATH, xpath):
                return True
        return False

    # --------------------------------
    # :: Open Message Dialog Method
    # --------------------------------

    """ 
    Open the message dialog by clicking the message button. This method tries multiple XPaths to find the message button,
    """

    def _open_message_dialog(self):
        for xpath in self.MESSAGE_BUTTON_XPATHS:
            btn = wait_for_clickable(self.driver, xpath, timeout=5)
            if btn:
                scroll_to(self.driver, btn)
                self.human.hover_element(btn)
                self.human.random_delay(0.4, 1.0)
                if safe_click(self.driver, btn):
                    self.human.random_delay(0.8, 1.8)
                    return True
        logger.warning("Message button not found or not clickable")
        return False

    # --------------------------------
    # :: Type Message Method
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _type_message(self, message):
        for xpath in self.TEXTBOX_XPATHS:
            textbox = wait_for_element(self.driver, xpath, timeout=8)
            if textbox and textbox.is_displayed():
                textbox.click()
                self.human.random_delay(0.3, 0.8)
                self.human.human_typing(textbox, message)
                return True
        logger.warning("Message textbox not found")
        return False

    # --------------------------------
    # :: Save Message Method
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _send_message(self):
        for xpath in self.SEND_BUTTON_XPATHS:
            btn = wait_for_clickable(self.driver, xpath, timeout=5)
            if btn and btn.is_enabled():
                self.human.random_delay(0.5, 1.2)
                if safe_click(self.driver, btn):
                    self.human.random_delay(1.0, 2.0)
                    return True
        logger.warning("Send button not found")
        return False
