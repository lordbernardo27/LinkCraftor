variable "environment" {
  description = "Canonical LinkCraftor environment."
  type        = string

  validation {
    condition = contains(
      [
        "development",
        "testing",
        "staging",
        "simulation-lab",
        "sandbox",
        "production"
      ],
      var.environment
    )

    error_message = "Invalid LinkCraftor environment."
  }
}

variable "account_name" {
  description = "Canonical AWS account name. Simulation Lab account name remains pending formal Cloud Organization freeze."
  type        = string
  default     = null
}

variable "aws_account_id" {
  description = "Actual AWS Account ID. Null until canonical account provisioning."
  type        = string
  default     = null

  validation {
    condition = (
      var.aws_account_id == null ||
      can(regex("^[0-9]{12}$", var.aws_account_id))
    )

    error_message = "aws_account_id must be null or a 12-digit AWS account ID."
  }
}

variable "aws_region" {
  description = "Canonical LinkCraftor AWS region."
  type        = string

  validation {
    condition = contains(
      [
        "eu-west-1",
        "us-east-1",
        "af-south-1"
      ],
      var.aws_region
    )

    error_message = "Invalid canonical AWS region."
  }
}

variable "region_role" {
  description = "Canonical region role."
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

    error_message = "region_role must be primary, disaster-recovery, or future."
  }
}

variable "terraform_role_arn" {
  description = "Optional Terraform execution role ARN."
  type        = string
  default     = null
}

variable "production" {
  description = "Whether this environment is Production."
  type        = bool
  default     = false
}
