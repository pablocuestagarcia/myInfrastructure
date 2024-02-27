

module "nginx-ingress" {
  source = "./nginx-ingress"
  
  # Variables if are needed
  namespace = var.namespace
  
}