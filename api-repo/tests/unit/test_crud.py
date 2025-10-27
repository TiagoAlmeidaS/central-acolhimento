"""Unit tests for CRUD operations."""

import pytest
from app.crud.contato import ContatoRepository
from app.models.contato import Contato


def test_create_contato(db, sample_contato_data):
    """Test creating a contact."""
    contato = ContatoRepository.create(db, sample_contato_data)
    
    assert contato.id is not None
    assert contato.nome == "Maria Silva"
    assert contato.telefone == "11-9999-8888"
    

def test_get_contato(db, sample_contato_data):
    """Test getting a contact by ID."""
    # Create a contact first
    contato = ContatoRepository.create(db, sample_contato_data)
    contato_id = contato.id
    
    # Get the contact
    retrieved = ContatoRepository.get(db, contato_id)
    
    assert retrieved is not None
    assert retrieved.id == contato_id
    assert retrieved.nome == "Maria Silva"


def test_get_contato_not_found(db):
    """Test getting a non-existent contact."""
    result = ContatoRepository.get(db, 99999)
    assert result is None


def test_get_by_telefone(db, sample_contato_data):
    """Test getting a contact by phone number."""
    # Create a contact
    ContatoRepository.create(db, sample_contato_data)
    
    # Get by phone
    retrieved = ContatoRepository.get_by_telefone(db, "11-9999-8888")
    
    assert retrieved is not None
    assert retrieved.telefone == "11-9999-8888"


def test_list_all_contatos(db):
    """Test listing all contacts."""
    # Create multiple contacts
    for i in range(5):
        ContatoRepository.create(db, {
            "nome": f"Test User {i}",
            "telefone": f"11-9999-{1000+i}",
            "motivo": f"test {i}"
        })
    
    # List all
    contatos = ContatoRepository.list_all(db, skip=0, limit=10)
    
    assert len(contatos) == 5


def test_list_contatos_with_filter(db):
    """Test listing contacts with filter."""
    # Create contacts with different motivos
    ContatoRepository.create(db, {
        "nome": "User 1",
        "telefone": "11-1111-1111",
        "motivo": "apoio emocional"
    })
    ContatoRepository.create(db, {
        "nome": "User 2",
        "telefone": "11-2222-2222",
        "motivo": "orientação jurídica"
    })
    
    # Filter by motivo
    contatos = ContatoRepository.list_all(db, motivo="apoio emocional")
    
    assert len(contatos) == 1
    assert contatos[0].motivo == "apoio emocional"


def test_update_contato(db, sample_contato_data):
    """Test updating a contact."""
    # Create a contact
    contato = ContatoRepository.create(db, sample_contato_data)
    contato_id = contato.id
    
    # Update it
    update_data = {"nome": "Maria Silva Updated"}
    updated = ContatoRepository.update(db, contato_id, update_data)
    
    assert updated.nome == "Maria Silva Updated"
    assert updated.telefone == "11-9999-8888"  # Unchanged


def test_delete_contato(db, sample_contato_data):
    """Test deleting a contact."""
    # Create a contact
    contato = ContatoRepository.create(db, sample_contato_data)
    contato_id = contato.id
    
    # Delete it
    success = ContatoRepository.delete(db, contato_id)
    
    assert success is True
    
    # Verify it's deleted
    retrieved = ContatoRepository.get(db, contato_id)
    assert retrieved is None


def test_count_contatos(db):
    """Test counting contacts."""
    # Create some contacts
    for i in range(3):
        ContatoRepository.create(db, {
            "nome": f"User {i}",
            "telefone": f"11-9999-{1000+i}",
            "motivo": "test"
        })
    
    count = ContatoRepository.count(db)
    assert count == 3
