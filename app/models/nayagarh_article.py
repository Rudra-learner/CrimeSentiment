from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class NayagarhArticle(Base):
    __tablename__ = "nayagarh_articles"

    id = Column(Integer, primary_key=True, index=True)

    
    processed_article_id = Column(
        Integer,
        ForeignKey("processed_articles.id"),
        nullable=False
    )

    title = Column(String(500))
    source = Column(String(100))
    url = Column(Text)

    clean_text = Column(Text)

    language = Column(String(20))
    content_hash = Column(String(64), unique=True)

    crime_category = Column(String(100))
    crime_subcategory = Column(String(100))

    location = Column(String(100))

    police_mentioned = Column(String(255))

    case_status = Column(String(100))

    
    news_event_id = Column(
        Integer,
        ForeignKey("news_events.id"),
        nullable=True
    )

    published_date = Column(DateTime)

    processed_at = Column(DateTime)

    
    processed_article = relationship("ProcessedArticle")
    news_event = relationship("NewsEvent")