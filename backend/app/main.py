"""
India News Tracker - FastAPI Application
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db, init_db, close_db
from app.api.v1 import router as api_v1_router

app = FastAPI(
    title="India News Tracker API",
    description="API for tracking and analyzing news incidents across India",
    version="0.1.0",
)

# Include API routes
app.include_router(api_v1_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    """Close database connections on shutdown"""
    await close_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "India News Tracker API",
        "version": "0.1.0",
        "status": "running",
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Try to execute a simple query
        await db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }
