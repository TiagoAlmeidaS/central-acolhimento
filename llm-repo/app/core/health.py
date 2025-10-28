"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "llm-service"}


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # TODO: Add Ollama connectivity check
    return {"status": "ready", "service": "llm-service"}
