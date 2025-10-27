# 11. Risks and Technical Debt

## 11.1 Risk Matrix

### High-Impact Risks (Mitigation Required)

| Risk ID | Risk | Impact | Probability | Mitigation Strategy | Status |
|---------|------|--------|-------------|---------------------|---------|
| R-1 | LLM hallucination (incorrect entity extraction) | High | Medium | Human validation before commit, comprehensive prompt engineering, test dataset validation | ⚠️ Active |
| R-2 | LLM service crashes or unavailable | High | Low | Fallback to manual input fields, circuit breaker, graceful degradation | ✅ Mitigated |
| R-3 | Data loss (SQLite corruption, disk failure) | High | Low | Daily backups, migration to PostgreSQL in production, automated restore testing | ✅ Mitigated |
| R-4 | Performance issues (LLM slow on CPU) | Medium | High | Accept latency (2-5s acceptable), consider GPU optimization in future | ✅ Accepted |
| R-5 | Security breach (API exposed, data leaked) | High | Low | JWT authentication, TLS 1.3, secrets management, network policies | ✅ Mitigated |
| R-6 | Vendor lock-in (cloud provider) | Medium | Low | Terraform multi-cloud, Kubernetes standards, S3-compatible abstractions | ✅ Mitigated |
| R-7 | Team expertise gap (MCP protocol, LLM engineering) | Medium | Medium | Comprehensive documentation, onboarding guide, training materials | ⚠️ Active |

### Medium-Impact Risks

| Risk ID | Risk | Impact | Probability | Mitigation Strategy | Status |
|---------|------|--------|-------------|---------------------|---------|
| R-8 | SQLite limitations in production (concurrency) | Medium | High | Planned migration to PostgreSQL early in production | ✅ Planned |
| R-9 | Limited observability (no distributed tracing) | Medium | Medium | OpenTelemetry integration in future sprints | 📅 Future |
| R-10 | LLM model outdated (newer llama versions) | Low | Medium | Pin model version, upgrade path documented | ✅ Low Priority |
| R-11 | Cost overrun (cloud resources, especially GPU) | Medium | Low | Resource limits, cost monitoring dashboards | ✅ Mitigated |
| R-12 | Documentation outdated | Low | Medium | Automated documentation checks in CI/CD, review process | ⚠️ Active |

### Low-Impact Risks

| Risk ID | Risk | Impact | Probability | Mitigation Strategy | Status |
|---------|------|--------|-------------|---------------------|---------|
| R-13 | Dependencies outdated (security vulnerabilities) | Low | Low | Automated dependabot alerts, quarterly dependency audit | ✅ Mitigated |
| R-14 | Git history bloated (large Docker images in history) | Low | Low | .dockerignore, multi-stage builds, cleanup policies | ✅ Mitigated |

## 11.2 Risk Assessment

### High-Impact, High-Probability (Critical)
Nenhum risco crítico identificado após mitigações.

### High-Impact, Low-Probability (Monitor)
- **R-2**: LLM service crashes → Mitigation: Circuit breaker, fallback manual input
- **R-3**: Data loss → Mitigation: Daily backups, PostgreSQL migration
- **R-5**: Security breach → Mitigation: JWT, TLS, secrets management

### Low-Impact, High-Probability (Technical Debt)
- **R-4**: LLM performance → Accepted as-is (2-5s latency acceptable for MVP)
- **R-8**: SQLite limitations → Planned migration to PostgreSQL

## 11.3 Risk Mitigation Strategies

### R-1: LLM Hallucination
**Severity**: High  
**Mitigation**:
1. Comprehensive prompt engineering (template testes em test suite)
2. Human validation UI (future: review screen antes de commit)
3. Confidence scores: Only commit if LLM confidence > threshold
4. Test dataset: 100 examples com ground truth, validate accuracy >90%

**Monitoring**: Track precision/recall metrics via Prometheus

