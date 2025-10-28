"""LLM integration service."""

from typing import Dict, Any
import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = structlog.get_logger()


class LLMIntegration:
    """Integration with LLM service via Ollama for entity extraction."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.LLM_URL
        self.timeout = settings.LLM_TIMEOUT

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from free text using LLM."""
        logger.info("llm_extraction_start", text_preview=text[:50])

        prompt = self._build_extraction_prompt(text)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": "llama3:8b", "prompt": prompt, "stream": False},
                )
                response.raise_for_status()

                result = response.json()
                entities = self._parse_entities(result.get("response", ""))

                logger.info("llm_extraction_success", entities=entities)
                return entities

        except Exception as e:
            logger.error("llm_extraction_failure", error=str(e))
            raise

    def _build_extraction_prompt(self, text: str) -> str:
        """Build prompt for entity extraction."""
        return f"""Você é um assistente especializado em extrair informações estruturadas de texto livre.

Tarefa: Extraia as seguintes entidades do texto fornecido:
- nome: Nome completo da pessoa
- telefone: Número de telefone no formato brasileiro (XX) XXXXX-XXXX
- email: Email válido (opcional)
- motivo: Motivo do contato (apoio emocional, orientação jurídica, etc.)
- data: Data do contato se mencionada (formato YYYY-MM-DD)

Texto de entrada:
{text}

Instruções:
1. Extraia APENAS as entidades explicitamente mencionadas no texto
2. Se uma entidade não for mencionada, retorne null
3. Telefone deve estar no formato brasileiro: XX-XXXX-XXXX (sem parênteses)
4. Email deve ser válido (contendo @)
5. Retorne APENAS JSON válido, sem markdown, sem explicações

Formato de saída (JSON):
{{
  "nome": "...",
  "telefone": "...",
  "email": "..." ou null,
  "motivo": "...",
  "data": "..." ou null
}}
"""

    def _parse_entities(self, response: str) -> Dict[str, str]:
        """Parse LLM response to extract entities."""
        import json
        import re

        # Try to extract JSON from response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                entities = json.loads(json_str)
                # Normalize phone format
                if entities.get("telefone"):
                    entities["telefone"] = self._normalize_phone(entities["telefone"])
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
