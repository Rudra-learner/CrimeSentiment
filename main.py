from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
import os

from app.database.database import initialize_database
from app.api.dashboard import router as dashboard_router

initialize_database()

app = FastAPI(
    title="Crime Sentiment Project"
)

app.include_router(dashboard_router)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
def login(request: LoginRequest):
    if request.username == "admin" and request.password == "admin123":
        res = JSONResponse(content={"message": "Success"})
        res.set_cookie(key="auth_token", value="valid_admin_token", httponly=True, samesite="lax", max_age=1800)
        return res
    return JSONResponse(content={"message": "Invalid credentials"}, status_code=401)

@app.post("/api/logout")
def logout():
    res = JSONResponse(content={"message": "Logged out"})
    res.delete_cookie("auth_token")
    return res

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    
    # Check if the path needs authentication
    if path.startswith("/dashboard"):
        # Allow access to login files without auth
        if "login" in path:
            return await call_next(request)
            
        token = request.cookies.get("auth_token")
        if token != "valid_admin_token":
            return RedirectResponse(url="/dashboard/login.html", status_code=303)
            
    elif path.startswith("/api/dashboard"):
        token = request.cookies.get("auth_token")
        if token != "valid_admin_token":
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
            
    return await call_next(request)

# Ensure dashboard directory exists
os.makedirs("dashboard", exist_ok=True)
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

@app.get("/")
def home():
    return RedirectResponse(url="/dashboard/")