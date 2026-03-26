import logging
from config import config
from bot.driver import wait_for_element
from selenium.webdriver.common.by import By


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


class LinkedInProfileScraper:
    _NAME_XPATHS = [
        "//h1[@class='text-heading-xlarge']",
        "//h1[contains(@class,'top-card-layout__title')]",
        config.XPATHS.get("profile_name", "//h1[@class='text-heading-xlarge']"),
    ]
    _HEADLINE_XPATH = "//div[@class='text-body-medium break-words']|//h2[contains(@class,'top-card-layout__headline')]"
    _LOCATION_XPATH = "//span[@class='text-body-small inline t-black--light break-words']|//span[contains(@class,'top-card__subline-item')]"
    _EXPERIENCE_XPATH = (
        "//section[.//div[contains(@id,'experience')]]//span[@aria-hidden='true']"
    )
    _CONNECTIONS_XPATH = "//*[contains(@class,'t-bold')][contains(text(),'connection')]"

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def __init__(self, driver, human_behavior):
        self.driver = driver
        self.human = human_behavior

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def scrape_profile(self, profile_url):
        profile = {
            "href": profile_url,
            "name": "",
            "headline": "",
            "title": "",
            "company": "",
            "location": "",
            "connections": None,
            "scraped": True,
        }
        try:
            self.human.human_like_navigation(profile_url)
            self.human.random_delay(2.0, 4.0)
            self.human.natural_page_scroll()
            profile["name"] = self._extract_name()
            profile["headline"] = self._extract_headline()
            profile["location"] = self._extract_location()
            profile["title"], profile["company"] = self._extract_experience()
            profile["connections"] = self._extract_connections()
            logger.info(f"Scraped profile: {profile['name']} ({profile_url})")
        except Exception as exc:
            logger.error(f"Error scraping profile {profile_url}: {exc}")
        return profile

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def scrape_profiles_batch(self, profile_urls):
        for url in profile_urls:
            try:
                data = self.scrape_profile(url)
                yield data
                self.human.random_delay(3.0, 7.0)
            except Exception as exc:
                logger.error(f"Batch scrape error for {url}: {exc}")
                continue

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _extract_name(self):
        for xpath in self._NAME_XPATHS:
            el = wait_for_element(self.driver, xpath, timeout=5)
            if el and el.text.strip():
                return el.text.strip()
        return ""

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _extract_headline(self):
        els = self.driver.find_elements(By.XPATH, self._HEADLINE_XPATH)
        return els[0].text.strip() if els else ""

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _extract_location(self):
        els = self.driver.find_elements(By.XPATH, self._LOCATION_XPATH)
        for el in els:
            text = el.text.strip()
            if text and "connection" not in text.lower():
                return text
        return ""

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _extract_experience(self):
        try:
            spans = self.driver.find_elements(By.XPATH, self._EXPERIENCE_XPATH)
            texts = [s.text.strip() for s in spans if s.text.strip()]
            if len(texts) >= 2:
                return texts[0], texts[1]
            elif texts:
                return texts[0], ""
        except Exception:
            pass
        return "", ""

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _extract_connections(self):
        try:
            els = self.driver.find_elements(By.XPATH, self._CONNECTIONS_XPATH)
            for el in els:
                text = el.text.strip().replace(",", "").replace("+", "")
                digits = "".join(c for c in text if c.isdigit())
                if digits:
                    return int(digits)
        except Exception:
            pass
        return None


_scraper_instance = None


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def get_profile_scraper(driver, human_behavior):
    global _scraper_instance
    if _scraper_instance is None or _scraper_instance.driver is not driver:
        _scraper_instance = LinkedInProfileScraper(driver, human_behavior)
    return _scraper_instance
