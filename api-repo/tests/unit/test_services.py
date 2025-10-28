"""Unit tests for Services."""

import pytest
from unittest.mock import patch
from app.services.crud_service import ContatoService
from app.schemas.contato import ContatoCreate, ContatoUpdate
from app.models.contato import Contato


@pytest.fixture
def contato_service():
    """Create ContatoService instance."""
    return ContatoService()


@pytest.fixture
def sample_contato_create():
    """Sample ContatoCreate data."""
    return ContatoCreate(
        nome="Maria Silva",
        telefone="11-9999-8888",
        email="maria@example.com",
        motivo="apoio emocional",
    )


@pytest.fixture
def sample_contato_create_llm():
    """Sample ContatoCreate with texto_livre."""
    return ContatoCreate(
        texto_livre="Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
    )


@pytest.fixture
def sample_contato():
    """Sample Contato model."""
    contato = Contato()
    contato.id = 1
    contato.nome = "Maria Silva"
    contato.telefone = "11-9999-8888"
    contato.email = "maria@example.com"
    contato.motivo = "apoio emocional"
    contato.status_mcp = "pendente"
    contato.data_cadastro = "2024-01-01T10:00:00"
    contato.created_at = "2024-01-01T10:00:00"
    return contato


@pytest.mark.asyncio
async def test_create_contato_manual_success(
    contato_service, db, sample_contato_create, sample_contato
):
    """Test successful manual contact creation."""
    # Mock repository
    with patch.object(
        contato_service.repository, "get_by_telefone", return_value=None
    ), patch.object(contato_service.repository, "create", return_value=sample_contato):

        result = await contato_service.create_contato(db, sample_contato_create)

        assert result.id == 1
        assert result.nome == "Maria Silva"
        assert result.telefone == "11-9999-8888"


@pytest.mark.asyncio
async def test_create_contato_duplicate_phone(
    contato_service, db, sample_contato_create, sample_contato
):
    """Test contact creation with duplicate phone number."""
    # Mock repository to return existing contact
    with patch.object(
        contato_service.repository, "get_by_telefone", return_value=sample_contato
    ):

        with pytest.raises(
            ValueError, match="Contact with this phone number already exists"
        ):
            await contato_service.create_contato(db, sample_contato_create)


@pytest.mark.asyncio
async def test_create_contato_missing_required_fields(contato_service, db):
    """Test contact creation with missing required fields."""
    data = ContatoCreate(nome="Maria", telefone=None, motivo=None)

    with patch.object(contato_service.repository, "get_by_telefone", return_value=None):
        with pytest.raises(ValueError, match="Nome, telefone and motivo are required"):
            await contato_service.create_contato(db, data)


@pytest.mark.asyncio
async def test_create_contato_with_llm_success(
    contato_service, db, sample_contato_create_llm, sample_contato
):
    """Test contact creation with LLM extraction."""
    # Mock LLM extraction
    mock_entities = {
        "nome": "Maria Silva",
        "telefone": "11-9999-8888",
        "email": "maria@example.com",
        "motivo": "apoio emocional",
    }

    with patch.object(
        contato_service.repository, "get_by_telefone", return_value=None
    ), patch.object(
        contato_service.llm, "extract_entities", return_value=mock_entities
    ), patch.object(
        contato_service.repository, "create", return_value=sample_contato
    ):

        result = await contato_service.create_contato(db, sample_contato_create_llm)

        assert result.id == 1
        assert result.nome == "Maria Silva"


@pytest.mark.asyncio
async def test_create_contato_llm_failure(
    contato_service, db, sample_contato_create_llm
):
    """Test contact creation when LLM extraction fails."""
    with patch.object(
        contato_service.repository, "get_by_telefone", return_value=None
    ), patch.object(
        contato_service.llm,
        "extract_entities",
        side_effect=Exception("LLM unavailable"),
    ):

        with pytest.raises(ValueError, match="LLM extraction failed"):
            await contato_service.create_contato(db, sample_contato_create_llm)


def test_get_contato_success(contato_service, db, sample_contato):
    """Test getting contact by ID."""
    with patch.object(contato_service.repository, "get", return_value=sample_contato):
        result = contato_service.get_contato(db, 1)

        assert result is not None
        assert result.id == 1
        assert result.nome == "Maria Silva"


def test_get_contato_not_found(contato_service, db):
    """Test getting non-existent contact."""
    with patch.object(contato_service.repository, "get", return_value=None):
        result = contato_service.get_contato(db, 999)

        assert result is None


def test_list_contatos_success(contato_service, db, sample_contato):
    """Test listing contacts."""
    contatos = [sample_contato]

    with patch.object(contato_service.repository, "list_all", return_value=contatos):
        result = contato_service.list_contatos(db, skip=0, limit=10)

        assert len(result) == 1
        assert result[0].id == 1


def test_list_contatos_with_filters(contato_service, db, sample_contato):
    """Test listing contacts with filters."""
    contatos = [sample_contato]

    with patch.object(contato_service.repository, "list_all", return_value=contatos):
        result = contato_service.list_contatos(
            db, skip=0, limit=10, motivo="apoio", status_mcp="pendente"
        )

        assert len(result) == 1


def test_update_contato_success(contato_service, db, sample_contato):
    """Test updating contact."""
    update_data = ContatoUpdate(nome="Maria Silva Updated")

    with patch.object(
        contato_service.repository, "get_by_telefone", return_value=None
    ), patch.object(contato_service.repository, "update", return_value=sample_contato):

        result = contato_service.update_contato(db, 1, update_data)

        assert result is not None
        assert result.id == 1


def test_update_contato_duplicate_phone(contato_service, db, sample_contato):
    """Test updating contact with duplicate phone."""
    update_data = ContatoUpdate(telefone="11-9999-8888")
    existing_contato = Contato()
    existing_contato.id = 2

    with patch.object(
        contato_service.repository, "get_by_telefone", return_value=existing_contato
    ):
        with pytest.raises(
            ValueError, match="Contact with this phone number already exists"
        ):
            contato_service.update_contato(db, 1, update_data)


def test_update_contato_not_found(contato_service, db):
    """Test updating non-existent contact."""
    update_data = ContatoUpdate(nome="Updated")

    with patch.object(
        contato_service.repository, "get_by_telefone", return_value=None
    ), patch.object(contato_service.repository, "update", return_value=None):

        result = contato_service.update_contato(db, 999, update_data)

        assert result is None


def test_delete_contato_success(contato_service, db):
    """Test deleting contact."""
    with patch.object(contato_service.repository, "delete", return_value=True):
        result = contato_service.delete_contato(db, 1)

        assert result is True


def test_delete_contato_not_found(contato_service, db):
    """Test deleting non-existent contact."""
    with patch.object(contato_service.repository, "delete", return_value=False):
        result = contato_service.delete_contato(db, 999)

        assert result is False


def test_export_to_excel_success(contato_service, db, sample_contato):
    """Test Excel export functionality."""
    contatos = [sample_contato]

    with patch.object(contato_service.repository, "list_all", return_value=contatos):
        result = contato_service.export_to_excel(db)

        assert isinstance(result, bytes)
        assert len(result) > 0
