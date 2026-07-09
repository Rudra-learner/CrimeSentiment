from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

from app.database.database import initialize_database
from app.api.dashboard import router as dashboard_router

initialize_database()

app = FastAPI(
    title="Crime Sentiment Project"
)

app.include_router(dashboard_router)

# Ensure dashboard directory exists
os.makedirs("dashboard", exist_ok=True)
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

@app.get("/")
def home():
    return RedirectResponse(url="/dashboard/")