# LinkCraftor Terraform Authority & Source-of-Truth Model

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.1 Terraform Authority & Source-of-Truth Model
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document establishes Terraform as the canonical Infrastructure as Code
authority for LinkCraftor cloud infrastructure.

Terraform defines intended cloud infrastructure state.

The AWS Console is not the authoritative configuration source.

---

# Core Rule

Terraform is the canonical infrastructure source of truth.

Infrastructure changes that belong to Terraform-managed scope must be expressed
through approved Terraform code.

Manual AWS Console changes must not become permanent authoritative
infrastructure state.

---

# Canonical Infrastructure Root

The canonical LinkCraftor infrastructure root is:

backend/infra/

Terraform implementation must remain under the approved infrastructure
structure.

---

# Architecture vs Implementation

Architecture documents define what must exist.

Terraform defines how approved infrastructure is provisioned.

Terraform must implement architecture.

Terraform must not silently redefine approved architecture.

---

# Source Control

Terraform code must be version controlled.

Infrastructure changes must be reviewable through source-control history.

Source control must preserve:

- Author
- Change
- Review evidence
- Version history
- Rollback context

---

# Manual Console Boundary

AWS Console may be used for:

- Read-only inspection
- Troubleshooting
- Emergency action where approved
- Validation
- AWS operations that cannot reasonably be represented immediately in Terraform

Console use must not establish undocumented permanent infrastructure.

---

# Drift Boundary

If live AWS state differs from Terraform-managed intended state, the difference
is drift.

Drift must be investigated.

Drift must not simply be accepted without architectural and operational review.

---

# Import Boundary

Existing AWS resources that later become Terraform-managed must be imported or
otherwise reconciled through a controlled process.

Terraform must not blindly recreate existing infrastructure.

---

# Terraform Ownership

Every Terraform-managed resource must have clear ownership.

Ownership should identify:

- Architecture phase
- Module
- Environment
- Account
- Region
- Service responsibility

---

# Environment Authority

Terraform must preserve:

- Development
- Testing
- Staging
- Sandbox
- Production

Environment authority must not be inferred solely from filenames.

Environment targeting must be explicit.

---

# Account Authority

Terraform must preserve the canonical eleven-account AWS architecture:

- LINKCRAFTOR-MANAGEMENT
- SECURITY
- LOG-ARCHIVE
- NETWORK
- SHARED-SERVICES
- DEPLOYMENT
- DEVELOPMENT
- TESTING
- STAGING
- SANDBOX
- PRODUCTION

---

# Region Authority

Terraform must preserve canonical regions:

- eu-west-1 — primary
- us-east-1 — disaster-recovery
- af-south-1 — future

The RegionRole value secondary is noncanonical.

---

# Production Authority

Production Terraform execution requires separately approved Production
authority.

Non-production Terraform credentials must not automatically mutate Production.

---

# Terraform Plan Boundary

Terraform plan evaluates proposed infrastructure change.

Plan does not authorize apply.

Plan and apply must remain separately governable.

---

# Terraform Apply Boundary

Terraform apply changes live infrastructure.

Apply therefore requires stronger authorization than local code editing or plan
generation.

Production apply must be independently controlled.

---

# Destructive Change Boundary

Terraform must not normalize accidental destructive changes.

Destructive operations require explicit review appropriate to risk.

Critical deletion protections will be defined further in Phase 3.10.

---

# Secrets Boundary

Secrets must not be hardcoded into Terraform source.

Sensitive values must use approved secret-management and variable mechanisms.

Terraform state must be treated as potentially sensitive.

---

# Credentials Boundary

AWS credentials must not be stored in Terraform files.

Terraform must obtain AWS authority through approved temporary credentials,
role assumption, or approved workload federation.

---

# State Boundary

Terraform state is part of the infrastructure control plane.

State must be:

- Protected
- Access controlled
- Versioned where supported
- Recoverable
- Environment-aware
- Protected from concurrent unsafe writes

Detailed state architecture is governed by 3.3.

---

# Architecture Change Boundary

If Terraform implementation reveals an architectural conflict, implementation
must not silently override the architecture.

The conflict must be resolved through the appropriate architecture change
process.

---

# Generated Files

Generated Terraform plans, caches, temporary files, and local state must not be
committed unless explicitly approved.

Examples normally excluded include:

- .terraform/
- terraform.tfstate
- terraform.tfstate.backup
- *.tfplan
- crash logs
- local credential files

---

# Terraform Version Governance

Terraform version must be pinned or constrained deliberately.

Unexpected automatic major-version changes must not silently alter
infrastructure behavior.

---

# Provider Version Governance

Terraform provider versions must be explicitly constrained.

Provider upgrades require review and validation.

---

# Auditability

Terraform changes must be attributable through:

- Source-control history
- CI/CD evidence
- Terraform plan evidence
- Terraform apply evidence
- AWS CloudTrail

---

# Fail-Closed Principle

Where environment, account, credentials, backend, or provider targeting cannot
be validated, Terraform execution must fail closed.

Unknown target state must not default to Production.

---

# Implementation Boundary

This section defines Terraform governance architecture only.

It does not yet:

- Initialize Terraform
- Configure AWS providers
- Configure remote state
- Create AWS accounts
- Create OUs
- Create SCPs
- Create IAM roles
- Run terraform apply
- Modify live AWS infrastructure

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- AWS Console used as permanent source of truth
- Production infrastructure changed manually without reconciliation
- AWS credentials embedded in Terraform
- Secrets hardcoded in Terraform
- Local state used as canonical Production state
- Unreviewed provider upgrades
- Terraform silently overriding architecture
- Non-production credentials applying Production
- Unknown environment defaulting to Production
- Blind recreation of existing AWS resources
- Unreviewed destructive apply

---

# Canonical Decision Summary

Terraform is LinkCraftor's canonical Infrastructure as Code implementation
authority.

Architecture defines approved infrastructure intent.

Terraform implements that intent.

AWS Console configuration does not replace Terraform-managed source of truth.

Production Terraform authority remains separately controlled.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
