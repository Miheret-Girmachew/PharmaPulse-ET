from pydantic import BaseModel
from datetime import datetime

class ChannelActivity(BaseModel):
    channel_name: str
    message_count: int
    first_message_date: datetime
    last_message_date: datetime

    class Config:
        from_attributes = True 