# Model Context Protocol (MCP) Integration

## Overview
O sistema Central de Acolhimento utiliza **Model Context Protocol (MCP)** para comunicação estruturada entre a API e o serviço LLM. MCP é um protocolo aberto padrão que permite intercâmbio bidirecional de contexto e ferramentas com LLMs.

## O que é MCP?

Model Context Protocol (MCP) é um protocolo baseado em JSON-RPC que padroniza a comunicação com modelos de linguagem, permitindo:
- **Tools**: LLMs podem invocar ferramentas externas
- **Resources**: LLMs podem acessar recursos de contexto
- **Prompts**: Templates de prompts estruturados
- **Bidirectional Communication**: Cliente e servidor podem enviar mensagens

## Arquitetura MCP no Sistema

```
┌─────────────────────────────────────────────────────────┐
│                   API Service                            │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ MCP Client (app/mcp/client.py)                  │   │
│  │ - Call tools                                      │   │
│  │ - Handle JSON-RPC requests                       │   │
│  │ - Parse responses                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                           │                             │
│                           ▼                             │
│                     HTTP/SSE/WebSocket                  │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   LLM Service                             │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ MCP Server (llm/mcp/server.py)                  │   │
│  │ - Handle JSON-RPC requests                      │   │
│  │ - Route to Ollama                                │   │
│  │ - Return structured responses                    │   │
│  └─────────────────────────────────────────────────┘   │
│                           │                             │
│                           ▼                             │
│                     Ollama + llama3:8b                  │
└──────────────────────────────────────────────────────────┘
```

## MCP Protocol Details

### Request Format (JSON-RPC)
```json
{
  "jsonrpc": "2.0",
  "method": "tools/extract_entities",
  "params": {
    "text": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional",
    "entity_types": ["nome", "telefone", "email", "motivo", "data"]
  },
  "id": "req_123"
}
```

### Response Format
```json
{
  "jsonrpc": "2.0",
  "result": {
    "entities": {
      "nome": "Maria Silva",
      "telefone": "11-9999-8888",
      "motivo": "apoio emocional",
      "confianca": 0.92
    }
  },
  "id": "req_123"
}
```

## MCP Tools Implemented

### 1. extract_entities
**Purpose**: Extrai entidades (nome, telefone, email, motivo) de texto livre

**Request**:
```json
{
  "method": "tools/extract_entities",
  "params": {
    "text": "Novo contato: João Silva, tel: 11-8888-7777, email: joao@example.com, motivo: orientação jurídica"
  }
}
```

**Response**:
```json
{
  "result": {
    "entities": {
      "nome": "João Silva",
      "telefone": "11-8888-7777",
      "email": "joao@example.com",
      "motivo": "orientação jurídica",
      "confianca": 0.95
    }
  }
}
```

**Implementation**: `llm/mcp/tools/extract_entities.py`

## MCP Resources

### Prompt Templates
MCP resources incluem templates de prompts para diferentes cenários:

- **entity_extraction_prompt**: Template para extração de entidades
- **validation_prompt**: Template para validação de dados extraídos
- **formatting_prompt**: Template para formatação de outputs

**Example Resource**:
```json
{
  "jsonrpc": "2.0",
  "method": "resources/get",
  "params": {
    "name": "entity_extraction_prompt"
  },
  "id": "req_456"
}
```

## Error Handling

### Error Response Format
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Internal error: LLM timeout",
    "data": {
      "timeout_seconds": 30,
      "retry_after": 5
    }
  },
  "id": "req_123"
}
```

### Error Codes
- `-32700`: Parse error (invalid JSON)
- `-32600`: Invalid Request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32000`: LLM timeout
- `-32001`: LLM unavailable

## Retry Logic

### Exponential Backoff
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def call_mcp_tool(tool_name: str, params: dict):
    """Call MCP tool with retry logic"""
    pass
```

### Circuit Breaker
Se 5 falhas consecutivas:
- **Open Circuit**: Return error immediately (no LLM calls)
- **Half-Open**: After 60s, test with single request
- **Closed**: Resume normal operation

## Documentation Files

- `docs/mcp/mcp-overview.md` (este arquivo)
- `docs/mcp/mcp-client.md` - Guia de uso do MCP client na API
- `docs/mcp/mcp-server.md` - Guia de implementação do MCP server
- `docs/mcp/prompts.md` - Prompt engineering para extração de entidades

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Ollama Documentation](https://ollama.ai/)
