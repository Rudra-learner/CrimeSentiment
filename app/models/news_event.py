from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Text

from app.database.database import Base


class NewsEvent(Base):

    __tablename__ = "news_events"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    event_title = Column(
        String(500)
    )

    crime_category = Column(
        String(100)
    )

    primary_location = Column(
        String(200)
    )

    event_summary = Column(
        Text
    )

    event_embedding = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )