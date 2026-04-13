import os
import json
import asyncio
import re
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# ==========================================
# 1. CONFIGURATION
# ==========================================
# 🛑 SECRETS SCRUBBED FOR GITHUB 🛑
# Replace these with your actual details when running locally.
API_ID = 12345678 # REPLACE WITH YOUR API ID
API_HASH = 'YOUR_API_HASH_HERE' # REPLACE WITH YOUR API HASH

# Files for sources and saving progress
SOURCES_FILE = "forwarder_sources.txt"  
PROGRESS_FILE = "forwarder_progress.json"
DESTINATION_CHANNEL = -1000000000000 # REPLACE WITH YOUR DESTINATION CHANNEL ID

# ==========================================
# 2. HELPER FUNCTIONS (Sources & Progress)
# ==========================================
def load_sources():
    sources = []
    # Adding your original hardcoded source so you don't lose it
    sources.append(-1000000000000) # REPLACE WITH YOUR HARDCODED SOURCE ID
    
    if os.path.exists(SOURCES_FILE):
        with open(SOURCES_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    sources.append(int(line))
                except ValueError:
                    sources.append(line)
    return list(set(sources))

SOURCE_CHANNELS = load_sources()

def load_progress():
    """Loads the saved message IDs so the bot remembers where it left off."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_progress(progress_dict):
    """Saves the current progress to a file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress_dict, f)

# ==========================================
# 3. INITIALIZE CLIENT
# ==========================================
client = TelegramClient('userbot_session', API_ID, API_HASH)

# ==========================================
# 4. 24/7 LISTENER LOGIC (For brand new posts)
# ==========================================
@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handler(event):
    if event.message.media: 
        try:
            original_text = event.message.text or ""
            
            # --- Link & Username Removal ---
            clean_text = re.sub(r'@[A-Za-z0-9_]+', '', original_text)
            clean_text = re.sub(r'(https?://\S+|www\.\S+|t\.me/\S+)', '', clean_text).strip()
            new_text = f"{clean_text}\n\n@joab_movies"

            await client.send_message(DESTINATION_CHANNEL, file=event.message.media, text=new_text)
            print(f"✅ Live Update: New movie successfully forwarded!")
            
            # Save progress so we don't copy this again on restart
            progress = load_progress()
            chat_id = str(event.chat_id)
            if event.message.id > progress.get(chat_id, 0):
                progress[chat_id] = event.message.id
                save_progress(progress)
            
        except Exception as e:
            print(f"❌ Error copying live message: {e}")

# ==========================================
# 5. STARTUP SEQUENCE
# ==========================================
async def main():
    await client.start()
    print("🚀 Forwarder Bot Started!")
    print(f"📡 Actively monitoring {len(SOURCE_CHANNELS)} source(s).")

    # Load our saved memory
    progress = load_progress()

    # --- STEP 1: RESUME BULK COPY ---
    print("⏳ Checking for missed movies since last run. (15 sec delay per message)...")
    total_messages_copied = 0

    for source in SOURCE_CHANNELS:
        try:
            # We fetch the exact numeric ID of the source channel so our memory file is accurate
            entity = await client.get_entity(source)
            source_id = str(entity.id)
            
            # Find out where we left off (default to 0 if this is the first time)
            last_copied_id = progress.get(source_id, 0)
            
            if last_copied_id == 0:
                print(f"\n🔄 Connecting to {source} (Starting from the VERY BEGINNING)")
            else:
                print(f"\n🔄 Connecting to {source} (Resuming from message ID: {last_copied_id})")

            # min_id ensures we ONLY fetch messages newer than our last saved position
            async for message in client.iter_messages(entity, min_id=last_copied_id, reverse=True):
                if message.media:
                    try:
                        original_text = message.text or ""
                        
                        # --- Link & Username Removal ---
                        clean_text = re.sub(r'@[A-Za-z0-9_]+', '', original_text)
                        clean_text = re.sub(r'(https?://\S+|www\.\S+|t\.me/\S+)', '', clean_text).strip()
                        new_text = f"{clean_text}\n\n@joab_movies"

                        await client.send_message(DESTINATION_CHANNEL, file=message.media, text=new_text)
                        total_messages_copied += 1
                        print(f"✅ Copied past message {total_messages_copied} (ID: {message.id})")

                        # Save our exact spot after a successful copy
                        progress[source_id] = message.id
                        save_progress(progress)

                        # Crucial 15-second delay to prevent rate limits
                        await asyncio.sleep(15)

                    except FloodWaitError as e:
                        print(f"⚠️ Telegram rate limit hit. Pausing for {e.seconds} seconds...")
                        await asyncio.sleep(e.seconds)
                    except Exception as e:
                        print(f"❌ Error copying past message {message.id}: {e}")
                        await asyncio.sleep(5)
                        
        except Exception as e:
            print(f"❌ Could not process source {source}. Error: {e}")

    print(f"\n🎉 Sync complete! Total historical messages caught up on: {total_messages_copied}")

    # --- STEP 2: RUN 24/7 LISTENER ---
    print("✨ Now switching to Live Standby. Waiting for new messages 24/7...")
    await client.run_until_disconnected()

# ==========================================
# 6. RUN THE SCRIPT
# ==========================================
if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())