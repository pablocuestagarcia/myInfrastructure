
module "kubernetes" {
  source = "./modules/kubernetes"
  
}

module "nginx_ingress" {
  source = "./modules/helm"

  # Variables if are needed
  namespace = module.kubernetes.namespace_ingress
}
