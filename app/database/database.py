from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker


import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Default to local SQLite if DATABASE_URL is not set
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DATA_DIR / 'crime_news.db'}")

# Remove check_same_thread for PostgreSQL, it's only for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
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
    from app.models.nayagarh_article import NayagarhArticle

    Base.metadata.create_all(bind=engine)