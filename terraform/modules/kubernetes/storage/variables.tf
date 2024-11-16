variable "storage_classes" {
  description = "Map of storage classes to create"
  type = map(object({
    labels = optional(map(string), {})
    reclaim_policy = optional(string, "Retain")
    binding_mode = optional(string, "WaitForFirstConsumer")
  }))
  default = {}
}

variable "persistent_volumes" {
  description = "Map of persistent volumes to create"
  type = map(object({
    storage_size = string
    access_modes = list(string)
    reclaim_policy = optional(string, "Retain")
    storage_class_name = string
    node_name = string
    host_path = string
    host_path_type = optional(string, "DirectoryOrCreate")
    labels = optional(map(string), {})
  }))
  default = {}
}