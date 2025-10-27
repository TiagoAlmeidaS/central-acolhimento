# 2. Constraints

## 2.1 Technical Constraints

### Infrastructure
- **Computational Resources**: LLM llama3:8b requer mínimo 8GB RAM, preferencialmente 16GB+ para performance adequada
- **Storage**: Database cresce ~1MB por 1000 contatos, considerar 100MB+ inicial para logs e backups
- **Network**: LLM service exposto via localhost no ambiente local, rede interna em produção
- **Container Orchestration**: Kubernetes 1.25+ ou compatível (GKE, EKS, AKS)
- **OS Compatibility**: Linux obrigatório para Ollama (Windows via WSL2 para dev)

### Technology Dependencies
- **Python Version**: Python 3.11+ obrigatório (features async, type hints avançados)
- **Database Engine**: SQLite 3.35+ (local), PostgreSQL 14+ (produção cloud)
- **Container Runtime**: Docker 24+ ou containerd 1.7+
- **Kubernetes API**: v1.25+ para features modernas (Gateway API, etc.)

### External Systems
- **MCP Server**: Deve estar acessível na mesma rede (localhost em dev, service mesh em prod)
- **No External LLM APIs**: OpenAI, Anthropic, etc. são **explícitamente proibidos** por privacidade
- **Database Cloud**: Apenas managed services (RDS, Cloud SQL, Azure Database) - não bare metal DB em cloud

## 2.2 Organisational Constraints

### Budget & Resources
- **Open Source First**: Preferir ferramentas open-source para reduzir custos
- **Team Composition**: 1-2 developers full-time inicialmente, possivelmente expandir para 3-4
- **Timeline**: MVP documentação em 2 semanas, implementação em 6 sprints (12 semanas)
- **Cloud Budget**: Máximo $200/mês em cloud (AWS/GCP/Azure free tier quando possível)

### Compliance & Legal
- **LGPD Compliance**: Obligatório - dados pessoais não podem sair do território brasileiro sem anonimização
- **Data Retention**: Política de retenção de dados conforme regulamentação interna
- **Audit Logging**: Todos os acessos a dados pessoais devem ser logados para auditoria
- **Security**: PCI-DSS não aplicável (não armazenamos cartões), mas ISO 27001 alignment desejável

### Regulatory
- **Localization**: Sistema deve suportar PT-BR como locale principal
- **Timestamp**: Usar timezone America/Sao_Paulo (UTC-3) para logs e timestamps
- **Data Sovereignty**: Dados devem residir em infraestrutura sob jurisdição brasileira (On-premise ou datacenter BR)

## 2.3 Conventions

### Code & Development
- **Code Style**: PEP 8, line length 88 (Black default), type hints obrigatórios
- **Git Workflow**: Conventional Commits (feat:, fix:, docs:, refactor:), feature branches
- **Testing**: Test coverage mínimo 80%, pytest, unittest style
- **Dependencies**: Poetry ou pip-tools para gerenciamento de dependências (requirements.txt baseline)

### Documentation
- **Markdown Standard**: CommonMark specification, arquivos em PT-BR
- **Architecture Docs**: Arc42 template (este documento)
- **API Docs**: OpenAPI 3.1 specification, Swagger UI auto-generated
- **Code Comments**: Google-style docstrings, PT-BR para business logic

### Deployment & Operations
- **Infrastructure as Code**: Terraform como ferramenta principal, estado remoto obrigatório
- **GitOps**: ArgoCD ou Flux para deployment contínuo em produção (futuro)
- **Container Registry**: Docker Hub público para imagens base, registry privado para builds
- **Secret Management**: HashiCorp Vault ou cloud-native (AWS Secrets Manager, GCP Secret Manager)

### Monitoring & Observability
- **Logging Format**: JSON structured logging (structlog), nível INFO por padrão
- **Metrics Standard**: Prometheus exposition format, scraping por port 9090
- **Alerting**: Alertmanager ou PagerDuty para notificações críticas
- **Dashboard**: Grafana dashboards por serviço

## 2.4 Known Issues & Technical Debt (Futuros)

### Short-term (Sprint 1-3)
- **SQLite Limitações**: Não suporta concorrência alta, migração para PostgreSQL priorizada
- **LLM Single Instance**: Uma única instância Ollama pode ser gargalo, considerar sharding horizontal
- **No Caching**: Adicionar Redis para cache de prompts/respostas frequentes
- **Limited Observability**: Apenas logs básicos, adicionar tracing distribuído (OpenTelemetry)

### Mid-term (Sprint 4-6)
- **No Multi-tenancy**: Sistema single-tenant, adicionar isolamento por organização se necessário
- **Static MCP Configuration**: MCP endpoints hardcoded, migrar para service discovery
- **Sequential Processing**: LLM é síncrono, adicionar queue (Celery/RQ) para assíncrono
- **Manual Deployment**: Deploy manual inicial, automatizar com CI/CD pipeline

### Long-term (Post-MVP)
- **No GPU Optimization**: Llama3:8b roda em CPU, otimizar para GPU se throughput aumentar
- **Prompt Engineering Manual**: Fine-tuning de modelo para domínio específico de atendimento
- **No Disaster Recovery Plan**: Adicionar backup automático, replication, failover regional
- **Limited Scalability Testing**: Load testing necessário para validar arquitetura em escala

## 2.5 Performance Constraints

### Response Time
- **API Endpoint**: P95 < 3 segundos para operações CRUD (excluindo processamento LLM)
- **LLM Processing**: P95 < 5 segundos para extração de entidades (depende do hardware)
- **Export Excel**: < 1 segundo para 1000 registros

