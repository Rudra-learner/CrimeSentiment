from fastapi import FastAPI

from app.database.database import engine, Base
from app.models.article import RawArticle

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Crime Sentiment Project"
)

@app.get("/")
def home():
    return {
        "message": "Crime Sentiment Project API Running"
    }