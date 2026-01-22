import json
from kafka import KafkaProducer

# Initialize the Producer
# 'localhost:9092' matches the port in your docker-compose
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_comment(comment_text, author):
    message = {
        "author": author,
        "text": comment_text
    }
    producer.send('youtube_comments', value=message)
    producer.flush()
    print(f"Sent to Kafka: {comment_text}")

# Test it
if __name__ == "__main__":
    send_comment("This project is looking great!", "DevUser")