# 9. Architectural Decisions

## 9.1 ADR Template

Este documento segue o padrão **MADR** (Markdown Architecture Decision Records). Cada decisão arquitetural tem:
- **Status**: proposed, accepted, rejected, deprecated, superseded
- **Context**: Situação que levou à decisão
- **Decision**: Decisão tomada
- **Consequences**: Impacto da decisão

## 9.2 ADR-001: Multi-Repo Architecture

**Status**: Accepted  
**Date**: 2024-01-15  
**Deciders**: Architecture Team

### Context
Sistema precisa separar API REST (FastAPI) e serviço LLM (Ollama) em componentes independentes.

### Decision
Adotar arquitetura **multi-repo** com 2 repositórios separados:
- `central-acolhimento-api` (FastAPI backend + MCP client)
- `central-acolhimento-llm` (LLM service + MCP server)

Interface entre serviços via **MCP (Model Context Protocol)** sobre HTTP.

### Consequences
**Pros:**
- Escalabilidade independente (LLM pode escalar separadamente)
- Desacoplamento forte (equipes podem trabalhar em paralelo)
- Deployment flexível (API em serverless, LLM em GPU cluster)
- Clear boundaries (MCP define contract)

**Cons:**
- Overhead de setup inicial (2 repositórios)
- Necessidade de comunicação inter-serviços (network latency)
- Gestão de dependências mais complexa (versions, deployments)

## 9.3 ADR-002: FastAPI over Flask/Django

**Status**: Accepted  
**Date**: 2024-01-15  
**Deciders**: Architecture Team

### Context
Precisamos escolher framework web Python para API REST.

### Decision
Usar **FastAPI** como framework principal.

### Consequences
**Pros:**
- Async/await nativo (melhor performance para I/O)
- Auto-documentation OpenAPI/Swagger out-of-the-box
- Type hints + Pydantic para validação robusta
- Performance comparável a Node.js/Go

**Cons:**
- Comunidade menor que Django
- Menos batteries-included que Django (precisamos adicionar mais features)

**Alternatives Considered:**
- Flask: Não oferece async nativo, menos performático
- Django: Overhead desnecessário para REST API simples, complexo

## 9.4 ADR-003: Local LLM (Ollama) over Cloud APIs

**Status**: Accepted  
**Date**: 2024-01-15  
**Deciders**: Architecture Team

### Context
Requirement de privacidade (LGPD) e custos: dados sensíveis de atendimento não podem vazar para APIs externas.

### Decision
Usar **Ollama + llama3:8b** (local LLM) ao invés de OpenAI/Anthropic/Claude APIs.

### Consequences
**Pros:**
- **LGPD Compliance**: Zero egress de dados pessoais
- **Zero Cost**: Open source, sem custos operacionais (vs. $0.01-0.03/request em APIs cloud)
- **Control**: Possibilidade de fine-tuning futuro
- **Privacy**: Dados nunca saem do ambiente

**Cons:**
- **Performance**: ~2-5s latency (vs. <1s em cloud APIs)
- **Hardware**: Requer 8-16GB RAM (llama3:8b)
- **Maintenance**: Precisa gerenciar Ollama + modelo localmente

**Alternatives Considered:**
- OpenAI API: ❌ Proibido por LGPD (dados saem para US)
- Anthropic Claude API: ❌ Proibido por LGPD
- Fine-tuned BERT: Mais complexo setup, llama3 é pré-treinado

## 9.5 ADR-004: MCP (Model Context Protocol)

**Status**: Accepted  
**Date**: 2024-01-15  
**Deciders**: Architecture Team

### Context
Precisamos de protocolo padronizado para comunicação API ↔ LLM.

### Decision
Adotar **Model Context Protocol (MCP)** como protocolo de comunicação.

### Consequences
**Pros:**
- **Standard**: Protocolo aberto especificado (JSON-RPC based)
- **Structured**: Comunicação bidirecional estruturada (tools, resources)
- **Future-proof**: Protocolo emergente, vendor-agnostic
- **Extensible**: Suporta streaming, context management, multi-turn conversations

