# Networking Module Variables

variable "cloud_provider" {
  description = "Cloud provider to use (aws, azure, gcp)"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

# AWS specific variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = ""
}

variable "aws_azs" {
  description = "AWS availability zones"
  type        = list(string)
  default     = []
}

# Azure specific variables
variable "azure_location" {
  description = "Azure location"
  type        = string
  default     = ""
}

variable "azure_rg_name" {
  description = "Azure resource group name"
  type        = string
  default     = ""
}

# GCP specific variables
variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = ""
}

variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
