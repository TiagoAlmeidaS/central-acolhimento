# 4. Solution Strategy

## 4.1 Technology Decisions

### 4.1.1 Backend Framework: FastAPI
**Decision**: Usar FastAPI como framework web principal

**Rationale**:
- **Performance**: Async/await nativo, comparable a Node.js/Go
- **Type Safety**: Type hints obrigatórios, validação com Pydantic v2
- **Developer Experience**: Auto-documentation OpenAPI/Swagger out-of-the-box
- **Ecosystem**: Compatível com SQLAlchemy 2.0 async, Alembic migrations
- **Standards**: Based on OpenAPI 3.1, JSON Schema, OAuth2

**Alternatives Considered**:
- Flask: Não oferece async nativo, mais verboso para REST APIs
- Django: Overhead desnecessário, focus em admin panel não necessário
- FastAPI vence por balancear performance e developer experience

### 4.1.2 LLM Runtime: Ollama
**Decision**: Ollama para execução local de LLM (Llama3:8b)

**Rationale**:
- **Privacy**: Zero egress de dados, processamento 100% local
- **Cost**: Open source, zero custos operacionais
- **LGPD Compliance**: Dados nunca saem do território brasileiro
- **Control**: Possibilidade de fine-tuning futuro
- **Performance**: llama3:8b roda eficientemente em CPU modesto

**Alternatives Considered**:
- OpenAI API: ❌ Proibido por privacidade (dados vazariam para US)
- Anthropic Claude API: ❌ Proibido por privacidade
- vLLM: Mais complexo setup, Ollama é mais simples para MVP

### 4.1.3 Communication Protocol: Model Context Protocol (MCP)
**Decision**: MCP como protocolo para comunicação API ↔ LLM

**Rationale**:
- **Standard**: Protocolo aberto especificado (2024), JSON-RPC based
- **Structured**: Comunicação bidirecional estruturada vs. prompts ad-hoc
- **Extensible**: Suporta tools, resources, bidirectional streaming
- **Future-proof**: Protocolo emergente adotado pela indústria
- **Compatibility**: Funciona com qualquer MCP-compatible LLM/API

**Alternatives Considered**:
- OpenAI Chat Completions API: Vendor lock-in, não é MCP-compatible
- LangChain: Overhead desnecessário, MCP é mais direto
- HTTP REST direto: Menos estruturado que MCP, sem padrão claro

### 4.1.4 Database: SQLite → PostgreSQL
**Decision**: SQLite para dev/MVP, PostgreSQL para produção

**Rationale**:
- **SQLite**: Zero setup, perfect para MVP e desenvolvimento local
- **PostgreSQL**: Production-grade, suporta concorrência, features avançadas (JSON, full-text search, replication)
- **Abstraction**: SQLAlchemy ORM abstrai diferenças, migração via Alembic
- **Migration Path**: Alembic migrations permitem transition seamless

**Alternatives Considered**:
- MongoDB: NoSQL não necessário, dados são relacionais
- Redis: In-memory DB, não adequado para persistência permanente
- SQLite-only: Limitações de concorrência, não adequado para produção

### 4.1.5 Architecture Pattern: Multi-Repo
**Decision**: Separar sistema em 2 repositórios (API + LLM)

**Rationale**:
- **Separation of Concerns**: API e LLM têm responsabilidades distintas
- **Independent Scaling**: LLM pode escalar independente de API
- **Team Collaboration**: Diferentes squads podem trabalhar em paralelo
- **Deployment Flexibility**: Deploy API e LLM em infraestruturas diferentes (ex.: API em serverless, LLM em GPU cluster)
- **Clear Boundaries**: Interface MCP define contract entre serviços

**Alternatives Considered**:
- Monorepo: Mais simples setup inicial, mas dificulta scaling futuro
- Microservices mais granulares: Over-engineering para MVP, 2 services é ideal

## 4.2 Architectural Patterns

### 4.2.1 Layered Architecture (API)
```
┌─────────────────────────────────────────┐
│ Layer: Presentation                     │
│ - FastAPI routers                       │
│ - Request/response validation           │
│ - Authentication middleware             │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ Layer: Business Logic                   │
│ - CRUD services                         │
│ - Entity extraction orchestration       │
│ - MCP client integration                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ Layer: Data Access                      │
│ - SQLAlchemy models                     │
│ - Repository pattern                    │
│ - Alembic migrations                    │
└─────────────────────────────────────────┘
```

