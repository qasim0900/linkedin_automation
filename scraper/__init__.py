"""
Scraper module for LinkedIn automation system.
Contains Google scraper for finding LinkedIn profiles.
"""

import logging
import time
from typing import List, Dict, Any, Generator
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from config import config
from database import db_manager
from bot import driver_manager
from utils import get_human_behavior

logger = logging.getLogger(__name__)

class GoogleScraper:
    """Scrapes LinkedIn profiles from Google search results."""
    
    def __init__(self):
        self.driver = None
        self.human_behavior = None
    
    def _initialize_driver(self) -> None:
        """Initialize WebDriver and human behavior."""
        if not self.driver:
            self.driver = driver_manager.get_driver()
            self.human_behavior = get_human_behavior(self.driver)
    
    def scrape_profiles(self, location: str = "USA", max_pages: int = 10) -> int:
        """Scrape LinkedIn profiles from Google search results."""
        self._initialize_driver()
        
        try:
            search_query = config.get_google_search_query(location)
            search_url = f"{config.GOOGLE_SEARCH_URL}?q={search_query}"
            
            logger.info(f"Starting Google scrape for {location}: {search_query}")
            
            profiles_scraped = 0
            page_count = 0
            
            self.human_behavior.human_like_navigation(search_url)
            
            while page_count < max_pages:
                page_count += 1
                logger.info(f"Scraping page {page_count}")
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                
                # Extract profiles from current page
                page_profiles = list(self._extract_profiles_from_page())
                
                if page_profiles:
                    # Store profiles in database
                    new_count = db_manager.bulk_insert_profiles(page_profiles)
                    profiles_scraped += new_count
                    
                    logger.info(f"Page {page_count}: Found {len(page_profiles)} profiles, {new_count} new")
                    
                    # Human-like behavior between pages
                    self.human_behavior.random_delay(3, 6)
                else:
                    logger.info(f"No profiles found on page {page_count}")
                
                # Navigate to next page
                if not self._go_to_next_page():
                    logger.info("No more pages available")
                    break
                
                # Random delay between pages
                self.human_behavior.random_delay(2, 5)
            
            logger.info(f"Google scraping completed. Total new profiles: {profiles_scraped}")
            return profiles_scraped
            
        except Exception as e:
            logger.error(f"Error during Google scraping: {e}")
            return 0
    
    def _extract_profiles_from_page(self) -> Generator[Dict[str, Any], None, None]:
        """Extract LinkedIn profile URLs from current page."""
        try:
            # Wait for search results to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@class='g']"))
            )
            
            # Find all search result containers
            search_results = self.driver.find_elements(By.XPATH, "//div[@class='g']")
            
            for result in search_results:
                try:
                    # Look for LinkedIn links within this result
                    links = result.find_elements(By.XPATH, ".//a[contains(@href, 'linkedin.com/in')]")
                    
                    for link in links:
                        href = link.get_attribute("href")
                        if href and self._is_valid_linkedin_profile(href):
                            # Extract title text for additional context
                            title_text = ""
                            try:
                                title_element = result.find_element(By.XPATH, ".//h3")
                                title_text = title_element.text.strip()
                            except:
                                pass
                            
                            yield {
                                "href": href,
                                "title": title_text,
                                "source": "google_search",
                                "location": self._extract_location_from_context(result),
                                "scraped_at": time.time()
                            }
                            
                            # Limit to one profile per search result to avoid duplicates
                            break
                
                except Exception as e:
                    logger.debug(f"Error processing search result: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error extracting profiles from page: {e}")
    
    def _is_valid_linkedin_profile(self, url: str) -> bool:
        """Check if URL is a valid LinkedIn profile URL."""
        if not url:
            return False
        
        # Basic validation for LinkedIn profile URLs
        valid_patterns = [
            "linkedin.com/in/",
            "www.linkedin.com/in/",
            "https://linkedin.com/in/",
            "https://www.linkedin.com/in/"
        ]
        
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in valid_patterns)
    
    def _extract_location_from_context(self, result_element) -> str:
        """Extract location information from search result context."""
        try:
            # Look for location indicators in the search result
            location_indicators = [
                "USA", "United States", "Lahore", "Pakistan", "UK", "United Kingdom", 
                "Canada", "California", "New York", "Texas", "Florida"
            ]
            
            result_text = result_element.text.lower()
            
            for location in location_indicators:
                if location.lower() in result_text:
                    return location
            
            return "Unknown"
            
        except Exception:
            return "Unknown"
    
    def _go_to_next_page(self) -> bool:
        """Navigate to the next page of search results."""
        try:
            # Look for next page link
            next_selectors = [
                "//a[@id='pnnext']",
                "//a[contains(@aria-label, 'Next')]",
                "//a[contains(text(), 'Next')]",
                "//span[contains(text(), 'Next')]/parent::a"
            ]
            
            for selector in next_selectors:
                next_link = self.driver.find_elements(By.XPATH, selector)
                if next_link:
                    href = next_link[0].get_attribute("href")
                    if href:
                        # Human-like navigation to next page
                        self.human_behavior.human_like_navigation(href)
                        return True
            
            logger.info("No next page link found")
            return False
            
        except Exception as e:
            logger.error(f"Error navigating to next page: {e}")
            return False
    
    def scrape_specific_query(self, query: str, max_pages: int = 5) -> int:
        """Scrape profiles for a specific custom query."""
        self._initialize_driver()
        
        try:
            search_url = f"{config.GOOGLE_SEARCH_URL}?q={query}"
            
            logger.info(f"Scraping custom query: {query}")
            
            profiles_scraped = 0
            page_count = 0
            
            self.human_behavior.human_like_navigation(search_url)
            
            while page_count < max_pages:
                page_count += 1
                
                # Extract profiles
                page_profiles = list(self._extract_profiles_from_page())
                
                if page_profiles:
                    # Add custom query metadata
                    for profile in page_profiles:
                        profile["search_query"] = query
                        profile["custom_search"] = True
                    
                    new_count = db_manager.bulk_insert_profiles(page_profiles)
                    profiles_scraped += new_count
                    
                    logger.info(f"Custom query page {page_count}: {new_count} new profiles")
                
                # Navigate to next page
                if not self._go_to_next_page():
                    break
                
                self.human_behavior.random_delay(2, 4)
            
            return profiles_scraped
            
        except Exception as e:
            logger.error(f"Error during custom query scraping: {e}")
            return 0
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get statistics about scraped profiles."""
        try:
            total_profiles = db_manager.profiles_collection.count_documents({})
            google_profiles = db_manager.profiles_collection.count_documents({"source": "google_search"})
            
            # Get profiles by location
            location_pipeline = [
                {"$match": {"source": "google_search"}},
                {"$group": {"_id": "$location", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            location_stats = list(db_manager.profiles_collection.aggregate(location_pipeline))
            
            return {
                "total_profiles": total_profiles,
                "google_scraped": google_profiles,
                "by_location": {item["_id"]: item["count"] for item in location_stats}
            }
            
        except Exception as e:
            logger.error(f"Error getting search statistics: {e}")
            return {}
    
    def cleanup_old_profiles(self, days_old: int = 30) -> int:
        """Remove old profiles from database."""
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            result = db_manager.profiles_collection.delete_many({
                "source": "google_search",
                "scraped_at": {"$lt": cutoff_date.timestamp()},
                "processed": False
            })
            
            logger.info(f"Cleaned up {result.deleted_count} old profiles")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old profiles: {e}")
            return 0

# Global scraper instance
google_scraper = GoogleScraper()