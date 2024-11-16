variable "namespace" {
  description = "Namespace where to deploy the stack"
  type        = string
  default     = "monitoring"
}

variable "storage_class" {
  description = "Storage class for PVCs"
  type        = string
}

variable "prometheus_storage_size" {
  description = "Storage size for Prometheus"
  type        = string
  default     = "50Gi"
}

variable "grafana_storage_size" {
  description = "Storage size for Grafana"
  type        = string
  default     = "10Gi"
}

variable "prometheus_retention" {
  description = "Data retention period for Prometheus"
  type        = string
  default     = "15d"
}

variable "grafana_admin_password" {
  description = "Admin password for Grafana"
  type        = string
  sensitive   = true
}

variable "cluster_domain" {
  description = "Cluster domain for ingress"
  type        = string
  default = "cluster.local"
}

variable "ingress_annotations" {
  description = "Ingress annotations"
  type        = map(string)
  default     = {}
}