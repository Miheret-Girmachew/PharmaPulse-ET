# src/enrichment/run_yolo.py

import os
import torch
from ultralytics import YOLO
import psycopg2
from dotenv import load_dotenv
import logging

# --- Setup ---
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

def setup_detection_table(conn):
    """Creates the table to store detection results if it doesn't exist."""
    with conn.cursor() as cur:
        # We create a new schema to keep enriched data separate
        cur.execute("CREATE SCHEMA IF NOT EXISTS enrichments;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS enrichments.image_detections (
                detection_id SERIAL PRIMARY KEY,
                message_id BIGINT,
                image_path VARCHAR(512),
                detected_class VARCHAR(255),
                confidence_score REAL,
                processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_message_id ON enrichments.image_detections (message_id);")
        conn.commit()
    logging.info("Enrichment table verified.")


def get_unprocessed_images(conn):
    """Finds images that haven't been processed yet by checking against the DB."""
    base_path = "data/raw/telegram_images"
    all_images = []
    # Walk through the directory to find all image files
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".jpg"):
                try:
                    # The filename is the message_id
                    message_id = int(os.path.splitext(file)[0])
                    all_images.append((message_id, os.path.join(root, file)))
                except ValueError:
                    logging.warning(f"Could not parse message_id from filename: {file}")
    
    # Get IDs of images already processed from the database
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT message_id FROM enrichments.image_detections;")
        processed_ids = {row[0] for row in cur.fetchall()}
    
    unprocessed = [img for img in all_images if img[0] not in processed_ids]
    logging.info(f"Found {len(unprocessed)} new images to process.")
    return unprocessed

def run_yolo_enrichment():
    """Runs YOLOv8 on new images and saves results to the database."""
    # Load a pre-trained YOLOv8 model ('n' is for nano, it's small and fast)
    model = YOLO('yolov8n.pt')
    
    conn = get_db_connection()
    setup_detection_table(conn)
    images_to_process = get_unprocessed_images(conn)
    
    with conn.cursor() as cur:
        for message_id, image_path in images_to_process:
            logging.info(f"Processing {image_path} for message {message_id}")
            try:
                # The 'app' service in docker-compose has the project directory mounted at /app
                container_image_path = os.path.join('/app', image_path)
                results = model(container_image_path)
                
                for r in results:
                    for box in r.boxes:
                        class_id = int(box.cls[0])
                        class_name = model.names[class_id]
                        confidence = float(box.conf[0])
                        
                        # Only save detections with a reasonable confidence score
                        if confidence > 0.4:
                            cur.execute(
                                """
                                INSERT INTO enrichments.image_detections 
                                (message_id, image_path, detected_class, confidence_score)
                                VALUES (%s, %s, %s, %s)
                                """,
                                (message_id, image_path, class_name, confidence)
                            )
            except Exception as e:
                logging.error(f"Failed to process {image_path}: {e}")
    
    conn.commit()
    conn.close()
    logging.info("YOLO enrichment process finished.")

if __name__ == "__main__":
    run_yolo_enrichment()