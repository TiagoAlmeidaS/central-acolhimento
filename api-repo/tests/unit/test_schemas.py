"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.contato import ContatoCreate, ContatoUpdate, ContatoOut


def test_contato_create_with_explicit_fields():
    """Test ContatoCreate with explicit fields."""
    data = ContatoCreate(
        nome="Maria Silva",
        telefone="11-9999-8888",
        email="maria@example.com",
        motivo="apoio emocional"
    )
    
    assert data.nome == "Maria Silva"
    assert data.telefone == "11-9999-8888"
    assert data.email == "maria@example.com"
    assert data.motivo == "apoio emocional"


def test_contato_create_with_texto_livre():
    """Test ContatoCreate with texto_livre for LLM extraction."""
    data = ContatoCreate(
        texto_livre="Novo contato: João, telefone 11-8888-7777"
    )
    
    assert data.texto_livre == "Novo contato: João, telefone 11-8888-7777"


def test_contato_update_partial():
    """Test ContatoUpdate with partial fields."""
    data = ContatoUpdate(nome="Maria Silva da Silva")
    
    # Only nome is set
    assert data.nome == "Maria Silva da Silva"
    assert data.telefone is None
    assert data.email is None
    assert data.motivo is None
