# Variables for Central de Acolhimento Infrastructure

variable "cloud_provider" {
  description = "Cloud provider to use (aws, azure, gcp)"
  type        = string
  default     = "aws"
  validation {
    condition     = contains(["aws", "azure", "gcp"], var.cloud_provider)
    error_message = "Cloud provider must be one of: aws, azure, gcp."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

# AWS Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# Azure Configuration
variable "azure_location" {
  description = "Azure location"
  type        = string
  default     = "East US"
}

variable "azure_rg_name" {
  description = "Azure resource group name"
  type        = string
  default     = "central-acolhimento-rg"
}

# GCP Configuration
variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
  default     = ""
}

# Database Configuration
variable "db_instance_class" {
  description = "Database instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Database allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "central_acolhimento"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "postgres"
}

# Kubernetes Configuration
variable "k8s_node_count" {
  description = "Number of Kubernetes nodes"
  type        = number
  default     = 2
}

variable "k8s_node_instance_type" {
  description = "Kubernetes node instance type"
  type        = string
  default     = "t3.medium"
}
