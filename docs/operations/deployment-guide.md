# Central de Acolhimento - Deployment Guide
# Complete guide for deploying the system

## Overview

This guide provides step-by-step instructions for deploying the Central de Acolhimento system across different environments and cloud providers.

## Prerequisites

### Required Tools
- **Terraform** >= 1.6.0
- **kubectl** >= 1.28.0
- **Helm** >= 3.12.0
- **Docker** >= 20.10.0
- **AWS CLI** >= 2.0.0 (for AWS deployment)
- **Azure CLI** >= 2.0.0 (for Azure deployment)
- **gcloud CLI** >= 400.0.0 (for GCP deployment)

### Required Access
- Cloud provider account with appropriate permissions
- Kubernetes cluster access
- Container registry access (GitHub Container Registry recommended)

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/central-acolhimento.git
cd central-acolhimento
```

### 2. Configure Environment Variables
```bash
# Copy example environment files
cp api-repo/.env.example api-repo/.env
cp llm-repo/.env.example llm-repo/.env

# Edit environment files with your configuration
nano api-repo/.env
nano llm-repo/.env
```

### 3. Set Up Secrets
```bash
# Create GitHub secrets for CI/CD
gh secret set AWS_ACCESS_KEY_ID --body "your-aws-access-key"
gh secret set AWS_SECRET_ACCESS_KEY --body "your-aws-secret-key"
gh secret set GITHUB_TOKEN --body "your-github-token"
```

## Infrastructure Deployment

### AWS Deployment

#### 1. Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

#### 2. Deploy Infrastructure
```bash
cd api-repo/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="cloud_provider=aws" -var="environment=prod" -out=tfplan

# Apply infrastructure
terraform apply tfplan
```

#### 3. Configure kubectl
```bash
aws eks update-kubeconfig --region us-east-1 --name central-acolhimento-prod
```

### Azure Deployment

#### 1. Configure Azure CLI
```bash
az login
az account set --subscription "your-subscription-id"
```

#### 2. Deploy Infrastructure
```bash
cd api-repo/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="cloud_provider=azure" -var="environment=prod" -out=tfplan

# Apply infrastructure
terraform apply tfplan
```

#### 3. Configure kubectl
```bash
az aks get-credentials --resource-group central-acolhimento-rg --name central-acolhimento-prod
```

### GCP Deployment

#### 1. Configure gcloud CLI
```bash
gcloud auth login
gcloud config set project your-project-id
```

#### 2. Deploy Infrastructure
```bash
cd api-repo/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="cloud_provider=gcp" -var="environment=prod" -out=tfplan

# Apply infrastructure
terraform apply tfplan
```

#### 3. Configure kubectl
```bash
gcloud container clusters get-credentials central-acolhimento-prod --region us-central1
```

## Kubernetes Deployment

### 1. Install Required Components

#### Install NGINX Ingress Controller
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

#### Install Cert-Manager
```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.0 \
  --set installCRDs=true
```

#### Install Prometheus Operator
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin123
```

### 2. Deploy Application

#### Deploy Core Services
```bash
# Apply Kubernetes manifests
kubectl apply -f api-repo/k8s/central-acolhimento.yaml
kubectl apply -f api-repo/k8s/ingress.yaml
kubectl apply -f api-repo/k8s/monitoring.yaml
kubectl apply -f api-repo/k8s/grafana.yaml
```

#### Verify Deployment
```bash
# Check pod status
kubectl get pods -n central-acolhimento

# Check service status
kubectl get services -n central-acolhimento

# Check ingress status
kubectl get ingress -n central-acolhimento
```

### 3. Configure DNS

#### Update DNS Records
```bash
# Get LoadBalancer IP
kubectl get service ingress-nginx-controller -n ingress-nginx

# Update DNS records to point to LoadBalancer IP
# api.central-acolhimento.com -> LoadBalancer IP
# llm.central-acolhimento.com -> LoadBalancer IP
# grafana.central-acolhimento.com -> LoadBalancer IP
```

## Application Configuration

### 1. Database Setup

#### Run Migrations
```bash
# Get database pod name
kubectl get pods -n central-acolhimento -l app=postgres

# Run Alembic migrations
kubectl exec -it postgres-deployment-xxx -n central-acolhimento -- \
  alembic upgrade head
```

#### Verify Database
```bash
# Connect to database
kubectl exec -it postgres-deployment-xxx -n central-acolhimento -- \
  psql -U postgres -d central_acolhimento

# Check tables
\dt
```

### 2. LLM Service Setup

#### Download Ollama Model
```bash
# Get Ollama pod name
kubectl get pods -n central-acolhimento -l app=ollama

# Download llama3:8b model
kubectl exec -it ollama-deployment-xxx -n central-acolhimento -- \
  ollama pull llama3:8b
```

