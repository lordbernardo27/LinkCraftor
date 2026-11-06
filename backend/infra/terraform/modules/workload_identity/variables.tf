variable "workload_name" {
  description = "Canonical workload name."
  type        = string

  validation {
    condition     = length(trimspace(var.workload_name)) > 0
    error_message = "workload_name must not be empty."
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

variable "trusted_service_principals" {
  description = "AWS service principals allowed to assume this workload role."
  type        = set(string)
  default     = []
}

variable "trusted_aws_principal_arns" {
  description = "Explicit AWS principal ARNs allowed to assume the workload role."
  type        = set(string)
  default     = []
}

variable "permission_policy_json" {
  description = "Least-privilege workload AWS permissions."
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
  description = "Additional workload tags."
  type        = map(string)
  default     = {}
}
