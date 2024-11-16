
module "namespaces" {
  source = "./modules/kubernetes/namespaces"

  namespaces = {
    monitoring = {
      labels = {
        name = "monitoring"
        part-of = "observability"
      }
      # resource_quotas = {
      #   limits_cpu = "3"
      #   limits_memory = "6Gi"
      #   pods = "10"
      # }
    }
  }
}

module "monitoring-storage" {
  source = "./modules/kubernetes/storage"
  storage_classes = {
    "hostpath-storage" = {
      labels = {
        type = "hostpath"
      }
    }
  }

  persistent_volumes = {
    "prometheus-storage" = {
      storage_size = "20Gi"
      access_modes = ["ReadWriteOnce"]
      storage_class_name = "hostpath-storage"
      node_name = "workstation"
      host_path = "/data/prometheus"
      labels = {
        app = "prometheus"
      }
    }
    "grafana-storage" = {
      storage_size = "10Gi"
      access_modes = ["ReadWriteOnce"]
      storage_class_name = "hostpath-storage"
      node_name = "workstation"
      host_path = "/data/grafana"
      labels = {
        app = "grafana"
      }
    }
  }
}

module "prometheus-stack" {
  source = "./modules/helm/prometheus"
  
  namespace           = module.namespaces.namespaces["monitoring"].name
  storage_class       = module.monitoring-storage.storage_classes["hostpath-storage"].metadata[0].name
  grafana_admin_password = "tu_password_seguro"
  
  prometheus_storage_size = "20Gi"
  grafana_storage_size    = "10Gi"

  depends_on = [
    module.namespaces,
    module.monitoring-storage
  ]
}