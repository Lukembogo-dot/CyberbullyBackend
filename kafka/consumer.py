import json
import joblib
from kafka import KafkaConsumer
from db.database import SessionLocal
from db.models import FlaggedComment
from datetime import datetime

# 1. Load your "Brain"
model = joblib.load('ml/model.pkl')

# 2. Setup the Consumer
consumer = KafkaConsumer(
    'youtube_comments',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Consumer active: Data-driven Risk Analysis mode (Percentages only)")

for message in consumer:
    data = message.value
    text = data.get('text', '')
    author = data.get('author', 'Unknown')
    video_id = data.get('video_id', 'N/A')
    
    # 3. Predict Probabilities
    # prob[0] = Toxic Score, prob[1] = Safe Score
    prob = model.predict_proba([text])[0]
    toxic_score = float(prob[0] * 100) 
    
    # 4. Filter Logic (Only ignore absolute 0-10% noise)
    should_save = toxic_score > 10 

    # 5. Database Logic
    save_status = "ℹ️ BELOW THRESHOLD (NOT SAVED)"
    if should_save:
        db = SessionLocal()
        try:
            new_entry = FlaggedComment(
                video_id=video_id,
                author_name=author,
                comment_body=text,
                # We store the percentage string as the label now
                prediction_label=f"{toxic_score:.1f}% Risk",
                confidence_score=toxic_score,
                created_at=datetime.utcnow()
            )
            db.add(new_entry)
            db.commit()
            save_status = f"✅ SAVED TO DATABASE"
        except Exception as e:
            db.rollback()
            save_status = f"❌ ERROR: {e}"
        finally:
            db.close()

    # 6. Simplified Output
    print(f"\n[ANALYSIS] Author: {author}")
    print(f"Comment: {text[:80]}...")
    print(f"AI Risk Score: {toxic_score:.2f}%")
    print(f"Status: {save_status}")
    print("-" * 40)