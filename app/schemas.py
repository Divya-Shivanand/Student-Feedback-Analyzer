# app/schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class FeedbackIn(BaseModel):
    name: str | None = None  # will be ignored for storage (anonymize)
    email: str | None = None # ignored
    feedback: str

class FeedbackOut(BaseModel):
    id: int
    text: str
    sentiment: float
    keywords: str
    created_at: datetime

    # Allow constructing from ORM (SQLAlchemy) objects (pydantic v2)
    model_config = ConfigDict(from_attributes=True)

class StatsOut(BaseModel):
    total_feedbacks: int
    avg_sentiment: float
    top_keywords: List[str]

    model_config = ConfigDict(from_attributes=True)
