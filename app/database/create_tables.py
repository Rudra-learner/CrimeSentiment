from app.database.database import engine, Base

# Import all models so SQLAlchemy registers them
from app.models.article import RawArticle
from app.models.processed_article import ProcessedArticle

print("Creating Tables...")

Base.metadata.create_all(bind=engine)

print("Tables Created Successfully")