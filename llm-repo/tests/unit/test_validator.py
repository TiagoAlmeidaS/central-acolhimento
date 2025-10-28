"""Unit tests for data validator."""

import pytest
from app.validators.validator import DataValidator


def test_validate_contact_data_valid(data_validator, sample_entities):
    """Test validation of valid contact data."""
    is_valid, corrected_data, errors = data_validator.validate_contact_data(sample_entities)
    
    assert is_valid is True
    assert len(errors) == 0
    assert corrected_data["nome"] == "Maria Silva"
    assert corrected_data["telefone"] == "11-9999-8888"


def test_validate_contact_data_invalid(data_validator):
    """Test validation of invalid contact data."""
    invalid_data = {
        "nome": "A",  # Too short
        "telefone": "invalid",  # Invalid format
        "email": "invalid-email",  # Invalid format
        "motivo": "OK",  # Too short
    }
    
    is_valid, corrected_data, errors = data_validator.validate_contact_data(invalid_data)
    
    assert is_valid is False
    assert len(errors) > 0
    assert "Nome deve ter pelo menos 2 caracteres" in errors
    assert "Telefone deve estar no formato XX-XXXX-XXXX" in errors


def test_validate_extraction_confidence(data_validator, sample_entities):
    """Test confidence calculation."""
    confidence = data_validator.validate_extraction_confidence(sample_entities)
    
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Should be high for complete data


def test_normalize_phone(data_validator):
    """Test phone normalization in validator."""
    assert data_validator._normalize_phone("(11) 9999-8888") == "11-9999-8888"
    assert data_validator._normalize_phone("11 9999 8888") == "11-9999-8888"
    assert data_validator._normalize_phone("1199998888") == "11-9999-8888"
