import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto

# --- Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Environment Variables ---
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE_NUMBER = os.getenv('TELEGRAM_PHONE_NUMBER')
SESSION_NAME = "telegram_session"

# --- Configuration ---
CHANNELS = [
    'Chemedpharmacy',
    'lobelia4cosmetics',
    'tikvahpharma',
]

RAW_DATA_PATH = "data/raw/telegram_messages"
IMAGE_DATA_PATH = "data/images"

def main():
    """Main function to scrape data from Telegram channels."""
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    with client:
        logging.info("Telegram client connected.")
        for channel_name in CHANNELS:
            try:
                logging.info(f"Scraping channel: {channel_name}")
                
                # Create partitioned directory for today's data
                today_str = datetime.now().strftime('%Y-%m-%d')
                channel_data_path = os.path.join(RAW_DATA_PATH, today_str, channel_name)
                os.makedirs(channel_data_path, exist_ok=True)
                
                channel_image_path = os.path.join(IMAGE_DATA_PATH, channel_name)
                os.makedirs(channel_image_path, exist_ok=True)

                for message in client.iter_messages(channel_name, limit=200): # Adjust limit as needed
                    if message.id and message.date:
                        message_data = {
                            "message_id": message.id,
                            "channel_name": channel_name,
                            "text": message.text,
                            "date": message.date.isoformat(),
                            "views": message.views,
                            "has_image": isinstance(message.media, MessageMediaPhoto)
                        }

                        # Save message metadata as JSON
                        file_path = os.path.join(channel_data_path, f"{message.id}.json")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(message_data, f, ensure_ascii=False, indent=4)
                        
                        # Download image if it exists
                        if message_data["has_image"]:
                            image_file_path = os.path.join(channel_image_path, f"{message.id}.jpg")
                            if not os.path.exists(image_file_path):
                                message.download_media(file=image_file_path)
                                logging.info(f"Downloaded image {message.id}.jpg from {channel_name}")

            except Exception as e:
                logging.error(f"Failed to scrape {channel_name}: {e}")

    logging.info("Scraping complete.")

if __name__ == "__main__":
    main()