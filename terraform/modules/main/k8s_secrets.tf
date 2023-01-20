resource "random_password" "database_password" {
  length = 20
}
resource "kubernetes_secret" "database_password" {
  metadata {
    name      = "database-password"
    namespace = var.environment
  }

  data = {
    password = random_password.database_password.result
  }
}

resource "random_password" "app_secret_key" {
  length = 32
}
resource "kubernetes_secret" "app_secret_key" {
  metadata {
    name      = "app-secret-key"
    namespace = var.environment
  }

  data = {
    key = random_password.app_secret_key.result
  }
}

resource "random_password" "admin_password" {
  length = 32
}
resource "kubernetes_secret" "admin_password" {
  metadata {
    name      = "admin-password"
    namespace = var.environment
  }

  data = {
    key = random_password.admin_password.result
  }
}
