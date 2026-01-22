from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import threading
from typing import Optional
from sqlalchemy.orm import Session

from collectors.youtube_worker import start_tracking
from db.database import get_db
from db.models import FlaggedComment
from db.database import engine
from db.models import Base

app = FastAPI(title="Kenya Sentinel API")

# This line creates all tables defined in models.py if they don't exist
Base.metadata.create_all(bind=engine)

# --- 1. RESULTS ENDPOINT (With Severity Filters) ---
@app.get("/flagged-comments")
def get_flagged_comments(
    label: Optional[str] = Query(None, description="Filter by: positive, negative, or neutral"),
    db: Session = Depends(get_db)
):
    query = db.query(FlaggedComment)
    
    # Apply filter if a specific label (other than 'all') is selected
    if label and label.lower() != "all":
        # Using .ilike for case-insensitive matching
        query = query.filter(FlaggedComment.prediction_label.ilike(label))
    
    # Fetch top 100 most recent items
    comments = query.order_by(FlaggedComment.created_at.desc()).limit(100).all()
    return comments

# --- 2. CORS CONFIGURATION ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

def extract_video_id(url: str):
    reg = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(reg, url)
    return match.group(1) if match else None

@app.get("/")
def health_check():
    return {
        "status": "online", 
        "engine": "CyberBully-V1",
        "infrastructure": "Kafka + Docker"
    }

# --- 3. UPDATED TRACKING ENDPOINT (Threading Fix) ---
@app.post("/track-video")
async def track_video(request: VideoRequest):
    video_id = extract_video_id(request.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    # Using threading instead of BackgroundTasks to prevent the request from hanging
    # daemon=True ensures the worker stops if the main FastAPI process stops
    worker_thread = threading.Thread(target=start_tracking, args=(video_id,))
    worker_thread.daemon = True
    worker_thread.start()
    
    return {
        "status": "success",
        "video_id": video_id,
        "message": f"Kenya Sentinel monitor launched for: {video_id}"
    }