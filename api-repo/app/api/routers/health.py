"""Health check and readiness probes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Liveness probe - service is running."""
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check():
    """Readiness probe - service is ready to accept requests."""
    return {"status": "ready"}
