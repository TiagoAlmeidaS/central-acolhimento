# 10. Quality Requirements

## 10.1 Overview
Este documento define os requisitos de qualidade para o sistema Central de Acolhimento MVP.

## 10.2 Quality Tree

```
Qualidade do Sistema
├── Funcionalidade
│   ├── Completeness (100% features MVP)
│   ├── Correctness (0% error rate em extração)
│   └── Appropriateness
├── Reliability
│   ├── Maturity
│   ├── Fault Tolerance
│   └── Recoverability
├── Usability
│   ├── Understandability
│   ├── Learnability
│   └── Operability
├── Efficiency
│   ├── Performance
│   ├── Resource Utilization
│   └── Scalability
└── Maintainability
    ├── Analyzability
    ├── Changeability
    ├── Stability
    └── Testability
```

## 10.3 Quality Requirements Table

| ID | Quality Goal | Scenario | Metric | Target Value | Priority |
|----|--------------|----------|--------|---------------|----------|
| Q-1 | **Response Time (API)** | User creates contact via LLM | P95 latency | < 3 seconds | High |
| Q-2 | **Response Time (LLM)** | Entity extraction from text | P95 latency | < 5 seconds | High |
| Q-3 | **Throughput** | API requests per minute | Requests/min | 100 req/min | Medium |
| Q-4 | **Availability** | System uptime | Uptime % | > 99.5% | High |
| Q-5 | **Accuracy (LLM)** | Entity extraction correctness | Precision/Recall | > 90% | High |
| Q-6 | **Error Rate** | Failed API requests | Error rate % | < 1% | High |
| Q-7 | **Database Performance** | Query response time | Query latency | < 100ms | Medium |
| Q-8 | **Concurrent Users** | Simultaneous users | Active users | 5-10 | Low |
| Q-9 | **Data Privacy** | LGPD compliance | Compliance score | 100% | High |
| Q-10 | **Code Quality** | Test coverage | Coverage % | > 80% | High |
| Q-11 | **Security** | Vulnerable dependencies | CVEs | 0 critical, < 5 high | High |
| Q-12 | **Documentation** | Arc42 completeness | Sections covered | 11/11 | Medium |

## 10.4 Quality Scenarios

### Q-1: Response Time (API)
**Scenario**: Atendente envia POST /contatos com texto livre e espera resposta.

**Trigger**: POST request received

**Reactions**:
1. API validates input (< 100ms)
2. API calls LLM service (< 500ms)
3. LLM processes text (< 3s, avg 2s)
4. API validates entities (< 100ms)
5. API inserts into DB (< 100ms)
6. Response returned (< 50ms)

**Expected Result**: Total < 3 seconds (P95)

**Measurement**: HTTP status code 201 returned within 3 seconds

### Q-2: LLM Processing Time
**Scenario**: LLM recebe prompt e retorna entidades extraídas.

**Expected Result**: < 5 seconds (P95) for llama3:8b on CPU

**Measurement**: Time from HTTP request to Ollama → response with entities

### Q-3: Throughput
**Scenario**: Múltiplos atendentes fazendo requests simultaneamente.

**Expected Result**: System handles 100 requests/minute without degradation

**Measurement**: Load testing com locust/artillery, monitor P95/P99 latency

### Q-4: Availability
**Scenario**: System should be available 24/7 except planned maintenance.

**Expected Result**: > 99.5% uptime (≈ 3.6 hours downtime/month acceptable)

**Measurement**: Prometheus monitoring, Grafana dashboards

### Q-5: LLM Accuracy
**Scenario**: LLM extrai entidades (nome, telefone, motivo) de texto livre.

**Expected Result**: > 90% precision (correct extractions / total extractions) e recall (extractions / actual entities)

**Measurement**: Manual evaluation on test dataset (100 examples)

### Q-6: Error Rate
**Scenario**: API requests devem ser bem-sucedidas na maioria dos casos.

**Expected Result**: < 1% error rate (HTTP 4xx, 5xx)

**Measurement**: Prometheus `api_requests_total{status=~"4..|5.."}`

### Q-7: Database Performance
**Scenario**: Queries devem retornar rapidamente mesmo com muitos registros.

**Expected Result**: Query latency < 100ms for indexed queries (SELECT, INSERT)

**Measurement**: SQLAlchemy query profiling, PostgreSQL slow query log

### Q-8: Concurrent Users
**Scenario**: Múltiplos atendentes acessando simultaneamente.

**Expected Result**: Support 5-10 simultaneous users without performance degradation

**Measurement**: Load testing, monitor P95 latency per user

### Q-9: Data Privacy (LGPD)
**Scenario**: Dados pessoais nunca devem sair do ambiente local.

**Expected Result**: 100% LGPD compliance (zero egress de dados para APIs externas)

**Measurement**: Audit log analysis, network egress monitoring

### Q-10: Code Quality (Test Coverage)
**Scenario**: Código deve ser testável e testado.

**Expected Result**: > 80% test coverage

**Measurement**: pytest-cov report

### Q-11: Security (Dependencies)
**Scenario**: Dependências não devem ter vulnerabilidades críticas.

**Expected Result**: 0 critical CVEs, < 5 high severity CVEs

**Measurement**: Automated scanning (dependabot, snyk)

### Q-12: Documentation
**Scenario**: Arc42 documentação deve estar completa.

**Expected Result**: All 11 sections documented

**Measurement**: Review checklist

## 10.5 Performance Requirements

