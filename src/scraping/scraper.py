import os
import json
import asyncio
from datetime import datetime
import logging
from dotenv import load_dotenv
from telethon.sync import TelegramClient

# --- Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Credentials & Config ---
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = os.getenv('TELEGRAM_SESSION_NAME')
CHANNELS = ['CheMed123', 'lobelia4cosmetics', 'tikvahpharma']

# --- Main Scraping Logic ---
async def scrape_channel(client, channel_name):
    """Scrapes a single Telegram channel and saves messages and images."""
    today_str = datetime.now().strftime('%Y-%m-%d')
    messages_path = f"data/raw/telegram_messages/{channel_name}/{today_str}"
    images_path = f"data/raw/telegram_images/{channel_name}/{today_str}"
    
    os.makedirs(messages_path, exist_ok=True)
    os.makedirs(images_path, exist_ok=True)
    
    logging.info(f"Scraping channel: {channel_name}")
    
    try:
        async for message in client.iter_messages(channel_name, limit=200): 
            if message.text or message.photo:
                message_data = {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'text': message.text,
                    'sender_id': message.sender_id,
                    'channel': channel_name,
                    'views': message.views,
                    'has_photo': message.photo is not None
                }
                
                # Save message as JSON
                message_file_path = os.path.join(messages_path, f"{message.id}.json")
                with open(message_file_path, 'w', encoding='utf-8') as f:
                    json.dump(message_data, f, ensure_ascii=False, indent=4)

                # Download image if it exists
                if message.photo:
                    image_file_path = os.path.join(images_path, f"{message.id}.jpg")
                    if not os.path.exists(image_file_path): # Avoid re-downloading
                        await message.download_media(file=image_file_path)
                        logging.info(f"Downloaded image {message.id}.jpg from {channel_name}")

    except Exception as e:
        logging.error(f"Error scraping {channel_name}: {e}")

async def main():
    """Main function to orchestrate scraping across all channels."""
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)
    logging.info("Scraping finished.")

if __name__ == "__main__":
   
    asyncio.run(main())