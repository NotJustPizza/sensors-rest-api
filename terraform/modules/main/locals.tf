locals {
  kube_config = yamldecode(
    base64decode(vultr_kubernetes.k8s.kube_config)
  )

  labels = {
    project     = var.project
    environment = var.environment
  }
}
