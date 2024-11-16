resource "helm_release" "monitoring" {
  name       = "kube-prometheus-stack"
  chart      = "charts/kube-prometheus-stack-66.1.1.tgz"
  namespace  = var.namespace

  # Configuración básica
  set {
    name  = "prometheusOperator.enabled"
    value = "true"
  }

  # Prometheus
  set {
    name  = "prometheus.enabled"
    value = "true"
  }

  set {
    name  = "prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.storageClassName"
    value = var.storage_class
  }

  set {
    name  = "prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage"
    value = var.prometheus_storage_size
  }

  set {
    name  = "prometheus.retention"
    value = var.prometheus_retention
  }

  # Grafana
  set {
    name  = "grafana.enabled"
    value = "true"
  }

  set {
    name  = "grafana.persistence.enabled"
    value = "true"
  }

  set {
    name  = "grafana.persistence.storageClassName"
    value = var.storage_class
  }

  set {
    name  = "grafana.persistence.size"
    value = var.grafana_storage_size
  }

  set {
    name  = "grafana.adminPassword"
    value = var.grafana_admin_password
  }

  # Ingress
  set {
    name  = "grafana.ingress.enabled"
    value = "false"
  }
}