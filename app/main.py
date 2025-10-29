"""
Unwoldam Tarot Card LLM API
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import tarot_reading, tarot_master

app = FastAPI(
    title="Unwoldam Tarot API",
    description="AI-powered Tarot Card Reading API with multiple LLM providers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tarot_reading.router, prefix="/api/v1/tarot", tags=["Tarot Reading"])
app.include_router(tarot_master.router, prefix="/api/v1/tarot", tags=["Tarot Master"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "active",
        "service": "Unwoldam Tarot API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "llm_providers": ["claude", "openai", "gemini"],
        "features": ["tarot_reading", "tarot_master", "rag", "session_management"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
