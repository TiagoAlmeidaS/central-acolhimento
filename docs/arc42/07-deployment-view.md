# 7. Deployment View

## 7.1 Target Deployment Platforms

### Development Environment (Local)
- **Purpose**: Development, testing, debugging
- **Setup**: Docker Compose
- **Components**:
  - FastAPI app (hot-reload enabled)
  - Ollama LLM service (llama3:8b)
  - SQLite database (file-based)

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./dev.db
      - LLM_URL=http://llm:11434
    volumes:
      - ./api:/app
      - ./dev.db:/app/dev.db
  
  llm:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: >
      sh -c "ollama pull llama3:8b && ollama serve"
```

### Production Environment (Cloud-Agnostic)

#### Option A: Kubernetes Deployment (Recommended)
- **Platform**: Any Kubernetes cluster (EKS, GKE, AKS, or on-premise)
- **Orchestration**: Kubernetes with Helm charts
- **Components**:
  - API Deployment (3 replicas)
  - LLM Deployment (1 replica, StatefulSet with PVC for model storage)
  - PostgreSQL database (managed service or StatefulSet)
  - Ingress (nginx-ingress or cloud LB)
  - Service Monitor (Prometheus)

#### Option B: Serverless Deployment (Alternative)
- **Platform**: AWS Lambda + Fargate, Google Cloud Functions + Cloud Run, Azure Functions + Container Apps
- **Components**:
  - API as containerized microservice (Fargate/Cloud Run)
  - LLM as long-running task (Fargate/Cloud Run - not serverless-compatible due to model size)
  - PostgreSQL as managed service (RDS, Cloud SQL, Azure Database)
  - API Gateway for routing

#### Option C: Hybrid Deployment
- **Components**:
  - API: Kubernetes pods (scales with traffic)
  - LLM: Long-running container in Fargate/Cloud Run (persistent GPU/memory)
  - Database: Managed PostgreSQL (RDS, Cloud SQL, Azure Database)

## 7.2 Kubernetes Deployment (Recommended)

### Namespace Structure
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: central-acolhimento
```

### API Deployment
```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: central-acolhimento
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: your-registry/central-acolhimento-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: LLM_URL
          value: "http://llm-service:11434"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: central-acolhimento
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### LLM Deployment (StatefulSet with Persistent Storage)
```yaml
# k8s/llm-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: llm
  namespace: central-acolhimento
spec:
  serviceName: llm-service
  replicas: 1  # Single replica (GPU constraints)
  selector:
    matchLabels:
      app: llm
  template:
    metadata:
      labels:
        app: llm
    spec:
      containers:
      - name: ollama
        image: ollama/ollama
        ports:
        - containerPort: 11434
        volumeMounts:
        - name: model-storage
          mountPath: /root/.ollama
        env:
        - name: OLLAMA_HOST
          value: "0.0.0.0:11434"
        resources:
          requests:
            memory: "12Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
        lifecycle:
          postStart:
            exec:
              command: ["/bin/sh", "-c", "ollama pull llama3:8b"]
  volumeClaimTemplates:
  - metadata:
      name: model-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi

---
apiVersion: v1
kind: Service
metadata:
  name: llm-service
  namespace: central-acolhimento
spec:
  selector:
    app: llm
  ports:
  - port: 11434
    targetPort: 11434
  type: ClusterIP
```

### Ingress (External Access)
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  namespace: central-acolhimento
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.central-acolhimento.com
    secretName: api-tls
  rules:
  - host: api.central-acolhimento.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
```

