import os
import sys
import signal
import logging
import argparse
from config import config
from tabulate import tabulate
from database import db_manager
from scraper import google_scraper
from bot.auth import linkedin_auth
from services import rate_limit_service
from scheduler import automation_orchestrator
from bot.automation import linkedin_automation


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(config.LOG_FILE), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


class LinkedInAutomationCLI:

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def __init__(self):
        self.running = False

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def setup_signal_handlers(self):
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def start_interactive_mode(self):
        print("\n" + "=" * 60)
        print("LINKEDIN AUTOMATION SYSTEM")
        print("=" * 60)
        print("\nWelcome to the LinkedIn Automation System!")
        print("This system provides safe, human-like LinkedIn automation.\n")
        while True:
            try:
                self.show_main_menu()
                choice = input("\nEnter your choice (1-8): ").strip()
                if choice == "1":
                    self.run_system_status()
                elif choice == "2":
                    self.run_scraping_menu()
                elif choice == "3":
                    self.run_automation_menu()
                elif choice == "4":
                    self.run_scheduler_menu()
                elif choice == "5":
                    self.start_full_automation()
                elif choice == "6":
                    self.stop_full_automation()
                elif choice == "7":
                    self.show_statistics()
                elif choice == "8":
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("Invalid choice. Please select 1-8.")

                input("\nPress Enter to continue...")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"Error: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def show_main_menu(self):
        options = [
            ["1", "System Status"],
            ["2", "Profile Scraping"],
            ["3", "Automation Actions"],
            ["4", "Scheduler Management"],
            ["5", "Start Full Automation"],
            ["6", "Stop Full Automation"],
            ["7", "Statistics & Reports"],
            ["8", "Exit"],
        ]

        print(
            "\n"
            + tabulate(
                options, headers=["Option", "Description"], tablefmt="fancy_grid"
            )
        )

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def run_system_status(self):
        print("\n📊 SYSTEM STATUS")
        print("-" * 40)

        try:
            print(
                "🗄️  Database Connection:",
                "Connected" if db_manager.db else "Disconnected",
            )
            auth_status = linkedin_auth.get_session_info()
            print(
                "🔐 LinkedIn Login:",
                "Logged in" if auth_status.get("logged_in") else "Not logged in",
            )
            rate_limits = rate_limit_service.get_rate_limit_status()
            print("\n Rate Limits:")
            for action, limits in rate_limits.items():
                print(
                    f"  {action.capitalize()}: {limits['daily_used']}/{limits['daily_limit']} daily"
                )
            system_status = automation_orchestrator.get_system_status()
            print(
                f"\n🤖 Automation: {'Running' if system_status['automation_running'] else 'Stopped'}"
            )
        except Exception as e:
            print(f"Error getting status: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def run_scraping_menu(self):
        print("\n PROFILE SCRAPING")
        print("-" * 40)

        options = [
            ["1", "Scrape USA Profiles"],
            ["2", "Scrape Lahore Profiles"],
            ["3", "Custom Query Scraping"],
            ["4", "View Scraping Statistics"],
            ["5", "Clean Old Profiles"],
        ]
        print(
            tabulate(options, headers=["Option", "Description"], tablefmt="fancy_grid")
        )
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice == "1":
            self.scrape_profiles("USA")
        elif choice == "2":
            self.scrape_profiles("Lahore")
        elif choice == "3":
            self.custom_scraping()
        elif choice == "4":
            self.show_scraping_stats()
        elif choice == "5":
            self.cleanup_old_profiles()

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def scrape_profiles(self, location):
        print(f"\n🔍 Scraping LinkedIn profiles for {location}...")
        try:
            result = google_scraper.scrape_profiles(location, max_pages=5)
            print(f"Successfully scraped {result} new profiles")
        except Exception as e:
            print(f"Scraping failed: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def custom_scraping(self):
        query = input("\nEnter custom search query: ").strip()
        if query:
            print(f"\n🔍 Scraping with query: {query}")
            try:
                result = google_scraper.scrape_specific_query(query, max_pages=3)
                print(f"Successfully scraped {result} new profiles")
            except Exception as e:
                print(f"Scraping failed: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def show_scraping_stats(self):
        """Show scraping statistics."""
        print("\n SCRAPING STATISTICS")
        print("-" * 40)
        try:
            stats = google_scraper.get_search_statistics()
            print(f"Total Profiles: {stats.get('total_profiles', 0)}")
            print(f"Google Scraped: {stats.get('google_scraped', 0)}")
            print("\nBy Location:")
            for location, count in stats.get("by_location", {}).items():
                print(f"  {location}: {count}")
        except Exception as e:
            print(f" Error getting stats: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def cleanup_old_profiles(self):
        print("\n🧹 Cleaning up old profiles...")

        try:
            removed = google_scraper.cleanup_old_profiles(days_old=30)
            print(f" Removed {removed} old profiles")
        except Exception as e:
            print(f" Cleanup failed: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def run_automation_menu(self):
        print("\n AUTOMATION ACTIONS")
        print("-" * 40)

        options = [
            ["1", "Visit Profiles"],
            ["2", "Send Connection Requests"],
            ["3", "Send Messages"],
            ["4", "Login to LinkedIn"],
            ["5", "Logout from LinkedIn"],
        ]
        print(
            tabulate(options, headers=["Option", "Description"], tablefmt="fancy_grid")
        )
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice == "1":
            self.visit_profiles()
        elif choice == "2":
            self.send_connections()
        elif choice == "3":
            self.send_messages()
        elif choice == "4":
            self.login_linkedin()
        elif choice == "5":
            self.logout_linkedin()

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def visit_profiles(self):
        count = input("Number of profiles to visit (default 10): ").strip()
        count = int(count) if count.isdigit() else 10

        print(f"\n Visiting {count} profiles...")

        try:
            result = linkedin_automation.visit_profiles(count)
            print(f" Successfully visited {result} profiles")
        except Exception as e:
            print(f" Profile visits failed: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def send_connections(self):
        count = input("Number of connection requests (default 5): ").strip()
        count = int(count) if count.isdigit() else 5

        print(f"\n Sending {count} connection requests...")

        try:
            result = linkedin_automation.send_connection_requests(count)
            print(f" Successfully sent {result} connection requests")
        except Exception as e:
            print(f" Connection requests failed: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def send_messages(self):
        count = input("Number of messages (default 3): ").strip()
        count = int(count) if count.isdigit() else 3
        print(f"\n Sending {count} messages...")

        try:
            result = linkedin_automation.send_messages(count)
            print(f" Successfully sent {result} messages")
        except Exception as e:
            print(f" Messaging failed: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def login_linkedin(self):
        """Login to LinkedIn."""
        print("\n Logging in to LinkedIn...")

        try:
            success = linkedin_auth.login()
            if success:
                print(" Successfully logged in")
            else:
                print(" Login failed")
        except Exception as e:
            print(f" Login error: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def logout_linkedin(self):
        print("\n🚪 Logging out from LinkedIn...")
        try:
            success = linkedin_auth.logout()
            if success:
                print(" Successfully logged out")
            else:
                print(" Logout failed")
        except Exception as e:
            print(f" Logout error: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def run_scheduler_menu(self):
        print("\n SCHEDULER MANAGEMENT")
        print("-" * 40)

        options = [
            ["1", "View Scheduler Status"],
            ["2", "Schedule Daily Scraping"],
            ["3", "Schedule Automation Session"],
            ["4", "View Task History"],
            ["5", "Cleanup Old Tasks"],
        ]
        print(
            tabulate(options, headers=["Option", "Description"], tablefmt="fancy_grid")
        )
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice == "1":
            self.show_scheduler_status()
        elif choice == "2":
            self.schedule_daily_scraping()
        elif choice == "3":
            self.schedule_automation_session()
        elif choice == "4":
            self.show_task_history()
        elif choice == "5":
            self.cleanup_tasks()

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def show_scheduler_status(self):
        print("\n⏰ SCHEDULER STATUS")
        print("-" * 40)

        try:
            status = automation_orchestrator.scheduler.get_scheduler_status()

            print(f"Running: {'OK' if status['running'] else 'ERROR'}")
            print(f"Total Tasks: {status['total_tasks']}")
            print(f"Pending Tasks: {status['pending_tasks']}")
            print(
                f"Within Working Hours: {'OK' if status['within_working_hours'] else 'ERROR'}"
            )
        except Exception as e:
            print(f" Error getting status: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def schedule_daily_scraping(self):
        location = input("Location (USA/Lahore): ").strip() or "USA"
        hour = input("Hour (0-23, default 8): ").strip()
        hour = int(hour) if hour.isdigit() else 8

        print(f"\n Scheduling daily scraping for {location} at {hour}:00...")

        try:
            task_id = automation_orchestrator.scheduler.schedule_daily_scraping(
                location, hour
            )
            print(f" Task scheduled: {task_id}")
        except Exception as e:
            print(f" Scheduling failed: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def schedule_automation_session(self):
        duration = input("Duration in minutes (default 60): ").strip()
        duration = int(duration) if duration.isdigit() else 60
        print(f"\n Scheduling automation session for {duration} minutes...")
        try:
            task_id = automation_orchestrator.scheduler.schedule_automation_session(
                duration
            )
            print(f" Task scheduled: {task_id}")
        except Exception as e:
            print(f" Scheduling failed: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def show_task_history(self):
        print("\n TASK HISTORY")
        print("-" * 40)
        try:
            history = automation_orchestrator.scheduler.get_execution_history(10)
            if not history:
                print("No recent task history")
                return
            for task in history:
                status_emoji = {
                    "completed": "OK",
                    "failed": "ERROR",
                    "cancelled": "⏹️",
                }.get(task.status.value, "⏳")
                print(f"{status_emoji} {task.name} - {task.status.value}")
        except Exception as e:
            print(f" Error getting history: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def cleanup_tasks(self):
        print("\n Cleaning up old tasks...")
        try:
            removed = automation_orchestrator.scheduler.cleanup_completed_tasks()
            print(f" Removed {removed} old tasks")
        except Exception as e:
            print(f" Cleanup failed: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def start_full_automation(self):
        print("\n🚀 STARTING FULL AUTOMATION")
        print("-" * 40)

        try:
            automation_orchestrator.start_automation()
            print(" Full automation system started successfully")
            print("The system will now run automatically during working hours")
        except Exception as e:
            print(f" Failed to start automation: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def stop_full_automation(self):
        print("\n STOPPING FULL AUTOMATION")
        print("-" * 40)

        try:
            automation_orchestrator.stop_automation()
            print("Full automation system stopped")
        except Exception as e:
            print(f"Failed to stop automation: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def show_statistics(self):
        print("\n SYSTEM STATISTICS")
        print("-" * 40)
        try:
            system_status = automation_orchestrator.get_system_status()
            db_stats = system_status["database_stats"]
            print(f"Database:")
            print(f"  Total Profiles: {db_stats['total_profiles']}")
            print(f"  Unprocessed: {db_stats['unprocessed_profiles']}")
            print(f"  Connected: {db_stats['connected_profiles']}")
            print(f"  Messaged: {db_stats['messaged_profiles']}")
            daily_stats = system_status["daily_stats"]
            print(f"\n Today's Activity:")
            for action, count in daily_stats.items():
                print(f"  {action.capitalize()}: {count}")
            rate_limits = system_status["rate_limits"]
            print(f"\n  Rate Limits:")
            for action, limits in rate_limits.items():
                print(
                    f"  {action.capitalize()}: {limits['daily_used']}/{limits['daily_limit']}"
                )
        except Exception as e:
            print(f" Error getting statistics: {e}")

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def shutdown(self):
        try:
            logger.info("Shutting down automation system...")
            automation_orchestrator.stop_automation()
            db_manager.close()
            logger.info("Shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Automation System")
    parser.add_argument(
        "--mode",
        choices=["interactive", "daemon"],
        default="interactive",
        help="Run mode: interactive (CLI) or daemon (background)",
    )
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()
    cli = LinkedInAutomationCLI()
    cli.setup_signal_handlers()

    try:
        config.validate_config()

        if args.mode == "interactive":
            cli.start_interactive_mode()
        else:
            print("Starting LinkedIn Automation System in daemon mode...")
            automation_orchestrator.start_automation()
            print("Automation system started. Press Ctrl+C to stop.")
            try:
                while True:
                    import time

                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n Stopping automation system...")
                cli.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

if __name__ == "__main__":
    main()
