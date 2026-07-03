from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'crime_news.db'}"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def initialize_database():
    from app.models.article import RawArticle
    from app.models.processed_article import ProcessedArticle
    from app.models.news_event import NewsEvent
    from app.models.analysis_result import AnalysisResult
    from app.models.officer_mention import OfficerMention

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    if existing_tables and {"officer_mentions", "processed_articles"}.issubset(existing_tables):
        return

    Base.metadata.create_all(bind=engine)