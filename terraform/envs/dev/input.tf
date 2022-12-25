variable "environment" {
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
variable "repository" {
  type    = string
  default = "NotJustPizza/sensors-rest-api"
}
variable "k8s_version" {
  type    = string
  default = null
}
variable "k8s_nodes_config" {
  type = object({
    node_quantity = number
    plan_name     = string
    min_nodes     = number
    max_nodes     = number
  })
  default = {
    node_quantity = 1
    plan_name     = "gc2"
    min_nodes     = 1
    max_nodes     = 2
  }
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
  default = {
    replicas = 1
    limits = {
      cpu    = "0.2"
      memory = "256Mi"
    }
    requests = {
      cpu    = "0.1"
      memory = "100Mi"
    }
  }
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
  default = {
    limits = {
      cpu    = "0.2"
      memory = "512Mi"
    }
    requests = {
      cpu    = "0.1"
      memory = "100Mi"
    }
    volume_size = "10Gi"
  }
}
