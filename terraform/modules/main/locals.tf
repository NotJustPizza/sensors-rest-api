locals {
  kube_config = yamldecode(
    base64decode(vultr_kubernetes.k8s.kube_config)
  )

  rest_api_labels = {
    application = "rest-api"
    project     = var.project
    environment = kubernetes_namespace.namespace.metadata[0].name
  }

  database_labels = {
    application = "database"
    project     = var.project
    environment = kubernetes_namespace.namespace.metadata[0].name
  }
}
