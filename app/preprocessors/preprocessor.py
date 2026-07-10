from datetime import datetime
from dateutil import parser

from app.database.database import SessionLocal
from app.models.article import RawArticle
from app.models.processed_article import ProcessedArticle
from app.models.news_event import NewsEvent

from app.preprocessors.cleaner import clean_text
from app.preprocessors.language_detector import detect_language
from app.preprocessors.hash_generator import generate_hash
from app.preprocessors.crime_detector import detect_crime
from app.preprocessors.location_detector import detect_location
from app.preprocessors.location_detector import LOCATIONS
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

            if language == "unknown":
                article.is_preprocessed = True
                db.commit()
                print("Unknown Language")
                continue

            content_hash = generate_hash(clean_article)

            crime_category = detect_crime(clean_article)

            if crime_category == "OTHER":
                article.is_preprocessed = True
                db.commit()
                print("Skipped - Not a Crime Article")
                continue

            location = detect_location(clean_article)

            allowed_locations = [loc.lower() for loc in LOCATIONS]

            if location.lower() not in allowed_locations:
                article.is_preprocessed = True
                db.commit()
                print(f"Skipped - Location not in allowed list: {location}")
                continue

            police = police_mentioned(clean_article)

            case_status = detect_case_status(clean_article)

            officers = detect_officers(clean_article)

            duplicate = (
                db.query(ProcessedArticle)
                .filter(ProcessedArticle.content_hash == content_hash)
                .first()
            )

            if duplicate:
                article.is_preprocessed = True
                db.commit()
                print("Duplicate Article Skipped")
                continue

            # Parse published date
            parsed_pub_date = article.collected_at or datetime.utcnow()
            if article.published_date:
                try:
                    parsed_pub_date = parser.parse(article.published_date)
                    # If naive, make it UTC-like or just leave as naive, since collected_at is naive UTC
                    if parsed_pub_date.tzinfo is not None:
                        parsed_pub_date = parsed_pub_date.replace(tzinfo=None)
                except Exception:
                    pass

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
                processed_at=datetime.utcnow(),
                published_date=parsed_pub_date
            )

            db.add(processed_article)

            article.is_preprocessed = True

            db.commit()

            print(f""" Processed Successfully

                        Crime : {crime_category}

                        Location : {location}

                        Police Mentioned : {police}

                        Case Status : {case_status}

                        Language : {language}

                                                """)

    except Exception as e:

        db.rollback()

        print(f"Preprocessing Error: {e}")

    finally:

        db.close()


if __name__ == "__main__":
    preprocess_articles()