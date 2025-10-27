# MCP Client Implementation Guide

## Overview
Este guia documenta como usar o MCP client na API para comunicação com o LLM service.

## Uso Básico

### Inicializar MCP Client
```python
from app.mcp.client import MCPClient

client = MCPClient(base_url="http://llm-service:11434")
```

### Chamar Tool de Extração
```python
# Extrair entidades de texto livre
texto = "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
entities = await client.extract_entities(texto)

print(entities)
# Output: {"nome": "Maria Silva", "telefone": "11-9999-8888", "motivo": "apoio emocional"}
```

## Implementação

### MCPClient Class
```python
import httpx
from typing import Dict, Any

class MCPClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool via JSON-RPC"""
        payload = {
            "jsonrpc": "2.0",
            "method": f"tools/{tool_name}",
            "params": params,
            "id": f"req_{id(self)}"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/mcp",
                json=payload
            )
            response.raise_for_status()
            json_response = response.json()
            
            if "error" in json_response:
                raise MCPError(
                    code=json_response["error"]["code"],
                    message=json_response["error"]["message"]
                )
            
            return json_response["result"]
    
    async def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract named entities from free text"""
        result = await self.call_tool("extract_entities", {
            "text": text,
            "entity_types": ["nome", "telefone", "email", "motivo"]
        })
        return result.get("entities", {})
```

## Error Handling

### Timeout Handling
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def extract_entities_with_retry(text: str):
    """Extract entities with retry logic"""
    try:
        return await client.extract_entities(text)
    except httpx.TimeoutException:
        raise LLMTimeoutError("LLM service timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code >= 500:
            raise LLMUnavailableError("LLM service unavailable")
        else:
            raise
```

### Fallback Strategy
```python
async def create_contato_with_fallback(data: ContatoCreate):
    """Create contact with LLM extraction, fallback to manual input"""
    try:
        # Try LLM extraction
        entities = await client.extract_entities(data.texto_livre)
        return await crud.create_contato(entities)
    except LLMUnavailableError:
        # Fallback: require explicit fields
        if not all([data.nome, data.telefone, data.motivo]):
            raise ValidationError("LLM unavailable, explicit fields required")
        return await crud.create_contato({
            "nome": data.nome,
            "telefone": data.telefone,
            "motivo": data.motivo
        })
```

## Logging e Observabilidade

### Métricas Prometheus
```python
from prometheus_client import Counter, Histogram

llm_calls_total = Counter('llm_calls_total', 'Total LLM calls', ['method', 'status'])
llm_duration = Histogram('llm_call_duration_seconds', 'LLM call duration')

async def extract_entities_with_metrics(text: str):
    """Extract entities with metrics"""
    start = time.time()
    try:
        entities = await client.extract_entities(text)
        llm_calls_total.labels(method='extract_entities', status='success').inc()
        return entities
    except Exception:
        llm_calls_total.labels(method='extract_entities', status='failure').inc()
        raise
    finally:
        llm_duration.observe(time.time() - start)
```

### Structured Logging
```python
import structlog

logger = structlog.get_logger()

async def extract_entities_with_logging(text: str):
    """Extract entities with structured logging"""
    logger.info("llm_extraction_start", text_preview=text[:50])
    try:
        entities = await client.extract_entities(text)
        logger.info("llm_extraction_success", entities=entities)
        return entities
    except Exception as e:
        logger.error("llm_extraction_failure", error=str(e), exc_info=True)
        raise
```

## Testing

### Mock MCP Client para Tests
```python
from unittest.mock import AsyncMock

@pytest.fixture
def mock_mcp_client():
    client = AsyncMock(spec=MCPClient)
    client.extract_entities.return_value = {
        "nome": "Test User",
        "telefone": "11-9999-8888",
        "motivo": "test"
    }
    return client

@pytest.mark.asyncio
async def test_create_contato_with_llm(mock_mcp_client):
    # Test with mocked LLM
    result = await create_contato_with_fallback(ContatoCreate(texto_livre="..."))
    assert result.nome == "Test User"
```

## Referências

- `app/mcp/client.py` - Implementação completa do MCP client
- `app/services/llm_integration.py` - Service layer que usa MCP client
- `docs/mcp/mcp-overview.md` - Overview do protocolo MCP