#### Verify LLM Service
```bash
# Test LLM service
kubectl port-forward service/llm-service 8000:8000 -n central-acolhimento

# In another terminal
curl http://localhost:8000/health
```

## Monitoring Setup

### 1. Access Grafana
```bash
# Port forward to Grafana
kubectl port-forward service/grafana-service 3000:3000 -n monitoring

# Access Grafana at http://localhost:3000
# Username: admin
# Password: admin123
```

### 2. Configure Dashboards
- Import Central de Acolhimento dashboard
- Configure alerting rules
- Set up notification channels

### 3. Verify Monitoring
```bash
# Check Prometheus targets
kubectl port-forward service/prometheus-service 9090:9090 -n monitoring

# Access Prometheus at http://localhost:9090
# Check targets are UP
```

## Testing Deployment

### 1. Health Checks
```bash
# Test API health
curl https://api.central-acolhimento.com/health

# Test LLM health
curl https://llm.central-acolhimento.com/health

# Test Grafana
curl https://grafana.central-acolhimento.com/api/health
```

### 2. Functional Tests
```bash
# Test API endpoints
curl -X POST https://api.central-acolhimento.com/contatos/ \
  -H "Content-Type: application/json" \
  -d '{"texto_livre": "João Silva, telefone 11-99999-1111, motivo: suporte"}'

# Test LLM endpoints
curl -X POST https://llm.central-acolhimento.com/mcp/extract \
  -H "Content-Type: application/json" \
  -d '{"texto": "João Silva, telefone 11-99999-1111, motivo: suporte"}'
```

### 3. Load Testing
```bash
# Install hey (load testing tool)
go install github.com/rakyll/hey@latest

# Run load test
hey -n 1000 -c 10 https://api.central-acolhimento.com/health
```

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting
```bash
# Check pod logs
kubectl logs -f deployment/api-deployment -n central-acolhimento

# Check pod events
kubectl describe pod api-deployment-xxx -n central-acolhimento
```

#### 2. Database Connection Issues
```bash
# Check database logs
kubectl logs -f deployment/postgres-deployment -n central-acolhimento

# Test database connectivity
kubectl exec -it api-deployment-xxx -n central-acolhimento -- \
  python -c "import psycopg2; print('DB connection OK')"
```

#### 3. LLM Service Issues
```bash
# Check LLM logs
kubectl logs -f deployment/llm-deployment -n central-acolhimento

# Check Ollama logs
kubectl logs -f deployment/ollama-deployment -n central-acolhimento
```

#### 4. Ingress Issues
```bash
# Check ingress controller logs
kubectl logs -f deployment/ingress-nginx-controller -n ingress-nginx

# Check ingress status
kubectl describe ingress central-acolhimento-ingress -n central-acolhimento
```

### Performance Optimization

#### 1. Resource Tuning
```bash
# Check resource usage
kubectl top pods -n central-acolhimento

# Adjust resource limits in manifests if needed
```

#### 2. Scaling
```bash
# Scale API deployment
kubectl scale deployment api-deployment --replicas=5 -n central-acolhimento

# Scale LLM deployment
kubectl scale deployment llm-deployment --replicas=3 -n central-acolhimento
```

## Maintenance

### 1. Backup Strategy
```bash
# Database backup
kubectl exec -it postgres-deployment-xxx -n central-acolhimento -- \
  pg_dump -U postgres central_acolhimento > backup.sql

# Volume snapshots
kubectl get pvc -n central-acolhimento
# Create snapshots using cloud provider tools
```

### 2. Updates
```bash
# Update application images
kubectl set image deployment/api-deployment api=central-acolhimento-api:new-tag -n central-acolhimento

# Update infrastructure
cd api-repo/terraform
terraform plan -var="environment=prod" -out=tfplan
terraform apply tfplan
```

### 3. Monitoring
- Check Grafana dashboards regularly
- Monitor Prometheus alerts
- Review application logs
- Check resource usage trends

## Security Considerations

### 1. Network Security
- Use security groups/firewall rules
- Enable VPC flow logs
- Implement network policies

### 2. Application Security
- Use HTTPS everywhere
- Implement proper authentication
- Regular security updates
- Container image scanning

### 3. Data Security
- Encrypt data at rest
- Encrypt data in transit
- Regular backups
- Access logging

## Support

For issues and questions:
- Check the troubleshooting section
- Review application logs
- Check monitoring dashboards
- Contact the development team

## Next Steps

After successful deployment:
1. Set up monitoring alerts
2. Configure backup schedules
3. Implement disaster recovery procedures
4. Plan for scaling and optimization
5. Schedule regular maintenance windows