**Benefits**:
- Separation of concerns claro
- Testável em camadas independentes
- Manutenível e extensível

### 4.2.2 Service-Oriented Architecture (Multi-Repo)
```
┌─────────────────┐        ┌─────────────────┐
│   API Service   │◄────MCP Protocol────►│   LLM Service  │
│   (FastAPI)     │                        │   (Ollama)    │
│                 │        HTTP/REST       │               │
│  - CRUD logic   │◄─────────────────────►│  - Entity     │
│  - Validation   │                        │    Extraction │
│  - Auth         │        Database        │  - Prompt     │
└────────┬────────┘        ◄────────────── └───────────────┘
         │
         ▼
   SQLite/PostgreSQL
```

**Benefits**:
- Decoupling forte entre API e LLM
- Escalabilidade independente
- Facilita replacement de LLM (exchangeable)

### 4.2.3 Repository Pattern (Data Access)
```python
# Example
class ContatoRepository:
    async def create(self, data: ContatoCreate) -> Contato
    async def get(self, id: int) -> Optional[Contato]
    async def list(self, filters: ContatoFilters) -> List[Contato]
    async def update(self, id: int, data: ContatoUpdate) -> Contato
    async def delete(self, id: int) -> None
```

**Benefits**:
- Abstraction de persistent storage
- Testável via mocks/stubs
- Facilita migration de DB (SQLite → PostgreSQL)

## 4.3 Integration Strategies

### 4.3.1 MCP Integration Strategy
**Architecture**: JSON-RPC over HTTP/SSE for bidirectional communication

**Flow**:
1. API client invokes MCP tool via JSON-RPC request
2. LLM service receives request, processes with Llama3:8b
3. LLM returns structured JSON response
4. API validates response and persists to database

**Error Handling**:
- Timeout: 30s default, retry with exponential backoff (3 attempts)
- Fallback: Se MCP/LLM indisponível, permitir cadastro manual
- Circuit Breaker: Abort after 3 consecutive failures

### 4.3.2 Database Integration Strategy
**ORM**: SQLAlchemy 2.0 async

**Connection Pooling**:
- pool_size: 10 connections
- max_overflow: 20 extra connections
- Timeout: 30s

**Transactions**: Autocommit off, commit após operações CRUD

**Migrations**: Alembic para versioning de schema

### 4.3.3 Observability Integration
**Three Pillars**:
1. **Logging**: structlog (structured JSON) → stdout/fluentd → ELK/Prometheus
2. **Metrics**: Prometheus exporter pattern → Scraping → Grafana dashboards
3. **Tracing**: OpenTelemetry (future, não no MVP)

**Log Levels**:
- ERROR: Falhas críticas (LLM timeout, DB unavailable)
- WARN: Degradações (fallback manual, retries)
- INFO: Business events (contato criado, atualizado)
- DEBUG: Request/response details (não em produção)

## 4.4 Deployment Strategy

### 4.4.1 Cloud-Agnostic Approach
**Principle**: Evitar vendor lock-in através de abstrações e standards

**Technologies**:
- **Orchestration**: Kubernetes (works on EKS, GKE, AKS)
- **IaC**: Terraform modules parameterized por provider
- **Storage**: S3-compatible APIs (S3, GCS, Azure Blob via SDK)
- **Databases**: PostgreSQL hosted (RDS, Cloud SQL, Azure Database)
- **Container Registry**: Docker Hub / registry local

**Terraform Modules Structure**:
```
terraform/
├── modules/
│   ├── k8s-cluster/     # Generic K8s (works on all clouds)
│   ├── postgres/        # Managed DB abstraction
│   ├── load-balancer/   # Cloud LB abstraction
│   └── storage/         # S3-compatible object storage
├── environments/
│   ├── aws/             # AWS-specific overrides
│   ├── gcp/             # GCP-specific overrides
│   └── azure/           # Azure-specific overrides
```

### 4.4.2 Containerization Strategy
**Multi-Stage Builds**:
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
RUN pip install poetry
COPY pyproject.toml poetry.lock .
RUN poetry export -f requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /app/requirements.txt .
RUN pip install --user -r requirements.txt
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Benefits**: Reduzir image size, cache layers eficientemente

### 4.4.3 CI/CD Strategy (GitHub Actions)
**Pipeline Stages**:
1. **Lint**: Ruff, Black, mypy type checking
2. **Test**: pytest (unit + integration tests)
3. **Build**: Docker build and push to registry
4. **Deploy**: Terraform apply to dev/staging (manual approval para prod)

