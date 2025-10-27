# ADR-0001: Multi-Repository Architecture

## Status
**Accepted** - 2024-01-15

## Context
O projeto Central de Acolhimento consiste de dois serviços principais:
1. **API Service** (FastAPI backend) - REST API com CRUD, MCP client
2. **LLM Service** (Ollama + llama3:8b) - Processamento NLP, MCP server

Decisão necessária: single repository (monorepo) vs. multi-repository.

## Decision
Adotar arquitetura **multi-repository** com 2 repositórios separados:
- `central-acolhimento-api` - Backend REST + MCP client
- `central-acolhimento-llm` - LLM service + MCP server

Interface entre serviços via **Model Context Protocol (MCP)** sobre HTTP.

## Consequences

### Positive Consequences
- **Separation of Concerns**: Cada repo tem responsabilidades distintas e bem definidas
- **Independent Scaling**: LLM pode escalar independentemente da API
- **Team Autonomy**: Diferentes equipes podem trabalhar em paralelo sem conflitos
- **Deployment Flexibility**: Deploy API e LLM em infraestruturas diferentes (ex.: API em serverless, LLM em GPU cluster)
- **Clear Boundaries**: MCP Protocol define contract claro entre serviços
- **Technology Flexibility**: API pode trocar LLM provider sem alterar LLM service (e vice-versa)
- **Smaller Git History**: Cada repo tem histórico mais limpo, focaco

### Negative Consequences
- **Setup Overhead**: Dois repositórios para setup inicial (mais complexo para começar)
- **Communication Overhead**: Necessário gerenciar comunicação inter-serviços (network latency, versionamento de API)
- **Dependency Management**: Versões de dependências devem ser sincronizadas entre repos (ex.: MCP protocol version)
- **CI/CD Overhead**: Duas pipelines para gerenciar
- **Documentation Duplication**: Documentação pode duplicar informações comuns

### Risks
- **Service Coupling**: Se MCP protocol evolve, ambos repos devem atualizar simultaneamente
- **Version Mismatch**: API pode ter versão MCP mais antiga que LLM (breaking changes)

### Mitigation Strategies
- **Semantic Versioning**: MCP Protocol usa semantic versioning (v1.0.0, v1.1.0, v2.0.0)
- **API First**: Design MCP protocol antes de implementar, garantir backward compatibility
- **Documentation**: Documentar versionamento de MCP protocol em ambos repos
- **Integration Tests**: Testes E2E para garantir compatibilidade de versões

## Alternatives Considered

### Alternative 1: Monorepo
**Pros**:
- Setup mais simples inicialmente
- Shared code (schemas, models) fácil de reutilizar
- Single CI/CD pipeline
- Single documentation repository

**Cons**:
- **Coupling**: Mudanças em API podem quebrar LLM (e vice-versa) - teste difícil
- **Scaling**: Difícil escalar API e LLM independentemente
- **Deployment**: Impossível deploy parcial (sempre deploy ambos)
- **Git History**: Histórico misturado, dificulta navegação

**Decision**: ❌ Rejected - too much coupling for MVP scale

### Alternative 2: Microservices + Separate Repos (3+ repos)
**Pros**:
- Ainda mais desacoplado
- Cada serviço pode evoluir independentemente

**Cons**:
- **Overhead**: Setup de 3+ repos muito trabalhoso para MVP
- **Over-engineering**: Overkill para 2-3 pessoas no time
- **Complexity**: Múltiplos serviços para gerenciar, muita infraestrutura

**Decision**: ❌ Rejected - over-engineering for MVP

## Implementation Details

### Repository Structure

#### central-acolhimento-api
```
├── app/
│   ├── api/              # FastAPI routers
│   ├── core/              # Config, security, dependencies
│   ├── crud/              # Database operations
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── mcp/               # MCP client
├── tests/
├── alembic/               # Database migrations
├── terraform/             # IaC for API deployment
├── k8s/                   # Kubernetes manifests
├── .github/workflows/     # CI/CD
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

#### central-acolhimento-llm
```
├── ollama/                # Ollama integration
│   ├── client.py
│   └── prompts.py
├── mcp/                   # MCP server
│   ├── server.py
│   ├── tools.py
│   └── resources.py
├── extraction/            # Entity extraction logic
│   ├── llm_extractor.py
│   └── validators.py
├── Dockerfile
├── docker-compose.yml
├── README.md
└── configs/              # Ollama configs
```

### Communication Protocol
- **Protocol**: Model Context Protocol (MCP) over HTTP
- **Base URL**: `http://llm-service:11434` (Kubernetes DNS)
- **Transport**: HTTP/1.1 or HTTP/2 (WebSocket optional for streaming)
- **Serialization**: JSON-RPC 2.0

### Deployment Strategy
- **Local Dev**: Docker Compose orchestrates both services
- **Production**: Kubernetes deployments independent (different scaling policies)

## References
- [Arc42 Section 4.4 - Solution Strategy](../arc42/04-solution-strategy.md)
- [Arc42 Section 5.2 - API Service Decomposition](../arc42/05-building-blocks.md)
- [MCP Protocol Documentation](../mcp/mcp-overview.md)

## Notes
- Esta decisão foi revisada por toda a equipe e aceita por consenso
- Consideramos migrar para monorepo no futuro se coordenação entre repos se tornar problemática
