# Central de Acolhimento - Infrastructure as Code
# Cloud-agnostic Terraform configuration

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

# Local variables for environment configuration
locals {
  environment = var.environment
  project_name = "central-acolhimento"
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "terraform"
    Repository  = "central-acolhimento"
  }
}

# Data sources
data "aws_availability_zones" "available" {
  count = var.cloud_provider == "aws" ? 1 : 0
  state = "available"
}

data "azurerm_client_config" "current" {
  count = var.cloud_provider == "azure" ? 1 : 0
}

# VPC/Network Module
module "networking" {
  source = "./modules/networking"
  
  cloud_provider = var.cloud_provider
  environment    = local.environment
  project_name   = local.project_name
  
  # AWS specific
  aws_region     = var.aws_region
  aws_azs        = var.cloud_provider == "aws" ? data.aws_availability_zones.available[0].names : []
  
  # Azure specific
  azure_location = var.azure_location
  azure_rg_name  = var.azure_rg_name
  
  # GCP specific
  gcp_region     = var.gcp_region
  gcp_project_id = var.gcp_project_id
  
  tags = local.common_tags
}

# Database Module
module "database" {
  source = "./modules/database"
  
  cloud_provider = var.cloud_provider
  environment    = local.environment
  project_name   = local.project_name
  
  # Network configuration
  vpc_id         = module.networking.vpc_id
  subnet_ids     = module.networking.private_subnet_ids
  security_group_ids = [module.networking.database_security_group_id]
  
  # Database configuration
  db_instance_class = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_name         = var.db_name
  db_username     = var.db_username
  
  tags = local.common_tags
}

# Kubernetes Cluster Module
module "kubernetes" {
  source = "./modules/kubernetes"
  
  cloud_provider = var.cloud_provider
  environment    = local.environment
  project_name   = local.project_name
  
  # Network configuration
  vpc_id         = module.networking.vpc_id
  subnet_ids     = module.networking.public_subnet_ids
  
  # Cluster configuration
  node_count     = var.k8s_node_count
  node_instance_type = var.k8s_node_instance_type
  
  tags = local.common_tags
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"
  
  cloud_provider = var.cloud_provider
  environment    = local.environment
  project_name   = local.project_name
  
  # Kubernetes configuration
  cluster_endpoint = module.kubernetes.cluster_endpoint
  cluster_ca_certificate = module.kubernetes.cluster_ca_certificate
  
  tags = local.common_tags
}

# Outputs
output "cluster_endpoint" {
  value = module.kubernetes.cluster_endpoint
}

output "cluster_ca_certificate" {
  value = module.kubernetes.cluster_ca_certificate
  sensitive = true
}

output "database_endpoint" {
  value = module.database.endpoint
  sensitive = true
}

output "monitoring_endpoint" {
  value = module.monitoring.grafana_endpoint
}
