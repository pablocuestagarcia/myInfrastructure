# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Personal local infrastructure repository for testing and development, supporting Docker Compose, Kubernetes (KinD and K0s), and Terraform+Helm deployments.

## Common Commands

### Docker Compose
```bash
# Start a specific stack (databases, kafka, elastic, analysis)
docker compose -f docker/databases/docker-compose.yaml up -d
docker compose -f docker/kafka/docker-compose.yaml up -d
docker compose -f docker/elastic/docker-compose.yaml up -d
docker compose -f docker/analysis/docker-compose.yaml up -d

# Stop and remove
docker compose -f docker/<stack>/docker-compose.yaml down

# Podman alternative
podman-compose -f podman/databases/podman-compose.yaml up -d
```

### Kubernetes Cluster Management
```bash
# Create/manage KinD cluster (local dev, 1 control-plane + 3 workers)
kind create cluster --config kubernetes/setup/kind-basic.yaml

# Deploy/manage K0s cluster (Raspberry Pi nodes)
k0sctl apply --config kubernetes/setup/k0sctl.yaml
k0sctl kubeconfig --config kubernetes/setup/k0sctl.yaml

# Apply manifests
kubectl apply -f kubernetes/cilium/network_policy.yaml
```

### Terraform
```bash
# All Terraform commands run from the terraform/ directory
cd terraform

terraform init
terraform plan
terraform apply
terraform destroy

# Target specific modules
terraform apply -target=module.helm
terraform apply -target=module.kubernetes
```

## Architecture Overview

### Deployment Layers

1. **Docker Compose** (`docker/`) — standalone multi-container stacks for local development. No inter-stack dependencies; each subdirectory is self-contained.

2. **Kubernetes manifests** (`kubernetes/`) — cluster configs and raw YAML:
   - `setup/` — cluster bootstrap: `kind-basic.yaml` (KinD, local) and `k0sctl.yaml` (K0s on Raspberry Pis at 192.168.68.60/61)
   - `helm/` — Helm values overrides (e.g. Airflow)
   - `cilium/` — Cilium CNI network policies

3. **Terraform + Helm** (`terraform/`) — IaC for deploying to Kubernetes clusters:
   - Root `main.tf` orchestrates two module groups: `modules/kubernetes/` and `modules/helm/`
   - `modules/kubernetes/` — namespaces, storage classes, persistent volumes
   - `modules/helm/` — Helm releases: prometheus, nginx-ingress, redis, postgresql, strimzi-kafka-op, grafana
   - Helm charts are pre-downloaded as `.tgz` files in `terraform/charts/`
   - State stored locally at `terraform/state/terraform.tfstate`
   - Kubeconfig read from `~/.kube/local_config`; context defaults to `kubernetes-admin@kubernetes`

### Key Service Ports
| Service | Port |
|---------|------|
| PostgreSQL | 5432 |
| Redis | 6379 |
| Kafka | 9092 |
| Elasticsearch / OpenSearch | 9200 |
| Kibana / OpenSearch Dashboards | 5601 |
| SonarQube | 9000 |
| KinD HTTP/HTTPS | 30000/30001 |

### Module Dependencies (Terraform)
The Helm module has an explicit `depends_on` the Kubernetes module, ensuring namespaces and storage are created before Helm releases. Within the Helm module, `prometheus` depends on `nginx-ingress`.