### Database (Managed Service or StatefulSet)
```yaml
# k8s/postgres-statefulset.yaml (Alternative to managed service)
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: central-acolhimento
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: central_acolhimento
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

## 7.3 Cloud-Specific Configurations

### AWS EKS Deployment
```hcl
# terraform/modules/eks/main.tf
resource "aws_eks_cluster" "main" {
  name     = "central-acolhimento"
  role_arn = aws_iam_role.cluster.arn
  
  vpc_config {
    subnet_ids              = module.vpc.private_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = true
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.cluster,
    aws_iam_role_policy_attachment.service,
  ]
}
```

### Google Cloud GKE Deployment
```hcl
# terraform/modules/gke/main.tf
resource "google_container_cluster" "main" {
  name     = "central-acolhimento"
  location = var.region
  
  node_config {
    machine_type = "e2-standard-4"
    disk_size_gb = 30
  }
  
  network    = module.vpc.network_name
  subnetwork = module.vpc.subnet_name
}
```

### Azure AKS Deployment
```hcl
# terraform/modules/aks/main.tf
resource "azurerm_kubernetes_cluster" "main" {
  name                = "central-acolhimento"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "central-acolhimento"
  
  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_D2s_v3"
  }
  
  network_profile {
    network_plugin = "azure"
  }
}
```

## 7.4 Infrastructure as Code (Terraform)

### Project Structure
```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf          # Dev-specific overrides
│   │   └── variables.tf
│   ├── staging/
│   │   ├── main.tf
│   │   └── variables.tf
│   └── prod/
│       ├── main.tf
│       └── variables.tf
├── modules/
│   ├── k8s-cluster/          # Generic K8s (works on AWS/GCP/Azure)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── postgres/             # Database (cloud-agnostic)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── load-balancer/        # Cloud LB abstraction
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/           # Prometheus + Grafana
│       ├── main.tf
│       └── variables.tf
├── main.tf
├── variables.tf
├── outputs.tf
└── versions.tf
```

### Main Terraform Configuration
```hcl
# terraform/main.tf
module "k8s_cluster" {
  source = "./modules/k8s-cluster"
  
  cluster_name = var.cluster_name
  region       = var.region
  environment  = var.environment
  
  # Cloud provider abstraction
  provider_name = var.cloud_provider  # "aws", "gcp", "azure"
}

module "postgres" {
  source = "./modules/postgres"
  
  name        = "central-acolhimento-db"
  environment = var.environment
  
  # Cloud-agnostic database configuration
  provider_name = var.cloud_provider
  region        = var.region
  instance_type = var.db_instance_type
}

module "monitoring" {
  source = "./modules/monitoring"
  
  namespace     = "monitoring"
  environment   = var.environment
  enable_tracing = false  # Future: OpenTelemetry
}
```

## 7.5 Deployment Pipeline (CI/CD)

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main, develop]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build API Docker image
      run: |
        docker build -t ${{ secrets.REGISTRY }}/central-acolhimento-api:${{ github.sha }} ./api
        docker push ${{ secrets.REGISTRY }}/central-acolhimento-api:${{ github.sha }}
    
    - name: Build LLM Docker image
      run: |
        docker build -t ${{ secrets.REGISTRY }}/central-acolhimento-llm:${{ github.sha }} ./llm
        docker push ${{ secrets.REGISTRY }}/central-acolhimento-llm:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      env:
        KUBECONFIG: ${{ secrets.KUBECONFIG }}
      run: |
        # Update image tags in K8s manifests
        sed -i "s|latest|${{ github.sha }}|g" k8s/*.yaml
        
        # Apply manifests
        kubectl apply -f k8s/ -n central-acolhimento
        
        # Wait for rollout
        kubectl rollout status deployment/api -n central-acolhimento
        kubectl rollout status statefulset/llm -n central-acolhimento
```

## 7.6 Deployment Strategies

### Rolling Update (Default)
- **Strategy**: Gradual replacement of old pods with new pods
- **Benefit**: Zero downtime
- **Configuration**: `spec.strategy.type: RollingUpdate`

### Blue/Green Deployment (Optional)
- **Strategy**: Deploy new version alongside old version, switch traffic
- **Benefit**: Instant rollback capability
- **Complexity**: Requires traffic routing (Ingress, Istio)

### Canary Deployment (Optional, Future)
- **Strategy**: Gradually increase traffic to new version
- **Benefit**: Test new version with fraction of traffic
- **Requirements**: Service mesh (Istio) or advanced Ingress

## 7.7 Monitoring & Observability in Deployment

### Prometheus ServiceMonitor
```yaml
# k8s/monitoring/prometheus-servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: api-metrics
  namespace: central-acolhimento
spec:
  selector:
    matchLabels:
      app: api
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### Grafana Dashboard
```yaml
# k8s/monitoring/grafana-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard-central-acolhimento
  namespace: monitoring
