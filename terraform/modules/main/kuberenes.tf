resource "vultr_kubernetes" "k8s" {
  region  = data.vultr_region.amsterdam.id
  label   = "k8s-${var.project}-${var.environment}"
  version = "v1.24.4+1"

  node_pools {
    node_quantity = var.k8s_nodes_config.node_quantity
    plan          = data.vultr_plan.plan[var.k8s_nodes_config.plan_name].id
    label         = "k8s-pool-${var.project}-${var.environment}"
    auto_scaler   = true
    min_nodes     = var.k8s_nodes_config.min_nodes
    max_nodes     = var.k8s_nodes_config.max_nodes
  }
}

resource "kubernetes_deployment" "rest-api" {
  metadata {
    name   = "k8s-deploy-${var.project}-${var.environment}"
    labels = local.labels
  }

  spec {
    replicas = var.k8s_rest_api_config.replicas

    selector {
      match_labels = local.labels
    }

    template {
      metadata {
        labels = local.labels
      }

      spec {
        container {
          image = "https://ghcr.io/${var.repository}:latest"
          name  = "rest-api"

          resources {
            limits   = var.k8s_rest_api_config.limits
            requests = var.k8s_rest_api_config.requests
          }

          liveness_probe {
            http_get {
              path = "/"
              port = 80
            }

            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }
      }
    }
  }
}

resource "kubernetes_deployment" "database" {
  metadata {
    name   = "k8s-deploy-${var.project}-${var.environment}-database"
    labels = local.labels
  }

  spec {
    replicas = var.k8s_database_config.replicas

    selector {
      match_labels = local.labels
    }

    template {
      metadata {
        labels = local.labels
      }

      spec {
        container {
          image = "postgres:15.0-alpine3.16"
          name  = "database"

          resources {
            limits   = var.k8s_database_config.limits
            requests = var.k8s_database_config.requests
          }

          liveness_probe {
            exec {
              command = ["/bin/sh -c exec pg_isready"]
            }
            initial_delay_seconds = 10
            period_seconds        = 10
          }
        }
      }
    }
  }
}
