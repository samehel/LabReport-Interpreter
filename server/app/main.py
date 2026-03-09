"""
LabReport Interpreter — FastAPI Backend

Main application entry point. Configures CORS, rate limiting,
registers all routers, and creates database tables on startup.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import create_tables

# Import routers
from app.routers import auth, reports, metrics, summary


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup: create DB tables and upload directory
    await create_tables()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print("✓ Database tables created")
    print("✓ Upload directory ready")
    print(f"✓ Server running — API docs at http://localhost:8000/docs")
    yield
    # Shutdown: nothing to clean up


# Create FastAPI application
app = FastAPI(
    title="LabReport Interpreter API",
    description=(
        "REST API for the LabReport Interpreter mobile application. "
        "Provides authentication, lab report management, ML-powered analysis "
        "(OCR, classification, condition prediction, summarization), "
        "trend tracking, and PDF report generation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(metrics.router)
app.include_router(summary.router)