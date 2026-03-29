import time
import logging
from config import config
from bot import driver_manager
from database import db_manager
from utils import get_human_behavior
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.parser import (
    parse_profile_card,
    parse_next_page_url,
)


logger = logging.getLogger(__name__)


class GoogleScraper:
    """Scrapes LinkedIn profile URLs from Google search results using Selenium."""

    def __init__(self):
        self.driver = None
        self.human_behavior = None

    def _initialize_driver(self):
        if not self.driver:
            self.driver = driver_manager.get_driver()
            self.human_behavior = get_human_behavior(self.driver)

    def scrape_profiles(self, location="USA", max_pages=10):
        """
        Scrape LinkedIn profiles for the given location.
        Uses the full pre-built Google URL from config when available,
        otherwise falls back to constructing a URL from the query constant.
        """
        self._initialize_driver()
        try:
            # Use the full pre-built URL from env (USA_GOOGLE / LAHORE_GOOGLE)
            search_url = config.get_google_search_url(location)
            logger.info(f"Starting Google scrape for {location}: {search_url[:80]}…")

            profiles_scraped = 0
            page_count = 0

            self.human_behavior.human_like_navigation(search_url)

            while page_count < max_pages:
                page_count += 1
                logger.info(f"Scraping page {page_count}")

                WebDriverWait(self.driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )

                page_profiles = list(self._extract_profiles_from_page())
                if page_profiles:
                    # Route profiles into the correct location-specific collection
                    new_count = db_manager.bulk_insert_profiles(
                        page_profiles, location=location
                    )
                    profiles_scraped += new_count
                    logger.info(
                        f"Page {page_count}: found {len(page_profiles)} profiles, "
                        f"{new_count} new"
                    )
                    self.human_behavior.random_delay(3, 6)
                else:
                    logger.info(f"No profiles found on page {page_count}")

                if not self._go_to_next_page():
                    logger.info("No more pages available")
                    break

                self.human_behavior.random_delay(2, 5)

            logger.info(
                f"Google scraping completed for {location}. "
                f"Total new profiles: {profiles_scraped}"
            )
            return profiles_scraped

        except Exception as e:
            logger.error(f"Error during Google scraping for {location}: {e}")
            return 0

    def _extract_profiles_from_page(self):
        """Extract LinkedIn profile data from the current Google results page."""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='g']|//div[@id='search']")
                )
            )
            result_cards = self.driver.find_elements(
                By.XPATH,
                "//div[@class='g']|//div[contains(@class,'MjjYud')]",
            )
            seen_hrefs = set()
            for card in result_cards:
                try:
                    profile_data = parse_profile_card(card)
                    href = profile_data.get("href")
                    if href and href not in seen_hrefs:
                        seen_hrefs.add(href)
                        yield {
                            **profile_data,
                            "source": "google_search",
                            "scraped_at": time.time(),
                        }
                except Exception as exc:
                    logger.debug(f"Error parsing card: {exc}")
                    continue
        except Exception as exc:
            logger.error(f"Error extracting profiles from page: {exc}")

    def _go_to_next_page(self):
        """Navigate to the next Google results page. Returns False when no next page exists."""
        try:
            next_url = parse_next_page_url(self.driver)
            if next_url:
                self.human_behavior.human_like_navigation(next_url)
                return True
            logger.info("No next page link found")
            return False
        except Exception as exc:
            logger.error(f"Error navigating to next page: {exc}")
            return False

    def scrape_specific_query(self, query, max_pages=5):
        """Scrape profiles using a custom search query string."""
        self._initialize_driver()
        try:
            search_url = f"{config.GOOGLE_SEARCH_URL}?q={query}"
            logger.info(f"Scraping custom query: {query}")

            profiles_scraped = 0
            page_count = 0

            self.human_behavior.human_like_navigation(search_url)

            while page_count < max_pages:
                page_count += 1
                page_profiles = list(self._extract_profiles_from_page())
                if page_profiles:
                    for profile in page_profiles:
                        profile["search_query"] = query
                        profile["custom_search"] = True
                    new_count = db_manager.bulk_insert_profiles(page_profiles)
                    profiles_scraped += new_count
                    logger.info(
                        f"Custom query page {page_count}: {new_count} new profiles"
                    )
                if not self._go_to_next_page():
                    break
                self.human_behavior.random_delay(2, 4)

            return profiles_scraped

        except Exception as e:
            logger.error(f"Error during custom query scraping: {e}")
            return 0

    def get_search_statistics(self):
        """Return scraping statistics from the database."""
        try:
            total_profiles = db_manager.profiles_collection.count_documents({})
            google_profiles = db_manager.profiles_collection.count_documents(
                {"source": "google_search"}
            )
            location_pipeline = [
                {"$match": {"source": "google_search"}},
                {"$group": {"_id": "$location", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
            location_stats = db_manager.profiles_collection.aggregate(location_pipeline)
            return {
                "total_profiles": total_profiles,
                "google_scraped": google_profiles,
                "by_location": {item["_id"]: item["count"] for item in location_stats},
            }
        except Exception as e:
            logger.error(f"Error getting search statistics: {e}")
            return {}

    def cleanup_old_profiles(self, days_old=30):
        """Remove unprocessed Google-scraped profiles older than `days_old` days."""
        try:
            from datetime import datetime, timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            result = db_manager.profiles_collection.delete_many(
                {
                    "source": "google_search",
                    "scraped_at": {"$lt": cutoff_date.timestamp()},
                    "processed": False,
                }
            )
            logger.info(f"Cleaned up {result.deleted_count} old profiles")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old profiles: {e}")
            return 0


google_scraper = GoogleScraper()
