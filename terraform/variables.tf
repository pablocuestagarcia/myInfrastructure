variable "k8s_context" {
  description = "The name of the Kubernetes context to use"
  type        = string
  default     = "kubernetes-admin@kubernetes"
}