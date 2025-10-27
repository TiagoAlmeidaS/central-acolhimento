# 8. Cross-Cutting Concepts

## 8.1 Security

### Authentication
- **Method**: JWT (JSON Web Tokens)
- **Token Expiration**: Access token 1 hour, refresh token 7 days
- **Storage**: Access token in HTTP-only cookie (preferred) or Authorization header
- **Implementation**: pyjwt library, symmetric HS256 or asymmetric RS256
- **Middleware**: FastAPI dependency injection for route-level auth

```python
# Example auth middleware
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

### Authorization
- **Model**: Role-Based Access Control (RBAC)
- **Roles**:
  - `admin`: Full access (CRUD + export + admin functions)
  - `user`: Limited access (create, read own contacts)
- **Future**: Attribute-Based Access Control (ABAC) if needed

### Encryption
- **In Transit**: TLS 1.3 for all HTTP/HTTPS communication
- **At Rest**: Database encryption (PostgreSQL pgcrypto or filesystem encryption)
- **Secrets**: Environment variables or external secret manager (AWS Secrets Manager, HashiCorp Vault)

### Input Validation
- **Framework**: Pydantic v2 schemas
- **Sanitization**: Strip whitespace, validate formats (phone, email, etc.)
- **SQL Injection Prevention**: ORM parameter binding (never string interpolation)
- **XSS Prevention**: HTML escaping if future web UI added

## 8.2 Logging

### Logging Strategy
- **Format**: Structured JSON logging (structlog)
- **Levels**: DEBUG, INFO, WARN, ERROR, CRITICAL
- **Output**: stdout/stderr (containerized apps)
- **Collection**: Log aggregation via fluentd/Fluent Bit → ELK, Loki, or cloud logging service

### Structured Logging Example
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "contact_created",
    contact_id=123,
    nome="Maria Silva",
    telefone="11-9999-8888",
    user="atendente_001",
    timestamp="2024-01-15T10:30:00Z"
)
```

### Log Levels by Use Case
- **DEBUG**: Request/response details, LLM prompts/responses (only in dev)
- **INFO**: Business events (contact created, updated, deleted), API requests
- **WARN**: Degraded functionality (LLM timeouts, fallback to manual), validation failures
- **ERROR**: Exceptions, LLM failures after retries
- **CRITICAL**: System failures, database unavailable

### Sensitive Data Masking
- **Phone Numbers**: Partial masking in logs (ex: `11-9***-****`)
- **Emails**: Domain-only in logs (ex: `***@example.com`)
- **Names**: Allow full names (business requirement for audit)

## 8.3 Error Handling

### Error Hierarchy
```python
# Custom exceptions
class CentralAcolhimentoError(Exception):
    """Base exception"""
    pass

class LLMTimeoutError(CentralAcolhimentoError):
    """LLM service timeout"""
    pass

class LLMUnavailableError(CentralAcolhimentoError):
    """LLM service unavailable"""
    pass

class DatabaseError(CentralAcolhimentoError):
    """Database operation failed"""
    pass

class ValidationError(CentralAcolhimentoError):
    """Input validation failed"""
    pass
```

### HTTP Status Codes
- **200 OK**: Successful GET/PUT (non-create operations)
- **201 Created**: Successful POST (create operation)
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: LLM unavailable, manual input required
- **500 Internal Server Error**: Unexpected server error
- **503 Service Unavailable**: LLM service down, fallback active

### Error Response Format
```json
{
  "error": {
    "code": "LLM_TIMEOUT",
    "message": "LLM service timed out after 30 seconds",
    "details": {
      "retry_after": 5,
      "fallback": "manual_input_required"
    }
  }
}
```

## 8.4 Data Privacy & LGPD Compliance

### Data Minimization
- **Collect Only Necessary Data**: Nome, telefone, motivo, email (optional)
- **No Unnecessary Metadata**: Avoid collecting IP, browser fingerprint unless required
- **Purpose Limitation**: Data used only for Central de Acolhimento operations

### Consent Management
- **Explicit Consent**: Database flag `consent_obtained` (boolean)
- **Consent Date**: Track when consent was obtained
- **Withdrawal**: Mechanism to revoke consent (marks data for deletion)

### Right to Deletion (Art. 18 LGPD)
- **Endpoint**: DELETE /contatos/{id}
- **Permanent Deletion**: Hard delete from database (no soft delete for compliance)
- **Audit Log**: Log all deletion requests with reason

### Data Portability (Art. 18 LGPD)
- **Export Endpoint**: GET /contatos/export/format=json or xlsx
- **Format**: Structured JSON or Excel with all contact fields

### Audit Logging
- **Log All Access**: CREATE, READ, UPDATE, DELETE operations logged
- **Fields**: user_id, action, resource_id, timestamp, IP address
- **Retention**: 365 days (configurable)

## 8.5 Observability

### Metrics (Prometheus)

#### API Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

# Histograms
api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

# Gauges
active_connections = Gauge(
    'api_active_connections',
    'Active connections'
)
```

#### Business Metrics
```python
# Counters
contacts_created_total = Counter(
    'contacts_created_total',
    'Total contacts created',
    ['method']  # 'llm_extracted' or 'manual'
)

llm_extractions_total = Counter(
    'llm_extractions_total',
    'Total LLM entity extractions',
    ['status']  # 'success' or 'failure'
)

