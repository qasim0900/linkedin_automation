import logging
from datetime import datetime, timedelta
from scheduler.tasks import (
    task_scrape_google,
    task_scrape_all_locations,
    task_send_connection_requests,
    task_send_messages,
    task_visit_profiles,
    task_accept_connection_requests,
    task_cleanup_profiles,
    task_remove_duplicates,
    task_generate_daily_report,
    task_ensure_db_indexes,
)


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


def _next_occurrence(hour, minute=0):
    now = datetime.utcnow()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_daily_google_scrape(location="USA", hour=7):
    return {
        "name": f"Daily Google Scrape [{location}]",
        "function": task_scrape_google,
        "kwargs": {"location": location, "max_pages": 10},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_scrape_all_locations(hour=6):
    return {
        "name": "Daily Multi-Location Scrape",
        "function": task_scrape_all_locations,
        "kwargs": {"max_pages_per_location": 3},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_morning_connection_batch(hour=9):
    return {
        "name": "Morning Connection Batch",
        "function": task_send_connection_requests,
        "kwargs": {"max_requests": 10},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_afternoon_connection_batch(hour=14):
    return {
        "name": "Afternoon Connection Batch",
        "function": task_send_connection_requests,
        "kwargs": {"max_requests": 10},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_morning_messages(hour=10):
    return {
        "name": "Morning Messaging Run",
        "function": task_send_messages,
        "kwargs": {"max_messages": 7},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_afternoon_messages(hour=15):
    return {
        "name": "Afternoon Messaging Run",
        "function": task_send_messages,
        "kwargs": {"max_messages": 7},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_profile_visits(hour=11):
    return {
        "name": "Midday Profile Visits",
        "function": task_visit_profiles,
        "kwargs": {"max_visits": 20},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_accept_requests(hour=8):
    return {
        "name": "Accept Pending Requests",
        "function": task_accept_connection_requests,
        "kwargs": {"max_accepts": 30},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_nightly_cleanup(hour=2):
    return {
        "name": "Nightly Profile Cleanup",
        "function": task_cleanup_profiles,
        "kwargs": {"days_old": 60},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_deduplication(hour=3):
    return {
        "name": "Nightly Deduplication",
        "function": task_remove_duplicates,
        "kwargs": {},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_daily_report(hour=22):
    return {
        "name": "Daily Activity Report",
        "function": task_generate_daily_report,
        "kwargs": {},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def job_ensure_indexes(hour=4):
    return {
        "name": "Ensure DB Indexes",
        "function": task_ensure_db_indexes,
        "kwargs": {},
        "scheduled_time": _next_occurrence(hour),
        "recur_hours": 24,
    }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def get_all_cron_jobs():
    return [
        job_accept_requests(hour=8),
        job_daily_google_scrape(location="USA", hour=7),
        job_daily_google_scrape(location="UK", hour=7),
        job_daily_google_scrape(location="Canada", hour=7),
        job_morning_connection_batch(hour=9),
        job_morning_messages(hour=10),
        job_profile_visits(hour=11),
        job_afternoon_connection_batch(hour=14),
        job_afternoon_messages(hour=15),
        job_daily_report(hour=22),
        job_nightly_cleanup(hour=2),
        job_deduplication(hour=3),
        job_ensure_indexes(hour=4),
    ]


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def register_all_cron_jobs(scheduler):
    jobs = get_all_cron_jobs()
    registered = 0
    for job in jobs:
        try:
            scheduler.schedule_task(
                name=job["name"],
                function=job["function"],
                scheduled_time=job["scheduled_time"],
                kwargs=job.get("kwargs", {}),
            )
            registered += 1
            logger.info(
                f"Registered cron job: {job['name']} "
                f"at {job['scheduled_time'].strftime('%H:%M UTC')}"
            )
        except Exception as exc:
            logger.error(f"Failed to register job '{job['name']}': {exc}")
    logger.info(f"Total cron jobs registered: {registered}")
    return registered


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def register_minimal_cron_jobs(scheduler):
    minimal_jobs = [
        job_daily_google_scrape(location="USA", hour=7),
        job_morning_connection_batch(hour=9),
        job_morning_messages(hour=10),
    ]
    registered = 0
    for job in minimal_jobs:
        try:
            scheduler.schedule_task(
                name=job["name"],
                function=job["function"],
                scheduled_time=job["scheduled_time"],
                kwargs=job.get("kwargs", {}),
            )
            registered += 1
        except Exception as exc:
            logger.error(f"Failed to register minimal job '{job['name']}': {exc}")
    return registered
