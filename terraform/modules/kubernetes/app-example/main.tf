resource "kubernetes_ingress_v1" "example_ingress" {
  metadata {
    name      = "example-ingress"
    namespace = "default"
  }

  spec {
    default_backend {
      service {
        name = "myapp-1"
        port {
          number = 8080
        }
      }
    }

    rule {
      http {
        path {
          backend {
            service {
              name = "myapp-1"
              port {
                number = 8080
              }
            }
          }

          path = "/app1/*"
        }

        path {
          backend {
            service {
              name = "myapp-2"
              port {
                number = 8080
              }
            }
          }

          path = "/app2/*"
        }
      }
    }

  }
}

resource "kubernetes_service_v1" "example" {
  metadata {
    name      = "myapp-1"
    namespace = "default"
  }
  spec {
    selector = {
      app = kubernetes_pod_v1.example.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 8080
      target_port = 80
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_service_v1" "example2" {
  metadata {
    name      = "myapp-2"
    namespace = "default"
  }
  spec {
    selector = {
      app = kubernetes_pod_v1.example2.metadata.0.labels.app
    }
    session_affinity = "ClientIP"
    port {
      port        = 8080
      target_port = 80
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_pod_v1" "example" {
  metadata {
    name      = "terraform-example"
    namespace = "default"
    labels = {
      app = "myapp-1"
    }
  }

  spec {
    container {
      image = "nginx:alpine"
      name  = "example"

      port {
        container_port = 80
      }
    }
  }
}

resource "kubernetes_pod_v1" "example2" {
  metadata {
    name      = "terraform-example2"
    namespace = "default"
    labels = {
      app = "myapp-2"
    }
  }

  spec {
    container {
      image = "nginx:alpine"
      name  = "example"

      port {
        container_port = 80
      }
    }
  }
}