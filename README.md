```
```
# 👑 13-Bot Empire: Watchdog & Universal Forwarder

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Telethon](https://img.shields.io/badge/Library-Telethon-lightgrey.svg)
![AsyncIO](https://img.shields.io/badge/Concurrency-AsyncIO-success.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Welcome to the **13-Bot Empire** repository! This project contains a production-grade Telegram automation platform designed for massive channel management, media scraping, and seamless content forwarding. 

Built with enterprise scalability in mind, this architecture handles everything from dynamic state management and API rate-limit mitigation to real-time server observability across a fleet of up to 13 managed Python processes.

---

## 📖 Table of Contents
1. [System Architecture](#-system-architecture)
2. [Tech Stack & Libraries](#-tech-stack--libraries)
3. [Deep Dive: Core Components](#-deep-dive-core-components)
4. [Engineering Challenges Solved](#-engineering-challenges-solved)
5. [Installation & Deployment](#-installation--deployment)
6. [Configuration](#️-configuration)
7. [Usage & Commands](#-usage--commands)
8. [Monitoring & Logs](#-monitoring--logs)
9. [Future Roadmap](#-future-roadmap)
10. [Security Notice](#️-security-notice)

---

## 🏗️ System Architecture

The project is divided into an orchestration layer (Watchdog) and an execution layer (Forwarders). This separation of concerns ensures that the dashboard remains responsive even while bots process gigabytes of media.

```text
[ Admin User ]
       │ (Sends Inline Keyboard Commands)
       ▼
┌────────────────────────────────────────────────────────┐
│               WATCHDOG ORCHESTRATOR                    │
│  - Parses OS-level metrics (psutil/subprocess)         │
│  - Manages SQLite/JSON configurations                  │
│  - Spawns/Kills child processes                        │
└────────────────────────────────────────────────────────┘
       │
       ▼ (Spawns & Orchestrates)
┌────────────────────────────────────────────────────────┐
│               FORWARDER FLEET (1 to 13)                │
│                                                        │
│  [Bot 1: Action]  [Bot 2: Horror]  [Bot 3: Comedy]     │
└────────────────────────────────────────────────────────┘
       │
       ├─► Source Channels (24/7 Listening & Bulk Sync)
       ├─► Regex Content Filter (Strip URLs/Usernames)
       ├─► Branding Engine (Append Custom @Username)
       │
       ▼
[ Destination Channel(s) ]
```

---

## 💻 Tech Stack & Libraries

* **Language:** Python 3.8+
* **Core Framework:** Telethon
* **Concurrency:** AsyncIO
* **Performance:** cryptg
* **State Management:** JSON Persistence
* **Deployment:** Linux / VPS (Ubuntu/Debian Recommended)

---

## 🔍 Deep Dive: Core Components

### 1. Watchdog Dashboard (`watchdog.py`)
Interactive Telegram-based server management panel.

**Features:**
* **Process Management:** Start/stop/restart up to 13 Python bots (Uses `pkill`, `nohup`, background execution).
* **Server Observability:** CPU / RAM / Disk monitoring with live health checks without SSH.
* **Log Aggregation:** Reads latest log lines and detects exceptions/tracebacks.
* **Dynamic Source Management:** Add/remove forwarding sources live.

### 2. Universal Forwarder (`forwarder.py`)
Asynchronous forwarding engine for all Telegram content types.

**Features:**
* **Historical Bulk Copy:** Fetches missed channel history on startup using dynamic `min_id`.
* **Persistent Memory:** Saves progress to `*_progress.json` to prevent duplicate forwards.
* **Sanitization Pipeline:** Removes usernames/links via Regex and cleans media captions before forwarding.
* **24/7 Live Listener:** Event-driven forwarding with Telethon.

---

## 🧠 Engineering Challenges Solved

* **Graceful Rate-Limit Handling:** Intercepts `FloodWaitError` and sleeps asynchronously using `asyncio.sleep()`.
* **Persistent Deduplication:** File-based state tracker prevents duplication after restart.
* **Scalable Orchestration:** Centralized Watchdog manages 13 independent bots.
* **Bandwidth Optimization:** `cryptg` accelerates Telegram media encryption/decryption.

---

## 🚀 Installation & Deployment

**Step 1: Clone Repository**
```bash
git clone [https://github.com/YourUsername/13-Bot-Empire.git](https://github.com/YourUsername/13-Bot-Empire.git)
cd 13-Bot-Empire
```

**Step 2: Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```
*(Windows: `venv\Scripts\activate`)*

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a `.env` file in the root directory:
```env
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=your_watchdog_bot_token_here
ADMIN_ID=1234567890
DEST_ID=-1001234567890
```

---

## ▶️ Running the System

**Start Watchdog:**
```bash
nohup python3 watchdog.py &
```

**Start Forwarder:**
```bash
python3 forwarder.py
```

---

## 📋 Usage & Commands

### Watchdog Dashboard
Use `/start` or `/menu` to open the Telegram inline dashboard.

### Forwarder Admin Commands
| Command | Description | Example |
|---------|-------------|---------|
| `#add` | Add source channel | `#add @ActionMovies` |
| `#remove` | Remove source channel | `#remove @ActionMovies` |
| `#list` | List tracked sources | `#list` |
| `#help` | Help menu | `#help` |

---

## 📈 Monitoring & Logs

* Each bot writes to a dedicated `.log` file.
* Logs are accessible via the Watchdog dashboard.
* Remote traceback detection supported.

---

## 🗺️ Future Roadmap

- [ ] Migrate JSON/TXT storage to SQLite/MongoDB
- [ ] Add image/video watermarking engine
- [ ] Integrate auto-translation pipeline
- [ ] Add Web Dashboard Interface
- [ ] Docker / Container Deployment Support

---

## ⚠️ Security Notice

### Secrets Management
Never hardcode `API_ID`, `API_HASH`, or `BOT_TOKEN`. Use environment variables only.

### Session Protection
Telethon `.session` files provide account access. **Never upload them publicly.** Ensure your `.gitignore` blocks them:

```text
*.session
*.session-journal
.env
__pycache__/
*.log
```

---

## 📜 License
MIT License

*Built with architecture in mind. Designed for the 13-Bot Empire.*
```
