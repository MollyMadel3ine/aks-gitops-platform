#variables.tf 

variable "resource_group_name" {
  description = "Name of the resource group for all cluster resources"
  type        = string
  default     = "rg-aks-gitops"
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "westus2"
}

variable "cluster_name" {
  description = "Name of the AKS cluster; also used as the DNS prefix"
  type        = string
  default     = "aks-gitops"
}

variable "tags" {
  description = "Tags applied to all resources in this configuration"
  type        = map(string)
  default = {
    project     = "aks-gitops-platform"
    environment = "demo"
    managed_by  = "terraform"
  }
}
