variable "namespace" {
  description = "The name of the Kubernetes namespace to use"
  type        = string
  default     = "default"
}

variable "prometheus_namespace" {
  description = "The name of the Kubernetes namespace to use"
  type        = string
  default     = "default"
}