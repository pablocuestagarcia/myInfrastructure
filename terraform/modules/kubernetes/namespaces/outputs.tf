output "namespace_name" {
  value = kubernetes_namespace.nginx-ingress.metadata.0.name  
}