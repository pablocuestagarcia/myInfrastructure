

resource "helm_release" "strimzi-kafka-operator" {
  name      = "strimzi-kafka-operator"
  chart     = "charts/strimzi-kafka-operator-0.39.0.tgz"
  namespace = var.namespace

}