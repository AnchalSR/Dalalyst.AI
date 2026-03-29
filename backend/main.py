from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from routes.auth_routes import router as auth_router
from routes.chart_routes import router as chart_router
from routes.chat_routes import router as chat_router
from routes.radar_routes import router as radar_router
from routes.video_routes import router as video_router

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Dalalyst AI",
    version="3.0.0",
    description="AI investor platform with Groq-powered stock workflows, authentication, and persistent analytics.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(radar_router, prefix="/radar", tags=["Opportunity Radar"])
app.include_router(chart_router, prefix="/chart", tags=["Chart Intelligence"])
app.include_router(chat_router, prefix="/chat", tags=["Market Chat"])
app.include_router(video_router, prefix="/video", tags=["Video Engine"])


@app.get("/")
async def root():
    return {
        "name": settings.project_name,
        "version": "3.0.0",
        "modules": ["radar", "chart", "chat", "video"],
        "auth": ["register", "login", "me"],
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "groq_configured": bool(settings.groq_api_key),
        "database": str(settings.sqlite_path),
    }
