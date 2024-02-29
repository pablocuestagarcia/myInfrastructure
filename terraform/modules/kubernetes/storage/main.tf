
resource "kubernetes_persistent_volume_v1" "storage" {
  metadata {
    name = "general-storage"
  }
  spec {
    capacity = {
      storage = "10Gi"
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

