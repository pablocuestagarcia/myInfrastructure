resource "helm_release" "postgres" {
  name = "postgres"
  chart = "charts/postgresql-14.2.3.tgz"
  namespace = var.namespace

  set {
    name = "auth.username"
    value = "user"
  }

  set {
    name = "auth.password"
    value = "password"
  }

  set {
    name = "primary.persistence.enabled"
    value = "true"
  }

  set {
    name = "primary.persistence.existingClaim"
    value = "postgres"
  }

}