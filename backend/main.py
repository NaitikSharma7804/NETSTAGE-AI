"""
NetSage AI FastAPI Application Entry Point.
"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import engine, Base
from backend.api import cases, diagnosis, review, verification, analytics, responsible_ai

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="NetSage AI Backend API",
    description="Evidence-driven Cisco Network Troubleshooting Assistant with Deterministic Validation and Human Review",
    version="1.2.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit frontend and local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(cases.router)
app.include_router(diagnosis.router)
app.include_router(review.router)
app.include_router(verification.router)
app.include_router(analytics.router)
app.include_router(responsible_ai.router)