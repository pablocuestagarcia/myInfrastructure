


resource "helm_release" "redis-sentinel" {
  name      = "redis"
  chart     = "charts/redis-18.17.0.tgz"
  namespace = var.namespace

  set {
    name  = "image.repository"
    value = "redis/redis-stack-server"
  }

  set {
    name  = "image.tag"
    value = "latest"
  }

  set {
    name  = "auth.password"
    value = "password"
  }

  set {
    name  = "master.configuration"
    value = <<-EOF
        dir /data
        loadmodule /opt/redis-stack/lib/rejson.so
        loadmodule /opt/redis-stack/lib/redisearch.so
      EOF
  }

  set {
    name  = "master.persistence.enabled"
    value = "false"
  }

  set {
    name  = "replica.configuration"
    value = <<-EOF
        dir /data
        loadmodule /opt/redis-stack/lib/rejson.so
        loadmodule /opt/redis-stack/lib/redisearch.so
      EOF
  }

  set {
    name  = "replica.persistence.enabled"
    value = "false"
  }

  set {
    name  = "sentinel.enabled"
    value = "true"
  }

  set {
    name  = "sentinel.persistence.enabled"
    value = "false"
  }
}