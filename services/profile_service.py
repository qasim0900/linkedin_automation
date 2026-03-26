import re
import logging
from database import db_manager
from datetime import datetime, timedelta


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

_RELEVANT_TITLES = [
    "software engineer",
    "developer",
    "programmer",
    "architect",
    "data scientist",
    "machine learning",
    "devops",
    "cloud engineer",
    "full stack",
    "backend",
    "frontend",
    "product manager",
    "cto",
    "vp engineering",
    "technical lead",
    "engineering manager",
]

_RELEVANT_INDUSTRIES = [
    "technology",
    "software",
    "saas",
    "fintech",
    "health tech",
    "edtech",
    "ai",
    "cybersecurity",
    "cloud",
    "consulting",
]

_SPAM_INDICATORS = [
    "earn money",
    "make $",
    "work from home",
    "mlm",
    "passive income",
    "forex",
    "crypto trading",
    "investment opportunity",
]


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


class ProfileService:

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def filter_by_keywords(
        self,
        profiles,
        keywords,
        fields,
    ):
        if fields is None:
            fields = ["title", "headline", "company"]
        keywords_lower = [kw.lower() for kw in keywords]
        result = []
        for profile in profiles:
            text = " ".join(str(profile.get(f, "")) for f in fields).lower()
            if any(kw in text for kw in keywords_lower):
                result.append(profile)
        return result

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def filter_by_location(self, profiles, location):
        pattern = re.compile(re.escape(location), re.IGNORECASE)
        return [p for p in profiles if pattern.search(p.get("location", ""))]

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def filter_unprocessed(self, profiles):
        return [
            p
            for p in profiles
            if not p.get("processed")
            and not p.get("connected")
            and not p.get("messaged")
        ]

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def remove_spam_profiles(self, profiles):
        clean = []
        for profile in profiles:
            text = (
                profile.get("title", "") + " " + profile.get("headline", "")
            ).lower()
            if not any(spam in text for spam in _SPAM_INDICATORS):
                clean.append(profile)
        return clean

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def score_profile(self, profile):
        score = 0.0
        title_text = (
            profile.get("title", "") + " " + profile.get("headline", "")
        ).lower()
        matched_titles = sum(1 for t in _RELEVANT_TITLES if t in title_text)
        score += min(matched_titles * 0.15, 0.45)
        company_text = profile.get("company", "").lower()
        matched_industries = sum(1 for i in _RELEVANT_INDUSTRIES if i in company_text)
        score += min(matched_industries * 0.1, 0.3)
        completeness = sum(
            bool(profile.get(f)) for f in ("name", "title", "location", "company")
        )
        score += completeness * 0.05
        href = profile.get("href", "")
        if href and "linkedin.com/in/" in href:
            score += 0.1
        return round(min(score, 1.0), 3)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def rank_profiles(self, profiles):
        return sorted(
            profiles,
            key=lambda p: self.score_profile(p),
            reverse=True,
        )

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def enrich_profile(self, href, extra_data):
        try:
            db_manager.profiles_collection.update_one(
                {"href": href},
                {"$set": {**extra_data, "enriched_at": datetime.utcnow()}},
                upsert=True,
            )
            return True
        except Exception as exc:
            logger.error(f"ProfileService.enrich_profile: {exc}")
            return False

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def bulk_enrich(self, enrichments):
        matched = 0
        for item in enrichments:
            href = item.pop("href", None)
            if href:
                if self.enrich_profile(href, item):
                    matched += 1
        return matched

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def find_duplicates(self):
        try:
            pipeline = [
                {"$group": {"_id": "$href", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}},
                {"$sort": {"count": -1}},
            ]
            return list(db_manager.profiles_collection.aggregate(pipeline))
        except Exception as exc:
            logger.error(f"ProfileService.find_duplicates: {exc}")
            return []

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def remove_duplicates(self):
        deleted = 0
        for dup in self.find_duplicates():
            href = dup["_id"]
            docs = list(
                db_manager.profiles_collection.find({"href": href}).sort("_id", -1)
            )
            for doc in docs[1:]:
                db_manager.profiles_collection.delete_one({"_id": doc["_id"]})
                deleted += 1
        logger.info(f"Removed {deleted} duplicate profile documents")
        return deleted

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def archive_stale_profiles(self, days_old=60):
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_old)
            result = db_manager.profiles_collection.update_many(
                {
                    "scraped_at": {"$lt": cutoff.timestamp()},
                    "processed": {"$ne": True},
                    "status": {"$exists": False},
                },
                {"$set": {"status": "archived", "archived_at": datetime.utcnow()}},
            )
            logger.info(f"Archived {result.modified_count} stale profiles")
            return result.modified_count
        except Exception as exc:
            logger.error(f"ProfileService.archive_stale_profiles: {exc}")
            return 0

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def delete_archived(self) -> int:
        try:
            result = db_manager.profiles_collection.delete_many({"status": "archived"})
            logger.info(f"Deleted {result.deleted_count} archived profiles")
            return result.deleted_count
        except Exception as exc:
            logger.error(f"ProfileService.delete_archived: {exc}")
            return 0

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def get_pipeline_stats(self):
        try:
            col = db_manager.profiles_collection
            total = col.count_documents({})
            unprocessed = col.count_documents(
                {"$or": [{"processed": {"$exists": False}}, {"processed": False}]}
            )
            connected = col.count_documents({"connected": True})
            messaged = col.count_documents({"messaged": True})
            pending = col.count_documents({"status": "pending"})
            archived = col.count_documents({"status": "archived"})

            return {
                "total": total,
                "unprocessed": unprocessed,
                "connected": connected,
                "messaged": messaged,
                "pending_requests": pending,
                "archived": archived,
                "conversion_rate": round(connected / total, 3) if total else 0,
            }
        except Exception as exc:
            logger.error(f"ProfileService.get_pipeline_stats: {exc}")
            return {}

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def get_profiles_by_status(self, status, limit=50):
        try:
            return db_manager.profiles_collection.find(
                {"status": status},
                {"_id": 0},
            ).limit(limit)
        except Exception as exc:
            logger.error(f"ProfileService.get_profiles_by_status: {exc}")
            return []

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def search_profiles(self, keyword, limit=20):
        try:
            pattern = {"$regex": keyword, "$options": "i"}
            query = {
                "$or": [
                    {"name": pattern},
                    {"title": pattern},
                    {"company": pattern},
                    {"location": pattern},
                ]
            }
            return db_manager.profiles_collection.find(query, {"_id": 0}).limit(limit)
        except Exception as exc:
            logger.error(f"ProfileService.search_profiles: {exc}")
            return []


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

profile_service = ProfileService()
