import logging
from config import config
from selenium.webdriver.common.by import By
from bot.driver import (
    wait_for_element,
    wait_for_clickable,
    safe_click,
    scroll_to,
    check_weekly_limit,
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
# :: ConnectionManager Class
# --------------------------------

""" 
ConnectionManager is responsible for managing connection requests on LinkedIn, including sending connection requests,
following profiles, and checking connection status. It provides a high-level API for interacting with LinkedIn profiles and abstracts away the underlying Selenium interactions.
"""


class ConnectionManager:
    CONNECT_XPATHS = [
        "//button[contains(@aria-label,'Connect')]",
        "//button[.//span[text()='Connect']]",
        config.XPATHS.get("connect_button", "//button[contains(., 'Connect')]"),
    ]

    FOLLOW_XPATHS = [
        "//button[contains(@aria-label,'Follow')]",
        "//button[.//span[text()='Follow']]",
        config.XPATHS.get("follow_button", "//button[contains(., 'Follow')]"),
    ]

    SEND_WITHOUT_NOTE_XPATHS = [
        "//button[contains(@aria-label,'Send without a note')]",
        "//button[contains(text(),'Send without a note')]",
        config.XPATHS.get(
            "send_without_note", "//button[contains(., 'Send without a note')]"
        ),
    ]

    # --------------------------------
    # :: Init Method
    # --------------------------------

    """
    Initializes the LinkedInAuth class with default values for the driver, human behavior simulator, login status,
    """

    def __init__(self, driver, human_behavior):
        self.driver = driver
        self.human = human_behavior

    # -----------------------------------
    # :: Send Connection Request Method
    # -----------------------------------

    """
    Sends a connection request to a LinkedIn profile. It first checks the current connection state with the profile and 
    then attempts to click the appropriate button (Connect or Follow). It also handles adding a note to the connection request if specified.
    """

    def send_connection_request(self, profile_url, add_note=False, note=""):
        result = {"success": False, "action": None}
        try:
            self.human.human_like_navigation(profile_url)
            self.human.random_delay(1.5, 3.0)
            if check_captcha(self.driver):
                return {**result, "error": "CAPTCHA detected"}
            if check_weekly_limit(self.driver):
                return {**result, "error": "Weekly connection limit reached"}
            connection_state = self._get_connection_state()
            if connection_state == "connected":
                logger.info(f"Already connected with {profile_url}")
                return {"success": True, "action": "already_connected"}
            if connection_state == "pending":
                logger.info(f"Connection request already pending for {profile_url}")
                return {"success": True, "action": "pending"}
            if connection_state == "can_connect":
                success = self._click_connect(add_note=add_note, note=note)
                if success:
                    result["success"] = True
                    result["action"] = "connect"
                    logger.info(f"Connection request sent to {profile_url}")
                    return result
            if connection_state in ("can_follow", "unknown"):
                success = self._click_follow()
                if success:
                    result["success"] = True
                    result["action"] = "follow"
                    logger.info(f"Followed profile {profile_url}")
                    return result
            result["error"] = f"No actionable button found (state={connection_state})"
            return result
        except Exception as exc:
            logger.error(f"Error sending connection request to {profile_url}: {exc}")
            return {**result, "error": str(exc)}

    # --------------------------------
    # :: Is Connected Method
    # --------------------------------

    """
    Checks if the current profile is already connected by inspecting the profile page for indicators of a connected state.
     Returns True if connected, False otherwise.
    """

    def is_connected(self):
        return self._get_connection_state() == "connected"

    # --------------------------------
    # :: Get Connection State Method
    # --------------------------------

    """
    Inspects the profile page and returns the current connection state with that profile
    """

    def _get_connection_state(self):
        if self.driver.find_elements(
            By.XPATH, "//button[contains(@aria-label,'Message')]"
        ):
            return "connected"
        if self.driver.find_elements(
            By.XPATH,
            "//*[contains(@aria-label,'Pending')]|//*[contains(text(),'Pending')]",
        ):
            return "pending"
        for xpath in self.CONNECT_XPATHS:
            if self.driver.find_elements(By.XPATH, xpath):
                return "can_connect"
        for xpath in self.FOLLOW_XPATHS:
            if self.driver.find_elements(By.XPATH, xpath):
                return "can_follow"
        return "unknown"

    # --------------------------------
    # :: Click Connect Method
    # --------------------------------

    """
    Clicks the Connect button on a profile page. If add_note is True, it will attempt to add a personalized note before sending the connection request.
    Returns True if the connection request was sent successfully, False otherwise.
    """

    def _click_connect(self, add_note=False, note=""):
        for xpath in self.CONNECT_XPATHS:
            btn = wait_for_clickable(self.driver, xpath, timeout=5)
            if btn:
                scroll_to(self.driver, btn)
                self.human.hover_element(btn)
                self.human.random_delay(0.5, 1.5)
                if not safe_click(self.driver, btn):
                    continue
                self.human.random_delay(1.0, 2.5)
                if add_note and note:
                    return self._add_note_and_send(note)
                else:
                    return self._send_without_note()
        logger.warning("Connect button not found")
        return False

    # --------------------------------
    # :: Send Without Note Method
    # --------------------------------

    """
    sends the connection request without adding a note. It looks for the "Send without a note" button in the connection dialog and clicks it. If the button is not found, it assumes that LinkedIn may have auto-sent the request and returns True.
     Returns True if the request was sent successfully, False otherwise.
    """

    def _send_without_note(self):
        for xpath in self.SEND_WITHOUT_NOTE_XPATHS:
            btn = wait_for_clickable(self.driver, xpath, timeout=5)
            if btn:
                self.human.random_delay(0.5, 1.5)
                if safe_click(self.driver, btn):
                    self.human.random_delay(1.0, 2.0)
                    return True
        logger.debug("Send-without-note button not found; may have sent automatically")
        return True

    # --------------------------------
    # :: Add Note and Send Method
    # --------------------------------

    """
    Handles the process of adding a personalized note to the connection request and sending it. It clicks the "Add a note" button, types the note, and then clicks the "Send now" button. If any step fails, it falls back to sending without a note.
     Returns True if the request was sent successfully, False otherwise.
    """

    def _add_note_and_send(self, note):
        try:
            add_note_xpath = "//button[contains(@aria-label,'Add a note')]|//button[contains(text(),'Add a note')]"
            add_note_btn = wait_for_clickable(self.driver, add_note_xpath, timeout=5)
            if add_note_btn:
                safe_click(self.driver, add_note_btn)
                self.human.random_delay(0.5, 1.0)
            note_input = wait_for_element(
                self.driver,
                "//textarea[@name='message']|//textarea[contains(@placeholder,'note')]",
                timeout=5,
            )
            if note_input:
                self.human.human_typing(note_input, note)
            send_btn = wait_for_clickable(
                self.driver,
                "//button[contains(@aria-label,'Send now')]|//button[contains(text(),'Send now')]",
                timeout=5,
            )
            if send_btn:
                self.human.random_delay(0.5, 1.5)
                return safe_click(self.driver, send_btn)
            return self._send_without_note()
        except Exception as exc:
            logger.error(f"Error adding note: {exc}")
            return self._send_without_note()

    # --------------------------------
    # :: Click Follow Method
    # --------------------------------

    """
    Clicks the Follow button on a profile page as a fallback if the Connect button is not available.
    Returns True if the follow action was successful,False otherwise.
    """

    def _click_follow(self):
        for xpath in self.FOLLOW_XPATHS:
            btn = wait_for_clickable(self.driver, xpath, timeout=5)
            if btn:
                scroll_to(self.driver, btn)
                self.human.hover_element(btn)
                self.human.random_delay(0.5, 1.2)
                if safe_click(self.driver, btn):
                    self.human.random_delay(1.0, 2.0)
                    return True
        return False
