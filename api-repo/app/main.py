"""FastAPI application main entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.api.routers import contatos
from app.api.routers.health import router as health_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Central de Acolhimento API",
    description="""
## 🏥 API para Central de Acolhimento

API REST para cadastro automatizado de contatos com processamento de linguagem natural via LLM local.

### Features

* **CRUD Completo** - Create, Read, Update, Delete de contatos
* **Extração LLM** - Processamento de texto livre via Ollama + llama3:8b
* **LGPD Compliant** - Dados processados 100% localmente
* **Export Excel** - Geração de relatórios em Excel

### Autenticação

Em desenvolvimento: Autenticação desabilitada  
Em produção: JWT obrigatório

### Endpoints Principais

* `POST /api/v1/contatos` - Cadastrar novo contato
* `GET /api/v1/contatos` - Listar todos os contatos
* `GET /api/v1/contatos/{id}` - Obter contato específico
* `PUT /api/v1/contatos/{id}` - Atualizar contato
* `DELETE /api/v1/contatos/{id}` - Deletar contato
* `GET /api/v1/contatos/export/excel` - Exportar para Excel

### Como Usar

1. Para extração via LLM:
   ```json
   {
     "texto_livre": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
   }
   ```

2. Para cadastro manual:
   ```json
   {
     "nome": "João Silva",
     "telefone": "11-8888-7777",
     "motivo": "orientação jurídica"
   }
   ```

### Documentação

* Swagger UI: `/docs` (interativo)
* ReDoc: `/redoc` (documentação formatada)
* OpenAPI JSON: `/openapi.json`
    """,
    version="0.1.0",
    contact={
        "name": "Central de Acolhimento",
        "url": "https://github.com/your-org/central-acolhimento-api",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "contatos",
            "description": "Operações CRUD para gerenciamento de contatos",
        },
        {
            "name": "health",
            "description": "Health checks e readiness probes",
        },
    ],
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
app.include_router(health_router)
app.include_router(contatos.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Central de Acolhimento API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
