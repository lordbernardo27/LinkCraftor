# LinkCraftor Terraform Repository & Module Structure

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.2 Terraform Repository & Module Structure
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical Terraform repository and module structure
for LinkCraftor.

The structure must support:

- Multiple AWS accounts
- Multiple environments
- Multiple regions
- Reusable modules
- Safe Production isolation
- Controlled Terraform state
- Future infrastructure expansion

---

# Canonical Terraform Root

Terraform implementation lives under:

backend/infra/terraform/

This directory is subordinate to the canonical infrastructure root:

backend/infra/

---

# Canonical Top-Level Structure

Canonical structure:

backend/infra/terraform/
├── bootstrap/
├── organization/
├── modules/
├── environments/
├── shared/
├── policies/
├── scripts/
└── tests/

Exact implementation files may be introduced incrementally.

---

# Bootstrap

bootstrap/ contains infrastructure required before the main Terraform system can
operate.

Potential scope includes:

- Remote-state infrastructure
- Locking infrastructure where required
- Initial Terraform roles
- Initial backend prerequisites

Bootstrap must remain minimal.

---

# Organization

organization/ contains AWS Organizations-level infrastructure.

Potential scope includes:

- Organizational Units
- Account governance
- SCPs
- Delegated administration
- Organization policy attachments

It must not become a general application-infrastructure directory.

---

# Modules

modules/ contains reusable Terraform modules.

Modules must represent cohesive infrastructure responsibilities.

Examples may later include:

- VPC
- IAM role
- KMS
- S3
- SQS
- ECS
- Database
- Logging
- Monitoring

Modules must not encode hidden Production assumptions.

---

# Environments

environments/ contains environment/account-specific Terraform composition.

Canonical environment structure should preserve:

- development
- testing
- staging
- sandbox
- production

Supporting accounts may use separate account-oriented compositions where
appropriate.

---

# Shared

shared/ contains approved shared infrastructure composition.

Shared infrastructure must not become a trust bridge that bypasses environment
boundaries.

---

# Policies

policies/ contains approved policy definitions or policy-generation inputs where
appropriate.

Potential content includes:

- SCPs
- IAM policies
- Resource policies
- KMS policy templates

Policy ownership must remain explicit.

---

# Scripts

scripts/ contains Terraform-supporting operational scripts.

Scripts must not bypass Terraform governance.

Scripts must not silently mutate Production infrastructure outside the approved
workflow.

---

# Tests

tests/ contains IaC validation and testing assets.

Testing may later include:

- terraform validate
- terraform fmt checks
- static analysis
- policy testing
- module tests
- plan inspection

---

# Root Module Boundary

Root modules compose reusable modules for a particular account, environment, or
governance scope.

Root modules must remain narrowly targeted.

A single universal root module spanning the entire organization without
appropriate isolation is prohibited.

---

# Module Reuse

Reusable modules should accept explicit inputs for:

- Environment
- Account
- Region
- Naming
- Tags
- Security settings

Modules must not assume Production by default.

---

# Environment Naming

Canonical environment names are:

- development
- testing
- staging
- sandbox
- production

Aliases must not silently create additional environments.

---

# Account Naming

Canonical account names remain those certified in Phase 2.

Terraform module structure must preserve those account identities.

---

# Region Naming

Canonical region codes may be used:

- euw1
- use1
- afs1

They map to:

- eu-west-1
- us-east-1
- af-south-1

---

# File Naming

Terraform files should use meaningful responsibility-based names.

Examples may include:

- providers.tf
- versions.tf
- variables.tf
- outputs.tf
- locals.tf
- backend.tf
- main.tf

Large modules should be split by responsibility where clarity improves.

---

# Provider Definition Boundary

Provider configuration must remain explicit.

Provider aliases must identify intended account and region.

Ambiguous default-provider behavior must not silently target Production.

---

# Variable Boundary

Variables must be:

- Typed where practical
- Documented
- Validated where security-sensitive
- Free from hardcoded secrets

---

# Local Values

Terraform locals may derive stable configuration.

Locals must not conceal privilege boundaries or override environment identity.

---

# Outputs

Terraform outputs must expose only necessary infrastructure information.

Sensitive outputs must be marked appropriately.

Credentials and secrets must not be emitted casually.

---

# Module Versioning

Shared modules must be version-controlled.

Changes to widely reused modules require impact analysis.

A module change affecting Production must receive appropriate review.

---

# Circular Dependency Boundary

Modules must avoid uncontrolled circular dependencies between accounts or
environments.

Cross-account dependencies must remain explicit.

---

# Production Separation

Production Terraform composition must remain separate from lower-environment
composition.

Development Terraform execution must not automatically load Production
configuration.

---

# Organization Separation

AWS Organization governance code must remain distinguishable from workload
infrastructure.

Organization-level changes require stronger review.

---

# State Separation

Terraform structure must allow separate state boundaries.

A single state file for the entire LinkCraftor AWS Organization is prohibited.

Detailed state segmentation is governed by 3.3.

---

# Future Expansion

The structure must allow future phases to add:

- Networking
- Compute
- Storage
- Databases
- IAM
- Secrets
- Load balancing
- Deployment
- Observability

without rebuilding the Terraform architecture.

---

# Implementation Boundary

This section defines repository architecture only.

It does not yet create live infrastructure.

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- One monolithic Terraform state for all AWS accounts
- Modules defaulting silently to Production
- Hidden account targeting
- Hidden region targeting
- Secrets committed in variable files
- Production config automatically loaded by Development
- Scripts bypassing Terraform governance
- Organization governance mixed indiscriminately with application resources
- Duplicate modules for identical responsibilities without justification

---

# Canonical Decision Summary

LinkCraftor Terraform shall use a structured repository under:

backend/infra/terraform/

The structure separates bootstrap, organization governance, reusable modules,
environment composition, shared infrastructure, policies, scripts, and tests.

Production remains structurally and operationally isolated.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
