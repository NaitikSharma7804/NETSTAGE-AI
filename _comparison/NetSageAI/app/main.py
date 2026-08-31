"""NetSage AI - FastAPI Main Backend Application."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database.database import Base, engine
from database.seed import seed_database
from app.api import routes_cases, routes_diagnosis, routes_review

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for database initialization and startup seeding."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(
    title="NetSage AI Backend API",
    description="Cisco Network Troubleshooting Assistant API combining deterministic rules and AI diagnosis.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit / Frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(routes_cases.router)
app.include_router(routes_diagnosis.router)
app.include_router(routes_review.router)


from ai.provider import get_llm_provider


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint confirming API operational status and active LLM mode."""
    provider = get_llm_provider()
    return {
        "status": "healthy",
        "service": "NetSage AI API",
        "llm_provider": provider.provider_name,
        "mode": provider.mode,
        "database": "sqlite"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
