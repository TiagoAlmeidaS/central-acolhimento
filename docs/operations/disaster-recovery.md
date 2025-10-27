# Disaster Recovery Plan - Central de Acolhimento

## Recovery Objectives

- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: < 15 minutes

## Backup Strategy

### Database Backups

#### Automated Backups
- **Frequency**: Daily full backup at 02:00 UTC
- **Retention**: 90 days
- **Location**: S3/GCS/Azure Blob
- **Encryption**: Yes (AES-256)

#### Backup Verification
- **Automated Tests**: Weekly backup restoration test
- **Manual Verification**: Monthly review of backup integrity

#### Backup Script
```bash
#!/bin/bash
# Automated backup script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DATE}.sql"

# Full backup
pg_dump $DATABASE_URL | gzip > ${BACKUP_FILE}.gz

# Upload to cloud storage
aws s3 cp ${BACKUP_FILE}.gz s3://backup-bucket/central-acolhimento/${BACKUP_FILE}.gz

# Encrypt backup
gpg --encrypt --recipient central-acolhimento@example.com ${BACKUP_FILE}.gz

# Remove local copy
rm ${BACKUP_FILE}.gz
```

### Configuration Backups
- **Kubernetes manifests**: In Git repository
- **Secrets**: In external secret manager (Vault, AWS Secrets Manager)
- **Environment variables**: Documented in `docs/operations/`

## Disaster Scenarios

### Scenario 1: Database Corruption

**Symptoms**: Unable to query database, connection errors

**Recovery Steps**:
1. Identify last good backup
2. Stop API service to prevent further writes
3. Restore database from backup
4. Verify data integrity
5. Restart API service
6. Monitor for any data loss

**RTO**: 30 minutes

### Scenario 2: Complete Infrastructure Loss

**Symptoms**: Entire Kubernetes cluster unavailable

**Recovery Steps**:
1. Provision new Kubernetes cluster
2. Restore database from backup
3. Deploy API and LLM services
4. Update DNS to point to new infrastructure
5. Verify all services operational

**RTO**: 1 hour

### Scenario 3: LLM Service Failure

**Symptoms**: API returns 503 when LLM unavailable

**Recovery Steps**:
1. Degrade to manual input mode (automatic fallback)
2. Restart LLM pod: `kubectl rollout restart statefulset/llm`
3. Monitor LLM service health
4. Re-enable LLM extraction when stable

**RTO**: 15 minutes

### Scenario 4: Data Breach/Security Incident

**Symptoms**: Unauthorized access detected

**Recovery Steps**:
1. Isolate affected services immediately
2. Revoke all credentials (API keys, JWT secrets)
3. Notify stakeholders and DPO
4. Conduct forensic analysis
5. Rotate all secrets
6. Deploy patched version
7. Document incident in post-mortem

**RTO**: 30 minutes

## Recovery Procedures

### Database Restore

```bash
# 1. Download backup from S3
aws s3 cp s3://backup-bucket/central-acolhimento/backup_20240115_020000.sql.gz .

# 2. Decrypt if encrypted
gpg --decrypt backup_20240115_020000.sql.gz > backup.sql

# 3. Drop and recreate database
dropdb central_acolhimento
createdb central_acolhimento

# 4. Restore backup
pg_restore -d central_acolhimento backup.sql

# 5. Verify data
psql -d central_acolhimento -c "SELECT COUNT(*) FROM contatos;"
```

### Complete Infrastructure Restore

```bash
# 1. Provision new Kubernetes cluster
eksctl create cluster --name central-acolhimento-prod-new

# 2. Restore database
./scripts/restore_database.sh

# 3. Deploy services
kubectl apply -f k8s/ -n central-acolhimento

# 4. Update DNS
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch '...'

# 5. Verify deployment
./scripts/verify_deployment.sh
```

## Testing and Drills

### Monthly DR Drill

**Date**: First Saturday of each month  
**Duration**: 2 hours

**Procedure**:
1. Identify test scenario (random selection)
2. Execute recovery procedure
3. Verify data integrity
4. Document results
5. Update procedures if needed

### Annual Full DR Test

**Date**: Q4 of each year  
**Duration**: 4 hours

**Procedure**:
1. Simulate complete infrastructure loss
2. Restore from scratch in new environment
3. Verify all functionality
4. Measure RTO and RPO
5. Update documentation

## Communication Plan

### Internal Notification
- **Slack**: #incidents channel
- **Email**: All team members
- **PagerDuty**: On-call engineer

### External Notification
- **Status Page**: Update status.central-acolhimento.com
- **Stakeholders**: Business team, DPO
- **Customers**: Automated email notification

### Status Page Template

```markdown
⚠️ Incident: Database connectivity issues
Status: Investigating
Affected: API service
Started: 2024-01-15 10:00 UTC
Updated: 2024-01-15 10:15 UTC

Current Status:
- Database restore in progress
- Estimated resolution: 30 minutes

Updates:
- 10:15 UTC: Restore started
- 10:00 UTC: Issue identified and investigating
```

## Post-Incident Review

### Post-Mortem Template

1. **Incident Summary**
   - What happened
   - When it happened
   - Impact (uptime, data loss)

2. **Timeline**
   - Detection time
   - Resolution time
   - Key milestones

3. **Root Cause Analysis**
   - Primary cause
   - Contributing factors

4. **Impact Assessment**
   - Data loss (if any)
   - Downtime duration
   - Users affected

5. **Remediation**
   - Immediate fixes
   - Long-term prevention
   - Action items with owners

### Example Post-Mortem

```markdown
# Post-Mortem: Database Cor坏ion Incident
Date: 2024-01-15
Duration: 45 minutes
Status: Resolved

## Summary
Database table corruption caused API downtime for 45 minutes.

## Timeline
- 10:00 UTC: First errors observed
- 10:05 UTC: Incident declared
- 10:10 UTC: Root cause identified (corrupted index)
- 10:45 UTC: Service fully restored

## Root Cause
Corrupted B-tree index in contatos table due to disk I/O error.

## Impact
- 45 minutes downtime
- 0 data loss (recovered from backup)
- ~50 users affected

## Remediation
1. Immediate: Automated index rebuild job
2. Short-term: Enhanced disk monitoring
3. Long-term: Implement database replication
```
