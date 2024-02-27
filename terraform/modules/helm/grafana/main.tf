

data "helm_repository" "grafana" {
  name = "grafana"
  url  = "https://grafana.github.io/helm-charts"  
}

resource "helm_release" "grafana" {
  name = "grafana"
  namespace = var.monitoring_namespace
  repository = data.helm_repository.grafana.name
  chart = "grafana"

}