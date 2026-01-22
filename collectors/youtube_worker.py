import os
import time
import json
from googleapiclient.discovery import build
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Initialize YouTube API
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Global tracker to prevent duplicate messages in Kafka
seen_comment_ids = set()

def fetch_comments(video_id):
    """Fetches the latest comments and pushes them to Kafka."""
    global seen_comment_ids
    print(f"--- Polling YouTube for video: {video_id} ---")
    
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=20,
            order="time" 
        )
        response = request.execute()

        new_count = 0
        for item in response.get('items', []):
            comment_id = item['id']
            
            # Check if this is a new comment we haven't sent yet
            if comment_id not in seen_comment_ids:
                comment = item['snippet']['topLevelComment']['snippet']
                data = {
                    "comment_id": comment_id,
                    "author": comment['authorDisplayName'],
                    "text": comment['textDisplay'],
                    "published_at": comment['publishedAt'],
                    "video_id": video_id
                }
                
                producer.send('youtube_comments', value=data)
                seen_comment_ids.add(comment_id)
                new_count += 1
        
        producer.flush()
        print(f"Success: {new_count} new comments sent to Kafka.")
        
        # Optional: Keep memory clean by limiting the set size
        if len(seen_comment_ids) > 1000:
            seen_comment_ids.clear()

    except Exception as e:
        print(f"Error fetching from YouTube: {e}")

def start_tracking(video_id: str):
    """Loop function to be called by FastAPI BackgroundTasks."""
    print(f"Worker started for video {video_id}. Press Ctrl+C to stop manually.")
    while True:
        fetch_comments(video_id)
        # Wait 60 seconds before checking for more comments
        time.sleep(60)

if __name__ == "__main__":
    # Local testing mode
    TEST_VIDEO_ID = "dQw4w9WgXcQ" 
    start_tracking(TEST_VIDEO_ID)