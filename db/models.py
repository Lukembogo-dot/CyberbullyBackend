from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class FlaggedComment(Base):
    __tablename__ = "flagged_comments"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True)
    author_name = Column(String)  # Changed from 'author' to match React
    comment_body = Column(String) # Changed from 'text' to match React
    prediction_label = Column(String) # Changed from 'sentiment_label' to match API
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow) # Changed from 'timestamp' to match API