resource "kubernetes_namespace" "nginx-ingress" {
  metadata {
    name = var.namespace
  }

}