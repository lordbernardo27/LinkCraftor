locals {
  canonical_environment = var.environment
  canonical_account     = var.account_name
  canonical_region      = var.aws_region
  canonical_region_role = var.region_role

  security_invariants = {
    static_credentials_prohibited  = true
    temporary_credentials_only     = true
    production_isolated            = true
    customer_identity_is_not_iam   = true
    runtime_worker_is_not_tf_admin = true
  }
}
