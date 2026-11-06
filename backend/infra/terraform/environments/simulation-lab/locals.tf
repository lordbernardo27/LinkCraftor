locals {
  canonical_environment = "simulation-lab"
  canonical_region      = var.aws_region
  canonical_region_role = var.region_role

  simulation_lab_invariants = {
    distinct_from_staging          = true
    distinct_from_production       = true
    synthetic_testing_only         = true
    production_customer_traffic    = false
    production_data_dependency     = false
    temporary_credentials_only     = true
    static_credentials_prohibited  = true
    runtime_worker_is_not_tf_admin = true
  }
}
