"""Entity extraction engine."""

import json
import re
from typing import Dict, Any, Optional
import structlog

from app.ollama_client.client import OllamaClient
from app.prompt_templates.manager import PromptTemplateManager
from app.core.config import settings

logger = structlog.get_logger()


class EntityExtractor:
    """Entity extraction engine using LLM."""

    def __init__(self):
        self.ollama = OllamaClient()
        self.template_manager = PromptTemplateManager()

    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text using LLM."""
        logger.info("entity_extraction_start", text_preview=text[:50])

        # Validate input
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")

        if len(text) > settings.MAX_TEXT_LENGTH:
            raise ValueError(f"Text too long (max {settings.MAX_TEXT_LENGTH} characters)")

        # Generate prompt
        prompt = self.template_manager.render_entity_extraction(text)

        try:
            # Call LLM
            response = await self.ollama.generate(prompt)
            llm_response = response.get("response", "")

            # Parse response
            entities = self._parse_entities(llm_response)

            # Validate extracted entities
            validated_entities = self._validate_entities(entities)

            logger.info("entity_extraction_success", entities=validated_entities)
            return validated_entities

        except Exception as e:
            logger.error("entity_extraction_failure", error=str(e))
            raise

    def _parse_entities(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract entities."""
        # Try to extract JSON from response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                entities = json.loads(json_str)
                return entities
            except json.JSONDecodeError:
                logger.warning("llm_json_parse_failed", response=response[:200])

        # Fallback: return empty entities
        return {
            "nome": None,
            "telefone": None,
            "email": None,
            "motivo": None,
            "data": None,
        }

    def _validate_entities(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize extracted entities."""
        validated = {}

        # Validate nome
        nome = entities.get("nome")
        if nome and isinstance(nome, str) and len(nome.strip()) > 0:
            validated["nome"] = nome.strip()
        else:
            validated["nome"] = None

        # Validate telefone
        telefone = entities.get("telefone")
        if telefone and isinstance(telefone, str):
            validated["telefone"] = self._normalize_phone(telefone)
        else:
            validated["telefone"] = None

        # Validate email
        email = entities.get("email")
        if email and isinstance(email, str) and "@" in email:
            validated["email"] = email.strip().lower()
        else:
            validated["email"] = None

        # Validate motivo
        motivo = entities.get("motivo")
        if motivo and isinstance(motivo, str) and len(motivo.strip()) > 0:
            validated["motivo"] = motivo.strip()
        else:
            validated["motivo"] = None

        # Validate data
        data = entities.get("data")
        if data and isinstance(data, str) and len(data.strip()) > 0:
            validated["data"] = data.strip()
        else:
            validated["data"] = None

        return validated

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
