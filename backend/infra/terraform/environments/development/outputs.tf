output "environment_binding" {
  value = {
    environment  = var.environment
    account_name = var.account_name
    aws_region   = var.aws_region
    region_role  = var.region_role
    production   = var.production
  }
}
