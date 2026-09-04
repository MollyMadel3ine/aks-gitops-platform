# main.tf 

#Dedicated resource group for the AKS cluster and its Terraform-managed
#resources. Separate from the tfstate RG so a 'terraform destroy' won't
#touch the state backend. (Note: AKS also auto-creates a second 'node' RG
#for VMs/disks - see README)  
resource "azurerm_resource_group" "aks" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Single D2s_v3 for cost (~$70/mo, destroyed between sessions) - demo-sized, not HA.
# CNI Overlay chosen over deprecated-path kubenet; img pulls use the kubelet identity.
resource "azurerm_kubernetes_cluster" "main" {
  name                = var.cluster_name
  location            = azurerm_resource_group.aks.location
  resource_group_name = azurerm_resource_group.aks.name
  dns_prefix          = var.cluster_name

  default_node_pool {
    name       = "system"
    node_count = 1
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
  }

  tags = var.tags
}

# Existing shared ACR (rg-container-shared) -referenced, never managed here. 
# Data source = read-only lookup; this config can;t modify or destroy it. 
data "azurerm_container_registry" "shared" {
    name = "acrcontainerdemomolly"
    resource_group_name = "rg-container-shared"
}

# Grant the cluster's kubelet identity pull rights on the shared ACR. 
# Kubelet identity (not the SystemAssigned control-plane identity) is what
# nodes authenticate with when pulling images - no ACR admin account needed. 
resource "azurerm_role_assignment" "acr_pull" {
    scope = data.azurerm_container_registry.shared.id
    role_definition_name = "AcrPull"
    principal_id = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}
