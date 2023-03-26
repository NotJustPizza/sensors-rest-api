module "main" {
  source = "../../modules/main"

  project     = "sensors"
  environment = var.environment
  credentials = var.credentials
  repository  = var.repository

  k8s_version         = var.k8s_version
  k8s_nodes_config    = var.k8s_nodes_config
  k8s_rest_api_config = var.k8s_rest_api_config
  k8s_database_config = var.k8s_database_config
}
