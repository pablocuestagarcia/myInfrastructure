resource "helm_release" "nginx_ingress" {
  name      = "nginx-ingress"
  chart     = "charts/ingress-nginx-4.9.1.tgz"
  namespace = var.namespace

  set {
    name  = "controller.service.type"
    value = "NodePort"
  }

  set {
    name  = "controller.watchIngressWithoutClass"
    value = "true"
  }

  set {
    name  = "controller.metrics.enabled"
    value = "true"
  }

  set {
    name  = "controller.metrics.serviceMonitor.enabled"
    value = "true"
  }

  set {
    name  = "controller.metrics.serviceMonitor.additionalLabels.release"
    value = var.prometheus_namespace
  }

  set {
    name = "controller.tcp.configMapNamespace"
    value = var.tcp_configmap_namespace
  }
}
