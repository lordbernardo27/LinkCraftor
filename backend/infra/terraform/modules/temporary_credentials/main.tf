data "aws_iam_policy_document" "temporary_trust" {

  statement {
    sid     = "TemporaryCredentialTrust"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = var.trusted_principal_arns
    }

    dynamic "condition" {
      for_each = var.external_id == null ? [] : [1]

      content {
        test     = "StringEquals"
        variable = "sts:ExternalId"
        values   = [var.external_id]
      }
    }

    dynamic "condition" {
      for_each = var.require_mfa ? [1] : []

      content {
        test     = "Bool"
        variable = "aws:MultiFactorAuthPresent"
        values   = ["true"]
      }
    }
  }
}

module "temporary_role" {
  source = "../iam"

  role_name = var.role_name

  description = "Temporary STS role for LinkCraftor ${var.environment}."

  max_session_duration = var.max_session_duration

  assume_role_policy_json = data.aws_iam_policy_document.temporary_trust.json

  permissions_boundary_arn = var.permissions_boundary_arn

  inline_policy_json = var.permission_policy_json

  tags = merge(
    {
      IdentityType      = "temporary-session"
      Environment       = var.environment
      CredentialModel   = "sts"
      StaticCredentials = "prohibited"
    },
    var.tags
  )
}
