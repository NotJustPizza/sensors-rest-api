resource "kubernetes_service" "database" {
  metadata {
    name      = "database"
    labels    = local.database_labels
    namespace = kubernetes_namespace.namespace.metadata[0].name
  }
  spec {
    selector = local.database_labels

    port {
      port        = 5432
      target_port = 5432
    }

    type = "ClusterIP"
  }
}

resource "kubernetes_service" "rest_api" {
  metadata {
    name      = "rest-api"
    labels    = local.rest_api_labels
    namespace = kubernetes_namespace.namespace.metadata[0].name
    annotations = {
      "service.beta.kubernetes.io/vultr-loadbalancer-protocol"  = "http"
      "service.beta.kubernetes.io/vultr-loadbalancer-algorithm" = "least_connections"
      # Should be simplified in next VKE release
      # Ref: https://github.com/vultr/vultr-cloud-controller-manager/pull/139
      "service.beta.kubernetes.io/vultr-loadbalancer-firewall-rules" = "${join(",80;", data.cloudflare_ip_ranges.cloudflare.ipv4_cidr_blocks)},80"
    }
  }
  spec {
    selector = local.rest_api_labels

    port {
      port        = 80
      target_port = 8000
    }

    type = "LoadBalancer"
  }
}
