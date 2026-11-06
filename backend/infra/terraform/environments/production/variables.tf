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
  description = "Canonical LinkCraftor AWS account logical name."
  type        = string

  validation {
    condition = contains(
      [
        "DEVELOPMENT",
        "TESTING",
        "STAGING",
        "SIMULATION-LAB",
        "SANDBOX",
        "PRODUCTION"
      ],
      var.account_name
    )

    error_message = "Invalid LinkCraftor AWS account name."
  }
}

variable "aws_account_id" {
  description = "Actual AWS Account ID. Null until canonical AWS account provisioning."
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

    error_message = "Invalid canonical LinkCraftor AWS region."
  }
}

variable "region_role" {
  description = "Canonical LinkCraftor region role."
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
  description = "Optional Terraform execution role ARN. Null until the approved role exists in AWS."
  type        = string
  default     = null

  validation {
    condition = (
      var.terraform_role_arn == null ||
      can(regex("^arn:aws:iam::[0-9]{12}:role/.+$", var.terraform_role_arn))
    )

    error_message = "terraform_role_arn must be null or a valid AWS IAM role ARN."
  }
}

variable "terraform_session_name" {
  description = "STS session name for Terraform role assumption."
  type        = string
  default     = "linkcraftor-terraform"
}

variable "production" {
  description = "Whether this environment is Production."
  type        = bool
}
