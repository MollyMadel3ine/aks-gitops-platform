# AKS GitOps Platform

A Terraform-provisioned AKS cluster where application deployments happen via
GitOps: nothing uses "kubectl apply" manually. A controller in the cluster
(Flux) watches this repo and reconciles the cluster to match it - 
pull-based delivery, in constrast to the push-based pipelines in my other repos.

Part of a portfolio of Azure infrastructure projects:
- [azure-webapp-iac](https://github.com/MollyMadel3ine/azure-webapp-iac) — hub-and-spoke landing zone with gated CI/CD
- [container-app-iac](https://github.com/MollyMadel3ine/container-app-iac) — containerized delivery to Azure Container Apps
- [azure-sql-cost-analytics](https://github.com/MollyMadel3ine/azure-sql-cost-analytics) — cost analysis of these projects, in SQL  
- 
## Architecture

*(Diagram coming with Phase 2 - cluster, ACR, Flux, and the deploy repo loop.)*

- [ ] **Phase 1 - Cluster via Terraform. ** Single-code AKS (Standard_B2s),
      managed-identity ACR pull (no admin credentials), remote state./
- [ ] **Phase 2 - GitOps controller.** Flux watching a `deploy/` folder of
      Kubernetes manifests; prove the loop: commit -> cluster converges,
      zero manual applies.
- [ ] **Phase 3 - Full CI/CD loop.** CI builds the image, pushes it to ACR,
      bumps the image tag in the deploy manifests via PR; Flux rolls the
      deployment. Dev/prod namespaces via Kustomize overlays.
- [ ] **Phase 4 - Kubernetes-native operations.** Probes, resource
      requests/limits, HPA, Azure Monitor for containers.

## Design Decisions

- **Flux over Argo CD.** Lighter footprints and first-party Azure integration
  (AKS GitOps extension). 
- **Single repo, `infra/` + `deploy` folders.** One repo keeps this project navigable. Real-world 
  implementations often split infrastructure and deployment manifests into separate repos with
  separate permissions. The folders mark where the separate repos would be theoretically.
- **(More to come in future phases.)**

## Cost notes

The AKS control plane is free; the single B2s node costs roughly $30/month if left running -
so it isn't left running. `terraform destroy` after each work session; the rebuild is
one `terraform apply` plus a Flux bootstrap, after that the cluster repopulates its own workloads from Git. Rebuild time: *(measured in phase 2)*.