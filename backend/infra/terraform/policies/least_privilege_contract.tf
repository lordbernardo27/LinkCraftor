variable "allowed_environment" {
  description = "Canonical LinkCraftor deployment environment."
  type        = string

  validation {
    condition = contains(
      [
        "development",
        "testing",
        "staging",
        "sandbox",
        "production"
      ],
      var.allowed_environment
    )

    error_message = "Environment must be development, testing, staging, sandbox, or production."
  }
}

variable "allowed_region" {
  description = "Canonical LinkCraftor AWS region."
  type        = string

  validation {
    condition = contains(
      [
        "eu-west-1",
        "us-east-1",
        "af-south-1"
      ],
      var.allowed_region
    )

    error_message = "AWS region is outside the certified LinkCraftor region model."
  }
}

variable "region_role" {
  description = "Canonical certified region role."
  type        = string

  validation {
    condition = contains(
      [
        "primary",
        "disaster-recovery",
        "future"
      ],
      var.region_role
    )

    error_message = "RegionRole must be primary, disaster-recovery, or future. secondary is noncanonical."
  }
}

locals {
  linkcraftor_security_invariants = {
    no_static_credentials        = true
    temporary_credentials_only   = true
    environment_isolation        = true
    production_separate          = true
    no_runtime_admin_role        = true
    no_customer_aws_identity     = true
    no_generic_service_admin     = true
    explicit_cross_account_trust = true
  }
}