**Cons:**
- **New Protocol**: Menos maturo que HTTP REST direto
- **Complexity**: Mais complexo que chamadas REST simples

**Alternatives Considered:**
- LangChain: Overhead desnecessário, MCP é mais direto
- OpenAI Chat Completions API: Vendor lock-in
- HTTP REST direto: Sem estrutura clara para tools/resources

## 9.6 ADR-005: SQLite → PostgreSQL

**Status**: Accepted  
**Date**: 2024-01-15  
**Deciders**: Architecture Team

### Context
MVP precisa de DB simples para desenvolvimento, mas produção precisa de features avançadas.

### Decision
Usar **SQLite** para desenvolvimento/MVP, **PostgreSQL** para produção.

### Consequences
**Pros:**
- **SQLite**: Zero setup, perfect para dev local e MVP
- **PostgreSQL**: Production-grade (concorrência, JSON, full-text search, replication)
- **Migration Path**: Alembic migrations permitem transition seamless
- **Abstraction**: SQLAlchemy ORM abstrai diferenças

**Cons:**
- **Migração**: Migração necessária de SQLite → PostgreSQL (mas Alembic facilita)
- **Setup**: PostgreSQL requer gerenciamento (managed service na cloud)

**Alternatives Considered:**
- PostgreSQL only: Mais complexo setup inicial para MVP
- MongoDB: NoSQL não necessário, dados são relacionais
- SQLite only: Limitações de concorrência em produção

## 9.7 ADR-006: Cloud-Agnostic Deployment

**Status**: Accepted  
**Date**: 2024-01-15  
**Deciders**: Architecture Team

### Context
Evitar vendor lock-in, permitir flexibilidade de provedor cloud.

### Decision
Adotar **cloud-agnostic** architecture com abstrações e padrões abertos.

### Consequences
**Pros:**
- **Vendor Independence**: Deploy no provedor que oferecer melhor custo/features
- **Terraform Modules**: Módulos reutilizáveis para AWS/GCP/Azure
- **Kubernetes Standard**: Funciona em qualquer cloud (EKS, GKE, AKS)
- **S3-compatible Storage**: Usar SDK abstrações (boto3, google-cloud-storage)

**Cons:**
- **Genericity Trade-off**: Não usa features cloud-native específicas (ex.: AWS Lambda, GCP Cloud Functions)
- **Additional Complexity**: Manter múltiplos providers aumenta complexidade de IaC

**Alternatives Considered:**
- AWS-only: Vendor lock-in, menos flexibilidade
- Cloud-agnostic com abstrações: ✅ Vencedor (balance)

## 9.8 ADR-007: Kubernetes over Docker Swarm

**Status**: Accepted  
**Date**: 2024-01-15  
**Deciders**: Architecture Team

### Context
Decidir orchestrator para deployment em produção.

### Decision
Usar **Kubernetes** ao invés de Docker Swarm.

### Consequences
**Pros:**
- **Industry Standard**: Maior ecossistema, comunidade, ferramentas
- **Cloud-Native**: Funciona igual em AWS (EKS), GCP (GKE), Azure (AKS)
- **Features**: RBAC, network policies, autoscaling, GitOps ready
- **Mature**: Kubernetes 1.25+, battle-tested

**Cons:**
- **Complexity**: Kubernetes é mais complexo que Swarm (curva de aprendizado)
- **Resource Overhead**: Mais recursos necessários (control plane)

**Alternatives Considered:**
- Docker Swarm: Mais simples mas menos features
- Nomad: Menos adotado na indústria
- Managed Kubernetes: ✅ Vencedor (simplifica operação)

## 9.9 ADR-008: Terraform over Pulumi/Ansible

**Status**: Accepted  
**Date**: 2024-01-15  
**Deciders**: Architecture Team

### Context
Escolher ferramenta de Infrastructure as Code (IaC).

### Decision
Usar **Terraform** como ferramenta de IaC.

