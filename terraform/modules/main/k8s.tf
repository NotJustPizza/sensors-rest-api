resource "vultr_kubernetes" "k8s" {
  region  = data.vultr_region.amsterdam.id
  label   = "${var.project}-${var.environment}"
  version = coalesce(var.k8s_version, "v1.25.6+2")

  node_pools {
    node_quantity = var.k8s_nodes_config.node_quantity
    plan          = data.vultr_plan.plan[var.k8s_nodes_config.plan_name].id
    label         = "${var.project}-${var.environment}"
    auto_scaler   = true
    min_nodes     = var.k8s_nodes_config.min_nodes
    max_nodes     = var.k8s_nodes_config.max_nodes
  }
}
