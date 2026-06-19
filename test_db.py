from app.database.database import SessionLocal
from app.models.article import RawArticle

db = SessionLocal()

article = RawArticle(
    title="Test Article",
    source="Test",
    url="https://test.com",
    language="en",
    published_date="2026-06-19",
    article_text="Testing database"
)

db.add(article)
db.commit()

print("Inserted Successfully")

db.close()