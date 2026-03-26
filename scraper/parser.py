import re
import logging
from selenium.webdriver.common.by import By


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)

_LI_PROFILE_RE = re.compile(r"https?://(?:www\.)?linkedin\.com/in/[^/?#&\s\"'>]+")


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def extract_linkedin_urls_from_text(text):
    raw = _LI_PROFILE_RE.findall(text)
    seen = set()
    result = []
    for url in raw:
        clean = _normalise(url)
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def extract_linkedin_urls_from_elements(elements):
    seen = set()
    result = []
    for el in elements:
        try:
            href = el.get_attribute("href") or ""
            if "linkedin.com/in/" in href:
                clean = _normalise(href)
                if clean and clean not in seen:
                    seen.add(clean)
                    result.append(clean)
        except Exception:
            continue
    return result


def parse_profile_card(card_element):
    data = {
        "href": None,
        "name": "",
        "title": "",
        "company": "",
        "location": "",
        "snippet": "",
    }
    try:
        links = card_element.find_elements(
            By.XPATH, ".//a[contains(@href,'linkedin.com/in')]"
        )
        if not links:
            return data
        href = _normalise(links[0].get_attribute("href") or "")
        if not href:
            return data
        data["href"] = href
        snippets = card_element.find_elements(
            By.XPATH, ".//div[@data-sncf]|.//div[@class='VwiC3b']|.//span[@class='st']"
        )
        snippet_text = " ".join(el.text for el in snippets if el.text).strip()
        data["snippet"] = snippet_text
        headings = card_element.find_elements(By.XPATH, ".//h3|.//h2")
        if headings:
            data["name"] = headings[0].text.strip().split(" - ")[0].strip()
    except Exception as exc:
        logger.debug(f"Error parsing profile card: {exc}")
    return data


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def parse_next_page_url(driver):
    selectors = [
        "//a[@id='pnnext']",
        "//a[contains(@aria-label,'Next')]",
        "//td[@class='b navend']/a",
    ]
    for xpath in selectors:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            if elements:
                href = elements[0].get_attribute("href")
                if href:
                    return href
        except Exception:
            continue
    return None


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def _normalise(url):
    if not url:
        return None
    url = re.sub(r"[?#].*$", "", url).rstrip("/")
    if "linkedin.com/in/" not in url:
        return None
    if not url.startswith("http"):
        url = "https://" + url
    return url
