# 1. Introduction and Goals

## 1.1 Requirements Overview

### Business Requirements
- **Primary Goal**: Automatizar o cadastro de contatos em uma Central de Acolhimento através de processamento de linguagem natural (NLP)
- **User Story**: Atendente pode ditar/copiar texto livre (ex.: "Novo contato: Maria Silva, telefone 11-9999-8888, motivo: apoio emocional") e o sistema extrai automaticamente e cadastra no banco
- **Compliance**: LGPD compliance - todos os dados permanecem locais, sem envio para APIs externas
- **Integration**: Integração opcional com Model Context Protocol (MCP) para enriquecimento de contexto de IA

### Technical Requirements
- **Performance**: Resposta de cadastro < 3 segundos (incluindo processamento LLM)
- **Scalability**: Suporte a 100-1000 contatos/dia inicialmente, escalável horizontalmente
- **Reliability**: 99.5% uptime, com fallback para cadastro manual se LLM indisponível
- **Security**: Autenticação JWT, HTTPS obrigatório em produção, secrets management
- **Privacy**: Zero egress de dados sensíveis, LLM local obrigatório
- **Maintainability**: Código testável (80%+ coverage), documentação completa, CI/CD automatizado

## 1.2 Quality Goals

| Priority | Quality Goal | Motivation | Success Criteria |
|----------|-------------|------------|------------------|
| 1 | **Privacy & Data Sovereignty** | LGPD compliance, dados sensíveis de atendimento | LLM local, zero envio de dados pessoais para externos |
| 2 | **Automation & Efficiency** | Reduzir tempo de cadastro manual de minutos para segundos | Cadastro via texto livre funcionando com acurácia >90% |
| 3 | **Cloud-Agnostic Deployment** | Evitar vendor lock-in, permitir flexibilidade de provedor | Deploy funcional em AWS, GCP, Azure com mesma configuração base |
| 4 | **Maintainability & Extensibility** | Facilitar evolução do sistema, novos modelos, features | Cobertura de testes >80%, documentação Arc42 completa |
| 5 | **Observability** | Troubleshooting rápido, monitoramento proativo | Logs estruturados, métricas Prometheus, traces distribuídos |
| 6 | **Performance** | Resposta rápida para melhor UX | P95 latência < 3s, throughput 100 req/min |

## 1.3 Stakeholders

| Stakeholder | Role | Interest | Expectations |
|-------------|------|----------|--------------|
| **Atendentes** | End Users | Usar sistema diariamente para cadastrar contatos | Interface simples, extração precisa de dados, poucos erros |
| **Gestores da Central** | Business Owners | Supervisionar operações, gerar relatórios | Exportação de dados, dashboards, relatórios de qualidade |
| **Desenvolvedores** | Development Team | Manter e evoluir sistema | Código limpo, documentação, testes, fácil para onboard |
| **DevOps/Infrastructure** | Operations Team | Deploy e monitoramento | Scripts IaC, observability, disaster recovery |
| **Data Protection Officer** | Compliance | LGPD compliance | Privacidade de dados, auditoria, retenção conforme política |

## 1.4 Scope and Context

### In Scope (MVP)
- ✅ CRUD completo de contatos (Create, Read, Update, Delete)
- ✅ Extração de entidades via LLM local (Llama3 8B via Ollama)
- ✅ Interface REST API (FastAPI)
- ✅ Banco de dados local (SQLite) com exportação Excel
- ✅ Integração Model Context Protocol (MCP) para comunicação com LLM
- ✅ Containerização via Docker + Docker Compose para LLM
- ✅ Documentação Arc42 completa
- ✅ Templates de deployment cloud-agnostic (Kubernetes, Terraform)

### Out of Scope (Future)
- ❌ UI Web completa (Streamlit opcional, foco na API REST)
- ❌ Notificações em tempo real (WebSockets, push)
- ❌ Multi-tenancy (single-tenant no MVP)
- ❌ Fine-tuning de modelo LLM (usar Llama3 pré-treinado)
- ❌ Integração com WhatsApp, Telegram (apenas API REST)
- ❌ Workflow engine complexo (regras de negócio simples no início)
- ❌ GPU clusters (llama3:8b roda em CPU modesto, otimizações futuras)

