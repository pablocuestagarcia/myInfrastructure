# modules/kubernetes/storage/outputs.tf
output "storage_classes" {
  description = "Created storage classes"
  value = kubernetes_storage_class.hostpath
}

output "persistent_volumes" {
  description = "Created persistent volumes"
  value = kubernetes_persistent_volume.hostpath
}