from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas, database

app = FastAPI(title="Kara Solutions Analytical API")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Ethiopian Medical Business Insights API"}

@app.get("/api/channels/{channel_name}/activity", response_model=schemas.ChannelActivity)
def read_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    activity = crud.get_channel_activity(db, channel_name=channel_name)
    if activity is None:
        raise HTTPException(status_code=404, detail="Channel not found or no activity")
    return activity