output "role_name" {
  value = module.workload_role.role_name
}

output "role_arn" {
  value = module.workload_role.role_arn
}

output "runtime_authority" {
  value = "Existing LinkCraftor Universal Runtime"
}
