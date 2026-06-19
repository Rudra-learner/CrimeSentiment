from app.database.database import engine
from app.models.article import Base

print("Creating Tables...")

Base.metadata.create_all(bind=engine)

print("Tables Created Successfully")