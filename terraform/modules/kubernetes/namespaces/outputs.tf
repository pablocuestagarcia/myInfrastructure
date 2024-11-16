output "namespaces" {
  description = "Map of created namespaces and their details"
  value = {
    for ns_name, ns in kubernetes_namespace.namespaces : ns_name => {
      name = ns.metadata[0].name
      uid  = ns.metadata[0].uid
    }
  }
}