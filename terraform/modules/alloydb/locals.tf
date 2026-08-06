locals {
  common_labels = {
    environment = var.environment
    managed_by  = "terraform"
    component   = "alloydb"
  }
}
