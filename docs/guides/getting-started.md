# Getting Started - Central de Acolhimento

## Prerequisites
- **Python**: 3.11+ (required)
- **Docker**: 24.0+ (required for local LLM)
- **Docker Compose**: 2.20+ (required for orchestration)
- **Git**: Para clonar repositórios
- **RAM**: Mínimo 8GB (16GB recommended para LLM)
- **Disk Space**: 10GB+ (para modelos LLM)

## Architecture Overview

O sistema consiste de dois serviços separados:
- **API Service** (FastAPI) - REST API com CRUD de contatos
- **LLM Service** (Ollama + llama3:8b) - Processamento de linguagem natural

## Quick Start

### 1. Clone Repositories
```bash
# Clone API repository
git clone https://github.com/your-org/central-acolhimento-api.git
cd central-acolhimento-api

# Clone LLM repository (opcional se rodar LLM via Docker Compose)
git clone https://github.com/your-org/central-acolhimento-llm.git
cd central-acolhimento-llm
```

### 2. Setup API Service

```bash
cd central-acolhimento-api

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

### 3. Setup LLM Service (Optional - use Docker Compose instead)

```bash
cd central-acolhimento-llm

# Start Ollama with Docker
docker run -d -p 11434:11434 --name ollama ollama/ollama

# Pull llama3:8b model
docker exec ollama ollama pull llama3:8b

# Verify
curl http://localhost:11434/api/generate -d '{"model": "llama3", "prompt": "Olá!"}'
```

### 4. Using Docker Compose (Recommended)

```bash
# In project root
docker-compose up -d

# This starts:
# - API service on http://localhost:8000
# - LLM service (Ollama) on http://localhost:11434
# - Database (SQLite in file)

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f llm
```

## Configuration

### Environment Variables (API)

Create `.env` file in `central-acolhimento-api/`:

```env
# Database
DATABASE_URL=sqlite:///./database.db
# For PostgreSQL: postgresql://user:password@localhost:5432/dbname

# LLM Service
LLM_URL=http://localhost:11434

# JWT Settings (production only)
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Application
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

### Docker Compose Configuration

Edit `docker-compose.yml`:

```yaml
version: '3.8'
services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./database.db
      - LLM_URL=http://llm:11434
    volumes:
      - ./api:/app
      - ./database.db:/app/database.db
    depends_on:
      - llm
  
  llm:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: >
      sh -c "ollama pull llama3:8b && ollama serve"

volumes:
  ollama_data:
```

## Testing the API

### Swagger UI
Navigate to http://localhost:8000/docs for interactive API documentation

### Create Contact (LLM Extraction)
```bash
curl -X POST http://localhost:8000/contatos \
  -H "Content-Type: application/json" \
  -d '{
    "texto_livre": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
  }'
```

### Create Contact (Manual)
```bash
curl -X POST http://localhost:8000/contatos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "telefone": "11-8888-7777",
    "motivo": "orientação jurídica"
  }'
```

### List Contacts
```bash
curl http://localhost:8000/contatos
```

### Get Contact by ID
```bash
curl http://localhost:8000/contatos/1
```

### Export to Excel
```bash
curl -O http://localhost:8000/contatos/export/excel
```

## Running Tests

### Unit Tests
```bash
# In central-acolhimento-api
pytest tests/ -v --cov=app --cov-report=html
```

### Integration Tests
```bash
# Start services
docker-compose up -d

# Run integration tests
pytest tests/integration/ -v
```

### E2E Tests (Future)
```bash
# Full system test
pytest tests/e2e/ -v
```

## Development Workflow

### 1. Feature Branch Workflow
```bash
# Create feature branch
git checkout -b feature/nova-funcionalidade

# Make changes
# ...

# Commit
git commit -m "feat: add new feature"

# Push
git push origin feature/nova-funcionalidade

# Create PR
```

### 2. Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### 3. Linting and Formatting
```bash
# Format code
black app/ tests/

# Lint
ruff check app/ tests/

# Type check
mypy app/
```

## Troubleshooting

### API won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Check Python version: `python --version` (must be 3.11+)
- Check dependencies: `pip install -r requirements.txt`

### LLM service unavailable
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check Docker logs: `docker-compose logs llm`
- Ensure enough RAM (llama3:8b needs 8GB+)

### Database errors
- Run migrations: `alembic upgrade head`
- Check database file permissions
- For PostgreSQL: verify connection string

### Import errors
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check PYTHONPATH: `export PYTHONPATH=$PWD`

## Next Steps

1. **Read Documentation**: Explore Arc42 documentation in `docs/arc42/`
2. **Explore API**: Use Swagger UI at http://localhost:8000/docs
3. **Review Code**: Check structure in `app/` directory
4. **Join Team**: Contact maintainers for access to shared resources

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ollama Documentation](https://ollama.ai/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check `docs/` for detailed guides
- **Team**: Contact maintainers via email or Slack
