import logging
from datetime import datetime


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


def task_scrape_google(location="USA", max_pages=10):
    from scraper import google_scraper

    logger.info(f"[task_scrape_google] location={location}, max_pages={max_pages}")
    start = datetime.utcnow()
    try:
        new_count = google_scraper.scrape_profiles(
            location=location, max_pages=max_pages
        )
        elapsed = (datetime.utcnow() - start).total_seconds()
        result = {
            "task": "scrape_google",
            "location": location,
            "new_profiles": new_count,
            "elapsed_seconds": round(elapsed, 1),
            "status": "success",
        }
        logger.info(
            f"[task_scrape_google] done — {new_count} new profiles in {elapsed:.1f}s"
        )
        return result
    except Exception as exc:
        logger.error(f"[task_scrape_google] error: {exc}")
        return {"task": "scrape_google", "status": "error", "error": str(exc)}


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def task_scrape_google_lightweight(location="USA", max_pages=5):
    from scraper.google_scraper import get_lightweight_scraper

    logger.info(f"[task_scrape_lightweight] location={location}, max_pages={max_pages}")
    start = datetime.utcnow()
    try:
        scraper = get_lightweight_scraper()
        new_count = scraper.scrape_by_location(location=location, max_pages=max_pages)
        elapsed = (datetime.utcnow() - start).total_seconds()
        return {
            "task": "scrape_google_lightweight",
            "location": location,
            "new_profiles": new_count,
            "elapsed_seconds": round(elapsed, 1),
            "status": "success",
        }
    except Exception as exc:
        logger.error(f"[task_scrape_lightweight] error: {exc}")
        return {
            "task": "scrape_google_lightweight",
            "status": "error",
            "error": str(exc),
        }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def task_scrape_all_locations(max_pages_per_location=3):
    from scraper.google_scraper import get_lightweight_scraper

    scraper = get_lightweight_scraper()
    results = scraper.scrape_all_locations(
        max_pages_per_location=max_pages_per_location
    )
    total = sum(results.values())
    return {
        "task": "scrape_all_locations",
        "by_location": results,
        "total_new": total,
        "status": "success",
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def task_send_connection_requests(max_requests=15):
    from bot.automation import linkedin_automation

    logger.info(f"[task_send_connections] max={max_requests}")
    start = datetime.utcnow()
    try:
        sent = linkedin_automation.send_connection_requests(max_requests)
        elapsed = (datetime.utcnow() - start).total_seconds()
        return {
            "task": "send_connection_requests",
            "sent": sent,
            "elapsed_seconds": round(elapsed, 1),
            "status": "success",
        }
    except Exception as exc:
        logger.error(f"[task_send_connections] error: {exc}")
        return {
            "task": "send_connection_requests",
            "status": "error",
            "error": str(exc),
        }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def task_send_messages(max_messages=10):
    from bot.automation import linkedin_automation

    logger.info(f"[task_send_messages] max={max_messages}")
    start = datetime.utcnow()
    try:
        sent = linkedin_automation.send_messages(max_messages)
        elapsed = (datetime.utcnow() - start).total_seconds()
        return {
            "task": "send_messages",
            "sent": sent,
            "elapsed_seconds": round(elapsed, 1),
            "status": "success",
        }
    except Exception as exc:
        logger.error(f"[task_send_messages] error: {exc}")
        return {"task": "send_messages", "status": "error", "error": str(exc)}


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def task_visit_profiles(max_visits=20):
    from bot.automation import linkedin_automation

    logger.info(f"[task_visit_profiles] max={max_visits}")
    start = datetime.utcnow()
    try:
        visited = linkedin_automation.visit_profiles(max_visits)
        elapsed = (datetime.utcnow() - start).total_seconds()
        return {
            "task": "visit_profiles",
            "visited": visited,
            "elapsed_seconds": round(elapsed, 1),
            "status": "success",
        }
    except Exception as exc:
        logger.error(f"[task_visit_profiles] error: {exc}")
        return {"task": "visit_profiles", "status": "error", "error": str(exc)}


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def task_accept_connection_requests(max_accepts=20):
    from bot.automation import linkedin_automation

    logger.info(f"[task_accept_connections] max={max_accepts}")
    start = datetime.utcnow()
    try:
        accepted = linkedin_automation.accept_connection_requests(max_accepts)
        elapsed = (datetime.utcnow() - start).total_seconds()
        return {
            "task": "accept_connection_requests",
            "accepted": accepted,
            "elapsed_seconds": round(elapsed, 1),
            "status": "success",
        }
    except Exception as exc:
        logger.error(f"[task_accept_connections] error: {exc}")
        return {
            "task": "accept_connection_requests",
            "status": "error",
            "error": str(exc),
        }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def task_cleanup_profiles(days_old=60):
    from services.profile_service import profile_service

    archived = profile_service.archive_stale_profiles(days_old=days_old)
    return {
        "task": "cleanup_profiles",
        "archived": archived,
        "status": "success",
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def task_remove_duplicates():
    from services.profile_service import profile_service

    deleted = profile_service.remove_duplicates()
    return {
        "task": "remove_duplicates",
        "deleted": deleted,
        "status": "success",
    }


def task_ensure_db_indexes():
    from database.indexes import ensure_indexes
    from database import db_manager

    ensure_indexes(db_manager.db)
    return {"task": "ensure_db_indexes", "status": "success"}


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def task_generate_daily_report():
    from database import db_manager
    from services import rate_limit_service

    try:
        daily_stats = db_manager.get_daily_stats()
        rate_status = rate_limit_service.get_rate_limit_status()
        report = {
            "task": "daily_report",
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "daily_stats": daily_stats,
            "rate_limit_status": rate_status,
            "status": "success",
        }
        logger.info(f"Daily report: {report}")
        return report
    except Exception as exc:
        logger.error(f"[task_daily_report] error: {exc}")
        return {"task": "daily_report", "status": "error", "error": str(exc)}
