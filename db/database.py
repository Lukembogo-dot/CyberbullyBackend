import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Use the pooled connection string from your Neon dashboard
DATABASE_URL = os.getenv("DATABASE_URL")

# pool_pre_ping=True is critical for Neon because it 
# handles the "wake up" if the DB was asleep (scaled to zero)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()