import os
import json
import asyncio
import re
import logging
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Config
API_ID = 12345678  # Replace
API_HASH = 'YOUR_API_HASH_HERE'  # Replace
DESTINATION_CHANNEL = -1000000000000  # Replace

SOURCES_FILE = "forwarder_sources.txt"
PROGRESS_FILE = "forwarder_progress.json"
WATERMARK = "@joab_movies"

client = TelegramClient('userbot_session', API_ID, API_HASH)

def get_source_channels():
    sources = [-1000000000000] # Hardcoded fallback
    
    if os.path.exists(SOURCES_FILE):
        with open(SOURCES_FILE, "r") as f:
            for line in f.read().splitlines():
                if not line: continue
                
                try:
                    sources.append(int(line))
                except ValueError:
                    sources.append(line)
                    
    return list(set(sources))

def load_state():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(state, f)

def format_caption(text):
    if not text:
        return f"\n\n{WATERMARK}"
        
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)
    text = re.sub(r'(https?://\S+|www\.\S+|t\.me/\S+)', '', text).strip()
    return f"{text}\n\n{WATERMARK}"

SOURCE_CHANNELS = get_source_channels()

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def live_forward_handler(event):
    if not event.message.media:
        return
        
    try:
        new_caption = format_caption(event.message.text)
        await client.send_message(DESTINATION_CHANNEL, file=event.message.media, message=new_caption)
        logger.info(f"Forwarded live media from {event.chat_id} (Msg ID: {event.message.id})")
        
        # Update high-water mark
        state = load_state()
        chat_id = str(event.chat_id)
        if event.message.id > state.get(chat_id, 0):
            state[chat_id] = event.message.id
            save_state(state)
            
    except Exception as e:
        logger.error(f"Failed to forward live message: {e}")

async def sync_history():
    state = load_state()
    total_synced = 0

    logger.info(f"Starting historical sync for {len(SOURCE_CHANNELS)} sources...")

    for source in SOURCE_CHANNELS:
        try:
            entity = await client.get_entity(source)
            source_id = str(entity.id)
            last_id = state.get(source_id, 0)
            
            logger.info(f"Syncing source {source_id} starting from msg_id {last_id}")

            async for message in client.iter_messages(entity, min_id=last_id, reverse=True):
                if not message.media:
                    continue
                    
                try:
                    new_caption = format_caption(message.text)
                    await client.send_message(DESTINATION_CHANNEL, file=message.media, message=new_caption)
                    total_synced += 1
                    
                    state[source_id] = message.id
                    save_state(state)
                    
                    # Rate limit pacing
                    await asyncio.sleep(15)

                except FloodWaitError as e:
                    logger.warning(f"Rate limit hit. Sleeping for {e.seconds}s")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    logger.error(f"Error processing historical msg {message.id}: {e}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            logger.error(f"Failed to access source {source}: {e}")

    logger.info(f"Historical sync complete. Total media forwarded: {total_synced}")

async def main():
    await client.start()
    logger.info("Client authenticated and running.")
    
    await sync_history()
    
    logger.info("Switching to live event listener mode.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
