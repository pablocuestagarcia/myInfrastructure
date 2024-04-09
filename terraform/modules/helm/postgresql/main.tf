resource "helm_release" "postgres" {
  name      = "postgres"
  chart     = "charts/postgresql-14.2.3.tgz"
  namespace = var.namespace

  set {
    name  = "auth.username"
    value = "user"
  }

  set {
    name  = "auth.password"
    value = "password"
  }

  set {
    name  = "primary.persistence.enabled"
    value = "true"
  }

  set {
    name  = "primary.persistence.existingClaim"
    value = "postgres"
  }

  // Asegurarse de que el contexto de seguridad del pod esté habilitado y configurado correctamente.
  set {
    name  = "primary.podSecurityContext.enabled"
    value = "true"
  }

  set {
    name  = "primary.podSecurityContext.fsGroup"
    value = "1001"
  }

  set {
    name  = "primary.podSecurityContext.fsGroupChangePolicy"
    value = "Always"
  }

  // Ajustar el contexto de seguridad del contenedor según las necesidades.
  set {
    name  = "primary.containerSecurityContext.enabled"
    value = "true"
  }

  set {
    name  = "primary.containerSecurityContext.runAsUser"
    value = "1001"
  }

  set {
    name  = "primary.containerSecurityContext.runAsGroup"
    value = "1001"
  }
}
