import os
import json
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events

# ==========================================
# ⚙️ SYSTEM CONFIGURATION
# ==========================================
# Load environment variables safely
load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')          # Only this user can use #add
DESTINATION_ID = os.getenv('DEST_ID')     # Where the messages go

# Ensure critical variables exist
if not all([API_ID, API_HASH, BOT_TOKEN, ADMIN_ID, DESTINATION_ID]):
    raise ValueError("🚨 Missing environment variables! Check your .env file.")

# Convert IDs to integers
try:
    ADMIN_ID = int(ADMIN_ID)
    # Handle destination ID (can be negative for channels, or a string username like '@mychannel')
    DESTINATION_ID = int(DESTINATION_ID) if DESTINATION_ID.lstrip('-').isdigit() else DESTINATION_ID
except ValueError:
    pass

# Setup Professional Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("ProForwarder")

# Initialize Telegram Client
client = TelegramClient('forwarder_session', int(API_ID), API_HASH)

# ==========================================
# 📂 SOURCE MANAGEMENT (JSON DB)
# ==========================================
SOURCES_FILE = 'sources.json'

def load_sources():
    """Load sources from JSON to persist memory across restarts."""
    if not os.path.exists(SOURCES_FILE):
        return []
    with open(SOURCES_FILE, 'r') as f:
        return json.load(f)

def save_sources(sources):
    """Save sources to JSON."""
    with open(SOURCES_FILE, 'w') as f:
        json.dump(sources, f, indent=4)

# Load into memory on boot
active_sources = load_sources()

# ==========================================
# 🛡️ ADMIN COMMAND HANDLER
# ==========================================
@client.on(events.NewMessage(chats=ADMIN_ID))
async def admin_handler(event):
    """Handles commands sent by the admin via private message."""
    text = event.raw_text.strip()
    global active_sources

    # COMMAND: #add <channel>
    if text.startswith('#add '):
        new_source = text.split(' ', 1)[1].strip()
        
        # Clean up input (handle full links or just usernames)
        if "t.me/" in new_source:
            new_source = new_source.split("t.me/")[1]
            if not new_source.startswith('@') and not new_source.startswith('+'):
                new_source = '@' + new_source

        if new_source in active_sources:
            await event.reply(f"⚠️ `{new_source}` is already in the forwarding list.")
        else:
            active_sources.append(new_source)
            save_sources(active_sources)
            await event.reply(f"✅ **Source Added!**\nNow forwarding messages from `{new_source}`.")
            logger.info(f"Admin added new source: {new_source}")

    # COMMAND: #remove <channel>
    elif text.startswith('#remove '):
        target = text.split(' ', 1)[1].strip()
        if target in active_sources:
            active_sources.remove(target)
            save_sources(active_sources)
            await event.reply(f"🗑 **Source Removed.**\nStopped forwarding from `{target}`.")
            logger.info(f"Admin removed source: {target}")
        else:
            await event.reply(f"❌ Cannot find `{target}` in the active sources.")

    # COMMAND: #list
    elif text == '#list':
        if not active_sources:
            await event.reply("📂 **Your source list is currently empty.**")
        else:
            msg = "📋 **Active Forwarding Sources:**\n"
            for src in active_sources:
                msg += f"• `{src}`\n"
            await event.reply(msg)

    # COMMAND: #help
    elif text == '#help' or text == '/start':
        help_text = (
            "👑 **Pro Forwarder Bot - Admin Panel** 👑\n\n"
            "Use the following commands to manage your sources:\n"
            "▫️ `#add @channel_username` - Add a new channel\n"
            "▫️ `#remove @channel_username` - Remove a channel\n"
            "▫️ `#list` - View all active sources"
        )
        await event.reply(help_text)

# ==========================================
# 🚀 CORE FORWARDING ENGINE
# ==========================================
@client.on(events.NewMessage())
async def forwarder_engine(event):
    """Listens to all incoming messages and forwards if they match our sources."""
    if not event.is_channel and not event.is_group:
        return # Ignore private messages

    try:
        # Get the chat information
        chat = await event.get_chat()
        chat_username = f"@{chat.username}" if getattr(chat, 'username', None) else None
        chat_id = str(chat.id)

        # Check if the incoming message is from one of our saved sources
        is_source = False
        if chat_username and chat_username in active_sources:
            is_source = True
        elif chat_id in active_sources or f"-100{chat_id}" in active_sources:
            is_source = True

        if is_source:
            # Forward the message to the destination
            await client.forward_messages(DESTINATION_ID, event.message)
            logger.info(f"Forwarded message from {chat_username or chat_id}")

    except Exception as e:
        logger.error(f"Error forwarding message: {e}")

# ==========================================
# 🔌 STARTUP ROUTINE
# ==========================================
if __name__ == '__main__':
    logger.info("Starting Pro Forwarder Bot...")
    logger.info(f"Currently tracking {len(active_sources)} sources.")
    client.start(bot_token=BOT_TOKEN)
    logger.info("Bot is online and listening!")
    client.run_until_disconnected()
