from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime

from app.database.database import Base


class RawArticle(Base):

    __tablename__ = "raw_articles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(String(1000))

    source = Column(String(200))

    url = Column(String(2000))

    language = Column(String(20))

    published_date = Column(String(100))

    article_text = Column(Text)

    collected_at = Column(DateTime)