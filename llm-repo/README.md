# Central de Acolhimento - LLM Service

LLM service para processamento de linguagem natural via Ollama + llama3:8b com integração Model Context Protocol (MCP).

## Arquitetura

Este repositório contém o **LLM Service** do sistema Central de Acolhimento:
- **MCP Server** - Servidor Model Context Protocol
- **Ollama Client** - Integração com Ollama local
- **Entity Extraction** - Extração de entidades de texto livre
- **Prompt Templates** - Templates otimizados para llama3:8b
- **Validators** - Validação de dados extraídos

## Features

- ✅ MCP Server para comunicação com API
- ✅ Integração com Ollama (llama3:8b)
- ✅ Extração de entidades estruturadas
- ✅ Templates de prompt otimizados
- ✅ Validação de dados extraídos
- ✅ Retry logic e error handling
- ✅ Logging estruturado

## Quick Start

### Prerequisites
- Python 3.8+
- Ollama instalado e rodando
- Modelo llama3:8b baixado

### Setup

```bash
# 1. Clone o repositório (se ainda não fez)
git clone <repo-url>
cd central-acolhimento/llm-repo

# 2. Crie virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com sua configuração

# 5. Inicie o servidor MCP
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Docker Compose

```bash
# Inicie todos os serviços (API + LLM + Ollama)
docker-compose up -d

# LLM Service disponível em http://localhost:8001
# MCP Server disponível em http://localhost:8002
```

## MCP Endpoints

- `POST /mcp/extract` - Extrair entidades de texto livre
- `POST /mcp/validate` - Validar dados extraídos
- `GET /mcp/health` - Health check
- `GET /mcp/models` - Listar modelos disponíveis

### Example: Extract Entities

```bash
curl -X POST http://localhost:8001/mcp/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
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
llm-repo/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── mcp_server/          # MCP server implementation
│   ├── ollama_client/       # Ollama integration
│   ├── prompt_templates/     # Prompt templates
│   ├── entity_extractors/   # Entity extraction logic
│   └── validators/           # Data validation
├── tests/
├── k8s/                     # Kubernetes manifests
├── terraform/               # IaC
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Documentation

Comprehensive documentation available in parent repository:
- [Arc42 Architecture Docs](../docs/arc42/)
- [MCP Integration Guide](../docs/mcp/)
- [LLM Service Specifications](../docs/llm/)

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit changes (`git commit -m 'feat: nova funcionalidade'`)
4. Push to branch (`git push origin feature/nova-funcionalidade`)
5. Open Pull Request

## License

MIT License
