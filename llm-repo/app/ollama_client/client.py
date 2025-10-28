"""Ollama client for LLM integration."""

import httpx
import structlog
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = structlog.get_logger()


class OllamaClient:
    """Client for Ollama LLM service."""

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    @retry(
        stop=stop_after_attempt(settings.OLLAMA_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def generate(
        self, prompt: str, system: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate text using Ollama."""
        logger.info("ollama_generate_start", model=self.model, prompt_preview=prompt[:50])

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "max_tokens": 1000,
            },
        }

        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()

                result = response.json()
                logger.info("ollama_generate_success", model=self.model)
                return result

        except Exception as e:
            logger.error("ollama_generate_failure", error=str(e), model=self.model)
            raise

    async def list_models(self) -> Dict[str, Any]:
        """List available models."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("ollama_list_models_failure", error=str(e))
            raise

    async def check_model(self, model: str = None) -> bool:
        """Check if model is available."""
        model = model or self.model
        try:
            models = await self.list_models()
            available_models = [m["name"] for m in models.get("models", [])]
            return model in available_models
        except Exception:
            return False

    async def pull_model(self, model: str = None) -> Dict[str, Any]:
        """Pull/download a model."""
        model = model or self.model
        logger.info("ollama_pull_model_start", model=model)

        try:
            async with httpx.AsyncClient(timeout=300) as client:  # Longer timeout for pull
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model},
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("ollama_pull_model_failure", error=str(e), model=model)
            raise
