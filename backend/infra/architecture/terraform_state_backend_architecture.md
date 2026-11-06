# LinkCraftor Terraform State & Backend Architecture

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.3 Terraform State & Backend Architecture
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical Terraform state and backend architecture for
LinkCraftor.

Terraform state is part of the infrastructure control plane and must receive
strong protection.

---

# Core Rule

Production and shared organizational Terraform state must not rely on unmanaged
local state.

Remote state is the canonical model for shared and Production infrastructure.

---

# State Sensitivity

Terraform state may contain:

- Resource identifiers
- Infrastructure topology
- Configuration values
- Metadata
- Potentially sensitive values

State must therefore be treated as sensitive infrastructure data.

---

# Canonical Backend Direction

The canonical AWS backend direction is:

- Amazon S3 for remote Terraform state
- S3 native state locking where supported by the approved Terraform version

The final implementation must verify the exact Terraform backend capabilities
and version before enabling locking.

Legacy DynamoDB-based locking must not be introduced automatically unless an
approved compatibility requirement justifies it.

---

# Bootstrap Boundary

Remote-state infrastructure creates a bootstrap dependency.

Terraform cannot use a remote backend before the backend exists.

Bootstrap infrastructure must therefore be created through a controlled
bootstrap process.

The bootstrap process must be minimal and documented.

---

# State Bucket Ownership

Terraform state storage must live in an approved governance account.

The final account placement must be explicitly selected during implementation.

State must not be placed casually in DEVELOPMENT or PRODUCTION merely for
convenience.

---

# State Segmentation

Terraform state must be segmented by responsibility.

State boundaries should consider:

- Organization governance
- Account
- Environment
- Region
- Infrastructure domain
- Blast radius
- Privilege level

---

# Prohibited Monolithic State

A single Terraform state containing the entire LinkCraftor AWS Organization is
prohibited.

A compromise or corruption of one state must not automatically expose or block
all infrastructure.

---

# Production State Isolation

Production state must remain separately protected from lower-environment state.

Development credentials must not automatically read or write Production state.

---

# Organization State Isolation

AWS Organizations and organization-level governance state requires stronger
protection.

Organization state must not be writable by ordinary application deployment
identities.

---

# State Key Naming

Remote state keys must identify their scope deterministically.

A state key should make clear:

- Account or governance scope
- Environment
- Region where applicable
- Infrastructure domain

Ambiguous state names are prohibited.

---

# Encryption at Rest

Terraform state must be encrypted at rest.

S3 server-side encryption must be enabled.

KMS-backed encryption may be used where approved.

Final key architecture belongs to later KMS/security implementation.

---

# Encryption in Transit

State access must use encrypted AWS APIs.

Unencrypted state transport is prohibited.

---

# Public Access

Terraform state storage must not be public.

S3 Block Public Access must be enabled for the state bucket.

---

# Bucket Versioning

Terraform state storage must use versioning.

Versioning supports recovery from:

- Accidental overwrite
- Corruption
- Failed apply
- Human error

Version history does not replace formal backup requirements.

---

# State Locking

Concurrent Terraform writes must be protected.

The implementation should use the approved Terraform S3 backend locking
capability where supported.

Locking must prevent unsafe simultaneous applies against the same state.

---

# State Access

State access must follow least privilege.

Separate permissions should exist where appropriate for:

- Terraform plan
- Terraform apply
- State administration
- Emergency recovery

Read access to state must not be granted casually.

---

# TerraformPlanRole

TerraformPlanRole should receive only the state and AWS permissions needed to
produce an approved plan.

Plan authority must not automatically grant unrestricted state administration.

---

# TerraformApplyRole

TerraformApplyRole receives the additional authority required for approved
infrastructure mutation.

Production apply authority must remain separately controlled.

---

# State Administrator

State administrative authority is highly privileged.

It may include:

- Recovery
- Version restoration
- Backend maintenance
- State migration

