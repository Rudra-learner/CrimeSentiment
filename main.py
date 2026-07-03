from fastapi import FastAPI

from app.database.database import initialize_database

initialize_database()

app = FastAPI(
    title="Crime Sentiment Project"
)

@app.get("/")
def home():
    return {
        "message": "Crime Sentiment Project API Running"
    }