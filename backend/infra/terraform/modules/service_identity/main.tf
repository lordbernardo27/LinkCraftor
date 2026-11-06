data "aws_iam_policy_document" "trust" {
  statement {
    sid     = "AllowApprovedAWSService"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = var.aws_service_principals
    }
  }
}

module "service_role" {
  source = "../iam"

  role_name = "linkcraftor-${var.environment}-${var.service_name}-service"

  description = "LinkCraftor ${var.service_name} service identity for ${var.environment}."

  assume_role_policy_json = data.aws_iam_policy_document.trust.json

  permissions_boundary_arn = var.permissions_boundary_arn

  inline_policy_json = var.permission_policy_json

  tags = merge(
    {
      IdentityType = "service"
      Environment  = var.environment
      Service      = var.service_name
    },
    var.tags
  )
}
