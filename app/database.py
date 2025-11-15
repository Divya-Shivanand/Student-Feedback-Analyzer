# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./feedback.db")

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)
