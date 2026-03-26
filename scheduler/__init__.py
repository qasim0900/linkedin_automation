import time
import logging
import threading
from enum import Enum
from config import config
from database import db_manager
from dataclasses import dataclass
from scraper import google_scraper
from bot.auth import linkedin_auth
from datetime import datetime, timedelta
from bot.automation import linkedin_automation
from typing import Dict, Any, Optional, Callable
from services import decision_engine, rate_limit_service

# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)


# --------------------------------
# :: Task Status Class
# --------------------------------

""" 
Task
"""


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


@dataclass
class ScheduledTask:
    id: str
    name: str
    function: Callable
    args: tuple
    kwargs: dict
    scheduled_time: datetime
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Any] = None


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


class AutomationScheduler:

    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def __init__(self):
        self.tasks = {}
        self.running = False
        self.scheduler_thread = None
        self.execution_history = []
        self.max_history_size = 100
        self.schedule_config = {
            "scraping_interval_hours": 24,
            "automation_start_hour": 9,
            "automation_end_hour": 18,
            "break_interval_minutes": 120,
            "max_daily_runtime_hours": 8,
        }


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def start_scheduler(self):
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop, daemon=True
        )
        self.scheduler_thread.start()
        logger.info("Scheduler started")


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def stop_scheduler(self):
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        logger.info("Scheduler stopped")


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def _scheduler_loop(self):
        logger.info("Scheduler loop started")
        while self.running:
            try:
                current_time = datetime.utcnow()
                if self._is_within_working_hours(current_time):
                    self._process_scheduled_tasks(current_time)
                    self._check_automated_actions(current_time)
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
        logger.info("Scheduler loop ended")


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def _is_within_working_hours(self, current_time):
        hour = current_time.hour
        start_hour = self.schedule_config["automation_start_hour"]
        end_hour = self.schedule_config["automation_end_hour"]
        return start_hour <= hour < end_hour


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def _process_scheduled_tasks(self, current_time):
        for task_id, task in list(self.tasks.items()):
            if (
                task.status == TaskStatus.PENDING
                and current_time >= task.scheduled_time
            ):
                self._execute_task(task)


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def _execute_task(self, task):
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            logger.info(f"Executing task: {task.name}")
            result = task.function(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            logger.info(f"Task completed: {task.name}")
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error_message = str(e)
            logger.error(f"Task failed: {task.name} - {e}")
        finally:
            self._add_to_history(task)


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def _check_automated_actions(self, current_time):
        try:
            next_action = decision_engine.get_next_action()
            if next_action:
                if decision_engine.should_take_break():
                    logger.info("Taking automated break")
                    time.sleep(300)
                    return
                self._execute_automated_action(next_action)
        except Exception as e:
            logger.error(f"Error in automated actions: {e}")


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def _execute_automated_action(self, action):
        action_type = action["action_type"]
        profiles = action["profiles"]
        logger.info(
            f"Executing automated action: {action_type} for {len(profiles)} profiles"
        )
        try:
            if action_type == "connections":
                result = linkedin_automation.send_connection_requests(len(profiles))
                logger.info(f"Connection requests sent: {result}")
            elif action_type == "messages":
                result = linkedin_automation.send_messages(len(profiles))
                logger.info(f"Messages sent: {result}")
            elif action_type == "visits":
                result = linkedin_automation.visit_profiles(len(profiles))
                logger.info(f"Profiles visited: {result}")
        except Exception as e:
            logger.error(f"Error executing automated action {action_type}: {e}")


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def schedule_task(
        self,
        name,
        function,
        scheduled_time,
        args,
        kwargs,
    ):
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        task = ScheduledTask(
            id=task_id,
            name=name,
            function=function,
            args=args,
            kwargs=kwargs or {},
            scheduled_time=scheduled_time,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        self.tasks[task_id] = task
        logger.info(f"Scheduled task: {name} at {scheduled_time}")
        return task_id


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def cancel_task(self, task_id):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                logger.info(f"Cancelled task: {task.name}")
                return True
        return False


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def schedule_daily_scraping(self, location = "USA", hour = 8):
        now = datetime.utcnow()
        next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        return self.schedule_task(
            name=f"Daily Scraping - {location}",
            function=google_scraper.scrape_profiles,
            scheduled_time=next_run,
            kwargs={"location": location, "max_pages": 10},
        )


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def schedule_automation_session(self, duration_minutes = 120):
        start_time = datetime.utcnow() + timedelta(minutes=5)
        return self.schedule_task(
            name="Automation Session",
            function=self._run_automation_session,
            scheduled_time=start_time,
            kwargs={"duration_minutes": duration_minutes},
        )


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def _run_automation_session(self, duration_minutes):
        session_start = datetime.utcnow()
        session_end = session_start + timedelta(minutes=duration_minutes)

        session_stats = {
            "start_time": session_start,
            "end_time": session_end,
            "actions_performed": {},
            "profiles_processed": 0,
            "errors": [],
        }
        logger.info(f"Starting automation session for {duration_minutes} minutes")
        try:
            if not linkedin_auth.verify_session():
                if not linkedin_auth.login():
                    raise Exception("Failed to login to LinkedIn")
            actions_performed = 0
            while datetime.utcnow() < session_end and actions_performed < 50:
                next_action = decision_engine.get_next_action()
                if not next_action:
                    logger.info("No more actions available")
                    break
                action_type = next_action["action_type"]
                if action_type == "connections":
                    result = linkedin_automation.send_connection_requests(5)
                elif action_type == "messages":
                    result = linkedin_automation.send_messages(3)
                else:
                    result = linkedin_automation.visit_profiles(10)

                session_stats["actions_performed"][action_type] = (
                    session_stats["actions_performed"].get(action_type, 0) + result
                )
                actions_performed += 1
                if decision_engine.should_take_break():
                    logger.info("Taking session break")
                    time.sleep(300)
                    break
                time.sleep(30)
            session_stats["profiles_processed"] = actions_performed
        except Exception as e:
            session_stats["errors"].append(str(e))
            logger.error(f"Automation session error: {e}")
        finally:
            logger.info("Automation session completed")
        return session_stats


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def get_task_status(self, task_id):
        return self.tasks.get(task_id)


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def get_all_tasks(self):
        return self.tasks.copy()


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def get_pending_tasks(self):
        return {
            task_id: task
            for task_id, task in self.tasks.items()
            if task.status == TaskStatus.PENDING
        }


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def _add_to_history(self, task):
        self.execution_history.append(task)
        if len(self.execution_history) > self.max_history_size:
            self.execution_history.pop(0)


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def get_execution_history(self, limit = 20):
        return self.execution_history[-limit:]


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def get_scheduler_status(self):
        return {
            "running": self.running,
            "total_tasks": len(self.tasks),
            "pending_tasks": len(self.get_pending_tasks()),
            "current_time": datetime.utcnow(),
            "within_working_hours": self._is_within_working_hours(datetime.utcnow()),
            "schedule_config": self.schedule_config,
            "recent_history": self.get_execution_history(5),
        }


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def cleanup_completed_tasks(self, older_than_hours = 24):
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        removed_count = 0
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (
                task.status
                in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
                and task.completed_at
                and task.completed_at < cutoff_time
            ):
                tasks_to_remove.append(task_id)
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            removed_count += 1
        logger.info(f"Cleaned up {removed_count} completed tasks")
        return removed_count


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


class AutomationOrchestrator:

    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def __init__(self):
        self.scheduler = AutomationScheduler()
        self.running = False


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def start_automation(self):
        if self.running:
            logger.warning("Automation is already running")
            return

        try:
            config.validate_config()
            self.scheduler.start_scheduler()
            self._schedule_initial_tasks()
            self.running = True
            logger.info("Automation system started successfully")
        except Exception as e:
            logger.error(f"Failed to start automation: {e}")
            self.stop_automation()
            raise


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def stop_automation(self) -> None:
        self.scheduler.stop_scheduler()
        self.running = False
        logger.info("Automation system stopped")


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def _schedule_initial_tasks(self) -> None:
        from scheduler.cron_jobs import register_all_cron_jobs
        registered = register_all_cron_jobs(self.scheduler)
        logger.info(f"Registered {registered} cron jobs")
        self.scheduler.schedule_automation_session(60)


    # --------------------------------
    # :: get Automation Stats Method
    # --------------------------------

    """
    Retrieves automation statistics including daily stats, rate limits, and session information.
    """

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "automation_running": self.running,
            "scheduler_status": self.scheduler.get_scheduler_status(),
            "rate_limits": rate_limit_service.get_rate_limit_status(),
            "database_stats": {
                "total_profiles": db_manager.profiles_collection.count_documents({}),
                "unprocessed_profiles": db_manager.profiles_collection.count_documents(
                    {"$or": [{"processed": {"$exists": False}}, {"processed": False}]}
                ),
                "connected_profiles": db_manager.profiles_collection.count_documents(
                    {"connected": True}
                ),
                "messaged_profiles": db_manager.profiles_collection.count_documents(
                    {"messaged": True}
                ),
            },
            "daily_stats": db_manager.get_daily_stats(),
        }


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

automation_orchestrator = AutomationOrchestrator()
