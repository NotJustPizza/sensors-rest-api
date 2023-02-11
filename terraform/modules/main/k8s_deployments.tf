resource "kubernetes_deployment" "rest_api" {
  # checkov:skip=CKV_K8S_35:We prefer secrets in environment variables

  metadata {
    name      = "rest-api"
    labels    = local.rest_api_labels
    namespace = kubernetes_namespace.namespace.metadata[0].name
  }

  spec {
    progress_deadline_seconds = 60
    replicas                  = var.k8s_rest_api_config.replicas

    selector {
      match_labels = local.rest_api_labels
    }

    template {
      metadata {
        labels = local.rest_api_labels
      }

      spec {
        container {
          image             = "ghcr.io/${lower(var.repository)}@sha256:45b23dee08af5e43a7fea6c4cf9c25ccf269ee113168c19722f87876677c5cb2"
          name              = "rest-api"
          image_pull_policy = "Always"

          security_context {
            read_only_root_filesystem = true
            capabilities {
              # Ref: https://docs.bridgecrew.io/docs/bc_k8s_27
              drop = ["ALL", "NET_RAW"]
            }
          }

          resources {
            # checkov:skip=CKV_K8S_10:Limits and requests are passed from variables
            # checkov:skip=CKV_K8S_11
            # checkov:skip=CKV_K8S_12
            # checkov:skip=CKV_K8S_13
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

          readiness_probe {
            http_get {
              path = "/actions/healthcheck"
              port = 8000
            }
            failure_threshold = 2
            success_threshold = 4
            period_seconds    = 3
          }

          liveness_probe {
            http_get {
              path = "/actions/healthcheck"
              port = 8000
            }

            failure_threshold = 3
            period_seconds    = 10
          }
        }
      }
    }
  }
}
