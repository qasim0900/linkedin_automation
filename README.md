# LinkedIn Automation System

🚀 **A production-ready LinkedIn automation system with human-like behavior, intelligent decision-making, and comprehensive safety features.**

## 🌟 Features

### Core Capabilities
- **🤖 Human-like Behavior**: Realistic typing, scrolling, and interaction patterns
- **🧠 Intelligent Decision Engine**: Smart profile selection and prioritization
- **⏱️ Advanced Rate Limiting**: Multi-level protection against detection
- **📅 Automated Scheduling**: Set-and-forget automation during optimal hours
- **📊 Comprehensive Analytics**: Detailed tracking and reporting

### Automation Features
- **Profile Scraping**: Extract LinkedIn profiles from Google search results
- **Smart Connections**: Send personalized connection requests
- **Intelligent Messaging**: Context-aware message delivery
- **Profile Visits**: Natural profile browsing simulation
- **Session Management**: Persistent login with cookie handling

### Safety & Compliance
- **Anti-Detection**: Undetected Chrome driver with stealth mode
- **Rate Limiting**: Daily, hourly, and cooldown period controls
- **CAPTCHA Handling**: Detection and graceful handling
- **Weekly Limits**: Automatic response to LinkedIn restrictions
- **Error Recovery**: Robust exception handling and retry logic

## 🏗️ Architecture

```
linkedin_automation/
├── config/           # Environment variables and settings
├── database/         # MongoDB connection and data operations
├── scraper/          # Google profile scraping
├── bot/              # LinkedIn automation and authentication
├── services/         # Decision engine and rate limiting
├── scheduler/        # Task scheduling and orchestration
├── utils/            # Human behavior simulation
├── data/             # Data storage (cookies, etc.)
├── logs/             # Application logs
└── main.py           # Entry point and CLI interface
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB
- Chrome/Chromium browser
- LinkedIn account

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linkedin_automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Environment Configuration (.env)**
   ```env
   # LinkedIn Credentials
   LINKEDIN_EMAIL=your_email@example.com
   LINKEDIN_PASSWORD=your_password

   # Database
   MONGO_CONNECTION=mongodb://localhost:27017/
   DATABASE_NAME=linkedin_automation

   # Rate Limits
   MAX_CONNECTIONS_PER_DAY=20
   MAX_MESSAGES_PER_DAY=15
   MAX_PROFILE_VISITS_PER_DAY=50

   # Behavior Settings
   MIN_DELAY_SECONDS=2.0
   MAX_DELAY_SECONDS=8.0
   HEADLESS_MODE=false
   ```

### Running the System

#### Interactive Mode (Recommended for beginners)
```bash
python main.py --mode interactive
```

#### Daemon Mode (Background automation)
```bash
python main.py --mode daemon
```

## 📖 Usage Guide

### Interactive CLI Interface

The system provides a comprehensive CLI with the following options:

1. **📊 System Status** - Monitor database, authentication, and rate limits
2. **🔍 Profile Scraping** - Scrape profiles from Google search
3. **🤖 Automation Actions** - Manual control of connections, messages, visits
4. **⏰ Scheduler Management** - Configure automated tasks
5. **🚀 Start Full Automation** - Enable complete automation system
6. **⏹️ Stop Full Automation** - Safely stop the system
7. **📈 Statistics & Reports** - View comprehensive analytics

### Example Workflows

#### Basic Profile Scraping
```bash
# Start interactive mode
python main.py

# Select option 2 (Profile Scraping)
# Select option 1 (Scrape USA Profiles)
# System will scrape LinkedIn profiles from Google search results
```

#### Automated Connection Building
```bash
# Start interactive mode
python main.py

