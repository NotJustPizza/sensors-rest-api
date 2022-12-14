terraform {
  required_providers {
    vultr = {
      source  = "vultr/vultr"
      version = "~> 2.11.4"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 3.27.0"
    }
    kubernetes = {
      version = "~> 2.15.0"
    }
  }

  required_version = "~> 1.3.4"
}

provider "vultr" {
  api_key = var.credentials.vultr.token
}

provider "cloudflare" {
  email   = var.credentials.cloudflare.email
  api_key = var.credentials.cloudflare.token
}

provider "kubernetes" {
  host                   = local.kube_config["clusters"][0]["cluster"]["server"]
  cluster_ca_certificate = base64decode(local.kube_config["clusters"][0]["cluster"]["certificate-authority-data"])
  username               = local.kube_config["users"][0]["name"]
  client_key             = base64decode(local.kube_config["users"][0]["user"]["client-key-data"])
  client_certificate     = base64decode(local.kube_config["users"][0]["user"]["client-certificate-data"])
}
