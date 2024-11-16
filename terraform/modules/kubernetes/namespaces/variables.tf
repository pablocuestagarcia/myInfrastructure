variable "namespaces" {
  description = "Map of namespaces to create with their specific configurations"
  type = map(object({
    labels = object({
      name = string
      part-of = string

      # Map adicional para otras etiquetas opcionales
      additional_labels = optional(map(string), {})
    })
    annotations = optional(map(string), {})
    resource_quotas = optional(object({
      requests_cpu = optional(string)
      requests_memory = optional(string)
      limits_cpu = optional(string)
      limits_memory = optional(string)
      pods = optional(string)
    }))
  }))
}