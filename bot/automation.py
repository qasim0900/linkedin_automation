import random
import logging
from bot import driver_manager
from database import db_manager
from bot.auth import linkedin_auth
from utils import get_human_behavior
from bot.message import MessageSender
from bot.accept import ConnectionAcceptor
from bot.connect import ConnectionManager
from selenium.webdriver.support.ui import WebDriverWait


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: LinkedInAutomation Class
# --------------------------------

""" 
LinkedInAutomation is the main class responsible for orchestrating the various automation tasks such as visiting profiles,
sending connection requests, messaging, and accepting connection requests. It manages the Selenium WebDriver session, interacts with the database 
for tracking activities and rate limits, and utilizes the human behavior simulator to mimic natural interactions on LinkedIn.
"""


class LinkedInAutomation:

    # --------------------------------
    # :: Init Method
    # --------------------------------

    """
    Initializes the LinkedInAutomation class with default values for the driver, human behavior simulator, login status,
    and counters for actions completed. This setup allows the class to manage its state and interactions effectively
    """

    def __init__(self):
        self.driver = None
        self.human_behavior = None
        self.actions_completed = 0
        self.session_active = False

    # --------------------------------
    # :: Initialize Session Method
    # --------------------------------

    """
    Initializes the Selenium WebDriver session and verifies the LinkedIn login status. If the session is not active or has expired, 
    it attempts to refresh the session by logging in again. This method ensures that the bot has a valid session before performing any automation tasks.
    """

    def _initialize_session(self):
        if not self.driver:
            self.driver = driver_manager.get_driver()
            self.human_behavior = get_human_behavior(self.driver)
        if not linkedin_auth.verify_session():
            logger.info("Session expired, attempting re-login")
            if not linkedin_auth.refresh_session():
                logger.error("Failed to establish session")
                return False
        self.session_active = True
        return True

    # --------------------------------
    # :: Visit Profiles Method
    # --------------------------------

    """
    Visits a list of LinkedIn profiles and performs actions on each one. It checks rate limits and logs activities.
    """

    def visit_profiles(self, max_profiles=20):
        if not self._initialize_session():
            return 0
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
                        db_manager.mark_profile_processed(profile_url, "visited")
                        db_manager.log_activity("visit", profile_url)
                        if self.human_behavior.should_take_break(
                            self.actions_completed
                        ):
                            self.human_behavior.break_session()
                        self.human_behavior.random_delay(3, 8)
                except Exception as e:
                    logger.error(f"Error visiting profile {profile_url}: {e}")
                    continue
            logger.info(f"Profile visits completed: {visited_count}")
            return visited_count
        except Exception as e:
            logger.error(f"Error in visit_profiles: {e}")
            return 0

    # --------------------------------
    # :: visit Profile Method
    # --------------------------------

    """
    Visits a single LinkedIn profile and performs interactions such as scrolling and hovering. It also checks for CAPTCHAs and handles them appropriately.
    """

    def _visit_profile(self, profile_url):
        try:
            self.human_behavior.human_like_navigation(profile_url)
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            if self.human_behavior.check_for_captcha():
                logger.warning("CAPTCHA detected, skipping profile")
                return False
            self.human_behavior.profile_interaction_sequence()
            self.human_behavior.random_scroll("down", random.randint(200, 500))
            self.human_behavior.random_delay(2, 4)
            if random.random() < 0.6:
                self.human_behavior.random_scroll("up", random.randint(100, 300))
            logger.debug(f"Successfully visited profile: {profile_url}")
            return True
        except Exception as e:
            logger.error(f"Error visiting profile {profile_url}: {e}")
            return False

    # --------------------------------------
    # :: Accept Connection Requests Method
    # --------------------------------------

    """
    Accepts pending connection requests up to a specified maximum. Navigates to the invitation manager, 
    checks for CAPTCHAs, and attempts to accept each pending request while mimicking human behavior.
    """

    def send_connection_requests(self, max_requests=15):
        if not self._initialize_session():
            return 0
        rate_limits = db_manager.check_rate_limits()
        if rate_limits["connections_reached"]:
            logger.warning("Daily connection limit reached")
            return 0
        manager = ConnectionManager(self.driver, self.human_behavior)
        connections_sent = 0
        try:
            profiles = list(db_manager.get_profiles_for_connection(max_requests))
            logger.info(f"Starting connection requests for {len(profiles)} profiles")
            for profile in profiles:
                if connections_sent >= max_requests:
                    break
                profile_url = profile.get("href")
                if not profile_url:
                    continue
                try:
                    result = manager.send_connection_request(profile_url)
                    if result.get("success") and result.get("action") not in (
                        "already_connected",
                        "pending",
                    ):
                        connections_sent += 1
                        self.actions_completed += 1
                        db_manager.mark_profile_processed(profile_url, "connected")
                        db_manager.log_activity("connection", profile_url, result)
                        if self.human_behavior.should_take_micro_break(
                            self.actions_completed
                        ):
                            self.human_behavior.session_break()
                        self.human_behavior.random_delay(5, 12)
                except Exception as exc:
                    logger.error(
                        f"Error sending connection request to {profile_url}: {exc}"
                    )
                    continue
            logger.info(f"Connection requests completed: {connections_sent}")
            return connections_sent
        except Exception as exc:
            logger.error(f"Error in send_connection_requests: {exc}")
            return 0

    # --------------------------------
    # :: Send Messages Method
    # --------------------------------

    """
    Sends personalized messages to a list of LinkedIn profiles. It checks rate limits, retrieves personalized messages, and logs activities.
    The method also handles exceptions and ensures that the bot mimics human behavior while sending messages.
    """

    def send_messages(self, max_messages=10):
        if not self._initialize_session():
            return 0
        rate_limits = db_manager.check_rate_limits()
        if rate_limits["messages_reached"]:
            logger.warning("Daily message limit reached")
            return 0
        sender = MessageSender(self.driver, self.human_behavior)
        messages_sent = 0
        try:
            profiles = list(db_manager.get_profiles_for_messaging(max_messages))
            logger.info(f"Starting messaging for {len(profiles)} profiles")
            for profile in profiles:
                if messages_sent >= max_messages:
                    break
                profile_url = profile.get("href")
                if not profile_url:
                    continue
                try:
                    message = self.human_behavior.get_personalized_message(profile)
                    result = sender.send_message(profile_url, message)
                    if result.get("success"):
                        messages_sent += 1
                        self.actions_completed += 1
                        db_manager.mark_profile_processed(profile_url, "messaged")
                        db_manager.log_activity("message", profile_url, result)
                        if self.human_behavior.should_take_micro_break(
                            self.actions_completed
                        ):
                            self.human_behavior.session_break()
                        self.human_behavior.random_delay(8, 15)
                except Exception as exc:
                    logger.error(f"Error messaging {profile_url}: {exc}")
                    continue
            logger.info(f"Messages sent: {messages_sent}")
            return messages_sent
        except Exception as exc:
            logger.error(f"Error in send_messages: {exc}")
            return 0

    # --------------------------------------
    # :: Accept Connection Requests Method
    # --------------------------------------

    """
    Accepts pending connection requests up to a specified maximum. Navigates to the invitation manager, 
    checks for CAPTCHAs, and attempts to accept each pending request while mimicking human behavior.
    """

    def accept_connection_requests(self, max_accepts=20):
        if not self._initialize_session():
            return 0
        acceptor = ConnectionAcceptor(self.driver, self.human_behavior)
        accepted = acceptor.accept_pending_requests(max_accepts)
        if accepted > 0:
            db_manager.log_activity(
                "accept_connections", "linkedin.com", {"count": accepted}
            )
        return accepted

    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def get_automation_stats(self):
        try:
            daily_stats = db_manager.get_daily_stats()
            rate_limits = db_manager.check_rate_limits()
            return {
                "daily_stats": daily_stats,
                "rate_limits": rate_limits,
                "session_active": self.session_active,
                "actions_completed": self.actions_completed,
            }
        except Exception as e:
            logger.error(f"Error getting automation stats: {e}")
            return {}


# --------------------------------------------
# :: Initialize LinkedInAutomation Instance
# --------------------------------------------

"""
Initialize a global instance of LinkedInAutomation that can be imported and used by other modules in the bot.
"""

linkedin_automation = LinkedInAutomation()