### Throughput
- **API**: 100 requests/minuto suportado sem otimizações
- **LLM**: ~10 extrações/minuto por instância Ollama (llama3:8b, CPU modesto)
- **Database**: Suporta 1000+ contatos iniciais, scaling horizontal necessário após

### Scalability Targets
- **Initial**: 100-1000 contatos/dia
- **Growth**: Suportar 10.000 contatos em 1 ano
- **Concurrent Users**: 5-10 atendentes simultâneos no MVP

## 2.6 Security Constraints

### Authentication & Authorization
- **JWT Required**: Autenticação obrigatória em produção (desenvolvimento pode ter modo debug sem auth)
- **Role-Based Access**: Básico no MVP (admin, user), RBAC completo em produção
- **Token Expiration**: JWT tokens expiram em 1 hora, refresh tokens validos por 7 dias

### Data Protection
- **Encryption in Transit**: TLS 1.3 obrigatório para API e comunicação inter-serviços
- **Encryption at Rest**: Database encryption ativado (PostgreSQL pgcrypto ou filesystem encryption)
- **Secrets**: Secrets nunca em código, uso de env vars ou secret managers
- **Backup Encryption**: Backups de banco de dados devem ser criptografados

### Auditing & Compliance
- **Audit Logs**: Todos os acessos a dados pessoais são logados (CREATE, READ, UPDATE, DELETE)
- **Data Retention**: Logs mantidos por 365 dias, snapshots de database por 90 dias
- **Access Logging**: IP address, user ID, timestamp para cada request
- **Privacy**: Logs não contém dados sensíveis completos (mascaramento de telefones, emails)

## 2.7 Infrastructure Constraints

### Cloud Provider Agnosticism
- **Avoid Vendor Lock-in**: Usar abstrações (S3-like APIs para storage, generic Kubernetes)
- **IaC Modules**: Terraform modules reutilizáveis para AWS, GCP, Azure
- **No Proprietary Services**: Evitar serviços específicos (Lambda específico AWS), usar padrões abertos

### Container & Orchestration
- **Container Base Image**: Alpine Linux ou distroless para reduzir tamanho e attack surface
- **Multi-stage Builds**: Otimizar imagens Docker, camadas cacheadas apropriadamente
- **Health Checks**: Health probes configurados em todos os containers (liveness, readiness)
- **Resource Limits**: CPU/memory limits definidos em todos os deployments

### Network & Connectivity
- **Internal Communication**: Services comunicam via service mesh ou network policies Kubernetes
- **External APIs**: Apenas egress permitido para registries (Docker Hub, PyPI)
- **VPN Required**: SSH/debug access somente via VPN ou bastion host
- **No Public IPs**: Services não expostos publicamente, use LoadBalancer ou Ingress com TLS

## 2.8 Compliance Constraints

### LGPD (Lei Geral de Proteção de Dados)
- **Consentimento**: Usuários devem consentir com coleta de dados pessoais
- **Anonimização**: Dados sensíveis devem ser anonimizados em logs e backups
- **Right to Deletion**: Usuários podem solicitar exclusão de dados pessoais (função de DELETE implementada)
- **Data Portability**: Exportação de dados em formato estruturado (Excel, JSON)

### Security Standards Alignment
- **OWASP Top 10**: Proteção contra vulnerabilidades comuns (SQL injection, XSS, CSRF)
- **PCI-DSS**: Não aplicável (não processamos cartões de crédito)
- **ISO 27001**: Alinhamento desejável para futura certificação

## 2.9 Operational Constraints

### Availability & Uptime
- **SLA Target**: 99.5% uptime (≈3.6 horas downtime/mês aceitável)
- **Planned Maintenance**: Janelas de manutenção noturnas (00:00-06:00 BR time)
- **Graceful Degradation**: Sistema continua funcional mesmo se LLM service estiver indisponível (fallback manual)

### Backup & Recovery
- **Database Backups**: Full backup diário, incrementais a cada 6 horas
- **Recovery Time Objective (RTO)**: < 1 hora para restauração completa
- **Recovery Point Objective (RPO)**: < 15 minutos de perda de dados (transactional replication)

### Support & Maintenance
- **Documentation**: Toda funcionalidade deve ter documentação atualizada
- **On-Call**: Developer deve estar disponível 24/7 para incidentes críticos (P1)
- **Incident Response**: SLA de 15 minutos para resposta em produção down

## 2.10 Technology Selection Rationale

### FastAPI over Flask/Django
- Async/await native para alta performance
- OpenAPI/Swagger automatic documentation
- Type hints e Pydantic para validação robusta

### Ollama over Cloud LLMs
- **Privacy**: Dados nunca saem do ambiente local
- **Cost**: Zero custo operacional (vs. $0.01-0.03 por request em OpenAI)
- **LGPD Compliance**: Garantia de soberania de dados
- **Control**: Fine-tuning futuro é viável

### SQLite → PostgreSQL
- **SQLite**: Simples para MVP local, zero setup
- **PostgreSQL**: Production-grade, suporte a concorrência, features avançadas (JSON, full-text search)
- **Migration Path**: SQLAlchemy abstrai diferenças, migração via Alembic

### Kubernetes over Docker Swarm
- **Industry Standard**: Maior ecossistema e community
- **Cloud-Agnostic**: Funciona igual em AWS, GCP, Azure
- **Features**: RBAC, network policies, autoscaling nativo
- **GitOps Ready**: Integração natural com ArgoCD/Flux

### Terraform over Ansible/Pulumi
- **IaC State Management**: Terraform state tracking é robusto
- **Provider Ecosystem**: Maior número de providers (AWS, GCP, Azure uniformemente suportado)
- **Declarative**: Descrever desired state vs. imperative scripts
- **Mature**: Ferramenta estável e amplamente adotada
