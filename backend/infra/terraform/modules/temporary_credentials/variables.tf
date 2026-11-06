variable "role_name" {
  description = "Role receiving temporary STS sessions."
  type        = string

  validation {
    condition     = length(trimspace(var.role_name)) > 0
    error_message = "role_name must not be empty."
  }
}

variable "environment" {
  description = "Canonical LinkCraftor environment."
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
      var.environment
    )

    error_message = "Invalid LinkCraftor environment."
  }
}

variable "trusted_principal_arns" {
  description = "Explicit AWS principals allowed to assume this role."
  type        = set(string)

  validation {
    condition     = length(var.trusted_principal_arns) > 0
    error_message = "At least one trusted principal ARN is required."
  }
}

variable "external_id" {
  description = "Optional ExternalId for approved third-party trust."
  type        = string
  default     = null
  sensitive   = true
}

variable "require_mfa" {
  description = "Require MFA for human-originated AssumeRole sessions where applicable."
  type        = bool
  default     = true
}

variable "max_session_duration" {
  description = "Maximum role session duration."
  type        = number
  default     = 3600

  validation {
    condition = (
      var.max_session_duration >= 3600 &&
      var.max_session_duration <= 43200
    )

    error_message = "max_session_duration must be between 3600 and 43200 seconds."
  }
}

variable "permission_policy_json" {
  description = "Least-privilege permissions granted to temporary sessions."
  type        = string
  sensitive   = true

  validation {
    condition     = can(jsondecode(var.permission_policy_json))
    error_message = "permission_policy_json must contain valid JSON."
  }
}

variable "permissions_boundary_arn" {
  description = "Optional permissions boundary."
  type        = string
  default     = null
}

variable "tags" {
  description = "Additional tags."
  type        = map(string)
  default     = {}
}
