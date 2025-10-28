"""Unit tests for entity extractor."""

import pytest
from unittest.mock import patch, AsyncMock
from app.entity_extractors.extractor import EntityExtractor


@pytest.mark.asyncio
async def test_extract_entities_success(entity_extractor, sample_text, sample_llm_response):
    """Test successful entity extraction."""
    with patch.object(entity_extractor.ollama, 'generate', return_value=sample_llm_response):
        result = await entity_extractor.extract_entities(sample_text)
        
        assert result["nome"] == "Maria Silva"
        assert result["telefone"] == "11-9999-8888"
        assert result["email"] == "maria@example.com"
        assert result["motivo"] == "apoio emocional"


@pytest.mark.asyncio
async def test_extract_entities_empty_text(entity_extractor):
    """Test extraction with empty text."""
    with pytest.raises(ValueError, match="Text cannot be empty"):
        await entity_extractor.extract_entities("")


@pytest.mark.asyncio
async def test_extract_entities_too_long(entity_extractor):
    """Test extraction with text too long."""
    long_text = "a" * 2001
    with pytest.raises(ValueError, match="Text too long"):
        await entity_extractor.extract_entities(long_text)


def test_normalize_phone(entity_extractor):
    """Test phone number normalization."""
    assert entity_extractor._normalize_phone("(11) 9999-8888") == "11-9999-8888"
    assert entity_extractor._normalize_phone("11 9999 8888") == "11-9999-8888"
    assert entity_extractor._normalize_phone("1199998888") == "11-9999-8888"


def test_parse_entities_valid_json(entity_extractor):
    """Test parsing valid JSON response."""
    response = '{"nome": "João", "telefone": "11-8888-7777"}'
    result = entity_extractor._parse_entities(response)
    
    assert result["nome"] == "João"
    assert result["telefone"] == "11-8888-7777"


def test_parse_entities_invalid_json(entity_extractor):
    """Test parsing invalid JSON response."""
    response = "Invalid response without JSON"
    result = entity_extractor._parse_entities(response)
    
    assert result["nome"] is None
    assert result["telefone"] is None
