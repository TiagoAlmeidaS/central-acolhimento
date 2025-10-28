# Central de Acolhimento - Deployment Diagrams
# Mermaid diagrams for deployment visualization

## System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Browser]
        MOBILE[Mobile App]
        API_CLIENT[API Client]
    end
    
    subgraph "Load Balancer"
        LB[NGINX Ingress Controller]
    end
    
    subgraph "Application Layer"
        subgraph "API Service"
            API1[API Pod 1]
            API2[API Pod 2]
            API3[API Pod 3]
        end
        
        subgraph "LLM Service"
            LLM1[LLM Pod 1]
            LLM2[LLM Pod 2]
        end
        
        subgraph "Ollama Service"
            OLLAMA[Ollama Pod]
        end
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL)]
        PVC[Persistent Volumes]
    end
    
    subgraph "Monitoring Layer"
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
        ALERTS[AlertManager]
    end
    
    WEB --> LB
    MOBILE --> LB
    API_CLIENT --> LB
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> LLM1
    API2 --> LLM2
    API3 --> LLM1
    
    LLM1 --> OLLAMA
    LLM2 --> OLLAMA
    
    API1 --> DB
    API2 --> DB
    API3 --> DB
    
    OLLAMA --> PVC
    DB --> PVC
    
    PROMETHEUS --> API1
    PROMETHEUS --> API2
    PROMETHEUS --> API3
    PROMETHEUS --> LLM1
    PROMETHEUS --> LLM2
    PROMETHEUS --> OLLAMA
    
    GRAFANA --> PROMETHEUS
    ALERTS --> PROMETHEUS
```

## Kubernetes Cluster Architecture

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Control Plane"
            MASTER[Master Node]
            ETCD[etcd]
            API_SERVER[API Server]
            SCHEDULER[Scheduler]
            CONTROLLER[Controller Manager]
        end
        
        subgraph "Worker Nodes"
            NODE1[Worker Node 1]
            NODE2[Worker Node 2]
            NODE3[Worker Node 3]
        end
        
        subgraph "Networking"
            CNI[CNI Plugin]
            DNS[CoreDNS]
            SERVICE[Service Mesh]
        end
        
        subgraph "Storage"
            PV[Persistent Volumes]
            PVC[Persistent Volume Claims]
            STORAGE[Storage Classes]
        end
        
        subgraph "Monitoring"
            METRICS[Metrics Server]
            PROMETHEUS[Prometheus]
            GRAFANA[Grafana]
        end
    end
    
    MASTER --> NODE1
    MASTER --> NODE2
    MASTER --> NODE3
    
    NODE1 --> CNI
    NODE2 --> CNI
    NODE3 --> CNI
    
    CNI --> DNS
    CNI --> SERVICE
    
    NODE1 --> PV
    NODE2 --> PV
    NODE3 --> PV
    
    PV --> PVC
    PVC --> STORAGE
    
    METRICS --> NODE1
    METRICS --> NODE2
    METRICS --> NODE3
    
    PROMETHEUS --> METRICS
    GRAFANA --> PROMETHEUS
```

## CI/CD Pipeline Flow

```mermaid
graph LR
    subgraph "Source Control"
        GIT[Git Repository]
        PR[Pull Request]
        MAIN[Main Branch]
        DEV[Develop Branch]
    end
    
    subgraph "CI/CD Pipeline"
        TRIGGER[GitHub Actions]
        TEST_API[API Tests]
        TEST_LLM[LLM Tests]
        BUILD[Build Images]
        PUSH[Push to Registry]
        DEPLOY_DEV[Deploy to Dev]
        DEPLOY_PROD[Deploy to Prod]
    end
    
    subgraph "Infrastructure"
        TERRAFORM[Terraform]
        K8S[Kubernetes]
        MONITORING[Monitoring]
    end
    
    subgraph "Environments"
        DEV_ENV[Development]
        PROD_ENV[Production]
    end
    
    GIT --> TRIGGER
    PR --> TRIGGER
    MAIN --> TRIGGER
    DEV --> TRIGGER
    
    TRIGGER --> TEST_API
    TRIGGER --> TEST_LLM
    
    TEST_API --> BUILD
    TEST_LLM --> BUILD
    
    BUILD --> PUSH
    PUSH --> DEPLOY_DEV
    PUSH --> DEPLOY_PROD
    
    DEPLOY_DEV --> DEV_ENV
    DEPLOY_PROD --> PROD_ENV
    
    TERRAFORM --> K8S
    K8S --> MONITORING
    
    DEV_ENV --> MONITORING
    PROD_ENV --> MONITORING
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant LLM
    participant Ollama
    participant DB
    participant Monitor
    
    Client->>API: POST /contatos (texto_livre)
    API->>LLM: POST /mcp/extract
    LLM->>Ollama: Generate response
    Ollama-->>LLM: Extracted entities
    LLM-->>API: Structured data
    API->>DB: INSERT contato
    DB-->>API: Success
    API-->>Client: 201 Created
    
    Note over API,Monitor: Metrics collection
    API->>Monitor: Prometheus metrics
    LLM->>Monitor: Prometheus metrics
    Ollama->>Monitor: Prometheus metrics
    
    Note over Client,Monitor: Health checks
    Client->>API: GET /health
    API-->>Client: 200 OK
    Client->>LLM: GET /health
    LLM-->>Client: 200 OK
```

