"""Test configuration and fixtures."""

import pytest
from unittest.mock import AsyncMock, patch
from app.entity_extractors.extractor import EntityExtractor
from app.validators.validator import DataValidator
from app.ollama_client.client import OllamaClient


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client."""
    client = OllamaClient()
    client.generate = AsyncMock()
    return client


@pytest.fixture
def entity_extractor():
    """Entity extractor instance."""
    return EntityExtractor()


@pytest.fixture
def data_validator():
    """Data validator instance."""
    return DataValidator()


@pytest.fixture
def sample_text():
    """Sample text for extraction."""
    return "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"


@pytest.fixture
def sample_entities():
    """Sample extracted entities."""
    return {
        "nome": "Maria Silva",
        "telefone": "11-9999-8888",
        "email": "maria@example.com",
        "motivo": "apoio emocional",
        "data": None,
    }


@pytest.fixture
def sample_llm_response():
    """Sample LLM response."""
    return {
        "response": '{"nome": "Maria Silva", "telefone": "11-9999-8888", "email": "maria@example.com", "motivo": "apoio emocional"}'
    }