data:
  dashboard.json: |
    {
      "title": "Central de Acolhimento API",
      "panels": [
        {
          "title": "Request Rate",
          "targets": [
            {"expr": "rate(http_requests_total{job='api'}[5m])"}
          ]
        },
        {
          "title": "LLM Latency",
          "targets": [
            {"expr": "histogram_quantile(0.95, llm_request_duration_seconds)"}
          ]
        }
      ]
    }
```

## 7.8 Environment Variables & Secrets

### Secrets Management
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: central-acolhimento
type: Opaque
data:
  url: <base64-encoded-postgres-url>
  user: <base64-encoded-username>
  password: <base64-encoded-password>

---
# In production, use external secret manager
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: central-acolhimento
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: db-credentials
    creationPolicy: Owner
  data:
  - secretKey: url
    remoteRef:
      key: central-acolhimento/db-url
  - secretKey: user
    remoteRef:
      key: central-acolhimento/db-user
  - secretKey: password
    remoteRef:
      key: central-acolhimento/db-password
```

## 7.9 Network Architecture

### Internal Communication (Service Mesh Optional)
```
┌───────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                 │
│                                                       │
│  ┌──────────────┐         ┌──────────────┐         │
│  │  Ingress     │◄────────│   External    │         │
│  │  (nginx)     │         │   Users       │         │
│  └──────┬───────┘         └───────────────┘         │
│         │                                           │
│         ▼                                           │
│  ┌──────────────┐                                  │
│  │  API Pods    │──Internal──►│  LLM Pod   │       │
│  │  (3 replicas)│             │  (1 replica)│       │
│  └──────┬───────┘             └────────────┘       │
│         │                                           │
│         ▼                                           │
│  ┌──────────────┐                                  │
│  │  PostgreSQL  │                                  │
│  │  Service     │                                  │
│  └──────────────┘                                  │
└───────────────────────────────────────────────────────┘
```

### Service Discovery
- **API → LLM**: Via Kubernetes Service DNS (`llm-service.central-acolhimento.svc.cluster.local:11434`)
- **API → Database**: Via PostgreSQL Service DNS
- **External → API**: Via Ingress hostname (`api.central-acolhimento.com`)

## 7.10 Scalability Considerations

### Horizontal Pod Autoscaling (HPA)
```yaml
# k8s/autoscaling/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: central-acolhimento
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
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### LLM Scaling Constraints
- **Single Replica**: LLM typically runs as single pod due to GPU/memory constraints
- **Alternative**: Vertical scaling (larger VM) or queue-based processing (Celery + Redis)

## 7.11 Backup & Disaster Recovery

### Database Backup
```yaml
# k8s/backup/cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
  namespace: central-acolhimento
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
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
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: url
          volumes:
          - name: backup-storage
            emptyDir: {}
          restartPolicy: OnFailure
```

### Disaster Recovery Plan
1. **RTO (Recovery Time Objective)**: < 1 hour
2. **RPO (Recovery Point Objective)**: < 15 minutes (transactional replication)
3. **Backup Strategy**: Daily full backups, 6-hourly incrementals
4. **Restore Procedure**: Documented in `docs/operations/disaster-recovery.md`

## 7.12 Cost Optimization

### Resource Requests/Limits
- **API**: Conservative limits (256Mi RAM, 100m CPU) to enable more replicas
- **LLM**: Larger limits (12Gi RAM, 4 CPUs) required for model
- **Database**: Managed service vs self-hosted trade-off analyzed per cloud provider

### Spot Instances (Cost Reduction)
- **LLM Pod**: Use spot instances for development/staging (not recommended for production)
- **Worker Nodes**: Mixed spot + on-demand for cost optimization

## 7.13 Security in Deployment

### Network Policies
```yaml
# k8s/security/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: central-acolhimento
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
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: llm
    ports:
    - protocol: TCP
      port: 11434
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### Pod Security Standards
```yaml
# k8s/security/psa.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: central-acolhimento
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```
