from app.preprocessors.preprocessor import preprocess_articles

from app.nlp.event_matcher import run_event_matching

from app.nlp.entity_extractor import run_entity_extractor

from app.nlp.sentiment_analyzer import run_sentiment_analyzer

from app.nlp.officer_sentiment import run_officer_sentiment


def run_complete_pipeline():

    print("Step 1 : Preprocessing")
    preprocess_articles()

    print("Step 2 : Event Matching")
    run_event_matching()

    print("Step 3 : Entity Extraction")
    run_entity_extractor()

    print("Step 4 : Sentiment Analysis")
    run_sentiment_analyzer()

    print("Step 5 : Officer Sentiment")
    run_officer_sentiment()

    print("Pipeline Completed")

if __name__ == "__main__":
    run_complete_pipeline()