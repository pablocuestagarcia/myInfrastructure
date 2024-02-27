resource "helm_release" "nginx_ingress" {
  name       = "nginx-ingress"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = var.namespace

  set {
    name  = "controller.service.type"
    value = "NodePort"
  }

  set {
    name  = "controller.watchIngressWithoutClass"
    value = "true"
  }
}
