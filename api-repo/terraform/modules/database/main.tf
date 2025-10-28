# Central de Acolhimento - Database Module
# Cloud-agnostic database configuration

terraform {
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
  }
}

# Random password for database
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# AWS RDS
resource "aws_db_subnet_group" "main" {
  count = var.cloud_provider == "aws" ? 1 : 0
  
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.subnet_ids
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-db-subnet-group"
  })
}

resource "aws_db_instance" "main" {
  count = var.cloud_provider == "aws" ? 1 : 0
  
  identifier = "${var.project_name}-db"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class
  
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_allocated_storage * 2
  storage_type         = "gp2"
  storage_encrypted    = true
  
  db_name  = var.db_name
  username = var.db_username
  password = random_password.db_password.result
  
  vpc_security_group_ids = var.security_group_ids
  db_subnet_group_name   = aws_db_subnet_group.main[0].name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = var.environment == "dev" ? true : false
  deletion_protection = var.environment == "prod" ? true : false
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-db"
  })
}

# Azure PostgreSQL
resource "azurerm_postgresql_flexible_server" "main" {
  count = var.cloud_provider == "azure" ? 1 : 0
  
  name                = "${var.project_name}-db"
  resource_group_name = var.azure_rg_name
  location            = var.azure_location
  
  administrator_login    = var.db_username
  administrator_password  = random_password.db_password.result
  
  sku_name   = "GP_Standard_D2s_v3"
  version    = "15"
  storage_mb = var.db_allocated_storage * 1024
  
  backup_retention_days        = 7
  geo_redundant_backup_enabled = var.environment == "prod" ? true : false
  
  tags = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  count = var.cloud_provider == "azure" ? 1 : 0
  
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.main[0].id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# GCP Cloud SQL
resource "google_sql_database_instance" "main" {
  count = var.cloud_provider == "gcp" ? 1 : 0
  
  name             = "${var.project_name}-db"
  database_version = "POSTGRES_15"
  region           = var.gcp_region
  
  settings {
    tier = var.db_instance_class
    
    disk_size = var.db_allocated_storage
    disk_type = "PD_SSD"
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
    }
    
    ip_configuration {
      ipv4_enabled = false
      private_network = var.vpc_id
    }
  }
  
  deletion_protection = var.environment == "prod" ? true : false
  
  depends_on = [var.gcp_project_id]
}

resource "google_sql_database" "main" {
  count = var.cloud_provider == "gcp" ? 1 : 0
  
  name     = var.db_name
  instance = google_sql_database_instance.main[0].name
}

resource "google_sql_user" "main" {
  count = var.cloud_provider == "gcp" ? 1 : 0
  
  name     = var.db_username
  instance = google_sql_database_instance.main[0].name
  password = random_password.db_password.result
}

# Outputs
output "endpoint" {
  value = var.cloud_provider == "aws" ? aws_db_instance.main[0].endpoint : (
    var.cloud_provider == "azure" ? azurerm_postgresql_flexible_server.main[0].fqdn : 
    google_sql_database_instance.main[0].private_ip_address
  )
}

output "port" {
  value = var.cloud_provider == "aws" ? aws_db_instance.main[0].port : (
    var.cloud_provider == "azure" ? 5432 : 
    5432
  )
}

output "username" {
  value = var.db_username
}

output "password" {
  value     = random_password.db_password.result
  sensitive = true
}

output "database_name" {
  value = var.db_name
}
