module "namespaces" {
  source = "./namespaces"

  # Variables if are needed
  namespace = "ingress"

}

module "monitoring" {
  source = "./namespaces"

  # Variables if are needed
  namespace = "monitoring"

}

module "namespace_redis" {
  source = "./namespaces"
  # Variables if are needed
  namespace = "redis"
}

module "namespace_kafka" {
  source = "./namespaces"
  # Variables if are needed
  namespace = "kafka"
}

module "storage" {
  source = "./storage"

}

