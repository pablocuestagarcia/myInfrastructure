
resource "kubernetes_storage_class" "hostpath" {
  for_each = var.storage_classes

  metadata {
    name = each.key
    labels = merge(
      {
        "kubernetes.io/managed-by" = "terraform"
      },
      each.value.labels
    )
  }
  storage_provisioner = "kubernetes.io/no-provisioner"
  reclaim_policy = each.value.reclaim_policy
  volume_binding_mode = each.value.binding_mode
}

resource "kubernetes_persistent_volume" "hostpath" {
  for_each = var.persistent_volumes

  metadata {
    name = each.key
    labels = merge(
      {
        "kubernetes.io/managed-by" = "terraform"
      },
      each.value.labels
    )
  }

  spec {
    capacity = {
      storage = each.value.storage_size
    }
    access_modes = each.value.access_modes
    persistent_volume_reclaim_policy = each.value.reclaim_policy
    storage_class_name = each.value.storage_class_name
    node_affinity {
      required {
        node_selector_term {
          match_expressions {
            key = "kubernetes.io/hostname"
            operator = "In"
            values = [each.value.node_name]
          }
        }
      }
    }
    persistent_volume_source {
      host_path {
        path = each.value.host_path
        type = each.value.host_path_type
      }
    }
  }
}


