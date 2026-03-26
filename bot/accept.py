import logging
from selenium.webdriver.common.by import By
from bot.driver import (
    find_elements,
    safe_click,
    scroll_to,
    check_captcha,
    dismiss_dialog,
)


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


INVITATIONS_URL = "https://www.linkedin.com/mynetwork/invitation-manager/"


# --------------------------------
# :: ConnectionAcceptor Class
# --------------------------------

""" 
ConnectionAcceptor is responsible for managing and accepting pending connection requests on LinkedIn.
"""


class ConnectionAcceptor:
    ACCEPT_BUTTON_XPATHS = [
        "//button[contains(@aria-label,'Accept')]",
        "//button[.//span[text()='Accept']]",
    ]
    INVITATION_CARD_XPATH = (
        "//li[contains(@class,'invitation-card')]"
        "|//li[contains(@class,'mn-invitation-list__item')]"
    )

    # --------------------------------
    # :: Init Method
    # --------------------------------

    """
    Initializes the ConnectionAcceptor with a Selenium WebDriver and a human behavior simulator.
    """

    def __init__(self, driver, human_behavior):
        self.driver = driver
        self.human = human_behavior

    # ------------------------------------
    # :: Accept Pending Requests Method
    # ------------------------------------

    """
    Accepts pending connection requests up to a specified maximum. Navigates to the invitation manager,
    """

    def accept_pending_requests(self, max_accepts=20):
        accepted = 0
        try:
            logger.info("Navigating to invitation manager…")
            self.human.human_like_navigation(INVITATIONS_URL)
            self.human.random_delay(2.0, 4.0)
            if check_captcha(self.driver):
                logger.warning("CAPTCHA on invitation page — skipping")
                return 0
            invitation_cards = find_elements(
                self.driver, self.INVITATION_CARD_XPATH, timeout=10
            )
            if not invitation_cards:
                logger.info("No pending connection requests found")
                return 0
            logger.info(f"Found {len(invitation_cards)} pending invitation(s)")
            for card in invitation_cards[:max_accepts]:
                if self._accept_card(card):
                    accepted += 1
                    self.human.random_delay(2.0, 5.0)
                    if accepted % 5 == 0:
                        self.human.thinking_pause()
        except Exception as exc:
            logger.error(f"Error processing pending requests: {exc}")
        logger.info(f"Accepted {accepted} connection request(s)")
        return accepted

    # ------------------------------------
    # :: Accept Card Method
    # ------------------------------------

    """
    Attempts to accept a connection request from a given invitation card element. It searches for the accept button
    """

    def _accept_card(self, card_element):
        for xpath in self.ACCEPT_BUTTON_XPATHS:
            try:
                btn = card_element.find_element(By.XPATH, f".{xpath}")
                if btn and btn.is_displayed():
                    scroll_to(self.driver, btn)
                    self.human.hover_element(btn)
                    self.human.random_delay(0.5, 1.5)
                    if safe_click(self.driver, btn):
                        self.human.random_delay(0.5, 1.0)
                        dismiss_dialog(self.driver)
                        logger.debug("Accepted one connection request")
                        return True
            except Exception:
                continue
        logger.debug("Accept button not found within card")
        return False
