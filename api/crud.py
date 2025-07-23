from sqlalchemy.orm import Session
from sqlalchemy import text

def get_channel_activity(db: Session, channel_name: str):
   
    query = text("""
        SELECT
            c.channel_name,
            COUNT(f.message_id) AS message_count,
            MIN(f.message_date) AS first_message_date,
            MAX(f.message_date) AS last_message_date
        FROM marts.fct_messages f
        JOIN marts.dim_channels c ON f.channel_key = c.channel_key
        WHERE c.channel_name = :c_name
        GROUP BY c.channel_name;
    """)
    result = db.execute(query, {"c_name": channel_name}).fetchone()
    return result