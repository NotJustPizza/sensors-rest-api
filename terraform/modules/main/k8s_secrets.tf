resource "random_password" "database_password" {
  length = 20
}

resource "kubernetes_secret" "database_password" {
  metadata {
    name = "database-password"
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
    name = "app-secret-key"
  }

  data = {
    key = random_password.app_secret_key.result
  }
}
