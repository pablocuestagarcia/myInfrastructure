

module "prometheus" {
  source = "./prometheus"
  
  # Variables if are needed
  namespace = var.monitoring_namespace  
}

module "nginx-ingress" {
  source = "./nginx-ingress"
  depends_on = [ module.prometheus ]
  
  # Variables if are needed
  namespace = var.namespace
  prometheus_namespace = var.monitoring_namespace
  
}

module "redis" {
  source = "./redis"
  depends_on = [ module.prometheus ]
  
  # Variables if are needed  
}