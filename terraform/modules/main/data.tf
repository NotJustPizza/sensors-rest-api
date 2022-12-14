data "vultr_region" "amsterdam" {
  filter {
    name   = "city"
    values = ["Amsterdam"]
  }
}

data "vultr_plan" "plan" {
  for_each = {
    gc2 = {
      price = 10
      ram   = 2048
      disk  = 55
    }
  }

  filter {
    name   = "monthly_cost"
    values = [each.value["price"]]
  }
  filter {
    name   = "ram"
    values = [each.value["ram"]]
  }
  filter {
    name   = "disk"
    values = [each.value["disk"]]
  }
}
