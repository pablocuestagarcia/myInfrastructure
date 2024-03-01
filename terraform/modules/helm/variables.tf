variable "namespace" {
  description = "The namespace where the resource will be deployed"
  type        = string

}

variable "monitoring_namespace" {
  description = "The namespace where the monitoring resources are deployed"
  type        = string
  default     = "monitoring"
}

variable "namespace_redis" {
  description = "The namespace to deploy the redis stack"
  type        = string
  default     = "default"
}