### R-2: LLM Service Unavailable
**Severity**: High  
**Mitigation**:
1. **Circuit Breaker**: Abort after 3 consecutive failures
2. **Fallback UI**: Require explicit fields (nome, telefone, motivo) if LLM unavailable
3. **Graceful Degradation**: API continues to work with manual input
4. **Health Checks**: Monitor LLM health, alert if down

**Monitoring**: Alert on LLM unavailability > 2 minutes

### R-3: Data Loss
**Severity**: High  
**Mitigation**:
1. **Daily Backups**: Automated CronJob backing up to S3/GCS/Azure Blob
2. **PostgreSQL Migration**: Migrate from SQLite to PostgreSQL in production (transactional replication)
3. **Point-in-Time Recovery**: PostgreSQL allows recovery to specific timestamp
4. **Restore Testing**: Monthly restore drills to validate backup integrity

**Monitoring**: Alert if backup job fails

### R-4: Performance (LLM Slow)
**Severity**: Medium  
**Acceptance**: P95 latency of 3-5s is acceptable for MVP

**Future Mitigation**:
1. **GPU Optimization**: Upgrade to llama3:8b on GPU (10-50x faster)
2. **Model Quantization**: Use quantized model (4-bit) for faster inference
3. **Caching**: Redis cache for repeated prompts

### R-5: Security Breach
**Severity**: High  
**Mitigation**:
1. **JWT Authentication**: Mandatory in production
2. **TLS 1.3**: All traffic encrypted in transit
3. **Secrets Management**: External secrets manager (AWS Secrets Manager, Vault)
4. **Network Policies**: Kubernetes network policies to isolate services
5. **Input Validation**: Pydantic schemas prevent injection attacks
6. **OWASP Compliance**: Regular dependency scanning

**Monitoring**: Alert on failed authentication attempts, suspicious API usage

### R-6: Vendor Lock-in
**Severity**: Medium  
**Mitigation**:
1. **Terraform Multi-Cloud**: Modules work on AWS, GCP, Azure
2. **Kubernetes Standards**: Use standard Kubernetes manifests (no cloud-specific features)
3. **S3-Compatible Storage**: Abstract storage layer (boto3, google-cloud-storage)
4. **Managed DB Abstraction**: SQLAlchemy ORM masks DB differences

## 11.4 Technical Debt Inventory

### Short-term Debt (Sprint 1-3)

#### TD-1: SQLite Database
**Issue**: SQLite não suporta concorrência alta, limitações de performance em produção  
**Impact**: Medium  
**Effort**: 2-4 hours to migrate to PostgreSQL  
**Priority**: High (migrate before high traffic)  
**Resolution**: Run PostgreSQL StatefulSet in Kubernetes, Alembic migration script

#### TD-2: No Caching Layer
**Issue**: LLM processa mesmo prompt repetidamente  
**Impact**: Low (performance)  
**Effort**: 4-8 hours to add Redis caching  
**Priority**: Low (acceptable in MVP)  
**Resolution**: Add Redis, cache LLM responses by input hash, TTL 1 hour

#### TD-3: Limited Observability
**Issue**: Apenas logs básicos, sem distributed tracing  
**Impact**: Medium (debugging difficult)  
**Effort**: 8-16 hours to add OpenTelemetry  
**Priority**: Medium  
**Resolution**: Integrate OpenTelemetry SDK, Jaeger backend

#### TD-4: Single LLM Instance
**Issue**: LLM não escalada horizontalmente  
**Impact**: Low (single LLM sufficient for MVP load)  
**Effort**: N/A (requires queue system)  
**Priority**: Low  
**Resolution**: Add Celery + Redis for async LLM processing (future)

### Mid-term Debt (Sprint 4-6)

#### TD-5: Manual Deployment
**Issue**: Deploy requires manual kubectl apply  
**Impact**: Medium (error-prone)  
**Effort**: 4-8 hours to setup CI/CD  
**Priority**: Medium  
**Resolution**: GitHub Actions pipeline, automated K8s deployment

