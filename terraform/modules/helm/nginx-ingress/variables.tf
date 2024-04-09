variable "namespace" {
  description = "The name of the Kubernetes namespace to use"
  type        = string
  default     = "ingress"
}

variable "prometheus_namespace" {
  description = "The name of the Kubernetes namespace to use"
  type        = string
  default     = "default"
}

variable "tcp_configmap_namespace" {
  description = "The name of the Kubernetes namespace to use"
  type        = string
  default     = "ingress"  
}