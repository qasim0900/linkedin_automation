import re
import time
import random
import logging
from database import db_manager
from config.constants import GOOGLE_SEARCH_QUERIES

try:
    import requests
    from bs4 import BeautifulSoup

    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


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

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

_LINKEDIN_PROFILE_PATTERN = re.compile(
    r"https?://(?:www\.)?linkedin\.com/in/([a-zA-Z0-9\-_%]+)/?",
    re.IGNORECASE,
)

_GOOGLE_BASE = "https://www.google.com/search"


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def _random_headers():
    return {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def _random_delay(min_s=2.0, max_s=6.0):
    time.sleep(random.uniform(min_s, max_s))


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def _extract_urls_from_html(html):
    return list(dict.fromkeys(_LINKEDIN_PROFILE_PATTERN.findall(html) or []))


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def _build_profile_dict(username, source_query=""):
    url = f"https://www.linkedin.com/in/{username}"
    return {
        "href": url,
        "username": username,
        "name": "",
        "title": "",
        "company": "",
        "location": "",
        "source": "google_requests",
        "search_query": source_query,
        "processed": False,
        "connected": False,
        "messaged": False,
        "scraped_at": time.time(),
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


class LightweightGoogleScraper:

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def __init__(self, session=None):
        if not _REQUESTS_AVAILABLE:
            raise ImportError(
                "requests and beautifulsoup4 are required for LightweightGoogleScraper. "
                "Install them with: pip install requests beautifulsoup4"
            )
        self.session = session or requests.Session()
        self.session.headers.update(_random_headers())

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def scrape_by_location(self, location="USA", max_pages=5):
        query = GOOGLE_SEARCH_QUERIES.get(location, GOOGLE_SEARCH_QUERIES["USA"])
        return self._scrape_query(query, max_pages=max_pages, location=location)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def scrape_custom_query(self, query: str, max_pages: int = 3) -> int:
        return self._scrape_query(query, max_pages=max_pages)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def scrape_all_locations(self, max_pages_per_location=3):
        results = {}
        for location in GOOGLE_SEARCH_QUERIES:
            logger.info(f"Scraping location: {location}")
            count = self.scrape_by_location(location, max_pages=max_pages_per_location)
            results[location] = count
            _random_delay(10, 20)
        return results

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _scrape_query(self, query, max_pages=5, location=""):
        total_new = 0
        start = 0
        for page in range(max_pages):
            params = {
                "q": query,
                "start": start,
                "num": 10,
                "hl": "en",
                "gl": "us",
            }

            logger.info(f"[LightGoogleScraper] page {page + 1} — start={start}")
            html = self._fetch_page(_GOOGLE_BASE, params)
            if html is None:
                logger.warning("Failed to fetch page — stopping early")
                break
            if "unusual traffic" in html.lower() or "captcha" in html.lower():
                logger.warning("Google CAPTCHA detected — aborting lightweight scrape")
                break
            usernames = self._extract_linkedin_usernames(html)
            if not usernames:
                logger.info("No profiles found on this page — stopping")
                break
            profiles = [_build_profile_dict(u, source_query=query) for u in usernames]
            new_count = db_manager.bulk_insert_profiles(profiles)
            total_new += new_count
            logger.info(f"  Found {len(usernames)} urls, {new_count} new")
            start += 10
            _random_delay(3, 7)
        logger.info(f"[LightGoogleScraper] '{query}' done — {total_new} new profiles")
        return total_new

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _fetch_page(self, url, params):
        try:
            self.session.headers.update(_random_headers())
            response = self.session.get(
                url,
                params=params,
                timeout=15,
            )
            if response.status_code == 200:
                return response.text
            logger.warning(f"HTTP {response.status_code} for {url}")
        except Exception as exc:
            logger.error(f"Request error: {exc}")
        return None

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def _extract_linkedin_usernames(self, html):
        soup = BeautifulSoup(html, "html.parser")
        usernames = []
        seen: set = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith("/url?q="):
                href = href.split("q=")[-1].split("&")[0]
            match = _LINKEDIN_PROFILE_PATTERN.search(href)
            if match:
                username = match.group(1).rstrip("/")
                if username and username not in seen:
                    seen.add(username)
                    usernames.append(username)
        return usernames

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def get_scrape_stats(self):
        try:
            total = db_manager.profiles_collection.count_documents(
                {"source": "google_requests"}
            )
            return {"source": "google_requests", "total_scraped": total}
        except Exception as exc:
            logger.error(f"Stats error: {exc}")
            return {}


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


lightweight_google_scraper = None



# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

def get_lightweight_scraper():
    global lightweight_google_scraper
    if lightweight_google_scraper is None:
        lightweight_google_scraper = LightweightGoogleScraper()
    return lightweight_google_scraper
