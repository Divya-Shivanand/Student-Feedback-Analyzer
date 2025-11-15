# app/models.py
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    sentiment = Column(Float, nullable=False)
    keywords = Column(String, nullable=True)  # comma separated
    created_at = Column(DateTime, nullable=False)
