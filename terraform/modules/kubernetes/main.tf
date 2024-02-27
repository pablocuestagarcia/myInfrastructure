module "namespaces" {
  source = "./namespaces"
  
  # Variables if are needed
  namespace = "ingress"
  
}

# module "app-example" {
#   source = "./app-example"
  
#   # Variables if are needed
#   # namespace = module.namespaces.namespace
#   # app_name = "nginx"
#   # app_image = "nginx:alpine"
#   # app_port = 80
# }