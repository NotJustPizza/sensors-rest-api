resource "kubernetes_stateful_set" "database" {
  metadata {
    name   = "database"
    labels = local.database_labels
  }

  spec {
    selector {
      match_labels = local.database_labels
    }

    service_name = kubernetes_service.database.metadata[0].name

    template {
      metadata {
        labels = local.database_labels
      }

      spec {
        container {
          image = "postgres:15.0-alpine3.16"
          name  = "database"

          resources {
            limits   = var.k8s_database_config.limits
            requests = var.k8s_database_config.requests
          }

          env {
            name = "POSTGRES_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.database_password.metadata[0].name
                key  = "password"
              }
            }
          }

          env {
            name  = "POSTGRES_DB"
            value = "sensors"
          }

          liveness_probe {
            exec {
              command = ["pg_isready"]
            }
            initial_delay_seconds = 10
            period_seconds        = 10
          }

          volume_mount {
            mount_path = "/var/lib/postgresql/data"
            name       = "database-volume"
          }

        }

        volume {
          name = "database-volume"

          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.database.metadata[0].name
          }
        }
      }
    }
  }
}