**Branch Strategy**:
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature branches (auto-merged to develop after approval)

## 4.5 Quality Attributes Strategy

### 4.5.1 Performance
- **API Response Time**: Async/await, connection pooling, cache de prompts (Redis futuro)
- **LLM Latency**: Acceptável até 5s (hardware CPU modesto)
- **Database Queries**: N+1 prevention, eager loading, indexes em colunas filtradas

### 4.5.2 Security
- **Authentication**: JWT tokens, refresh tokens
- **Authorization**: RBAC (roles: admin, user)
- **Encryption**: TLS 1.3, database encryption at rest
- **Secrets Management**: AWS Secrets Manager / Vault
- **Input Validation**: Pydantic schemas em todos os endpoints
- **SQL Injection Prevention**: ORM parameters (never string interpolation)

### 4.5.3 Scalability
- **Horizontal Scaling**: Kubernetes pod autoscaling (CPU/memory based)
- **Stateless API**: All state in database, permite multiple replicas
- **Database Scaling**: Read replicas se necessário (PostgreSQL)
- **LLM Scaling**: Multiple LLM pods (load balanced) se throughput aumentar

### 4.5.4 Maintainability
- **Code Quality**: Type hints, PEP 8, test coverage >80%
- **Documentation**: Arc42 completo, README per repositório
- **Dependency Management**: requirements.txt ou Poetry
- **Refactoring Safety**: Tests garantem que refactoring não quebra features

### 4.5.5 Reliability
- **Health Checks**: Liveness probe (API), readiness probe (API + DB)
- **Circuit Breaker**: Falha rápida se LLM indisponível (fallback manual)
- **Retry Logic**: Exponential backoff para transient failures
- **Backups**: Automated daily backups, point-in-time recovery

### 4.5.6 Privacy (LGPD)
- **Data Localization**: LLM local, nunca envia dados externos
- **Consent Management**: Database flag de consentimento por contato
- **Right to Deletion**: DELETE endpoint permite exclusão de dados pessoais
- **Audit Logging**: Log all accesses to personal data
- **Data Minimization**: Apenas coletar dados necessários

## 4.6 Technology Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM Hallucination | Alto | Média | Validação humana antes de commit, prompts cuidadosamente testados |
| Performance de LLM (CPU) | Médio | Alta | Aceitar latência de 5s, considerar GPU future |
| Vendor Lock-in Cloud | Baixo | Média | Terraform multi-cloud, Kubernetes padrão |
| SQLite Data Loss | Alto | Baixa | Migrar para PostgreSQL em produção, backups diários |
| MCP Protocol Evolution | Baixo | Baixa | Versionar API MCP, suportar múltiplas versões |
| Team Expertise | Médio | Baixa | Documentation completa, onboarding guide |

## 4.7 Technology Alternatives (Not Selected)

### 4.7.1 Flask instead of FastAPI
**Why Not**: Async nativo limitado, menos performático, sem type safety out-of-the-box

### 4.7.2 Cloud LLMs (OpenAI/Anthropic)
**Why Not**: Privacy concerns, LGPD compliance, custos operacionais

### 4.7.3 Monolith vs Multi-Repo
**Why Not**: Monolith seria mais simples inicialmente mas dificultaria scaling independente

### 4.7.4 LangChain for LLM integration
**Why Not**: Overhead desnecessário, MCP é mais direto e padrão emergente

### 4.7.5 Serverless-first (Lambda/Functions)
**Why Not**: LLM requer GPU/persistent state, serverless não é adequado para long-running tasks

## 4.8 Evolution Path

### Phase 1 (MVP - Current)
- Single LLM instance (llama3:8b CPU)
- SQLite database
- Basic MCP integration
- Manual deployment

### Phase 2 (Production-Ready)
- PostgreSQL database
- Multiple LLM instances (load balanced)
- Automated CI/CD pipeline
- Prometheus + Grafana monitoring

### Phase 3 (Scale)
- GPU optimization (llama3:70b ou fine-tuned model)
- Kubernetes horizontal pod autoscaling
- Redis caching for prompts/responses
- Advanced RBAC, audit logging

### Phase 4 (Advanced)
- Fine-tuned LLM para domínio específico
- Multi-tenant support
- Advanced BI/Analytics
- Disaster recovery automation