#### TD-6: No Disaster Recovery Plan
**Issue**: Backup exists but no documented DR procedure  
**Impact**: High if disaster occurs  
**Effort**: 4-8 hours to document and test DR  
**Priority**: High  
**Resolution**: Document DR runbook in `docs/operations/disaster-recovery.md`, test monthly

#### TD-7: Static MCP Configuration
**Issue**: MCP endpoints hardcoded in code  
**Impact**: Low (flexibility)  
**Effort**: 2-4 hours to externalize config  
**Priority**: Low  
**Resolution**: Environment variables, Helm values

### Long-term Debt (Post-MVP)

#### TD-8: No Multi-tenancy
**Issue**: Sistema single-tenant, não suporta múltiplas organizações  
**Impact**: High if multi-tenancy required  
**Effort**: 40-80 hours to refactor  
**Priority**: Low (not required in MVP)  
**Resolution**: Add organization_id to all tables, implement tenant isolation

#### TD-9: No GPU Optimization
**Issue**: llama3:8b em CPU, lento comparado a GPU  
**Impact**: Low (performance acceptable for MVP)  
**Effort**: 8-16 hours to migrate to GPU  
**Priority**: Low  
**Resolution**: Deploy LLM pod to GPU node, use llama3:8b GPU image

#### TD-10: Prompt Engineering Manual
**Issue**: Prompts hardcoded, sem versionamento  
**Impact**: Low (maintainability)  
**Effort**: 4-8 hours to add prompt versioning  
**Priority**: Low  
**Resolution**: Store prompts in database, versionamento, A/B testing

#### TD-11: Limited Test Coverage
**Issue**: Some edge cases not tested  
**Impact**: Medium (bugs may slip through)  
**Effort**: 16-32 hours to increase coverage  
**Priority**: Medium  
**Resolution**: Add tests for edge cases (missing fields, malformed input, concurrent requests)

## 11.5 Technical Debt Management

### Debt Repayment Strategy
- **Sprint Planning**: Allocate 20% of sprint to technical debt
- **Prioritization**: High-impact, low-effort debts tackled first
- **Refactoring Budget**: Regular refactoring sprints (1/4 sprints)

### Debt Tracking
- **Tools**: GitHub Issues labeled `technical-debt`
- **Metrics**: Track debt trend (total issues, by severity)
- **Reviews**: Quarterly technical debt review sessions

## 11.6 Known Issues

### Current Known Issues
1. **No rate limiting**: API can be overwhelmed by burst traffic (TD future: add rate limiter)
2. **No pagination limits**: Max 1000 items, may timeout on large datasets (TD: add streaming export)
3. **Export format hardcoded**: Excel only (TD future: add CSV, JSON export)
4. **LLM model hardcoded**: llama3:8b only (TD future: support multiple models via config)

### Workarounds
- Use manual rate limiting via nginx or API Gateway
- Filter exports by date range to reduce dataset size
- Use pandas to convert Excel to other formats externally (workaround for now)

## 11.7 Risk Monitoring

### Continuous Monitoring
- **Prometheus Alerts**: Alert on high error rate, LLM downtime, slow queries
- **Log Analysis**: Automated log parsing for error patterns
- **Dependency Scanning**: Automated CVE detection via dependabot/snyk

### Quarterly Reviews
- **Risk Review**: Reassess all risks quarterly, update mitigation strategies
- **Technical Debt Review**: Prioritize debt repayment, track progress
- **Security Audit**: Third-party security audit annually

## 11.8 Contingency Plans

### Plan A: LLM Service Crash
1. Circuit breaker opens after 3 failures
2. API degrades to manual input mode
3. Notify administrators via PagerDuty
4. Investigate root cause, restart LLM service

### Plan B: Database Corruption
1. Restore from latest backup (automatic)
2. Apply incremental backups to minimize data loss
3. Validate data integrity
4. Resume operations

### Plan C: Data Breach
1. Isolate affected components
2. Rotate all secrets immediately
3. Notify stakeholders and DPO
4. Conduct forensic analysis
5. Document incident in runbook
