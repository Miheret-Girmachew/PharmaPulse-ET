import os
import json
import psycopg2
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- DB Connection Details ---
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )

def setup_database(conn):
    """Sets up the necessary schema and table."""
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.telegram_messages (
                message_id BIGINT PRIMARY KEY,
                channel VARCHAR(255),
                data JSONB,
                loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        conn.commit()
    logging.info("Database schema and table verified.")

def load_data_to_raw():
    """Loads JSON data from the data lake into the raw.telegram_messages table."""
    conn = get_db_connection()
    setup_database(conn)
    base_path = "data/raw/telegram_messages"
    
    with conn.cursor() as cur:
        for channel_folder in os.listdir(base_path):
            channel_path = os.path.join(base_path, channel_folder)
            if os.path.isdir(channel_path):
                for date_folder in os.listdir(channel_path):
                    date_path = os.path.join(channel_path, date_folder)
                    if os.path.isdir(date_path):
                        for filename in os.listdir(date_path):
                            if filename.endswith(".json"):
                                file_path = os.path.join(date_path, filename)
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    message_id = data.get('id')
                                    channel = data.get('channel')
                                    # Use ON CONFLICT to prevent duplicates and handle updates if needed
                                    cur.execute(
                                        """
                                        INSERT INTO raw.telegram_messages (message_id, channel, data)
                                        VALUES (%s, %s, %s)
                                        ON CONFLICT (message_id) DO UPDATE SET
                                            data = EXCLUDED.data,
                                            loaded_at = NOW();
                                        """,
                                        (message_id, channel, json.dumps(data))
                                    )
    conn.commit()
    conn.close()
    logging.info("Successfully loaded raw data into PostgreSQL.")

if __name__ == "__main__":
    load_data_to_raw()