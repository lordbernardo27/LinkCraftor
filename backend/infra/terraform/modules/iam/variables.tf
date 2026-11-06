variable "role_name" {
  description = "Canonical IAM role name."
  type        = string

  validation {
    condition     = length(trimspace(var.role_name)) > 0
    error_message = "role_name must not be empty."
  }
}

variable "role_path" {
  description = "IAM role path."
  type        = string
  default     = "/linkcraftor/"
}

variable "description" {
  description = "IAM role description."
  type        = string
}

variable "max_session_duration" {
  description = "Maximum STS session duration in seconds."
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

variable "assume_role_policy_json" {
  description = "Validated IAM trust policy JSON."
  type        = string
  sensitive   = true

  validation {
    condition     = can(jsondecode(var.assume_role_policy_json))
    error_message = "assume_role_policy_json must contain valid JSON."
  }
}

variable "permissions_boundary_arn" {
  description = "Optional IAM permissions boundary."
  type        = string
  default     = null
}

variable "managed_policy_arns" {
  description = "Approved managed policies attached to this role."
  type        = set(string)
  default     = []
}

variable "inline_policy_json" {
  description = "Optional least-privilege inline policy JSON."
  type        = string
  default     = null
  sensitive   = true

  validation {
    condition = (
      var.inline_policy_json == null ||
      can(jsondecode(var.inline_policy_json))
    )

    error_message = "inline_policy_json must be null or valid JSON."
  }
}

variable "tags" {
  description = "Canonical resource tags."
  type        = map(string)
  default     = {}
}