### Latency Requirements
| Operation | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| GET /contatos/{id} | 10ms | 50ms | 100ms |
| POST /contatos (LLM) | 2s | 3s | 5s |
| POST /contatos (manual) | 100ms | 200ms | 500ms |
| PUT /contatos/{id} | 50ms | 150ms | 300ms |
| DELETE /contatos/{id} | 20ms | 100ms | 200ms |
| GET /contatos/export | 500ms | 1s | 2s |

### Throughput Requirements
| Endpoint | Concurrent Users | Requests/min |
|----------|------------------|--------------|
| POST /contatos (LLM) | 10 | 100 |
| GET /contatos | 10 | 200 |
| PUT /contatos/{id} | 5 | 50 |

### Resource Requirements
| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| API Service | 100m (request), 500m (limit) | 256Mi (request), 512Mi (limit) | N/A |
| LLM Service | 4 CPU (request), 8 CPU (limit) | 12Gi (request), 16Gi (limit) | 20Gi (model storage) |
| Database | 250m (request), 500m (limit) | 512Mi (request), 1Gi (limit) | 10Gi (data) |

## 10.6 Reliability Requirements

### Fault Tolerance
- **API Service**: Automatically restarts on crash (Kubernetes liveness probe)
- **LLM Service**: Graceful degradation if LLM unavailable (fallback to manual input)
- **Database**: Connection retry with exponential backoff

### Recovery Time
- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: < 15 minutes

### Backup Strategy
- **Database**: Daily full backup, 6-hourly incremental
- **Backup Retention**: 90 days
- **Restore Testing**: Monthly

## 10.7 Security Requirements

### Authentication & Authorization
- **Method**: JWT tokens
- **Token Expiration**: 1 hour (access), 7 days (refresh)
- **Role-Based Access**: admin, user roles

### Data Protection
- **Encryption in Transit**: TLS 1.3 mandatory
- **Encryption at Rest**: Database encryption (pgcrypto or filesystem encryption)
- **Secrets Management**: External secret manager (AWS Secrets Manager, Vault)

### Vulnerability Management
- **Dependency Scanning**: Automated (dependabot, snyk)
- **Patch Policy**: Critical patches applied within 24 hours
- **Penetration Testing**: Annual third-party audit

## 10.8 Usability Requirements

### API Usability
- **Self-Documenting**: OpenAPI/Swagger auto-generated
- **Clear Error Messages**: Human-readable error responses
- **Consistent Format**: Predictable response structure

### Operational Usability
- **Health Checks**: /health endpoint for monitoring
- **Metrics**: Prometheus /metrics endpoint
- **Logs**: Structured JSON logs (stdout)

## 10.9 Maintainability Requirements

### Code Quality
- **Type Hints**: Mandatory for all functions
- **Docstrings**: Google-style for public APIs
- **Linting**: Ruff, Black, mypy compliance

### Testability
- **Test Coverage**: > 80%
- **Unit Tests**: pytest for all business logic
- **Integration Tests**: FastAPI TestClient for API endpoints
- **Mocking**: LLM responses mocked for deterministic tests

### Documentation
- **Arc42**: Complete architecture documentation
- **API Docs**: OpenAPI/Swagger
- **Runbooks**: Operational procedures documented

## 10.10 Scalability Requirements

### Horizontal Scaling
- **API Pods**: 2-10 replicas (autoscaling based on CPU/memory)
- **LLM Pods**: 1 replica (single instance due to GPU/memory constraints)
- **Database**: Read replicas if needed (PostgreSQL)

### Vertical Scaling
- **API**: Scale up to 4 CPU, 2Gi RAM per pod if needed
- **LLM**: Scale up to 16Gi RAM for larger models (llama3:70b)
- **Database**: Upgrade to larger instance type (managed service)

## 10.11 Compliance Requirements

### LGPD (Lei Geral de Proteção de Dados)
- **Data Minimization**: Collect only necessary data
- **Consent Management**: Track and manage user consent
- **Right to Deletion**: Implement DELETE endpoint
- **Data Portability**: Export data in JSON/Excel format
- **Audit Logging**: Log all access to personal data

### Security Standards
- **OWASP Top 10**: Protection against common vulnerabilities
- **TLS 1.3**: Encrypted communication
- **Secrets Rotation**: Rotate credentials quarterly

## 10.12 Quality Metrics Dashboard

### Prometheus Metrics to Monitor
```yaml
# Examples of metrics to track
api_requests_total{method="POST", endpoint="/contatos", status="201"}
api_request_duration_seconds{method="POST", endpoint="/contatos"}
llm_extractions_total{status="success"}
llm_extraction_duration_seconds
contacts_created_total{method="llm_extracted"}
database_query_duration_seconds{operation="INSERT"}
```

### Grafana Dashboard Panels
- **Request Rate**: Requests per second
- **Error Rate**: % of failed requests
- **Latency**: P50, P95, P99 distribution
- **LLM Processing Time**: Average LLM call duration
- **Database Performance**: Query latency
- **Availability**: Uptime percentage

## 10.13 Quality Assurance Strategy

### Unit Testing
- **Framework**: pytest
- **Coverage Target**: > 80%
- **Scope**: All business logic, CRUD operations, MCP client

### Integration Testing
- **Framework**: pytest + FastAPI TestClient
- **Scope**: Full request/response cycle (no external LLM)
- **Mocking**: LLM responses mocked with expected values

### E2E Testing (Optional, Future)
- **Framework**: pytest + httpx
- **Scope**: Full system test (API + LLM + Database)
- **Frequency**: Nightly in CI/CD

### Load Testing
- **Framework**: Locust or Artillery
- **Target**: 100 req/min sustained
- **Frequency**: Pre-production deployment
