resource "kubernetes_persistent_volume_claim" "database" {
  metadata {
    name      = "database"
    labels    = local.database_labels
    namespace = kubernetes_namespace.namespace.metadata[0].name
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = var.k8s_database_config.volume_size
      }
    }
    storage_class_name = "vultr-block-storage"
  }
}