State administration must not become routine developer access.

---

# State Mutation Boundary

Direct manual state mutation must be exceptional.

Commands such as:

- terraform state rm
- terraform state mv
- terraform import
- backend migration

require controlled procedures where Production or shared infrastructure is
affected.

---

# State Recovery

State recovery procedures must be documented.

Recovery may use:

- S3 version restoration
- Known-good state evidence
- Terraform reconciliation
- Import
- Controlled state repair

Blind state reconstruction is prohibited.

---

# State Deletion

Production or organization state must not be casually deleted.

Deletion requires strong authorization and recovery planning.

---

# State Retention

State versions should be retained according to approved recovery and governance
requirements.

Retention architecture may later integrate with backup and compliance policy.

---

# Logging

State-bucket access must be auditable.

Relevant AWS control-plane actions must be observable through CloudTrail.

Additional S3 access evidence may be enabled where justified.

---

# Cross-Account State Access

Where Terraform executes from a Deployment account but manages destination
accounts, state access and destination AWS access remain separate permissions.

Access to Terraform state does not automatically grant destination-resource
authority.

Destination-resource authority does not automatically grant state access.

---

# Credentials Boundary

Terraform backend credentials must use approved AWS temporary credentials or
workload federation.

Long-lived embedded backend credentials are prohibited.

---

# Secret Boundary

Secrets must not be intentionally stored in state when avoidable.

Where Terraform inevitably records sensitive values, state protection becomes
the controlling security boundary.

---

# Local State Boundary

Local state may be used only for controlled bootstrap or isolated development
cases where explicitly approved.

Local state is not canonical for Production infrastructure.

Local state files must not be committed to source control.

---

# Backend Configuration

Backend configuration must not contain secrets.

Backend targeting must be explicit.

Unknown backend configuration must fail closed.

---

# Environment Separation

Each environment must have an independently identifiable state boundary.

Development must not share writable state with Production.

---

# Region Separation

Region-specific infrastructure may receive separate state boundaries where doing
so reduces blast radius or clarifies ownership.

---

# Lock Failure

If a required state lock cannot be acquired, Terraform apply must stop.

Lock bypass must not become normal practice.

---

# Force Unlock

Force-unlock is an exceptional operation.

It must only be performed after verifying that no active Terraform operation
still owns the lock.

Production force-unlock requires heightened care and audit evidence.

---

# Backend Migration

Backend migration must be planned and validated.

State must not be migrated casually between buckets, accounts, or key paths.

---

# Backup Relationship

S3 versioning provides state-version recovery but does not by itself replace the
broader backup architecture.

Later backup phases may impose stronger requirements.

---

# Fail-Closed Requirement

Terraform must fail closed when:

- Backend cannot be identified
- State cannot be loaded safely
- Required lock cannot be acquired
- Credentials are invalid
- State environment does not match target environment
- Production state authorization is missing

---

# Implementation Boundary

This section defines backend architecture only.

It does not yet:

- Create an S3 state bucket
- Create KMS keys
- Configure backend.tf
- Migrate existing state
- Enable remote locking
- Create Terraform IAM roles
- Execute terraform init
- Execute terraform plan
- Execute terraform apply

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Production canonical state stored only locally
- Terraform state committed to Git
- Public state bucket
- Unencrypted state
- Bucket versioning disabled for canonical state
- One state file for the entire AWS Organization
- Development identities modifying Production state
- Shared static credentials for backend access
- Routine force-unlock
- Direct state deletion without recovery planning
- Secrets embedded in backend configuration
- Unknown backend defaulting to Production

---

# Canonical Decision Summary

LinkCraftor shall use protected remote Terraform state for shared and Production
infrastructure.

Amazon S3 is the canonical backend direction.

S3-native locking should be used where supported by the approved Terraform
version.

State must be encrypted, versioned, non-public, access-controlled, segmented,
auditable, recoverable, and isolated by environment and responsibility.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
