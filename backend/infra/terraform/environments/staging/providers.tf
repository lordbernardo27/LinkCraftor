provider "aws" {
  region = var.aws_region

  dynamic "assume_role" {
    for_each = var.terraform_role_arn == null ? [] : [var.terraform_role_arn]

    content {
      role_arn     = assume_role.value
      session_name = var.terraform_session_name
    }
  }
}