## Security Architecture

```mermaid
graph TB
    subgraph "External Security"
        WAF[Web Application Firewall]
        DDoS[DDoS Protection]
        SSL[SSL/TLS Termination]
    end
    
    subgraph "Network Security"
        VPC[Virtual Private Cloud]
        SG[Security Groups]
        NACL[Network ACLs]
        VPN[VPN Gateway]
    end
    
    subgraph "Application Security"
        RBAC[Role-Based Access Control]
        JWT[JWT Tokens]
        CORS[CORS Policy]
        RATE[Rate Limiting]
    end
    
    subgraph "Data Security"
        ENCRYPTION[Data Encryption]
        BACKUP[Backup Encryption]
        AUDIT[Audit Logging]
        SECRETS[Secrets Management]
    end
    
    subgraph "Monitoring Security"
        SIEM[SIEM System]
        ALERTS[Security Alerts]
        LOGS[Security Logs]
        COMPLIANCE[Compliance Checks]
    end
    
    WAF --> VPC
    DDoS --> VPC
    SSL --> VPC
    
    VPC --> SG
    VPC --> NACL
    VPC --> VPN
    
    SG --> RBAC
    NACL --> RBAC
    VPN --> RBAC
    
    RBAC --> JWT
    RBAC --> CORS
    RBAC --> RATE
    
    JWT --> ENCRYPTION
    CORS --> ENCRYPTION
    RATE --> ENCRYPTION
    
    ENCRYPTION --> BACKUP
    ENCRYPTION --> AUDIT
    ENCRYPTION --> SECRETS
    
    BACKUP --> SIEM
    AUDIT --> SIEM
    SECRETS --> SIEM
    
    SIEM --> ALERTS
    SIEM --> LOGS
    SIEM --> COMPLIANCE
```

## Disaster Recovery Architecture

```mermaid
graph TB
    subgraph "Primary Region"
        PRIMARY[Primary Cluster]
        PRIMARY_DB[(Primary DB)]
        PRIMARY_BACKUP[Primary Backup]
    end
    
    subgraph "Secondary Region"
        SECONDARY[Secondary Cluster]
        SECONDARY_DB[(Secondary DB)]
        SECONDARY_BACKUP[Secondary Backup]
    end
    
    subgraph "Backup Strategy"
        SCHEDULED[Scheduled Backups]
        CONTINUOUS[Continuous Replication]
        SNAPSHOTS[Volume Snapshots]
    end
    
    subgraph "Recovery Process"
        FAILOVER[Automatic Failover]
        RESTORE[Data Restore]
        VALIDATION[Recovery Validation]
    end
    
    subgraph "Monitoring"
        HEALTH[Health Checks]
        ALERTS[Disaster Alerts]
        NOTIFICATIONS[Recovery Notifications]
    end
    
    PRIMARY --> PRIMARY_DB
    PRIMARY_DB --> PRIMARY_BACKUP
    
    SECONDARY --> SECONDARY_DB
    SECONDARY_DB --> SECONDARY_BACKUP
    
    PRIMARY_BACKUP --> SCHEDULED
    PRIMARY_DB --> CONTINUOUS
    PRIMARY --> SNAPSHOTS
    
    SCHEDULED --> SECONDARY_BACKUP
    CONTINUOUS --> SECONDARY_DB
    SNAPSHOTS --> SECONDARY
    
    HEALTH --> FAILOVER
    ALERTS --> FAILOVER
    
    FAILOVER --> RESTORE
    RESTORE --> VALIDATION
    
    VALIDATION --> NOTIFICATIONS
    HEALTH --> NOTIFICATIONS
    ALERTS --> NOTIFICATIONS
```
