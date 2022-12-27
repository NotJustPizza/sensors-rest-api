resource "kubernetes_deployment" "rest_api" {
  metadata {
    name   = "rest-api"
    labels = local.rest_api_labels
  }

  spec {
    replicas = var.k8s_rest_api_config.replicas

    selector {
      match_labels = local.rest_api_labels
    }

    template {
      metadata {
        labels = local.rest_api_labels
      }

      spec {
        container {
          image = "ghcr.io/${lower(var.repository)}:latest"
          name  = "rest-api"

          resources {
            limits   = var.k8s_rest_api_config.limits
            requests = var.k8s_rest_api_config.requests
          }

          env {
            name = "APP_SECRET"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app_secret_key.metadata[0].name
                key  = "key"
              }
            }
          }

          env {
            name = "ADMIN_PASS"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.admin_password.metadata[0].name
                key  = "key"
              }
            }
          }

          env {
            name  = "DB_HOST"
            value = "database.default.svc.cluster.local"
          }

          env {
            name = "DB_PASS"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.database_password.metadata[0].name
                key  = "password"
              }
            }
          }

          liveness_probe {
            http_get {
              path = "/"
              port = 8000
            }

            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }
      }
    }
  }
}