### Consequences
**Pros:**
- **State Management**: Terraform state tracking robusto
- **Provider Ecosystem**: Maior número de providers (AWS, GCP, Azure uniformemente suportado)
- **Declarative**: Descrever desired state (vs. imperative scripts)
- **Mature**: Ferramenta estável, amplamente adotada

**Cons:**
- **HCL Syntax**: Requer aprender Domain-Specific Language (HCL)
- **State Management**: Pode ser complexo em multi-remote backends

**Alternatives Considered:**
- Pulumi: Boa ferramenta mas menor ecossistema
- Ansible: Imperative (playbooks), mais para configuration management
- CloudFormation/CDK: Vendor lock-in AWS

## 9.10 ADR-009: JWT Authentication

**Status**: Accepted  
**Date**: 2024-01-15  
**Deciders**: Architecture Team

### Context
Necessidade de autenticação stateless para API REST.

### Decision
Usar **JWT (JSON Web Tokens)** para autenticação.

### Consequences
**Pros:**
- **Stateless**: Não requer server-side session storage
- **Scalable**: Permite múltiplas réplicas de API (sem sticky sessions)
- **Standard**: Protocolo amplamente adotado
- **Security**: Tokens signed com secret/key

**Cons:**
- **Revocation**: Difícil invalidar tokens antes do expiration (necessita blacklist ou refresh tokens)
- **Token Size**: JWT tokens maiores que session IDs

**Alternatives Considered:**
- OAuth2: Mais complexo que necessário para single-service
- Session-based: Requer sticky sessions, não escala horizontalmente

## 9.11 ADR-010: Container-First Architecture

**Status**: Accepted  
**Date**: 2024-01-15  
**Deciders**: Architecture Team

### Context
Todas as funções do sistema devem ser containerizáveis.

### Decision
Construir sistema **container-first** com Docker + Kubernetes.

### Consequences
**Pros:**
- **Portability**: Roda em qualquer ambiente (dev, staging, prod, cloud, on-premise)
- **Isolation**: Containers isolam dependências
- **Orchestration**: Kubernetes gerencia lifecycle, health checks, scaling
- **DevOps**: CI/CD pipelines simplificados

**Cons:**
- **Overhead**: Containers têm overhead (minimal com Docker optimizations)
- **Complexity**: Setup de Docker/Kubernetes requer conhecimento

**Alternatives Considered:**
- Bare metal deployment: Não escalável, dificulta CI/CD
- VM-based deployment: Mais overhead que containers
- Serverless (Lambda/Functions): Limitação para LLM (modelo grande + cold start)

## 9.12 Summary of Decisions

| ADR | Title | Status | Key Impact |
|-----|-------|--------|------------|
| ADR-001 | Multi-Repo Architecture | ✅ Accepted | Separa API e LLM em repos independentes |
| ADR-002 | FastAPI Framework | ✅ Accepted | Async, type-safe, auto-docs |
| ADR-003 | Local LLM (Ollama) | ✅ Accepted | LGPD compliant, zero cost |
| ADR-004 | MCP Protocol | ✅ Accepted | Comunicação estruturada com LLM |
| ADR-005 | SQLite → PostgreSQL | ✅ Accepted | DB para dev e prod |
| ADR-006 | Cloud-Agnostic | ✅ Accepted | Flexibilidade de provedor |
| ADR-007 | Kubernetes | ✅ Accepted | Industry standard orchestration |
| ADR-008 | Terraform | ✅ Accepted | IaC declarativo |
| ADR-009 | JWT Authentication | ✅ Accepted | Auth stateless |
| ADR-010 | Container-First | ✅ Accepted | Portabilidade, isolation |

## 9.13 Upcoming Decisions

Decisões ainda a serem tomadas (documentar quando resolvidas):
- ADR-011: GPU vs CPU for LLM (alguma GPU necessária ou CPU suficiente?)
- ADR-012: Queue System (Celery/RQ para async LLM processing?)
- ADR-013: Multi-tenancy support (single-tenant vs multi-tenant?)
- ADR-014: Fine-tuning strategy (fine-tune llama3 ou usar prompts engineering?)

## 9.14 Deprecated Decisions

N/A (nenhuma decisão foi deprecada ainda).
