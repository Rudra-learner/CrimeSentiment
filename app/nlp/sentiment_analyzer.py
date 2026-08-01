import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from datetime import datetime
import torch
from transformers import pipeline

from app.database.database import SessionLocal
from app.models.news_event import NewsEvent
from app.models.processed_article import ProcessedArticle
from app.models.nayagarh_article import NayagarhArticle
from app.models.analysis_result import AnalysisResult


MODEL_NAME = "typeform/distilbert-base-uncased-mnli"


class SentimentAnalyzer:

    def __init__(self):
        print("Loading Zero-Shot Sentiment Model...")

        self.db = SessionLocal()

        self.classifier = pipeline(
            "zero-shot-classification",
            model=MODEL_NAME,
            device=-1 # CPU
        )

        self.candidate_labels = [
            "opposing police statements, alleging investigation faults, or saying important facts are missing",
            "supporting police reports, endorsing police statements, or praising effective police action"
        ]
        
        self.label_mapping = {
            "opposing police statements, alleging investigation faults, or saying important facts are missing": "Negative",
            "supporting police reports, endorsing police statements, or praising effective police action": "Positive"
        }

        print("Sentiment Model Loaded Successfully.")

    def predict_sentiment(self, text):
        if not text:
            return None, None

        # Truncate text to roughly 512 tokens to avoid length errors
        text = text[:2000]

        result = self.classifier(
            text,
            candidate_labels=self.candidate_labels,
            multi_label=True,
            hypothesis_template="The media stance in this article is {}."
        )
        
        top_label = result['labels'][0]
        top_score = result['scores'][0]
        
        # If neither supporting nor opposing probability exceeds 0.50, it is neutral reporting
        if top_score < 0.50:
            sentiment = "Neutral"
            confidence = round((1.0 - top_score) * 100, 2)
        else:
            sentiment = self.label_mapping[top_label]
            confidence = round(top_score * 100, 2)

        return sentiment, confidence

    def determine_severity_and_cpi(self, crime_category):
        category = (crime_category or "").lower()
        
        if "murder" in category:
            return 10, "Very High"
        elif "kidnapping" in category or "rape" in category:
            return 9, "Very High"
        elif "arms" in category:
            return 8, "High"
        elif "drug" in category:
            return 7, "High"
        elif "assault" in category or "robbery" in category:
            return 6, "Medium"
        elif "cyber" in category: # cyber fraud
            return 5, "Medium"
        elif "theft" in category:
            return 4, "Low"
        elif "fraud" in category:
            return 3, "Low"
        else:
            return 3, "Low"

    def article_already_analyzed(self, article_id):
        article = (
            self.db.query(AnalysisResult)
            .filter(AnalysisResult.processed_article_id == article_id)
            .first()
        )

        return article is not None

    def save_analysis_result(self, article, sentiment, confidence, severity_score, cpi):
        target_id = getattr(article, 'processed_article_id', article.id)
        result = AnalysisResult(
            processed_article_id=target_id,
            news_event_id=article.news_event_id,

        article_title=article.title,

        source=article.source,

        url=article.url,

        sentiment=sentiment,

        severity_score=severity_score,

        crime_priority_index=cpi,

        confidence=confidence

    )

        self.db.add(result)

        self.db.commit()

        safe_title = str(article.title).encode('ascii', 'replace').decode('ascii')
        print(f"Sentiment Saved : {safe_title}")

    def analyze_article(self, article):
        target_id = getattr(article, 'processed_article_id', article.id)
        safe_title = str(article.title).encode('ascii', 'replace').decode('ascii')
        if self.article_already_analyzed(target_id):
            print(f"Already Analyzed : {safe_title}")
            return

        print(f"\nAnalyzing : {safe_title}")

        if not article.clean_text:
            return

        sentiment, confidence = self.predict_sentiment(article.clean_text)

        if sentiment is None:
            print("Empty Article.")
            return

        severity_score, cpi = self.determine_severity_and_cpi(article.crime_category)

        print(f"Sentiment : {sentiment} (Severity: {severity_score}, CPI: {cpi})")
        print(f"Confidence : {confidence:.2f}%")

        self.save_analysis_result(article, sentiment, confidence, severity_score, cpi)

    def process_all_articles(self):
        articles = (
            self.db.query(NayagarhArticle)
            .filter(
                NayagarhArticle.news_event_id.isnot(None)
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