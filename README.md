# Central de Acolhimento

Sistema de cadastro automatizado de contatos para Central de Acolhimento, utilizando processamento de linguagem natural (NLP) via LLM local (Ollama + llama3:8b) e integração Model Context Protocol (MCP).

## Arquitetura

### Sistema Multi-Repository
O projeto está dividido em 2 repositórios independentes:
- **API Service** ([central-acolhimento-api](https://github.com/your-org/central-acolhimento-api)) - Backend REST (FastAPI) com CRUD de contatos
- **LLM Service** ([central-acolhimento-llm](https://github.com/your-org/central-acolhimento-llm)) - Serviço de processamento NLP (Ollama + llama3:8b)

### Componentes Principais
- **FastAPI**: Framework web Python para API REST
- **Ollama**: Runtime para LLM local (llama3:8b)
- **SQLite/PostgreSQL**: Banco de dados para persistência
- **MCP (Model Context Protocol)**: Comunicação estruturada API ↔ LLM
- **Kubernetes**: Deployment em produção (cloud-agnostic)
- **Terraform**: Infrastructure as Code (IaC)

## Quick Start

### Pré-requisitos
- Python 3.11+
- Docker 24.0+
- Docker Compose 2.20+
- 8GB+ RAM (16GB recomendado)

### Setup Local
```bash
# Clone repositório
git clone https://github.com/your-org/central-acolhimento-api.git
cd central-acolhimento-api

# Start com Docker Compose
docker-compose up -d

# API disponível em http://localhost:8000
# Swagger UI em http://localhost:8000/docs
```

## Funcionalidades

### API REST
- ✅ CRUD de contatos (Create, Read, Update, Delete)
- ✅ Extração automática de entidades via LLM
- ✅ Cadastro manual (fallback)
- ✅ Filtros e paginação
- ✅ Exportação para Excel
- ✅ Integração MCP

### LLM Integration
- ✅ Extração de entidades (nome, telefone, email, motivo)
- ✅ Processamento de texto livre em linguagem natural
- ✅ Validação e formatação de dados extraídos
- ✅ Protocolo MCP para comunicação estruturada

### Observability
- ✅ Prometheus metrics
- ✅ Structured logging (JSON)
- ✅ Health checks
- ✅ Grafana dashboards (opcional)

## Documentação

Documentação completa seguindo padrão Arc42 disponível em `docs/`:

- **Arc42**: Arquitetura completa (sections 1-11)
- **MCP**: Integração Model Context Protocol
- **API**: Especificações OpenAPI
- **Guides**: Getting started, development workflow
- **Infrastructure**: Deployment cloud-agnostic
- **Operations**: Runbooks e disaster recovery

### Documentos Principais
- [Getting Started](docs/guides/getting-started.md) - Setup local e desenvolvimento
- [Architecture Overview](docs/arc42/03-context-scope.md) - Visão geral da arquitetura
- [Deployment Strategy](docs/infrastructure/deployment-strategy.md) - Guia de deployment
- [MCP Integration](docs/mcp/mcp-overview.md) - Protocolo MCP
- [API Specification](docs/api/openapi-overview.md) - Endpoints REST

## Exemplos de Uso

### Criar Contato via LLM
```bash
curl -X POST http://localhost:8000/contatos \
  -H "Content-Type: application/json" \
  -d '{
    "texto_livre": "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional"
  }'
```

### Listar Contatos
```bash
curl http://localhost:8000/contatos
```

### Exportar para Excel
```bash
curl -O http://localhost:8000/contatos/export/excel
```

## Tecnologias

### Backend
- **FastAPI** - Framework web Python
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Pydantic** - Validation

### LLM
- **Ollama** - LLM runtime local
- **llama3:8b** - Modelo de linguagem (Quantized)
- **MCP** - Model Context Protocol

### Infrastructure
- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **Terraform** - IaC
- **Prometheus** - Metrics
- **Grafana** - Dashboards

## LGPD Compliance

✅ **Dados Locais**: Todo processamento LLM ocorre localmente (zero egress de dados pessoais)  
✅ **Privacidade**: LGPD compliant - dados nunca saem do ambiente  
✅ **Audit Logging**: Todos os acessos a dados pessoais são logados  
✅ **Right to Deletion**: Endpoint DELETE permite exclusão de dados  
✅ **Data Portability**: Exportação em JSON/Excel

## Desenvolvimento

### Estrutura do Projeto
```
central-acolhimento/
├── app/              # Código da aplicação
│   ├── api/          # Endpoints REST
│   ├── crud/         # Operações de banco
│   ├── models/       # Modelos SQLAlchemy
│   ├── schemas/      # Schemas Pydantic
│   ├── services/     # Lógica de negócio
│   └── mcp/          # Integração MCP
├── tests/            # Testes
├── alembic/          # Migrations
├── terraform/        # IaC
├── k8s/              # Manifests Kubernetes
└── docs/             # Documentação Arc42
```

### Running Tests
```bash
# Unit tests
pytest tests/ -v --cov=app

# Integration tests
pytest tests/integration/ -v
```

### Linting & Formatting
```bash
# Format
black app/ tests/

# Lint
ruff check app/ tests/

# Type check
mypy app/
```

## Roadmap

### MVP (Atual)
- ✅ CRUD de contatos
- ✅ Extração LLM
- ✅ Integração MCP
- ✅ Deployment local

### Próximas Fases
- 📋 Migração SQLite → PostgreSQL
- 📋 GPU optimization para LLM
- 📋 CI/CD pipeline completo
- 📋 Observabilidade distribuída (OpenTelemetry)
- 📋 Multi-tenant support
- 📋 Fine-tuning de modelo

## Contribuindo

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

### Guidelines
- Siga [Conventional Commits](https://www.conventionalcommits.org/)
- Mantenha test coverage >80%
- Atualize documentação
- Use pre-commit hooks

## Licença

Este projeto está licenciado sob a MIT License.

## Contato

- **GitHub Issues**: [Reportar problemas](https://github.com/your-org/central-acolhimento/issues)
- **Documentation**: Ver `docs/` para guias detalhados
- **Email**: contato@central-acolhimento.org

## Referências

- [Arc42 Documentation](https://arc42.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Ollama Documentation](https://ollama.ai/)