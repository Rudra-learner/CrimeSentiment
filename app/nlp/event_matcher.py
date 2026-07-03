import json
from datetime import datetime

import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

from app.database.database import SessionLocal
from app.models.article import RawArticle
from app.models.processed_article import ProcessedArticle
from app.models.news_event import NewsEvent
from app.models.analysis_result import AnalysisResult
from app.models.officer_mention import OfficerMention

from app.nlp.embedding_generator import EmbeddingGenerator


SIMILARITY_THRESHOLD = 0.82


class EventMatcher:

    def __init__(self):
        self.db = SessionLocal()
        self.embedding_generator = EmbeddingGenerator()

    def calculate_similarity(self, embedding1, embedding2):
        similarity = cosine_similarity(
            embedding1.reshape(1, -1),
            embedding2.reshape(1, -1)
        )[0][0]
        return similarity

    def load_existing_events(self , article):
        events = (

    self.db.query(NewsEvent)

    .filter(

        NewsEvent.crime_category == article.crime_category

    )

    .all()

)
        return events

    def generate_event_embedding(self, article):
        text = article.clean_text
        return self.embedding_generator.generate_embedding(text)

    def get_best_matching_event(
    self,
    article,
    article_embedding
):
        events = self.load_existing_events(article)
        best_event = None
        highest_similarity = 0

        for event in events:
            if not event.event_embedding:
                continue

            event_embedding = self.embedding_generator.json_to_embedding(
                event.event_embedding
            )

            similarity = self.calculate_similarity(
                article_embedding,
                event_embedding
            )

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_event = event

        return best_event, highest_similarity

    def create_new_event(self, article, article_embedding):
        new_event = NewsEvent(
            event_title=article.title,
            crime_category=article.crime_category,
            primary_location=article.location,
            event_summary=article.clean_text[:1000],
            event_embedding=self.embedding_generator.embedding_to_json(
                article_embedding
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(new_event)
        self.db.commit()
        self.db.refresh(new_event)

        print(f"New Event Created : {new_event.id}")

        return new_event

    def assign_existing_event(self, article, event):
        article.news_event_id = event.id
        event.updated_at = datetime.utcnow()

        article.news_event_id = event.id

        self.db.commit()

        self.db.refresh(article)

        print(f"Matched with Event ID : {event.id}")

        return event

    def match_article(self, article):
        print(f"\nMatching : {article.title}")

        article_embedding = self.generate_event_embedding(article)
        best_event, similarity = self.get_best_matching_event(
    article,
    article_embedding
)

        if best_event is None:
            print("No Existing Events Found.")
            event = self.create_new_event(article, article_embedding)
            article.news_event_id = event.id
            self.db.commit()
            return event.id

        print(f"Highest Similarity : {similarity:.4f}")

        if similarity >= SIMILARITY_THRESHOLD:
            event = self.assign_existing_event(article, best_event)
            return event.id

        print("Similarity Below Threshold.")
        event = self.create_new_event(article, article_embedding)
        article.news_event_id = event.id
        self.db.commit()

        return event.id

    def process_articles(self):
        articles = (
            self.db.query(ProcessedArticle)
            .filter(
ProcessedArticle.news_event_id.is_(None)
)
            .all()
        )

        print(f"\nFound {len(articles)} articles to process.\n")

        for article in articles:
            try:
                event_id = self.match_article(article)
                print(f"Article Assigned to Event : {event_id}")
            except Exception as e:
                print(f"Error Processing Article {article.id}: {e}")
                self.db.rollback()

        print("\nEvent Matching Completed.\n")

    def close(self):
        self.db.close()


def run_event_matching():
    matcher = EventMatcher()
    try:
        matcher.process_articles()
    finally:
        matcher.close()


if __name__ == "__main__":
    run_event_matching()