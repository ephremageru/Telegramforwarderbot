import os
import json
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
DESTINATION_ID = os.getenv('DEST_ID')

if not all([API_ID, API_HASH, BOT_TOKEN, ADMIN_ID, DESTINATION_ID]):
    raise ValueError("Missing required environment variables in .env")

# Type cast IDs safely
ADMIN_ID = int(ADMIN_ID)
try:
    DESTINATION_ID = int(DESTINATION_ID) if DESTINATION_ID.lstrip('-').isdigit() else DESTINATION_ID
except ValueError:
    pass

SOURCES_FILE = 'sources.json'

def load_sources():
    if not os.path.exists(SOURCES_FILE):
        return []
    with open(SOURCES_FILE, 'r') as f:
        return json.load(f)

def save_sources(sources):
    with open(SOURCES_FILE, 'w') as f:
        json.dump(sources, f, indent=4)

active_sources = load_sources()
client = TelegramClient('forwarder_session', int(API_ID), API_HASH)

@client.on(events.NewMessage(chats=ADMIN_ID))
async def admin_handler(event):
    text = event.raw_text.strip()
    global active_sources

    if text.startswith('#add '):
        new_source = text.split(' ', 1)[1].strip()
        
        if "t.me/" in new_source:
            new_source = new_source.split("t.me/")[1]
            if not new_source.startswith('@') and not new_source.startswith('+'):
                new_source = '@' + new_source

        if new_source in active_sources:
            await event.reply(f"Target `{new_source}` is already active.")
            return

        active_sources.append(new_source)
        save_sources(active_sources)
        await event.reply(f"Source added: `{new_source}`")
        logger.info(f"Source added by admin: {new_source}")

    elif text.startswith('#remove '):
        target = text.split(' ', 1)[1].strip()
        
        if target in active_sources:
            active_sources.remove(target)
            save_sources(active_sources)
            await event.reply(f"Source removed: `{target}`")
            logger.info(f"Source removed by admin: {target}")
        else:
            await event.reply(f"Target `{target}` not found in active list.")

    elif text == '#list':
        if not active_sources:
            await event.reply("The source list is currently empty.")
            return
            
        msg = "**Active Sources:**\n" + "\n".join([f"- `{src}`" for src in active_sources])
        await event.reply(msg)

    elif text in ('#help', '/start'):
        help_text = (
            "**Forwarder Admin Panel**\n\n"
            "`#add @channel` - Add a new source\n"
            "`#remove @channel` - Remove a source\n"
            "`#list` - View active sources"
        )
        await event.reply(help_text)

@client.on(events.NewMessage())
async def forwarder_engine(event):
    if not event.is_channel and not event.is_group:
        return 

    try:
        chat = await event.get_chat()
        chat_username = f"@{chat.username}" if getattr(chat, 'username', None) else None
        chat_id = str(chat.id)

        is_source = bool(
            (chat_username and chat_username in active_sources) or 
            (chat_id in active_sources or f"-100{chat_id}" in active_sources)
        )

        if is_source:
            await client.forward_messages(DESTINATION_ID, event.message)
            logger.info(f"Forwarded message from {chat_username or chat_id}")

    except Exception as e:
        logger.error(f"Forwarding error: {e}")

if __name__ == '__main__':
    logger.info(f"Starting bot. Tracking {len(active_sources)} sources.")
    client.start(bot_token=BOT_TOKEN)
    logger.info("Bot is active and listening.")
    client.run_until_disconnected()
