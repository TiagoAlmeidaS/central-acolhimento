# Deployment Strategy - Cloud-Agnostic Architecture

## Overview
Esta estratégia de deployment visa evitar vendor lock-in, permitindo deployment do Central de Acolhimento em múltiplas clouds (AWS, GCP, Azure) com configuração mínima.

## Architecture Patterns

### Option A: Kubernetes (Recommended)
**Complexity**: Medium  
**Cost**: Low to Medium  
**Scalability**: High  
**Best For**: Production workloads, multiple environments

```
┌─────────────────────────────────────────────────┐
│              Kubernetes Cluster                  │
│                                                  │
│  ┌────────────┐      ┌────────────┐            │
│  │ API Pods   │◄────►│  LLM Pod   │            │
│  │ (3 replicas)│      │ (1 replica)│            │
│  └─────┬──────┘      └────────────┘            │
│        │                                        │
│        ▼                                        │
│  ┌────────────┐                                │
│  │ PostgreSQL │                                │
│  │ (Stateful) │                                │
│  └────────────┘                                │
│                                                  │
│  + Ingress (nginx)                              │
│  + Prometheus + Grafana                         │
│  + Cert-manager (TLS)                           │
└─────────────────────────────────────────────────┘
```

### Option B: Serverless/Hybrid
**Complexity**: High  
**Cost**: Low (pay per use)  
**Scalability**: High (auto-scaling)  
**Best For**: Variable workloads, cost optimization

**Components**:
- API: Containerized service (Fargate/Cloud Run)
- LLM: Long-running task (Fargate/Cloud Run - needs persistent memory)
- Database: Managed PostgreSQL (RDS/Cloud SQL)

## Platform Comparison

### AWS (EKS)
**Pros**:
- EKS (managed Kubernetes) - zero control plane maintenance
- RDS (managed PostgreSQL) - automated backups, scaling
- IAM integration - fine-grained access control
- Cost: ~$150/month (EKS + nodes + RDS)

**Cons**:
- EKS control plane costs ($0.10/hour)
- Complex networking (VPC, subnets, security groups)

### Google Cloud (GKE)
**Pros**:
- GKE autopilot - fully managed, zero node management
- Cloud SQL (managed PostgreSQL) - automated backups, HA
- Native integration with Google services
- Cost: ~$100/month (GKE Autopilot + Cloud SQL)

**Cons**:
- GKE Autopilot less flexible than standard GKE
- Egress costs higher than AWS/Azure

### Azure (AKS)
**Pros**:
- AKS free control plane (vs. EKS $72/month)
- Azure Database for PostgreSQL - managed, HA
- Azure Monitor - integrated observability
- Cost: ~$80/month (nodes + PostgreSQL)

**Cons**:
- Less mature Kubernetes integration than GKE/EKS
- Network policies more complex

**Recommendation**: **GKE Autopilot** for simplicity, **EKS** for enterprise features.

## Terraform Modules (Cloud-Agnostic)

### Module Structure
```
terraform/
├── modules/
│   ├── k8s-cluster/          # Generic K8s (abstracts EKS/GKE/AKS)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── postgres/             # Database (abstracts RDS/Cloud SQL/Azure DB)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── load-balancer/        # Ingress (abstracts AWS LB/GCP LB/Azure LB)
│   │   ├── main.tf
│   │   └── variables.tf
│   └── monitoring/           # Prometheus + Grafana
│       ├── main.tf
│       └── variables.tf
```

### K8s Cluster Module (Abstract)
```hcl
# modules/k8s-cluster/main.tf
variable "provider_name" {
  description = "Cloud provider: aws, gcp, or azure"
  type        = string
}

variable "cluster_name" {
  type = string
}

variable "region" {
  type = string
}

# AWS-specific
resource "aws_eks_cluster" "main" {
  count = var.provider_name == "aws" ? 1 : 0
  name  = var.cluster_name
  # ... AWS-specific config
}

# GCP-specific
resource "google_container_cluster" "main" {
  count    = var.provider_name == "gcp" ? 1 : 0
  name     = var.cluster_name
  location = var.region
  # ... GCP-specific config
}

# Azure-specific
resource "azurerm_kubernetes_cluster" "main" {
  count               = var.provider_name == "azure" ? 1 : 0
  name                = var.cluster_name
  resource_group_name = var.resource_group_name
  # ... Azure-specific config
}
```

