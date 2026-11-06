data "aws_iam_policy_document" "trust" {

  dynamic "statement" {
    for_each = length(var.trusted_service_principals) > 0 ? [1] : []

    content {
      sid     = "ApprovedAWSServiceWorkloadTrust"
      effect  = "Allow"
      actions = ["sts:AssumeRole"]

      principals {
        type        = "Service"
        identifiers = var.trusted_service_principals
      }
    }
  }

  dynamic "statement" {
    for_each = length(var.trusted_aws_principal_arns) > 0 ? [1] : []

    content {
      sid     = "ApprovedAWSPrincipalWorkloadTrust"
      effect  = "Allow"
      actions = ["sts:AssumeRole"]

      principals {
        type        = "AWS"
        identifiers = var.trusted_aws_principal_arns
      }
    }
  }
}

module "workload_role" {
  source = "../iam"

  role_name = "linkcraftor-${var.environment}-${var.workload_name}-workload"

  description = "AWS workload identity for LinkCraftor ${var.workload_name} in ${var.environment}."

  assume_role_policy_json = data.aws_iam_policy_document.trust.json

  permissions_boundary_arn = var.permissions_boundary_arn

  inline_policy_json = var.permission_policy_json

  tags = merge(
    {
      IdentityType = "workload"
      Environment  = var.environment
      Workload     = var.workload_name

      RuntimeAuthority = "existing-universal-runtime"
    },
    var.tags
  )
}
