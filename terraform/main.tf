
module "kubernetes" {
  source = "./modules/kubernetes"
  
}

module "helm" {
  source = "./modules/helm"

  # Variables if are needed
  namespace = module.kubernetes.namespace_ingress
  monitoring_namespace = module.kubernetes.namespace_monitoring
}
