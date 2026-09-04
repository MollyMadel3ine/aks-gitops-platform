# outputs.tf 

output "resource_group_name" {
    description = "Resource group containing the AKS cluster."
    value = azurerm_resource_group.aks.name
}

output "cluster_name" {
    description = "Name of the AKS cluster, for az aks get-credentials"
    value = azurerm_kubernetes_cluster.main.name
}
