# Central de Acolhimento - API Service

API REST para cadastro de contatos com processamento de linguagem natural via LLM local (Ollama + llama3:8b) e integração Model Context Protocol (MCP).

## Arquitetura

Este repositório contém o **API Service** do sistema Central de Acolhimento:
- **FastAPI** - Framework web Python com async/await
- **SQLAlchemy** - ORM para banco de dados
- **Alembic** - Database migrations
- **MCP Client** - Integração com LLM service via Model Context Protocol
- **Pydantic** - Validação de dados e schemas

## Features

- ✅ CRUD completo de contatos
- ✅ Extração automática de entidades via LLM
- ✅ Cadastro manual (fallback se LLM indisponível)
- ✅ Filtros e paginação
- ✅ Exportação para Excel
- ✅ Integração MCP com LLM service

## Quick Start

### Prerequisites
- Python 3.11+
- Docker 24.0+ (para LLM service via docker-compose)

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose (with LLM)

```bash
# Start all services (API + LLM + DB)
docker-compose up -d

# API available at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

## API Endpoints

- `POST /contatos` - Create contact (with LLM extraction or manual)
- `GET /contatos` - List all contacts (with pagination/filters)
- `GET /contatos/{id}` - Get contact by ID
- `PUT /contatos/{id}` - Update contact
- `DELETE /contatos/{id}` - Delete contact
- `GET /contatos/export/excel` - Export to Excel

### Example: Create Contact

**LLM Extraction:**
```bash
curl -X POST http://localhost:8000/contatos \
  -H "Content-Type: application/json" \
  -d '{
    "texto_livre": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
  }'
```

**Manual:**
```bash
curl -X POST http://localhost:8000/contatos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "telefone": "11-8888-7777",
    "motivo": "orientação jurídica"
  }'
```

## Development

### Running Tests
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Linting & Formatting
```bash
# Format code
black app/ tests/

# Lint
ruff check app/ tests/

# Type check
mypy app/
```

## Project Structure

```
api-repo/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── api/                 # API routers
│   ├── core/                # Config, security, deps
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── crud/                # Database operations
│   ├── services/            # Business logic
│   └── mcp/                 # MCP client
├── tests/
├── alembic/                 # Migrations
├── terraform/               # IaC
├── k8s/                     # Kubernetes manifests
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Documentation

Comprehensive documentation available in parent repository:
- [Arc42 Architecture Docs](../docs/arc42/)
- [MCP Integration Guide](../docs/mcp/)
- [API Specifications](../docs/api/)
- [Getting Started Guide](../docs/guides/getting-started.md)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit changes (`git commit -m 'feat: nova funcionalidade'`)
4. Push to branch (`git push origin feature/nova-funcionalidade`)
5. Open Pull Request

## License

MIT License
