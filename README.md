🐍 Backend README (/backend/README.md)

🛡️ AI Content Guard - Backend (Kafka + ML)

This is the engine of the project. It handles real-time data streaming from YouTube, runs AI inference via a custom Scikit-Learn model, and persists high-risk data to a Neon PostgreSQL database.

📂 Folder Structure

backend/
├── db/                # Database configuration & Models
│   ├── database.py    # SQLAlchemy engine
│   └── models.py      # PostgreSQL schema
├── kafka/             # Streaming logic
│   └── consumer.py    # Main Kafka consumer & ML loop
├── ml/                # Machine Learning assets
│   └── model.pkl      # Trained Logistic Regression model
├── .env               # Database credentials & API keys
└── main.py            # FastAPI entry point

🛠️ Installation & Setup

1. Initialize Environment:
```
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
2. Start Kafka: Ensure your Kafka broker is running (via Docker or local install) at localhost:9092.

3. Run the Consumer:
```
$env:PYTHONPATH = "." # Set python path
python kafka/consumer.py
```

4. Start the API:
```
Bash
uvicorn main:app --reload
```
