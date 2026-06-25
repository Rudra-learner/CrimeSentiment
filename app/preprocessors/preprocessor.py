from datetime import datetime

from app.database.database import SessionLocal
from app.models.article import RawArticle
from app.models.processed_article import ProcessedArticle

from app.preprocessors.cleaner import clean_text
from app.preprocessors.language_detector import detect_language
from app.preprocessors.hash_generator import generate_hash
from app.preprocessors.crime_detector import detect_crime
from app.preprocessors.location_detector import detect_location
from app.preprocessors.police_detector import police_mentioned
from app.preprocessors.case_status_detector import detect_case_status
from app.preprocessors.officer_detector import detect_officers


def preprocess_articles():

    db = SessionLocal()

    try:

        raw_articles = (
            db.query(RawArticle)
            .filter(RawArticle.is_preprocessed == False)
            .all()
        )

        print(f"\nFound {len(raw_articles)} raw articles.\n")

        for article in raw_articles:

            print(f"Processing: {article.title}")

            clean_article = clean_text(article.article_text)

            language = detect_language(clean_article)

            content_hash = generate_hash(clean_article)

            crime_category = detect_crime(clean_article)

            location = detect_location(clean_article)

            # Only process articles related to Nayagarh
            if location.lower() != "nayagarh":
                article.is_preprocessed = True
                db.commit()
                print(f"Skipped - Location: {location}")
                continue

            police = police_mentioned(clean_article)

            case_status = detect_case_status(clean_article)

            officers = detect_officers(clean_article)

            processed_article = ProcessedArticle(
                raw_article_id=article.id,
                title=article.title,
                source=article.source,
                url=article.url,
                clean_text=clean_article,
                language=language,
                content_hash=content_hash,
                crime_category=crime_category,
                location=location,
                police_mentioned=police,
                case_status=case_status,
                processed_at=datetime.utcnow()
            )

            db.add(processed_article)

            article.is_preprocessed = True

            db.commit()

            print("Processed Successfully")

    except Exception as e:

        db.rollback()

        print(f"Preprocessing Error: {e}")

    finally:

        db.close()


if __name__ == "__main__":
    preprocess_articles()