import time
import random
import logging
from config import config
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


class HumanBehavior:

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def __init__(self, driver):
        self.driver = driver
        self.actions = ActionChains(driver)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def random_delay(self, min_seconds, max_seconds):
        min_d = min_seconds if min_seconds is not None else config.MIN_DELAY_SECONDS
        max_d = max_seconds if max_seconds is not None else config.MAX_DELAY_SECONDS
        delay = random.uniform(min_d, max_d)
        logger.debug(f"Human delay: {delay:.2f}s")
        time.sleep(delay)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def reading_pause(self, word_count=50):
        reading_time = (word_count / 200) * 60
        jitter = random.uniform(0.8, 1.4)
        time.sleep(reading_time * jitter)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def thinking_pause(self) -> None:
        time.sleep(random.uniform(0.5, 2.5))

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def session_break(self):
        break_time = random.uniform(30, 120)
        logger.info(f"Taking a session break for {break_time:.0f}s")
        time.sleep(break_time)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def human_typing(self, element, text):
        if not element:
            return
        try:
            element.click()
            element.clear()
        except Exception:
            pass
        for char in text:
            delay = random.uniform(config.MIN_TYPING_DELAY, config.MAX_TYPING_DELAY)
            if random.random() < 0.03:
                wrong_char = random.choice("qwertyuiopasdfghjklzxcvbnm")
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.05, 0.15))
            element.send_keys(char)
            time.sleep(delay)
        self.random_delay(0.5, 1.5)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def random_scroll(self, direction="down", amount=None):
        if amount is None:
            amount = random.randint(200, 700)
        if direction == "down":
            self.driver.execute_script(f"window.scrollBy(0, {amount});")
        elif direction == "up":
            self.driver.execute_script(f"window.scrollBy(0, -{amount});")
        self.random_delay(0.4, 1.8)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def natural_page_scroll(self):
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        current_pos = 0
        while current_pos < total_height - viewport_height:
            scroll_amount = random.randint(150, 500)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            current_pos += scroll_amount
            self.random_delay(0.3, 1.5)
            if random.random() < 0.15:
                back = random.randint(50, 200)
                self.driver.execute_script(f"window.scrollBy(0, -{back});")
                current_pos -= back
                self.random_delay(0.3, 0.8)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def random_mouse_movement(self):
        try:
            width = self.driver.execute_script("return window.innerWidth")
            height = self.driver.execute_script("return window.innerHeight")
            x = random.randint(10, max(10, width - 10))
            y = random.randint(10, max(10, height - 10))
            body = self.driver.find_element(By.TAG_NAME, "body")
            ActionChains(self.driver).move_to_element_with_offset(body, x, y).perform()
            self.random_delay(0.1, 0.4)
        except Exception as e:
            logger.debug(f"Mouse movement skipped: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def hover_element(self, element):
        try:
            ActionChains(self.driver).move_to_element(element).perform()
            self.random_delay(0.4, 1.2)
        except Exception as e:
            logger.debug(f"Hover skipped: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def random_click_position(self, element):
        try:
            size = element.size
            x_off = random.randint(-size["width"] // 4, size["width"] // 4)
            y_off = random.randint(-size["height"] // 4, size["height"] // 4)
            ActionChains(self.driver).move_to_element_with_offset(
                element, x_off, y_off
            ).click().perform()
            self.random_delay(0.4, 1.5)
        except Exception as e:
            logger.debug(f"Offset click failed, falling back: {e}")
            try:
                element.click()
            except Exception:
                pass

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def human_like_navigation(self, url):
        self.random_delay(1.0, 3.0)
        try:
            self.driver.get(url)
        except WebDriverException as e:
            logger.error(f"Navigation error to {url}: {e}")
            return
        self.random_delay(1.5, 4.0)
        self.natural_page_scroll()

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def safe_click(self, element):
        try:
            self.hover_element(element)
            if element.is_enabled() and element.is_displayed():
                element.click()
                return True
        except Exception as e:
            logger.debug(f"Normal click failed: {e}")
        try:
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            logger.error(f"JS click also failed: {e}")
            return False

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def get_connection_message(self):
        messages = [
            "Hi! I came across your profile and was impressed by your work. I'd love to connect!",
            "Hello! Your background really caught my attention. Would be great to connect and share insights.",
            "Hi there! I think we share some interesting professional interests. Let's connect!",
            "Hello! I admire your work and would love to add you to my network.",
            "Hi! Your experience is really inspiring. Looking forward to staying connected.",
            "Good day! Your profile stood out to me. I'd love to connect with professionals like you.",
            "Hello! I believe we could benefit from connecting. Looking forward to future conversations.",
            "Hi! Came across your profile and thought it would be great to connect professionally.",
        ]
        return random.choice(messages)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def get_personalized_message(self, profile_data):
        name = profile_data.get("name", "there")
        company = profile_data.get("company", "your company")
        title = profile_data.get("title", "professional")
        industry = profile_data.get("industry", "your field")

        templates = [
            "Hello {name}! I noticed your work at {company} and was really impressed by your experience as {title}.",
            "Hi {name}! Your background in {industry} caught my attention, especially your time at {company}.",
            "Hello {name}! I came across your profile and was impressed by your journey as a {title}.",
        ]
        try:
            message = random.choice(templates).format(
                name=name, company=company, title=title, industry=industry
            )
        except KeyError:
            message = f"Hello {name}! I came across your profile and was impressed by your background."
        message += " Would love to connect and learn more about your work."
        return message

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def shuffle_actions(self, actions):
        shuffled = actions.copy()
        random.shuffle(shuffled)
        return shuffled

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def should_take_micro_break(self, action_count):
        return action_count > 0 and action_count % random.randint(5, 10) == 0

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def should_take_break(self, actions_completed):
        return self.should_take_micro_break(actions_completed)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def break_session(self, min_break=30, max_break=120):
        break_time = random.uniform(min_break, max_break)
        logger.info(f"Taking a session break for {break_time:.0f}s")
        time.sleep(break_time)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def scroll_to_element(self, element):
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});",
                element,
            )
        except Exception as exc:
            logger.debug(f"scroll_to_element failed: {exc}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def check_for_captcha(self):
        from bot.driver import check_captcha

        return check_captcha(self.driver)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def handle_weekly_limit(self):
        from bot.driver import check_weekly_limit

        return check_weekly_limit(self.driver)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def profile_interaction_sequence(self):
        self.random_scroll("down", random.randint(300, 600))
        self.random_delay(1.0, 3.0)
        if random.random() < 0.6:
            self.random_scroll("up", random.randint(100, 300))
            self.random_delay(0.5, 1.5)
        self.random_scroll("down", random.randint(200, 500))
        self.reading_pause(random.randint(30, 80))
        if random.random() < 0.3:
            self.random_mouse_movement()

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def natural_page_navigation(self):
        self.profile_interaction_sequence()

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def simulate_reading_time(self, min_seconds=3, max_seconds=8):
        total = random.randint(min_seconds, max_seconds)
        for _ in range(total):
            time.sleep(1)
            if random.random() < 0.1:
                self.random_scroll("down", random.randint(100, 300))
            elif random.random() < 0.05:
                self.random_mouse_movement()
