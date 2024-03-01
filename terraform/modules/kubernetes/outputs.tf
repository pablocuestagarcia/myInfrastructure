output "namespace_ingress" {
  value = module.namespaces.namespace_name
}

output "namespace_monitoring" {
  value = module.monitoring.namespace_name
}

output "namespace_redis" {
  value = module.namespace_redis.namespace_name
}