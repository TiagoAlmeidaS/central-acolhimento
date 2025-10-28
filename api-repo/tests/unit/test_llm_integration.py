"""Unit tests for LLM integration."""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.llm_integration import LLMIntegration


@pytest.mark.asyncio
async def test_extract_entities_success():
    """Test successful entity extraction."""
    # Mock LLM response
    mock_response = {
        "response": '{"nome": "Maria Silva", "telefone": "11-9999-8888", "email": "maria@example.com", "motivo": "apoio emocional"}'
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            json=lambda: mock_response, raise_for_status=lambda: None
        )

        llm = LLMIntegration(base_url="http://test-ollama")
        entities = await llm.extract_entities(
            "Novo contato: Maria Silva, telefone 11-9999-8888"
        )

        assert entities["nome"] == "Maria Silva"
        assert entities["telefone"] == "11-9999-8888"


@pytest.mark.asyncio
async def test_extract_entities_with_retry():
    """Test entity extraction with retry on failure."""
    # Mock LLM to fail first two times
    call_count = 0

    async def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("LLM unavailable")
        return AsyncMock(
            json=lambda: {"response": '{"nome": "Test"}'}, raise_for_status=lambda: None
        )

    # llm = LLMIntegration(base_url="http://test-ollama")
    # This should succeed after retries
    # (implementation needs tenacity for this to work in real scenario)
    pass  # Placeholder test


def test_normalize_phone():
    """Test phone number normalization."""
    llm = LLMIntegration()

    # Test various formats
    assert llm._normalize_phone("(11) 9999-8888") == "11-9999-8888"
    assert llm._normalize_phone("11 9999 8888") == "11-9999-8888"
    assert llm._normalize_phone("1199998888") == "11-9999-8888"


def test_build_extraction_prompt():
    """Test prompt building for entity extraction."""
    llm = LLMIntegration()
    text = "Novo contato: João, tel 11-8888-7777"
    prompt = llm._build_extraction_prompt(text)

    assert text in prompt
    assert "nome" in prompt
    assert "telefone" in prompt
    assert "email" in prompt
    assert "motivo" in prompt
