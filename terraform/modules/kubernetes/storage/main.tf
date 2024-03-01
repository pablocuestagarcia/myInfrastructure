
resource "kubernetes_persistent_volume_v1" "storage" {
  metadata {
    name = "general-storage"
    labels = {
      "type":"general"
    }
  }
  spec {
    capacity = {
      storage = "5Gi"
    }
    access_modes = ["ReadWriteMany"]
    persistent_volume_source {
      host_path {
        path = "/data"
        type = "DirectoryOrCreate"
      }
    }
  }
}

resource "kubernetes_persistent_volume_claim_v1" "postgres" {
  metadata {
    name = "postgres"
  }
  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = "5Gi"
      }
    }
    volume_name = kubernetes_persistent_volume_v1.storage.metadata.0.name
  }
}


