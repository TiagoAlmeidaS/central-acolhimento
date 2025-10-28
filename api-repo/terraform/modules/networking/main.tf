# Central de Acolhimento - Networking Module
# Cloud-agnostic networking configuration

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

# AWS Networking
resource "aws_vpc" "main" {
  count = var.cloud_provider == "aws" ? 1 : 0
  
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-vpc"
  })
}

resource "aws_internet_gateway" "main" {
  count = var.cloud_provider == "aws" ? 1 : 0
  
  vpc_id = aws_vpc.main[0].id
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-igw"
  })
}

resource "aws_subnet" "public" {
  count = var.cloud_provider == "aws" ? length(var.aws_azs) : 0
  
  vpc_id                  = aws_vpc.main[0].id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone        = var.aws_azs[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-public-subnet-${count.index + 1}"
    Type = "public"
  })
}

resource "aws_subnet" "private" {
  count = var.cloud_provider == "aws" ? length(var.aws_azs) : 0
  
  vpc_id            = aws_vpc.main[0].id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = var.aws_azs[count.index]
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-private-subnet-${count.index + 1}"
    Type = "private"
  })
}

resource "aws_route_table" "public" {
  count = var.cloud_provider == "aws" ? 1 : 0
  
  vpc_id = aws_vpc.main[0].id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main[0].id
  }
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-public-rt"
  })
}

resource "aws_route_table_association" "public" {
  count = var.cloud_provider == "aws" ? length(aws_subnet.public) : 0
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[0].id
}

# Security Groups
resource "aws_security_group" "api" {
  count = var.cloud_provider == "aws" ? 1 : 0
  
  name_prefix = "${var.project_name}-api-"
  vpc_id      = aws_vpc.main[0].id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-api-sg"
  })
}

resource "aws_security_group" "database" {
  count = var.cloud_provider == "aws" ? 1 : 0
  
  name_prefix = "${var.project_name}-db-"
  vpc_id      = aws_vpc.main[0].id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.api[0].id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-db-sg"
  })
}

# Azure Networking
resource "azurerm_virtual_network" "main" {
  count = var.cloud_provider == "azure" ? 1 : 0
  
  name                = "${var.project_name}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = var.azure_location
  resource_group_name = var.azure_rg_name
  
  tags = var.tags
}

resource "azurerm_subnet" "public" {
  count = var.cloud_provider == "azure" ? 1 : 0
  
  name                 = "${var.project_name}-public-subnet"
  resource_group_name  = var.azure_rg_name
  virtual_network_name = azurerm_virtual_network.main[0].name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "private" {
  count = var.cloud_provider == "azure" ? 1 : 0
  
  name                 = "${var.project_name}-private-subnet"
  resource_group_name  = var.azure_rg_name
  virtual_network_name = azurerm_virtual_network.main[0].name
  address_prefixes     = ["10.0.2.0/24"]
}

# GCP Networking
resource "google_compute_network" "main" {
  count = var.cloud_provider == "gcp" ? 1 : 0
  
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
  
  depends_on = [var.gcp_project_id]
}

resource "google_compute_subnetwork" "public" {
  count = var.cloud_provider == "gcp" ? 1 : 0
  
  name          = "${var.project_name}-public-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main[0].id
}

resource "google_compute_subnetwork" "private" {
  count = var.cloud_provider == "gcp" ? 1 : 0
  
  name          = "${var.project_name}-private-subnet"
  ip_cidr_range = "10.0.2.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main[0].id
}

# Outputs
output "vpc_id" {
  value = var.cloud_provider == "aws" ? aws_vpc.main[0].id : (
    var.cloud_provider == "azure" ? azurerm_virtual_network.main[0].id : 
    google_compute_network.main[0].id
  )
}

output "public_subnet_ids" {
  value = var.cloud_provider == "aws" ? aws_subnet.public[*].id : (
    var.cloud_provider == "azure" ? [azurerm_subnet.public[0].id] : 
    [google_compute_subnetwork.public[0].id]
  )
}

output "private_subnet_ids" {
  value = var.cloud_provider == "aws" ? aws_subnet.private[*].id : (
    var.cloud_provider == "azure" ? [azurerm_subnet.private[0].id] : 
    [google_compute_subnetwork.private[0].id]
  )
}

output "api_security_group_id" {
  value = var.cloud_provider == "aws" ? aws_security_group.api[0].id : null
}

output "database_security_group_id" {
  value = var.cloud_provider == "aws" ? aws_security_group.database[0].id : null
}
