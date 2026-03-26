"""
LinkedIn Automation System - Main Entry Point

A production-ready LinkedIn automation system with:
- Human-like behavior simulation
- Rate limiting and safety features
- Intelligent profile selection
- Automated scheduling
- Comprehensive logging and monitoring

Author: LinkedIn Automation Team
Version: 1.0.0
"""

import logging
import os
import sys
import signal
import argparse
from typing import Optional
from tabulate import tabulate

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import system modules
from config import config
from database import db_manager
from scheduler import automation_orchestrator
from scraper import google_scraper
from bot import linkedin_automation
from bot.auth import linkedin_auth
from services import rate_limit_service

# Configure logging
os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class LinkedInAutomationCLI:
    """Command-line interface for LinkedIn automation system."""
    
    def __init__(self):
        self.running = False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start_interactive_mode(self):
        """Start interactive CLI mode."""
        print("\n" + "="*60)
        print("🚀 LINKEDIN AUTOMATION SYSTEM")
        print("="*60)
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
                    print("❌ Invalid choice. Please select 1-8.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"❌ Error: {e}")
    
    def show_main_menu(self):
        """Display main menu options."""
        options = [
            ["1", "📊 System Status"],
            ["2", "🔍 Profile Scraping"],
            ["3", "🤖 Automation Actions"],
            ["4", "⏰ Scheduler Management"],
            ["5", "🚀 Start Full Automation"],
            ["6", "⏹️  Stop Full Automation"],
            ["7", "📈 Statistics & Reports"],
            ["8", "🚪 Exit"]
        ]
        
        print("\n" + tabulate(options, headers=["Option", "Description"], tablefmt="fancy_grid"))
    
    def run_system_status(self):
        """Show comprehensive system status."""
        print("\n📊 SYSTEM STATUS")
        print("-" * 40)
        
        try:
            # Database status
            print("🗄️  Database Connection:", "✅ Connected" if db_manager.db else "❌ Disconnected")
            
            # Authentication status
            auth_status = linkedin_auth.get_session_info()
            print("🔐 LinkedIn Login:", "✅ Logged in" if auth_status.get("logged_in") else "❌ Not logged in")
            
            # Rate limits
            rate_limits = rate_limit_service.get_rate_limit_status()
            print("\n📊 Rate Limits:")
            for action, limits in rate_limits.items():
                status = "✅" if limits["can_perform"] else "❌"
                print(f"  {action.capitalize()}: {status} {limits['daily_used']}/{limits['daily_limit']} daily")
            
            # Automation status
            system_status = automation_orchestrator.get_system_status()
            print(f"\n🤖 Automation: {'✅ Running' if system_status['automation_running'] else '❌ Stopped'}")
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    def run_scraping_menu(self):
        """Show scraping options."""
        print("\n🔍 PROFILE SCRAPING")
        print("-" * 40)
        
        options = [
            ["1", "Scrape USA Profiles"],
            ["2", "Scrape Lahore Profiles"],
            ["3", "Custom Query Scraping"],
            ["4", "View Scraping Statistics"],
            ["5", "Clean Old Profiles"]
        ]
        
        print(tabulate(options, headers=["Option", "Description"], tablefmt="fancy_grid"))
        
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
    
    def scrape_profiles(self, location: str):
        """Scrape profiles for specified location."""
        print(f"\n🔍 Scraping LinkedIn profiles for {location}...")
        
        try:
            result = google_scraper.scrape_profiles(location, max_pages=5)
            print(f"✅ Successfully scraped {result} new profiles")
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
    
    def custom_scraping(self):
        """Run custom query scraping."""
        query = input("\nEnter custom search query: ").strip()
        if query:
            print(f"\n🔍 Scraping with query: {query}")
            try:
                result = google_scraper.scrape_specific_query(query, max_pages=3)
                print(f"✅ Successfully scraped {result} new profiles")
            except Exception as e:
                print(f"❌ Scraping failed: {e}")
    
    def show_scraping_stats(self):
        """Show scraping statistics."""
        print("\n📊 SCRAPING STATISTICS")
        print("-" * 40)
        
        try:
            stats = google_scraper.get_search_statistics()
            
            print(f"Total Profiles: {stats.get('total_profiles', 0)}")
            print(f"Google Scraped: {stats.get('google_scraped', 0)}")
            
            print("\nBy Location:")
            for location, count in stats.get('by_location', {}).items():
                print(f"  {location}: {count}")
                
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
    
    def cleanup_old_profiles(self):
        """Clean up old profiles."""
        print("\n🧹 Cleaning up old profiles...")
        
        try:
            removed = google_scraper.cleanup_old_profiles(days_old=30)
            print(f"✅ Removed {removed} old profiles")
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
    
    def run_automation_menu(self):
        """Show automation options."""
        print("\n🤖 AUTOMATION ACTIONS")
        print("-" * 40)
        
        options = [
            ["1", "Visit Profiles"],
            ["2", "Send Connection Requests"],
            ["3", "Send Messages"],
            ["4", "Login to LinkedIn"],
            ["5", "Logout from LinkedIn"]
        ]
        
        print(tabulate(options, headers=["Option", "Description"], tablefmt="fancy_grid"))
        
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
    
    def visit_profiles(self):
        """Visit profiles."""
        count = input("Number of profiles to visit (default 10): ").strip()
        count = int(count) if count.isdigit() else 10
        
        print(f"\n👁️  Visiting {count} profiles...")
        
        try:
            result = linkedin_automation.visit_profiles(count)
            print(f"✅ Successfully visited {result} profiles")
        except Exception as e:
            print(f"❌ Profile visits failed: {e}")
    
    def send_connections(self):
        """Send connection requests."""
        count = input("Number of connection requests (default 5): ").strip()
        count = int(count) if count.isdigit() else 5
        
        print(f"\n🤝 Sending {count} connection requests...")
        
        try:
            result = linkedin_automation.send_connection_requests(count)
            print(f"✅ Successfully sent {result} connection requests")
        except Exception as e:
            print(f"❌ Connection requests failed: {e}")
    
    def send_messages(self):
        """Send messages."""
        count = input("Number of messages (default 3): ").strip()
        count = int(count) if count.isdigit() else 3
        
        print(f"\n💬 Sending {count} messages...")
        
        try:
            result = linkedin_automation.send_messages(count)
            print(f"✅ Successfully sent {result} messages")
        except Exception as e:
            print(f"❌ Messaging failed: {e}")
    
    def login_linkedin(self):
        """Login to LinkedIn."""
        print("\n🔐 Logging in to LinkedIn...")
        
        try:
            success = linkedin_auth.login()
            if success:
                print("✅ Successfully logged in")
            else:
                print("❌ Login failed")
        except Exception as e:
            print(f"❌ Login error: {e}")
    
    def logout_linkedin(self):
        """Logout from LinkedIn."""
        print("\n🚪 Logging out from LinkedIn...")
        
        try:
            success = linkedin_auth.logout()
            if success:
                print("✅ Successfully logged out")
            else:
                print("❌ Logout failed")
        except Exception as e:
            print(f"❌ Logout error: {e}")
    
    def run_scheduler_menu(self):
        """Show scheduler options."""
        print("\n⏰ SCHEDULER MANAGEMENT")
        print("-" * 40)
        
        options = [
            ["1", "View Scheduler Status"],
            ["2", "Schedule Daily Scraping"],
            ["3", "Schedule Automation Session"],
            ["4", "View Task History"],
            ["5", "Cleanup Old Tasks"]
        ]
        
        print(tabulate(options, headers=["Option", "Description"], tablefmt="fancy_grid"))
        
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
    
    def show_scheduler_status(self):
        """Show scheduler status."""
        print("\n⏰ SCHEDULER STATUS")
        print("-" * 40)
        
        try:
            status = automation_orchestrator.scheduler.get_scheduler_status()
            
            print(f"Running: {'✅' if status['running'] else '❌'}")
            print(f"Total Tasks: {status['total_tasks']}")
            print(f"Pending Tasks: {status['pending_tasks']}")
            print(f"Within Working Hours: {'✅' if status['within_working_hours'] else '❌'}")
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    def schedule_daily_scraping(self):
        """Schedule daily scraping."""
        location = input("Location (USA/Lahore): ").strip() or "USA"
        hour = input("Hour (0-23, default 8): ").strip()
        hour = int(hour) if hour.isdigit() else 8
        
        print(f"\n📅 Scheduling daily scraping for {location} at {hour}:00...")
        
        try:
            task_id = automation_orchestrator.scheduler.schedule_daily_scraping(location, hour)
            print(f"✅ Task scheduled: {task_id}")
        except Exception as e:
            print(f"❌ Scheduling failed: {e}")
    
    def schedule_automation_session(self):
        """Schedule automation session."""
        duration = input("Duration in minutes (default 60): ").strip()
        duration = int(duration) if duration.isdigit() else 60
        
        print(f"\n🤖 Scheduling automation session for {duration} minutes...")
        
        try:
            task_id = automation_orchestrator.scheduler.schedule_automation_session(duration)
            print(f"✅ Task scheduled: {task_id}")
        except Exception as e:
            print(f"❌ Scheduling failed: {e}")
    
    def show_task_history(self):
        """Show task execution history."""
        print("\n📋 TASK HISTORY")
        print("-" * 40)
        
        try:
            history = automation_orchestrator.scheduler.get_execution_history(10)
            
            if not history:
                print("No recent task history")
                return
            
            for task in history:
                status_emoji = {"completed": "✅", "failed": "❌", "cancelled": "⏹️"}.get(task.status.value, "⏳")
                print(f"{status_emoji} {task.name} - {task.status.value}")
                
        except Exception as e:
            print(f"❌ Error getting history: {e}")
    
    def cleanup_tasks(self):
        """Clean up old tasks."""
        print("\n🧹 Cleaning up old tasks...")
        
        try:
            removed = automation_orchestrator.scheduler.cleanup_completed_tasks()
            print(f"✅ Removed {removed} old tasks")
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
    
    def start_full_automation(self):
        """Start full automation system."""
        print("\n🚀 STARTING FULL AUTOMATION")
        print("-" * 40)
        
        try:
            automation_orchestrator.start_automation()
            print("✅ Full automation system started successfully")
            print("The system will now run automatically during working hours")
        except Exception as e:
            print(f"❌ Failed to start automation: {e}")
    
    def stop_full_automation(self):
        """Stop full automation system."""
        print("\n⏹️  STOPPING FULL AUTOMATION")
        print("-" * 40)
        
        try:
            automation_orchestrator.stop_automation()
            print("✅ Full automation system stopped")
        except Exception as e:
            print(f"❌ Failed to stop automation: {e}")
    
    def show_statistics(self):
        """Show comprehensive statistics."""
        print("\n📈 SYSTEM STATISTICS")
        print("-" * 40)
        
        try:
            system_status = automation_orchestrator.get_system_status()
            
            # Database stats
            db_stats = system_status['database_stats']
            print(f"📊 Database:")
            print(f"  Total Profiles: {db_stats['total_profiles']}")
            print(f"  Unprocessed: {db_stats['unprocessed_profiles']}")
            print(f"  Connected: {db_stats['connected_profiles']}")
            print(f"  Messaged: {db_stats['messaged_profiles']}")
            
            # Daily stats
            daily_stats = system_status['daily_stats']
            print(f"\n📅 Today's Activity:")
            for action, count in daily_stats.items():
                print(f"  {action.capitalize()}: {count}")
            
            # Rate limits
            rate_limits = system_status['rate_limits']
            print(f"\n⏱️  Rate Limits:")
            for action, limits in rate_limits.items():
                print(f"  {action.capitalize()}: {limits['daily_used']}/{limits['daily_limit']}")
                
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    def shutdown(self):
        """Graceful shutdown."""
        try:
            logger.info("Shutting down automation system...")
            automation_orchestrator.stop_automation()
            db_manager.close()
            logger.info("Shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LinkedIn Automation System")
    parser.add_argument("--mode", choices=["interactive", "daemon"], default="interactive",
                       help="Run mode: interactive (CLI) or daemon (background)")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = LinkedInAutomationCLI()
    cli.setup_signal_handlers()
    
    try:
        # Validate configuration
        config.validate_config()
        
        if args.mode == "interactive":
            cli.start_interactive_mode()
        else:
            # Daemon mode - start automation and run in background
            print("🚀 Starting LinkedIn Automation System in daemon mode...")
            automation_orchestrator.start_automation()
            
            print("✅ Automation system started. Press Ctrl+C to stop.")
            
            # Keep running
            try:
                while True:
                    import time
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n🛑 Stopping automation system...")
                cli.shutdown()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()






