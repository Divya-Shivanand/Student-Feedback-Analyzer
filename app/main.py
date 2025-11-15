# app/main.py
import os
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import database, models, analyzer, schemas

# Create app
app = FastAPI(title="Student Feedback Analyzer")

# CORS (allow local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production restrict this
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files from ../frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
frontend_path = os.path.abspath(frontend_path)
if os.path.isdir(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

    @app.get("/", response_class=FileResponse)
    def serve_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

# Simple DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Startup tasks
@app.on_event("startup")
def on_startup():
    # create sqlite tables in the configured location
    database.create_tables()
    # ensure nltk vader lexicon present (downloads if necessary)
    try:
        analyzer.ensure_nltk()
    except Exception as e:
        # Log but continue; if analyzer fails, calls that use it may still error
        print("Warning: analyzer.ensure_nltk() failed:", e)

# Endpoints
@app.post("/feedback", response_model=schemas.FeedbackOut)
def submit_feedback(payload: schemas.FeedbackIn, db: Session = Depends(get_db)):
    text = payload.feedback.strip() if payload.feedback else ""
    if not text:
        raise HTTPException(status_code=400, detail="Feedback text required")

    sent_score = analyzer.get_sentiment_score(text)
    keywords = analyzer.extract_keywords(text)

    fb = models.Feedback(
        text=text,
        sentiment=sent_score,
        keywords=",".join(keywords),
        created_at=datetime.utcnow()
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    # return pydantic model from ORM (schemas configured to accept from_attributes)
    return schemas.FeedbackOut.from_orm(fb)

@app.get("/feedbacks", response_model=List[schemas.FeedbackOut])
def list_feedbacks(limit: int = 100, db: Session = Depends(get_db)):
    rows = db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).limit(limit).all()
    return [schemas.FeedbackOut.from_orm(r) for r in rows]

@app.get("/stats", response_model=schemas.StatsOut)
def stats(db: Session = Depends(get_db)):
    rows = db.query(models.Feedback).all()
    total = len(rows)
    avg_sent = sum([r.sentiment for r in rows]) / total if total else 0.0

    kw_counts = {}
    for r in rows:
        for k in (r.keywords or "").split(","):
            if k:
                kw_counts[k] = kw_counts.get(k, 0) + 1
    top_keywords = sorted(kw_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return schemas.StatsOut(total_feedbacks=total, avg_sentiment=avg_sent, top_keywords=[k for k, c in top_keywords])
