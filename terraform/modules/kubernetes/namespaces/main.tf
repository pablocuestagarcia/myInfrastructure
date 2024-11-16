resource "kubernetes_namespace" "namespaces" {
  for_each = var.namespaces

  metadata {
    name = each.key
    labels = merge(
      {
        "kubernetes.io/managed-by" = "terraform"
        "app.kubernetes.io/name" = each.value.labels.name
        "app.kubernetes.io/part-of" = each.value.labels.part-of
      },
      each.value.labels.additional_labels
    )
    annotations = each.value.annotations
  }
}


# Crear Resource Quotas si están especificadas
resource "kubernetes_resource_quota" "namespace_quotas" {
  for_each = {
    for ns_name, ns in var.namespaces : ns_name => ns
    if ns.resource_quotas != null
  }

  metadata {
    name = "quota-${each.key}"
    namespace = kubernetes_namespace.namespaces[each.key].metadata[0].name
  }

  spec {
    hard = {
      "requests.cpu"    = each.value.resource_quotas.requests_cpu
      "requests.memory" = each.value.resource_quotas.requests_memory
      "limits.cpu"      = each.value.resource_quotas.limits_cpu
      "limits.memory"   = each.value.resource_quotas.limits_memory
      "pods"           = each.value.resource_quotas.pods
    }
  }
}