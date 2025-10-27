"""FastAPI application main entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routers import contatos, health

app = FastAPI(
    title="Central de Acolhimento API",
    description="API REST para cadastro de contatos com processamento LLM local",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(contatos.router, prefix="/api/v1", tags=["contatos"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Central de Acolhimento API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