# Select option 5 (Start Full Automation)
# System will automatically:
# - Scrape new profiles
# - Send connection requests
# - Visit profiles naturally
# - Send follow-up messages
# - Respect all rate limits
```

#### Custom Query Scraping
```bash
# In the scraping menu, select option 3
# Enter custom query: "site:linkedin.com/in software engineer New York"
# System will scrape profiles matching your criteria
```

## 🧠 Intelligent Features

### Human Behavior Simulation
- **Random Delays**: Variable timing between actions (2-8 seconds)
- **Natural Typing**: Character-by-character typing with realistic speed
- **Mouse Movement**: Random cursor movements and scroll patterns
- **Reading Simulation**: Variable time spent "reading" profiles
- **Break Periods**: Automated breaks after sustained activity

### Smart Profile Selection
- **Relevance Scoring**: Profiles scored by location, title, company
- **Connection Potential**: Assessment of profile quality
- **Activity Timing**: Optimal times for different actions
- **Deduplication**: Intelligent duplicate detection and handling

### Rate Limiting System
- **Daily Limits**: Maximum actions per day (configurable)
- **Hourly Limits**: Actions per hour restrictions
- **Cooldown Periods**: Minimum time between similar actions
- **Weekly Limits**: Automatic response to LinkedIn restrictions

## 📊 Analytics & Monitoring

### Activity Tracking
- All actions logged with timestamps
- Success/failure rates tracked
- Profile engagement metrics
- Connection and message statistics

### Rate Limit Monitoring
- Real-time limit status
- Time until next available action
- Daily/hourly usage tracking
- Automatic limit compliance

### Performance Metrics
- Profile processing speed
- Success rates by action type
- Error frequency and types
- System health indicators

## ⚙️ Configuration

### Rate Limits
```python
# Daily limits
MAX_CONNECTIONS_PER_DAY = 20
MAX_MESSAGES_PER_DAY = 15
MAX_PROFILE_VISITS_PER_DAY = 50

# Hourly limits
CONNECTIONS_PER_HOUR = 5
MESSAGES_PER_HOUR = 3
VISITS_PER_HOUR = 10
```

### Behavior Settings
```python
# Timing (seconds)
MIN_DELAY_SECONDS = 2.0
MAX_DELAY_SECONDS = 8.0
MIN_TYPING_DELAY = 0.05
MAX_TYPING_DELAY = 0.15

# Scheduling
AUTOMATION_START_HOUR = 9
AUTOMATION_END_HOUR = 18
```

### Browser Settings
```python
WINDOW_SIZE = (1600, 900)
HEADLESS_MODE = False
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
```

## 🔒 Safety & Compliance

### Anti-Detection Measures
- **Undetected Chrome**: Advanced browser fingerprinting avoidance
- **Stealth Mode**: Automation detection bypass
- **Random Patterns**: Unpredictable behavior sequences
- **Session Management**: Natural login/logout cycles

### LinkedIn Compliance
- **Weekly Limit Handling**: Automatic response to restrictions
- **CAPTCHA Detection**: Graceful handling of verification
- **Rate Limiting**: Strict adherence to platform limits
- **Error Recovery**: Robust handling of platform changes

### Data Protection
- **Local Storage**: All data stored locally in MongoDB
- **Cookie Security**: Encrypted session storage
- **Log Rotation**: Automatic log file management
- **Privacy Focused**: No data shared with third parties

## 🐛 Troubleshooting

### Common Issues

#### Login Problems
```bash
# Check credentials in .env file
# Verify LinkedIn account is active
# Try manual login first
```

#### Chrome Driver Issues
```bash
# Update Chrome browser
# Check Chrome version compatibility
# Try running in non-headless mode
```

#### MongoDB Connection
```bash
# Verify MongoDB is running
# Check connection string in .env
# Ensure database permissions
```

#### Rate Limit Issues
```bash
# Check daily limits in configuration
# Review activity logs
# Wait for cooldown periods
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

### Log Files
```bash
# View application logs
tail -f logs/app.log

# Check for errors
grep ERROR logs/app.log
```

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Code formatting
black .
flake8 .
```

### Code Standards
- Follow PEP 8 style guidelines
- Add comprehensive logging
- Include error handling
- Write unit tests
- Document functions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

**Important**: This tool is for educational and personal use only. Users are responsible for:
- Complying with LinkedIn's Terms of Service
- Respecting rate limits and platform policies
- Using ethically and responsibly
- Understanding local automation laws

The authors are not responsible for any misuse or consequences of using this software.

## 🆘 Support

### Getting Help
- Check the troubleshooting section
- Review log files for errors
- Verify configuration settings
- Test with smaller batches first

### Feature Requests
- Open an issue with detailed description
- Include use case and expected behavior
- Provide configuration examples

### Bug Reports
- Include error messages and logs
- Describe reproduction steps
- Specify environment details

---

**Built with ❤️ for professional networking automation**