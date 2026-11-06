resource "aws_iam_role" "this" {
  name                 = var.role_name
  path                 = var.role_path
  description          = var.description
  assume_role_policy   = var.assume_role_policy_json
  max_session_duration = var.max_session_duration
  permissions_boundary = var.permissions_boundary_arn

  tags = merge(
    {
      ManagedBy = "Terraform"
      Product   = "LinkCraftor"
      IaCModule = "iam"
    },
    var.tags
  )
}

resource "aws_iam_role_policy_attachment" "managed" {
  for_each = var.managed_policy_arns

  role       = aws_iam_role.this.name
  policy_arn = each.value
}

resource "aws_iam_role_policy" "inline" {
  count = var.inline_policy_json == null ? 0 : 1

  name   = "${var.role_name}-least-privilege"
  role   = aws_iam_role.this.id
  policy = var.inline_policy_json
}
