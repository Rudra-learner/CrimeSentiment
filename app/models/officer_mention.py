from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from app.database.database import Base


class OfficerMention(Base):

    __tablename__ = "officer_mentions"
    __table_args__ = {"extend_existing": True}

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

    officer_name = Column(
        String(200)
    )

    designation = Column(
        String(100)
    )

    police_station = Column(
        String(200)
    )