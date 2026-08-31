"""
FastAPI main application entry point.
Starts the backend server with all routes registered.

Run: uvicorn backend.main:app --reload --port 8000
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.database import init_db
from database.seed import run as seed_db

from backend.routes import profile, analysis, recommendations, assessment, progress, chat, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB and seed data on startup."""
    print("🚀 LearnPath AI Backend starting up...")
    init_db()
    seed_db()
    # Initialize knowledge graph eagerly
    try:
        from ml.knowledge_graph import get_knowledge_graph
        get_knowledge_graph()
    except Exception as e:
        print(f"⚠️  KG init warning: {e}")
    yield
    print("🛑 LearnPath AI Backend shutting down.")


app = FastAPI(
    title="LearnPath AI API",
    description="AI-Powered Personalized Learning Path Recommender — HCLTech AMPLIFIED Hackathon",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allows Streamlit frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(recommendations.router, prefix="/api", tags=["Recommendations"])
app.include_router(assessment.router, prefix="/api", tags=["Assessment"])
app.include_router(progress.router, prefix="/api", tags=["Progress"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "LearnPath AI Backend is running!",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "LearnPath AI"}
