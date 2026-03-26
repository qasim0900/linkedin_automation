"""
Scheduler module for LinkedIn automation system.
Handles automated execution and timing.
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from config import config
from database import db_manager
from scraper import google_scraper
from bot import linkedin_automation
from bot.auth import linkedin_auth
from services import decision_engine, rate_limit_service

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ScheduledTask:
    """Represents a scheduled task."""
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

class AutomationScheduler:
    """Advanced scheduler for LinkedIn automation tasks."""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.execution_history = []
        self.max_history_size = 100
        
        # Default schedule configuration
        self.schedule_config = {
            "scraping_interval_hours": 24,  # Scrape every 24 hours
            "automation_start_hour": 9,     # Start at 9 AM
            "automation_end_hour": 18,      # End at 6 PM
            "break_interval_minutes": 120,  # Break every 2 hours
            "max_daily_runtime_hours": 8    # Max 8 hours per day
        }
    
    def start_scheduler(self) -> None:
        """Start the scheduler in background thread."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler started")
    
    def stop_scheduler(self) -> None:
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        logger.info("Scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                # Check if within working hours
                if self._is_within_working_hours(current_time):
                    # Process scheduled tasks
                    self._process_scheduled_tasks(current_time)
                    
                    # Check for automated actions
                    self._check_automated_actions(current_time)
                
                # Sleep for 1 minute before next check
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
        
        logger.info("Scheduler loop ended")
    
    def _is_within_working_hours(self, current_time: datetime) -> bool:
        """Check if current time is within working hours."""
        hour = current_time.hour
        start_hour = self.schedule_config["automation_start_hour"]
        end_hour = self.schedule_config["automation_end_hour"]
        
        return start_hour <= hour < end_hour
    
    def _process_scheduled_tasks(self, current_time: datetime) -> None:
        """Process and execute scheduled tasks."""
        for task_id, task in list(self.tasks.items()):
            if task.status == TaskStatus.PENDING and current_time >= task.scheduled_time:
                self._execute_task(task)
    
    def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a scheduled task."""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            
            logger.info(f"Executing task: {task.name}")
            
            # Execute the task function
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
            # Add to history
            self._add_to_history(task)
    
    def _check_automated_actions(self, current_time: datetime) -> None:
        """Check for and execute automated actions."""
        try:
            # Get next action from decision engine
            next_action = decision_engine.get_next_action()
            
            if next_action:
                # Check if we should take a break
                if decision_engine.should_take_break():
                    logger.info("Taking automated break")
                    time.sleep(300)  # 5 minute break
                    return
                
                # Execute the action
                self._execute_automated_action(next_action)
                
        except Exception as e:
            logger.error(f"Error in automated actions: {e}")
    
    def _execute_automated_action(self, action: Dict[str, Any]) -> None:
        """Execute an automated action."""
        action_type = action["action_type"]
        profiles = action["profiles"]
        
        logger.info(f"Executing automated action: {action_type} for {len(profiles)} profiles")
        
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
    
    def schedule_task(self, name: str, function: Callable, scheduled_time: datetime, 
                     args: tuple = (), kwargs: dict = None) -> str:
        """Schedule a task for execution."""
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            function=function,
            args=args,
            kwargs=kwargs or {},
            scheduled_time=scheduled_time,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.tasks[task_id] = task
        logger.info(f"Scheduled task: {name} at {scheduled_time}")
        
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                logger.info(f"Cancelled task: {task.name}")
                return True
        return False
    
    def schedule_daily_scraping(self, location: str = "USA", hour: int = 8) -> str:
        """Schedule daily profile scraping."""
        # Schedule for next occurrence at specified hour
        now = datetime.utcnow()
        next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        if next_run <= now:
            next_run += timedelta(days=1)
        
        return self.schedule_task(
            name=f"Daily Scraping - {location}",
            function=google_scraper.scrape_profiles,
            scheduled_time=next_run,
            kwargs={"location": location, "max_pages": 10}
        )
    
    def schedule_automation_session(self, duration_minutes: int = 120) -> str:
        """Schedule an automation session."""
        start_time = datetime.utcnow() + timedelta(minutes=5)
        
        return self.schedule_task(
            name="Automation Session",
            function=self._run_automation_session,
            scheduled_time=start_time,
            kwargs={"duration_minutes": duration_minutes}
        )
    
    def _run_automation_session(self, duration_minutes: int) -> Dict[str, Any]:
        """Run an automation session for specified duration."""
        session_start = datetime.utcnow()
        session_end = session_start + timedelta(minutes=duration_minutes)
        
        session_stats = {
            "start_time": session_start,
            "end_time": session_end,
            "actions_performed": {},
            "profiles_processed": 0,
            "errors": []
        }
        
        logger.info(f"Starting automation session for {duration_minutes} minutes")
        
        try:
            # Ensure logged in
            if not linkedin_auth.verify_session():
                if not linkedin_auth.login():
                    raise Exception("Failed to login to LinkedIn")
            
            actions_performed = 0
            
            while datetime.utcnow() < session_end and actions_performed < 50:
                # Get next action
                next_action = decision_engine.get_next_action()
                
                if not next_action:
                    logger.info("No more actions available")
                    break
                
                # Execute action
                action_type = next_action["action_type"]
                
                if action_type == "connections":
                    result = linkedin_automation.send_connection_requests(5)
                elif action_type == "messages":
                    result = linkedin_automation.send_messages(3)
                else:  # visits
                    result = linkedin_automation.visit_profiles(10)
                
                session_stats["actions_performed"][action_type] = \
                    session_stats["actions_performed"].get(action_type, 0) + result
                
                actions_performed += 1
                
                # Check for break
                if decision_engine.should_take_break():
                    logger.info("Taking session break")
                    time.sleep(300)  # 5 minute break
                    break
                
                # Small delay between actions
                time.sleep(30)
            
            session_stats["profiles_processed"] = actions_performed
            
        except Exception as e:
            session_stats["errors"].append(str(e))
            logger.error(f"Automation session error: {e}")
        
        finally:
            logger.info("Automation session completed")
        
        return session_stats
    
    def get_task_status(self, task_id: str) -> Optional[ScheduledTask]:
        """Get status of a specific task."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, ScheduledTask]:
        """Get all scheduled tasks."""
        return self.tasks.copy()
    
    def get_pending_tasks(self) -> Dict[str, ScheduledTask]:
        """Get all pending tasks."""
        return {
            task_id: task for task_id, task in self.tasks.items()
            if task.status == TaskStatus.PENDING
        }
    
    def _add_to_history(self, task: ScheduledTask) -> None:
        """Add task to execution history."""
        self.execution_history.append(task)
        
        # Limit history size
        if len(self.execution_history) > self.max_history_size:
            self.execution_history.pop(0)
    
    def get_execution_history(self, limit: int = 20) -> list:
        """Get recent execution history."""
        return self.execution_history[-limit:]
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get comprehensive scheduler status."""
        return {
            "running": self.running,
            "total_tasks": len(self.tasks),
            "pending_tasks": len(self.get_pending_tasks()),
            "current_time": datetime.utcnow(),
            "within_working_hours": self._is_within_working_hours(datetime.utcnow()),
            "schedule_config": self.schedule_config,
            "recent_history": self.get_execution_history(5)
        }
    
    def cleanup_completed_tasks(self, older_than_hours: int = 24) -> int:
        """Clean up completed tasks older than specified hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        removed_count = 0
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                task.completed_at and task.completed_at < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            removed_count += 1
        
        logger.info(f"Cleaned up {removed_count} completed tasks")
        return removed_count

class AutomationOrchestrator:
    """High-level orchestrator for the entire automation system."""
    
    def __init__(self):
        self.scheduler = AutomationScheduler()
        self.running = False
    
    def start_automation(self) -> None:
        """Start the complete automation system."""
        if self.running:
            logger.warning("Automation is already running")
            return
        
        try:
            # Validate configuration
            config.validate_config()
            
            # Start scheduler
            self.scheduler.start_scheduler()
            
            # Schedule initial tasks
            self._schedule_initial_tasks()
            
            self.running = True
            logger.info("Automation system started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start automation: {e}")
            self.stop_automation()
            raise
    
    def stop_automation(self) -> None:
        """Stop the automation system."""
        self.scheduler.stop_scheduler()
        self.running = False
        logger.info("Automation system stopped")
    
    def _schedule_initial_tasks(self) -> None:
        """Schedule initial automation tasks."""
        # Schedule daily scraping
        self.scheduler.schedule_daily_scraping("USA", 8)
        self.scheduler.schedule_daily_scraping("Lahore", 9)
        
        # Schedule initial automation session
        self.scheduler.schedule_automation_session(60)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "automation_running": self.running,
            "scheduler_status": self.scheduler.get_scheduler_status(),
            "rate_limits": rate_limit_service.get_rate_limit_status(),
            "database_stats": {
                "total_profiles": db_manager.profiles_collection.count_documents({}),
                "unprocessed_profiles": db_manager.profiles_collection.count_documents({
                    "$or": [{"processed": {"$exists": False}}, {"processed": False}]
                }),
                "connected_profiles": db_manager.profiles_collection.count_documents({"connected": True}),
                "messaged_profiles": db_manager.profiles_collection.count_documents({"messaged": True})
            },
            "daily_stats": db_manager.get_daily_stats()
        }

# Global orchestrator instance
automation_orchestrator = AutomationOrchestrator()