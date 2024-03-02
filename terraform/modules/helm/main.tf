

module "prometheus" {
  source = "./prometheus"

  # Variables if are needed
  namespace = var.monitoring_namespace
}

module "nginx-ingress" {
  source     = "./nginx-ingress"
  depends_on = [module.prometheus]

  # Variables if are needed
  namespace            = var.namespace
  prometheus_namespace = var.monitoring_namespace

}

module "redis" {
  source     = "./redis"
  depends_on = [module.prometheus]

  # Variables if are needed
  namespace = var.namespace_redis
}

module "postgresql" {
  source     = "./postgresql"
  depends_on = [module.prometheus]

  # Variables if are needed
  namespace = var.namespace_postgres

}


module "strimzi-kafka-op" {
  source     = "./strimzi-kafka-op"
  depends_on = [module.prometheus]

  # Variables if are needed
  namespace = var.namespace_kafka

}