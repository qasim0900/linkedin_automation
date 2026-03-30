#!/usr/bin/env python3
"""
Simple Database Setup Script

यह script MongoDB database को easily setup करने के लिए है।
Usage: python setup_database.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_init import DatabaseInitializer

def main():
    print("🚀 LinkedIn Automation Database Setup")
    print("=" * 50)
    
    initializer = DatabaseInitializer()
    
    try:
        success = initializer.initialize_database()
        
        if success:
            print("\n" + "🎉" * 20)
            print("DATABASE SETUP SUCCESSFUL! 🎉")
            print("🎉" * 20)
            print("\nअब आप LinkedIn automation को run कर सकते हैं:")
            print("  python main.py --mode interactive")
            print("  python main.py --mode daemon")
            print("\nDatabase details:")
            print(f"  - Database: linked_connections")
            print(f"  - USA Profiles: usa_google_connections")
            print(f"  - Lahore Profiles: lahore_google_connections")
            print(f"  - USA Messages: usa_linkedin_connections")
            print(f"  - Lahore Messages: lahore_linkedin_connections")
            print(f"  - Activity Log: activity_log")
        else:
            print("\n❌" * 20)
            print("DATABASE SETUP FAILED! ❌")
            print("❌" * 20)
            print("\nPlease check:")
            print("  1. MongoDB is running on your system")
            print("  2. Connection string in .env file is correct")
            print("  3. MongoDB is accessible from your network")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Setup cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        initializer.close_connection()
    
    return 0

if __name__ == "__main__":
    exit(main())
