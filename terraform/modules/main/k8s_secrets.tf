resource "random_password" "database" {
  length = 20
}

resource "kubernetes_secret" "database_password" {
  metadata {
    name = "database-password"
  }

  data = {
    password = random_password.database.result
  }
}
