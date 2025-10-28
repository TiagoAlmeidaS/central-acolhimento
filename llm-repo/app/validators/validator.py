"""Data validators for extracted entities."""

import re
from typing import Dict, Any, List, Tuple
import structlog

logger = structlog.get_logger()


class DataValidator:
    """Validator for extracted entity data."""

    def __init__(self):
        self.phone_pattern = re.compile(r"^\d{2}-\d{4,5}-\d{4}$")
        self.email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        self.date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def validate_contact_data(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Validate contact data and return validation result."""
        errors = []
        corrected_data = {}

        # Validate nome
        nome = data.get("nome")
        if not nome or not isinstance(nome, str) or len(nome.strip()) < 2:
            errors.append("Nome deve ter pelo menos 2 caracteres")
            corrected_data["nome"] = None
        else:
            corrected_data["nome"] = nome.strip()

        # Validate telefone
        telefone = data.get("telefone")
        if not telefone or not isinstance(telefone, str):
            errors.append("Telefone é obrigatório")
            corrected_data["telefone"] = None
        else:
            normalized_phone = self._normalize_phone(telefone)
            if not self.phone_pattern.match(normalized_phone):
                errors.append("Telefone deve estar no formato XX-XXXX-XXXX")
                corrected_data["telefone"] = None
            else:
                corrected_data["telefone"] = normalized_phone

        # Validate email (optional)
        email = data.get("email")
        if email and isinstance(email, str) and email.strip():
            email = email.strip().lower()
            if not self.email_pattern.match(email):
                errors.append("Email deve ter formato válido")
                corrected_data["email"] = None
            else:
                corrected_data["email"] = email
        else:
            corrected_data["email"] = None

        # Validate motivo
        motivo = data.get("motivo")
        if not motivo or not isinstance(motivo, str) or len(motivo.strip()) < 3:
            errors.append("Motivo deve ter pelo menos 3 caracteres")
            corrected_data["motivo"] = None
        else:
            corrected_data["motivo"] = motivo.strip()

        # Validate data (optional)
        data_contato = data.get("data")
        if data_contato and isinstance(data_contato, str) and data_contato.strip():
            data_contato = data_contato.strip()
            if not self.date_pattern.match(data_contato):
                errors.append("Data deve estar no formato YYYY-MM-DD")
                corrected_data["data"] = None
            else:
                corrected_data["data"] = data_contato
        else:
            corrected_data["data"] = None

        is_valid = len(errors) == 0
        return is_valid, corrected_data, errors

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to Brazilian format."""
        # Remove all non-digit characters
        digits = "".join(filter(str.isdigit, phone))

        # Format as XX-XXXX-XXXX or XX-9XXXX-XXXX if 11 digits
        if len(digits) == 11:
            # Mobile format: XX-9XXXX-XXXX
            return f"{digits[0:2]}-{digits[2:7]}-{digits[7:]}"
        elif len(digits) == 10:
            # Landline format: XX-XXXX-XXXX
            return f"{digits[0:2]}-{digits[2:6]}-{digits[6:]}"

        return phone

    def validate_extraction_confidence(self, entities: Dict[str, Any]) -> float:
        """Calculate confidence score for extracted entities."""
        total_fields = 5  # nome, telefone, email, motivo, data
        filled_fields = sum(1 for value in entities.values() if value is not None)

        # Base confidence on filled fields
        base_confidence = filled_fields / total_fields

        # Bonus for required fields
        required_fields = ["nome", "telefone", "motivo"]
        required_filled = sum(1 for field in required_fields if entities.get(field) is not None)
        required_bonus = (required_filled / len(required_fields)) * 0.3

        confidence = min(base_confidence + required_bonus, 1.0)
        return round(confidence, 2)
