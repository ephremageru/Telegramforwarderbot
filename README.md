👑 13-Bot Empire: Watchdog & Universal Forwarder

￼ ￼ ￼ ￼

Welcome to the 13-Bot Empire repository! This project contains a production-grade Telegram automation platform designed for massive channel management, media scraping, and seamless content forwarding.

Built with enterprise scalability in mind, this architecture handles everything from dynamic state management and API rate-limit mitigation to real-time server observability across a fleet of up to 13 managed Python processes.

📖 Table of Contents

System Architecture

Tech Stack & Libraries

Deep Dive: Core Components

Engineering Challenges Solved

Installation & Deployment

Configuration

Usage & Commands

Monitoring & Logs

Future Roadmap

Security Notice

🏗️ System Architecture

The project is divided into an orchestration layer (Watchdog) and an execution layer (Forwarders).

This separation of concerns ensures that the dashboard remains responsive even while bots process gigabytes of media.

[ Admin User ] │ (Sends Inline Keyboard Commands) ▼ ┌────────────────────────────────────────────────────────┐ │ WATCHDOG ORCHESTRATOR │ │ - Parses OS-level metrics (psutil/subprocess) │ │ - Manages SQLite/JSON configurations │ │ - Spawns/Kills child processes │ └────────────────────────────────────────────────────────┘ │ ▼ ┌────────────────────────────────────────────────────────┐ │ FORWARDER FLEET (1 to 13) │ │ │ │ [Bot 1: Action] [Bot 2: Horror] [Bot 3: Comedy] │ └────────────────────────────────────────────────────────┘ │ ├─► Source Channels (24/7 Listening & Bulk Sync) ├─► Regex Content Filter (Strip URLs/Usernames) ├─► Branding Engine (Append Custom @Username) ▼ [ Destination Channel(s) ] 

💻 Tech Stack & Libraries

Language: Python 3.8+

Core Framework: Telethon

Concurrency: AsyncIO

Performance: cryptg

State Management: JSON Persistence

Deployment: Linux / VPS (Ubuntu/Debian Recommended)

🔍 Deep Dive: Core Components

1. Watchdog Dashboard (watchdog.py)

Interactive Telegram-based server management panel.

Features

Process Management

Start/stop/restart up to 13 Python bots

Uses pkill, nohup, background execution

Server Observability

CPU / RAM / Disk monitoring

Live health checks without SSH

Log Aggregation

Reads latest log lines

Detects exceptions/tracebacks

Dynamic Source Management

Add/remove forwarding sources live

2. Universal Forwarder (forwarder.py)

Asynchronous forwarding engine for all Telegram content types.

Features

Historical Bulk Copy

Fetches missed channel history on startup

Uses dynamic min_id

Persistent Memory

Saves progress to *_progress.json

Prevents duplicate forwards

Sanitization Pipeline

Removes usernames/links via Regex

Cleans media captions before forwarding

24/7 Live Listener

Event-driven forwarding with Telethon

🧠 Engineering Challenges Solved

Graceful Rate-Limit Handling

Intercepts FloodWaitError

Sleeps asynchronously using asyncio.sleep()

Persistent Deduplication

File-based state tracker prevents duplication after restart

Scalable Orchestration

Centralized Watchdog manages 13 independent bots

Bandwidth Optimization

cryptg accelerates Telegram media encryption/decryption

🚀 Installation & Deployment

Step 1: Clone Repository

git clone https://github.com/YourUsername/13-Bot-Empire.git cd 13-Bot-Empire 

Step 2: Create Virtual Environment

python3 -m venv venv source venv/bin/activate 

Windows:

venv\Scripts\activate 

Step 3: Install Dependencies

pip install -r requirements.txt 

⚙️ Configuration

Create .env file:

API_ID=12345678 API_HASH=your_api_hash_here BOT_TOKEN=your_watchdog_bot_token_here ADMIN_ID=1234567890 DEST_ID=-1001234567890 

▶️ Running the System

Start Watchdog

nohup python3 watchdog.py & 

Start Forwarder

python3 forwarder.py 

📋 Usage & Commands

Watchdog Dashboard

Use:

/start /menu 

To open the Telegram inline dashboard.

Forwarder Admin Commands

CommandDescriptionExample#addAdd source channel#add @ActionMovies#removeRemove source channel#remove @ActionMovies#listList tracked sources#list#helpHelp menu#help 

📈 Monitoring & Logs

Each bot writes to dedicated .log file

Logs accessible via Watchdog dashboard

Remote traceback detection supported

🗺️ Future Roadmap

[ ] Migrate JSON/TXT storage to SQLite/MongoDB

[ ] Add image/video watermarking engine

[ ] Integrate auto-translation pipeline

[ ] Add Web Dashboard Interface

[ ] Docker / Container Deployment Support

⚠️ Security Notice

Secrets Management

Never hardcode:

API_ID

API_HASH

BOT_TOKEN

Use environment variables only.

Session Protection

Telethon .session files provide account access.

Never upload them publicly.

Ensure .gitignore blocks:

*.session .env __pycache__/ *.log 

📜 License

MIT License

Built with architecture in mind. Designed for the 13-Bot Empire.


