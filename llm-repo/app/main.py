"""LLM Service main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.mcp_server.router import router as mcp_router
from app.core.health import router as health_router

app = FastAPI(
    title="Central de Acolhimento LLM Service",
    description="""
## 🤖 LLM Service para Central de Acolhimento

Serviço de processamento de linguagem natural via Ollama + llama3:8b com integração Model Context Protocol (MCP).

### Features

* **MCP Server** - Servidor Model Context Protocol
* **Entity Extraction** - Extração de entidades de texto livre
* **Ollama Integration** - Integração com Ollama local
* **Prompt Templates** - Templates otimizados para llama3:8b
* **Data Validation** - Validação de dados extraídos

### Endpoints Principais

* `POST /mcp/extract` - Extrair entidades de texto livre
* `POST /mcp/validate` - Validar dados extraídos
* `GET /mcp/models` - Listar modelos disponíveis
* `GET /health` - Health check

### Como Usar

1. Para extração de entidades:
   ```json
   {
     "text": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
   }
   ```

2. Para validação de dados:
   ```json
   {
     "data": {
       "nome": "Maria Silva",
       "telefone": "11-9999-8888",
       "email": "maria@example.com",
       "motivo": "apoio emocional"
     }
   }
   ```

### Documentação

* Swagger UI: `/docs` (interativo)
* ReDoc: `/redoc` (documentação formatada)
* OpenAPI JSON: `/openapi.json`
    """,
    version="0.1.0",
    contact={
        "name": "Central de Acolhimento LLM Service",
        "url": "https://github.com/your-org/central-acolhimento-llm",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(mcp_router, prefix="/mcp", tags=["mcp"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Central de Acolhimento LLM Service",
        "version": "0.1.0",
        "status": "running",
        "mcp_endpoints": [
            "/mcp/extract",
            "/mcp/validate",
            "/mcp/models",
        ],
    }
