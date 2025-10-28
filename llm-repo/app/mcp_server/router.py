"""MCP Server implementation."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from app.entity_extractors.extractor import EntityExtractor
from app.validators.validator import DataValidator
from app.ollama_client.client import OllamaClient

router = APIRouter()

# Initialize services
extractor = EntityExtractor()
validator = DataValidator()
ollama_client = OllamaClient()


class ExtractRequest(BaseModel):
    """Request model for entity extraction."""
    text: str = Field(..., description="Text to extract entities from", max_length=2000)


class ExtractResponse(BaseModel):
    """Response model for entity extraction."""
    entities: Dict[str, Any]
    confidence: float
    success: bool
    message: Optional[str] = None


class ValidateRequest(BaseModel):
    """Request model for data validation."""
    data: Dict[str, Any] = Field(..., description="Data to validate")


class ValidateResponse(BaseModel):
    """Response model for data validation."""
    valid: bool
    corrected_data: Dict[str, Any]
    errors: List[str]
    success: bool
    message: Optional[str] = None


class ModelsResponse(BaseModel):
    """Response model for available models."""
    models: List[Dict[str, Any]]
    current_model: str
    success: bool


@router.post("/extract", response_model=ExtractResponse)
async def extract_entities(request: ExtractRequest):
    """Extract entities from text using LLM."""
    try:
        # Extract entities
        entities = await extractor.extract_entities(request.text)
        
        # Calculate confidence
        confidence = validator.validate_extraction_confidence(entities)
        
        return ExtractResponse(
            entities=entities,
            confidence=confidence,
            success=True,
            message="Entities extracted successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/validate", response_model=ValidateResponse)
async def validate_data(request: ValidateRequest):
    """Validate extracted data."""
    try:
        # Validate data
        is_valid, corrected_data, errors = validator.validate_contact_data(request.data)
        
        return ValidateResponse(
            valid=is_valid,
            corrected_data=corrected_data,
            errors=errors,
            success=True,
            message="Data validated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """List available Ollama models."""
    try:
        models_data = await ollama_client.list_models()
        models = models_data.get("models", [])
        current_model = ollama_client.model
        
        return ModelsResponse(
            models=models,
            current_model=current_model,
            success=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/health")
async def mcp_health():
    """MCP service health check."""
    try:
        # Check Ollama connectivity
        is_available = await ollama_client.check_model()
        
        return {
            "status": "healthy" if is_available else "degraded",
            "service": "mcp",
            "ollama_available": is_available,
            "current_model": ollama_client.model
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "mcp",
            "error": str(e)
        }
