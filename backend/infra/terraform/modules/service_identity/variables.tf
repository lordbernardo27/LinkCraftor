variable "service_name" {
  description = "Canonical LinkCraftor service name."
  type        = string

  validation {
    condition     = length(trimspace(var.service_name)) > 0
    error_message = "service_name must not be empty."
  }
}

variable "environment" {
  description = "Deployment environment."
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

variable "aws_service_principals" {
  description = "AWS services allowed to assume this service identity."
  type        = set(string)

  validation {
    condition     = length(var.aws_service_principals) > 0
    error_message = "At least one AWS service principal is required."
  }
}

variable "permission_policy_json" {
  description = "Least-privilege AWS permissions required by the service."
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
