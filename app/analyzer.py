# app/analyzer.py
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from collections import Counter
import re

_nltk_ready = False
sia = None
STOPWORDS = {
    "the","and","is","in","it","to","a","of","for","that","this","was","with","as","on","are","be","i","we","you","they","their","my"
}

def ensure_nltk():
    global _nltk_ready, sia
    if _nltk_ready:
        return
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()
    _nltk_ready = True

def get_sentiment_score(text: str) -> float:
    global sia
    if not sia:
        ensure_nltk()
    s = sia.polarity_scores(text)
    # return compound (-1..1)
    return s["compound"]

def extract_keywords(text: str, top_n: int = 3):
    # simple keyword extractor: lowercase, remove punctuation, split, remove stopwords, count
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    counts = Counter(words)
    top = [w for w,_ in counts.most_common(top_n)]
    return top