# Histograms
llm_extraction_duration_seconds = Histogram(
    'llm_extraction_duration_seconds',
    'LLM extraction duration'
)
```

### Tracing (Future: OpenTelemetry)
- **Instrumentation**: FastAPI middleware for automatic tracing
- **Spans**: API request, LLM call, DB query
- **Distributed Tracing**: Trace requests across services (API → LLM)
- **Exporter**: Jaeger or Grafana Tempo

### Alerting Rules
```yaml
# prometheus/alerts.yml
groups:
- name: central_acolhimento
  interval: 30s
  rules:
  - alert: HighErrorRate
    expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.01
    for: 5m
    annotations:
      summary: "High error rate detected"
  
  - alert: LLMServiceDown
    expr: up{job="llm"} == 0
    for: 2m
    annotations:
      summary: "LLM service is down"
  
  - alert: HighLatency
    expr: histogram_quantile(0.95, api_request_duration_seconds) > 3
    for: 10m
    annotations:
      summary: "P95 latency exceeds 3 seconds"
```

## 8.6 Resilience Patterns

### Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def call_mcp_service():
    """Retry MCP call with exponential backoff"""
    pass
```

### Circuit Breaker
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
async def call_llm_service():
    """Circuit breaker for LLM service"""
    pass
```

### Timeouts
- **API Request**: 30 seconds (configurable)
- **LLM Processing**: 60 seconds (llama3:8b can be slow on CPU)
- **Database Query**: 10 seconds (connection pool timeout)

### Graceful Degradation
- **LLM Unavailable**: Require explicit fields (nome, telefone, motivo) instead of free text
- **Database Read-Only**: Serve cached data if database write fails
- **Partial Failures**: Return 207 Multi-Status if batch operations partially fail

## 8.7 Caching Strategy (Future)

### Redis Caching (Post-MVP)
- **Cache LLM Responses**: Cache extracted entities for similar inputs
- **Cache Policy**: TTL 1 hour, key by input text hash
- **Cache Invalidation**: Manual invalidation on data schema changes

### Application-Level Caching
- **Prompt Templates**: Cache loaded prompts in memory
- **Database Queries**: Cache frequently accessed contacts (if needed)

## 8.8 Configuration Management

### Environment Variables
```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    llm_url: str = "http://localhost:11434"
    jwt_secret_key: str
    environment: str = "development"
    
    class Config:
        env_file = ".env"
```

### Secrets Management
- **Development**: `.env` file (git-ignored)
- **Production**: External secret manager (AWS Secrets Manager, HashiCorp Vault)
- **Kubernetes**: Secrets as ConfigMaps or External Secrets Operator

## 8.9 Internationalization (i18n)

### Locale Support
- **Primary Locale**: PT-BR (Portuguese Brazil)
- **DateTime Format**: ISO 8601 with timezone (America/Sao_Paulo)
- **Number Format**: PT-BR conventions (decimal comma, thousand dot)
- **Phone Format**: E.164 or Brazilian format (XX) XXXXX-XXXX

### Future Support
- **Multi-locale**: Add `locale` parameter to API endpoints
- **Translation**: API responses in multiple languages (future enhancement)

## 8.10 Code Quality

### Linting & Formatting
- **Formatter**: Black (line length 88)
- **Linter**: Ruff (fast Python linter)
- **Type Checking**: mypy (strict mode)
- **Import Sorting**: isort (automated)

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/psf/black
  rev: 23.12.0
  hooks:
  - id: black
  
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.1.6
  hooks:
  - id: ruff
  
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.7.1
  hooks:
  - id: mypy
    additional_dependencies: [types-all]
```

### Testing Strategy
- **Unit Tests**: pytest, coverage >80%
- **Integration Tests**: TestAPI client for FastAPI endpoints
- **E2E Tests**: pytest + httpx for full request/response cycle
- **Mocking**: LLM responses mocked for deterministic tests

## 8.11 Documentation Standards

### Code Documentation
- **Docstrings**: Google style for functions/classes
- **Type Hints**: Mandatory for all function signatures
- **Comments**: Inline comments for complex business logic

### API Documentation
- **OpenAPI/Swagger**: Auto-generated from FastAPI
- **Endpoint Descriptions**: Clear summary and detailed description
- **Request/Response Examples**: Include example payloads
- **Authentication**: Document how to obtain/use JWT tokens

### Architecture Documentation
- **Arc42**: This document (complete architecture overview)
- **Diagrams**: C4 model, sequence diagrams, deployment diagrams
- **ADRs**: Architecture Decision Records for major decisions
- **Runbooks**: Operational procedures in `docs/operations/`

## 8.12 Dependencies & Version Management

### Python Dependencies
```txt
# requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
alembic==1.13.0
pydantic==2.5.3
pydantic-settings==2.1.0
structlog==24.1.0
prometheus-client==0.19.0
pytest==7.4.4
httpx==0.26.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### Version Pinning Strategy
- **Exact Versions**: Pin major.minor.patch for reproducibility
- **Security Updates**: Automated dependabot alerts
- **Major Upgrades**: Manual review and testing required

## 8.13 Accessibility (Future UI)

### WCAG Compliance (Level AA)
- **Screen Reader Support**: Semantic HTML (aria-labels if web UI added)
- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Color Contrast**: 4.5:1 ratio for text (if UI added)

### API Accessibility
- **Consistent Response Format**: Predictable structure
- **Clear Error Messages**: Human-readable error descriptions
- **Versioning**: API versioning for backward compatibility (v1, v2)
