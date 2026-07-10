from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from app.database.database import Base


class AnalysisResult(Base):

    __tablename__ = "analysis_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    processed_article_id = Column(
        Integer,
        ForeignKey("processed_articles.id"),
        nullable=False
    )

    news_event_id = Column(
        Integer,
        ForeignKey("news_events.id"),
        nullable=False
    )

    article_title = Column(String)

    source = Column(String)

    url = Column(String)

    sentiment = Column(
        String(20)
    )

    severity_score = Column(
        Integer,
        default=3
    )

    crime_priority_index = Column(
        String(20),
        default="Low"
    )

    confidence = Column(
        Float
    )

    analyzed_at = Column(
        DateTime,
        default=datetime.utcnow
    )