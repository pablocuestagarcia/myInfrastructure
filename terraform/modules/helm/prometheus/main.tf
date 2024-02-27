
resource "helm_release" "monitoring" {
  name       = "kube-prometheus-stack"
  chart      = "charts/kube-prometheus-stack-56.13.1.tgz"
  namespace  = "monitoring"

  set {
    name  = "grafana.enabled"
    value = "true"
  }
}