### System Context
```
┌─────────────────┐
│   Atendentes    │───┐
│  (API Clients)  │   │
└─────────────────┘   │
                      │
                      ▼
        ┌─────────────────────┐
        │   REST API (FastAPI)│
        │   - CRUD Operations │
        │   - MCP Integration │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────┐    ┌─────────────────┐
│   SQLite     │    │  LLM Local      │
│   Database   │    │  (Ollama MCP)   │
└──────────────┘    └─────────────────┘
                            │
                            │ (MCP Protocol)
                            ▼
                  ┌──────────────────┐
                  │  Model Context    │
                  │  Protocol Server  │
                  │  (Llama3:8b)      │
                  └──────────────────┘
```

## 1.5 Constraints

### Technical Constraints
- **LLM Local Obrigatório**: Não usar APIs externas (OpenAI, Anthropic) por privacidade
- **Python 3.11+**: Todas as dependências devem ser compatíveis
- **Container Orchestration**: Kubernetes ou serverless, mas não bare metal
- **Database Migration Path**: SQLite → PostgreSQL (suportado via SQLAlchemy)
- **Deployment Target**: Pelo menos uma major cloud (AWS/GCP/Azure)

### Organizational Constraints
- **Budget**: Open source tools preferred (FastAPI, Ollama, SQLite, PostgreSQL)
- **Team Size**: Solo developer inicialmente, depois possivelmente 2-3 pessoas
- **Timeline**: MVP em 6 sprints (3 meses), documentação antes de implementação
- **Compliance**: LGPD compliance mandatory

### Conventions
- **Documentation**: Markdown, Arc42 standard
- **Code Style**: PEP 8, Black formatter, Ruff linter
- **Git Workflow**: Conventional commits, feature branches, PR reviews
- **API Design**: RESTful, OpenAPI/Swagger documentation
- **Architecture**: Multi-repo (API + LLM services separados)

## 1.6 Technology Stack

### Backend
- **Framework**: FastAPI 0.109+
- **ORM**: SQLAlchemy 2.0+ (async support)
- **Database**: SQLite → PostgreSQL
- **Migrations**: Alembic
- **Validation**: Pydantic v2

### LLM & AI
- **Runtime**: Ollama (local)
- **Model**: Llama3:8b (quantized for efficiency)
- **Protocol**: Model Context Protocol (MCP)
- **Prompt Engineering**: In-house prompts, future fine-tuning possible

### Infrastructure
- **Containers**: Docker, Docker Compose
- **Orchestration**: Kubernetes (generic manifests)
- **IaC**: Terraform (cloud-agnostic modules)
- **CI/CD**: GitHub Actions (generic, can port to GitLab)

### Observability
- **Logging**: structlog (structured JSON logs)
- **Metrics**: Prometheus (exporter pattern)
- **Tracing**: OpenTelemetry (optional, future)
- **Monitoring**: Grafana dashboards

### Security
- **Authentication**: JWT (pyjwt)
- **Secrets**: HashiCorp Vault / AWS Secrets Manager (cloud)
- **Encryption**: TLS 1.3 in transit, encryption at rest
- **RBAC**: Role-based access control (future)

## 1.7 Definitions and Glossary

| Term | Definition |
|------|------------|
| **MCP (Model Context Protocol)** | Protocolo padrão aberto para comunicação com LLMs locais/externas, permitindo troca de contexto estruturado |
| **Central de Acolhimento** | Ambiente onde atendentes recebem e cadastram contatos de pessoas que buscam apoio/atendimento |
| **Entity Extraction** | Processo de identificar e extrair informações estruturadas de texto livre (ex.: nome, telefone, endereço) |
| **Prompt Engineering** | Técnica de construção de prompts para LLMs gerarem outputs no formato desejado |
| **Cloud-Agnostic** | Arquitetura que permite deployment em múltiplos provedores cloud sem vendor lock-in |
| **IaC** | Infrastructure as Code - gestão de infraestrutura via código (Terraform, Pulumi) |
| **Arc42** | Padrão de documentação arquitetural com 12 seções cobrindo todos os aspectos do sistema |

## 1.8 References

- [Arc42 Official Documentation](https://arc42.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Ollama Documentation](https://ollama.ai/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
