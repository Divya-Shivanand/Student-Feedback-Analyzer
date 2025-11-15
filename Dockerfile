FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential curl --no-install-recommends \
 && pip install --no-cache-dir -r requirements.txt \
 && rm -rf /var/lib/apt/lists/*

COPY app ./app
COPY frontend ./frontend

# Ensure NLTK resources are downloaded when container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
