import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
import re

analyzer = SentimentIntensityAnalyzer()

def load_reviews(filepath):
    df = pd.read_csv(filepath)
    df = df.dropna(subset=["text"])
    df["text"] = df["text"].astype(str)
    return df

def get_sentiment(text):
    score = analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        return "Positive", score
    elif score <= -0.05:
        return "Negative", score
    else:
        return "Neutral", score

def add_sentiment_column(df):
    results = df["text"].apply(get_sentiment)
    df["sentiment"] = results.apply(lambda x: x[0])
    df["sentiment_score"] = results.apply(lambda x: x[1])
    return df

STOPWORDS = {"the","and","was","for","this","that","with","have","were","are",
             "but","not","you","your","they","its","it's","just","very"}

def get_top_words(df, sentiment_type, top_n=10):
    subset = df[df["sentiment"] == sentiment_type]
    words = []
    for text in subset["text"]:
        cleaned = re.findall(r'\b[a-z]{3,}\b', text.lower())
        words.extend([w for w in cleaned if w not in STOPWORDS])
    return Counter(words).most_common(top_n)