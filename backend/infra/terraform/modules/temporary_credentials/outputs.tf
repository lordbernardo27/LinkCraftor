output "role_name" {
  value = module.temporary_role.role_name
}

output "role_arn" {
  value = module.temporary_role.role_arn
}

output "credential_model" {
  value = "AWS STS temporary credentials"
}
