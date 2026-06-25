from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from datetime import datetime

from app.database.database import Base


class ProcessedArticle(Base):

    __tablename__ = "processed_articles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    raw_article_id = Column(
        Integer,
        ForeignKey("raw_articles.id"),
        nullable=False
    )

    title = Column(
        String(1000)
    )

    source = Column(
        String(200)
    )

    url = Column(
        String(2000)
    )

    clean_text = Column(
        Text
    )

    language = Column(
        String(20)
    )

    content_hash = Column(
        String(64),
        index=True
    )

    crime_category = Column(
        String(100)
    )

    location = Column(
        String(200)
    )

    police_mentioned = Column(
        Boolean,
        default=False
    )

    case_status = Column(
        String(50)
    )

    processed_at = Column(
        DateTime,
        default=datetime.utcnow
    )