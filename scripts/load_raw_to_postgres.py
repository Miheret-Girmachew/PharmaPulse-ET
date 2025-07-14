# scripts/load_raw_to_postgres.py
import os
import json
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
import logging

# --- Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- DB Connection ---
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

def main():
    conn = get_db_connection()
    cur = conn.cursor()

    # Create schema and table for raw data if they don't exist
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            id SERIAL PRIMARY KEY,
            data JSONB,
            loaded_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    logging.info("Raw schema and table are ready.")

    # Walk through the raw data directory
    raw_data_dir = "data/raw/telegram_messages"
    for root, _, files in os.walk(raw_data_dir):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Insert data into the jsonb column
                    cur.execute("INSERT INTO raw.telegram_messages (data) VALUES (%s);", (Json(data),))
    
    conn.commit()
    cur.close()
    conn.close()
    logging.info("Successfully loaded all raw JSON files into PostgreSQL.")

if __name__ == "__main__":
    main()