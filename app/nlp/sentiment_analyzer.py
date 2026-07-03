from datetime import datetime

import torch
from scipy.special import softmax
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification

from app.database.database import SessionLocal
from app.models.news_event import NewsEvent
from app.models.processed_article import ProcessedArticle
from app.models.analysis_result import AnalysisResult


MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"


class SentimentAnalyzer:

    def __init__(self):
        print("Loading RoBERTa Sentiment Model...")

        self.db = SessionLocal()

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

        self.model.to("cpu")

        self.labels = [
            "Negative",
            "Neutral",
            "Positive"
        ]

        print("Sentiment Model Loaded Successfully.")

    def predict_sentiment(self, text):
        if not text:
            return None, None

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        scores = outputs.logits[0].numpy()
        probabilities = softmax(scores)
        predicted_index = probabilities.argmax()
        sentiment = self.labels[predicted_index]
        confidence = round(float(probabilities[predicted_index]) * 100, 2)

        return sentiment, confidence

    def article_already_analyzed(self, article_id):
        article = (
            self.db.query(AnalysisResult)
            .filter(AnalysisResult.processed_article_id == article_id)
            .first()
        )

        return article is not None

    def save_analysis_result(self, article, sentiment, confidence):

        result = AnalysisResult(

        processed_article_id=article.id,

        news_event_id=article.news_event_id,

        article_title=article.title,

        source=article.source,

        url=article.url,

        sentiment=sentiment,

        confidence=confidence

    )

        self.db.add(result)

        self.db.commit()

        print(f"Sentiment Saved : {article.title}")

    def analyze_article(self, article):
        if self.article_already_analyzed(article.id):
            print(f"Already Analyzed : {article.title}")
            return

        print(f"\nAnalyzing : {article.title}")

        if not article.clean_text:
            return

        sentiment, confidence = self.predict_sentiment(article.clean_text)

        if sentiment is None:
            print("Empty Article.")
            return

        print(f"Sentiment : {sentiment}")
        print(f"Confidence : {confidence:.2f}%")

        self.save_analysis_result(article, sentiment, confidence)

    def process_all_articles(self):
        articles = (
    self.db.query(ProcessedArticle)
    .filter(
        ProcessedArticle.news_event_id.isnot(None)
    )
    .all()
)

        print(f"\nFound {len(articles)} articles.\n")

        for article in articles:
            try:
                self.analyze_article(article)
            except Exception as e:
                print(f"Sentiment Analysis Error : {e}")
                self.db.rollback()

        print("\nSentiment Analysis Completed.\n")

    def close(self):
        self.db.close()


def run_sentiment_analyzer():
    analyzer = SentimentAnalyzer()

    try:
        analyzer.process_all_articles()
    finally:
        analyzer.close()


if __name__ == "__main__":
    run_sentiment_analyzer()