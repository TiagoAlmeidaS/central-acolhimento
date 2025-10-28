"""Unit tests for models."""

from datetime import datetime
from app.models.contato import Contato


def test_contato_model_creation(db, sample_contato_data):
    """Test Contato model creation."""
    contato = Contato(**sample_contato_data)
    db.add(contato)
    db.commit()
    db.refresh(contato)

    assert contato.id is not None
    assert contato.nome == "Maria Silva"
    assert contato.telefone == "11-9999-8888"
    assert contato.email == "maria@example.com"
    assert contato.motivo == "apoio emocional"
    assert contato.status_mcp == "pendente"
    assert isinstance(contato.created_at, datetime)


def test_contato_repr(db, sample_contato_data):
    """Test Contato __repr__ method."""
    contato = Contato(**sample_contato_data)
    db.add(contato)
    db.commit()
    db.refresh(contato)

    repr_str = repr(contato)
    assert "Contato" in repr_str
    assert str(contato.id) in repr_str
    assert "Maria Silva" in repr_str


def test_contato_without_email(db):
    """Test Contato without email (optional field)."""
    contato_data = {
        "nome": "João Silva",
        "telefone": "11-8888-7777",
        "motivo": "orientação jurídica",
    }
    contato = Contato(**contato_data)
    db.add(contato)
    db.commit()
    db.refresh(contato)

    assert contato.email is None
