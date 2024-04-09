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

variable "namespace_postgres" {
  description = "The namespace to deploy the postgres stack"
  type        = string
  default     = "default"
}

variable "namespace_kafka" {
  description = "The namespace to deploy the kafka stack"
  type        = string
  default     = "default"

}

variable "cluster_domain" {
  description = "The domain of the cluster"
  type        = string
  default     = "cluster.local"  
}