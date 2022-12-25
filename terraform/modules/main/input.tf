variable "project" {
  type = string
}
variable "environment" {
  type = string
}
variable "repository" {
  type = string
}
variable "credentials" {
  sensitive = true
  type = object({
    cloudflare = object({
      email = string
      token = string
    })
    vultr = object({
      token = string
    })
    aws = object({
      access_key = string
      secret_key = string
    })
  })
}
variable "k8s_version" {
  type = string
}
variable "k8s_nodes_config" {
  type = object({
    node_quantity = number
    plan_name     = string
    min_nodes     = number
    max_nodes     = number
  })
}
variable "k8s_rest_api_config" {
  type = object({
    replicas = number
    limits = object({
      cpu    = string
      memory = string
    })
    requests = object({
      cpu    = string
      memory = string
    })
  })
}
variable "k8s_database_config" {
  type = object({
    limits = object({
      cpu    = string
      memory = string
    })
    requests = object({
      cpu    = string
      memory = string
    })
    volume_size = string
  })
}