## Deployment Pipeline

### CI/CD (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main, develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v3
    
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v3
    
    - name: Terraform Apply
      env:
        TF_VAR_cloud_provider: ${{ secrets.CLOUD_PROVIDER }}
        TF_VAR_cluster_name: central-acolhimento
      run: |
        terraform init
        terraform plan
        terraform apply -auto-approve
    
    - name: Build and Push Docker
      run: |
        docker build -t $REGISTRY/api:$GITHUB_SHA ./api
        docker push $REGISTRY/api:$GITHUB_SHA
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/api api=$REGISTRY/api:$GITHUB_SHA
        kubectl rollout status deployment/api
```

## Cost Comparison

| Component | AWS (EKS) | GCP (GKE Autopilot) | Azure (AKS) |
|-----------|-----------|---------------------|-------------|
| Control Plane | $72/month | Free | Free |
| Nodes (3x e2-medium) | $60/month | $60/month | $50/month |
| PostgreSQL (managed) | $100/month (RDS) | $80/month (Cloud SQL) | $70/month (Azure DB) |
| Load Balancer | $15/month | $15/month | $20/month |
| Storage | $10/month | $8/month | $12/month |
| **Total** | **~$257/month** | **~$163/month** | **~$152/month** |

**Winner**: Azure AKS (lowest cost), **GKE Autopilot** (ease of use)

## Scalability Considerations

### Horizontal Pod Autoscaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Database Scaling
- **Read Replicas**: PostgreSQL replicas for read-heavy workloads
- **Vertical Scaling**: Upgrade instance type (CPU/memory)
- **Connection Pooling**: SQLAlchemy pool_size=10, max_overflow=20

## Migration Path

### Phase 1: Local Development
- Docker Compose
- SQLite database
- Ollama LLM local

### Phase 2: Cloud Development
- Kubernetes cluster (dev environment)
- Managed PostgreSQL
- Deploy API and LLM as K8s deployments

### Phase 3: Production
- Kubernetes cluster (prod environment)
- High-availability PostgreSQL (multi-AZ)
- Auto-scaling, monitoring, backups

## Backup and Disaster Recovery

### Database Backups
```yaml
# CronJob for daily backups
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: pg-backup
            image: postgres:15
            command:
            - /bin/sh
            - -c
            - |
              pg_dump $DATABASE_URL > /backup/backup-$(date +%Y%m%d).sql
              aws s3 cp /backup/backup-$(date +%Y%m%d).sql s3://backup-bucket/
```

### Disaster Recovery Plan
1. **RTO (Recovery Time Objective)**: < 1 hour
2. **RPO (Recovery Point Objective)**: < 15 minutes
3. **Backup Retention**: 90 days
4. **Testing**: Monthly restore drills

## Security Hardening

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: llm
    - podSelector:
        matchLabels:
          app: postgres
```

### TLS/SSL
- **Cert-Manager**: Automated TLS certificates (Let's Encrypt)
- **Ingress TLS**: HTTPS-only traffic
- **mTLS**: Mutual TLS for inter-service communication (Istio optional)

## Monitoring and Observability

### Prometheus + Grafana
- **Metrics**: API latency, LLM processing time, DB query duration
- **Dashboards**: Request rate, error rate, availability
- **Alerts**: High error rate, LLM downtime, slow queries

### Logging
- **Centralized Logging**: Fluentd → ELK, Loki, or cloud logging (CloudWatch, Stackdriver, Log Analytics)
- **Log Aggregation**: JSON structured logs from all services

## References

- `terraform/` - Terraform modules and configurations
- `k8s/` - Kubernetes manifests
- `docs/infrastructure/kubernetes/` - K8s-specific guides
- `docs/infrastructure/terraform/` - IaC documentation
