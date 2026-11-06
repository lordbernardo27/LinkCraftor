# LinkCraftor Terraform Drift, Import & Existing-Resource Governance

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.9 Drift, Import & Existing-Resource Governance
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines how LinkCraftor handles infrastructure that already exists,
configuration drift, Terraform imports, state reconciliation, and manual AWS
changes.

Terraform must adopt infrastructure safely rather than blindly recreating or
destroying it.

---

# Architectural Authorities

This architecture consumes and preserves:

- 3.1 Terraform Authority & Source-of-Truth Model
- 3.3 Terraform State & Backend Architecture
- 3.4 Provider & Account Targeting Architecture
- 3.5 Environment Configuration Model
- 3.7 Plan / Apply Separation
- 3.8 Terraform Identity & Credential Model

---

# Core Rule

Existing AWS resources must be discovered and classified before Terraform
attempts to create, import, replace, or destroy them.

Drift must be investigated.

Import must be controlled.

---

# Existing-Resource Classification

An existing resource encountered during Terraform implementation must be
classified as one of:

- Terraform-managed
- Intended for Terraform adoption
- Externally managed
- Legacy
- Temporary
- Orphaned
- Unknown

Unknown resources must not be destroyed automatically.

---

# Terraform-Managed Resource

A Terraform-managed resource is represented in approved configuration and
tracked by canonical Terraform state.

---

# Terraform Adoption Candidate

A resource may be adopted into Terraform when:

- It is architecturally approved
- Ownership is known
- Configuration is understood
- Import path is known
- State destination is correct
- Destructive differences are reviewed

---

# Externally Managed Resource

Some resources may remain outside Terraform where explicitly approved.

Their ownership must be documented.

Terraform must not attempt to manage them accidentally.

---

# Legacy Resource

Legacy resources require classification before modification.

Legacy does not automatically mean obsolete or safe to destroy.

---

# Temporary Resource

Temporary resources must have:

- Owner
- Purpose
- Expiry or cleanup condition
- Environment
- Cost attribution

Temporary resources should not become permanent unmanaged infrastructure.

---

# Orphaned Resource

An orphaned resource has no valid owner or declared purpose.

It must be investigated before cleanup.

Production or security-sensitive orphaned resources require heightened review.

---

# Unknown Resource

Unknown means Terraform does not yet have enough evidence to classify the
resource.

Unknown resources fail closed against destructive action.

---

# Drift Definition

Drift exists when live AWS resource state differs materially from the canonical
Terraform-managed intended state.

---

# Drift Sources

Potential drift sources include:

- Manual Console changes
- AWS CLI changes
- Direct API changes
- Emergency actions
- External automation
- Provider behavior
- Service-managed changes
- Failed Terraform apply
- Configuration rollback
- Import mismatch

---

# Drift Detection

Terraform plan may reveal drift.

Additional governance or monitoring may later detect infrastructure changes
outside Terraform.

---

# Drift Classification

Detected drift should be classified as:

- Expected
- Benign
- Corrective
- Security-relevant
- Destructive-risk
- Unknown

---

# Expected Drift

Some AWS services may modify service-managed properties.

Expected drift must be explicitly understood.

Lifecycle ignore rules must not be used broadly to hide uncontrolled drift.

---

# lifecycle ignore_changes Boundary

`ignore_changes` may be used only where justified.

It must not become a generic mechanism for hiding configuration conflicts.

Security-critical properties must not be ignored casually.

---

# Manual Change Reconciliation

Approved manual changes must be reconciled through one of:

- Update Terraform code
- Revert live change
- Import or state reconciliation
- Approved architectural exception

Manual changes must not remain undocumented permanent drift.

---

# Emergency Change Reconciliation

Emergency AWS changes must be reconciled after the incident.

Emergency status does not make manual configuration permanently authoritative.

---

# Import Governance

Terraform import is a state-management operation.

Import must occur only after confirming:

- Correct AWS account
- Correct environment
- Correct region
- Correct resource identity
- Correct Terraform address
- Correct state boundary
- Correct ownership

---

# Import Does Not Create Configuration

Importing a resource into state does not by itself establish complete canonical
Terraform configuration.

Configuration must accurately represent the adopted resource.

---

# Import Plan Review

After import, Terraform plan must be reviewed.

Unexpected replacement, deletion, or mutation must be resolved before apply.

---

# State Address

Imported resources must use stable Terraform addresses.

State addresses should reflect module and ownership architecture.

---

# Import to Wrong State

Importing a resource into the wrong state is prohibited.

Production resources must never be imported into Development state.

---

# Cross-Account Import

Cross-account import requires explicit destination identity and state selection.

Organization membership alone does not justify import authority.

---

# Cross-Region Import

Region-specific resources must be imported using the correct provider and region.

---

# Resource Replacement Risk

Terraform may propose replacement when configuration differs from existing
resource properties.

Replacement must be treated as potentially destructive until reviewed.

---

# Resource Naming Collision

A naming collision does not prove that a resource is Terraform-owned.

Existing ownership must be established independently.

---

# Resource Discovery

Before implementing a new Terraform resource in an existing AWS estate,
discovery should determine whether an equivalent resource already exists.

---

# Duplicate Resource Prevention

Terraform implementation must avoid creating duplicate:

- Networks
- Buckets
- Queues
- Databases
- IAM roles
- KMS keys
- Security services
- Logging infrastructure

where an approved reusable resource already exists.

---

# Data-Bearing Resource Protection

Resources holding data require heightened care.

Examples include:

- S3 buckets
- Databases
- EBS volumes
- File systems
- Backup vaults

Import, replacement, or deletion must account for data retention.

---

# IAM Resource Protection

Existing IAM roles, policies, trusts, and permission boundaries must be reviewed
before Terraform adoption.

Terraform must not unintentionally widen privilege.

---

# KMS Resource Protection

Existing KMS keys must be treated as security-sensitive.

Key replacement or policy change may affect recoverability and data access.

---

# Network Resource Protection

Existing networks and routing may contain dependencies outside Terraform's
immediate scope.

Network adoption requires dependency review.

---

# Security Resource Protection

Existing audit, monitoring, security, and evidence infrastructure must not be
destroyed or disabled during adoption.

---

# Production Adoption

Production resource adoption requires stronger review.

A successful import does not itself authorize Production mutation.

---

# State Removal

`terraform state rm` removes Terraform state ownership but does not destroy the
live resource.

State removal must be deliberate and reviewed.

---

# State Move

`terraform state mv` changes Terraform state address.

It must be used carefully during refactoring or module migration.

---

# Resource Forgetting Boundary

Terraform must not "forget" resources simply to suppress inconvenient plans.

Ownership changes must be intentional.

---

# Terraform Refresh

Provider refresh may update observed state.

Unexpected refresh changes require investigation where security or destructive
risk exists.

---

# Import Evidence

Import evidence should record:

- Resource identifier
- Account
- Environment
- Region
- Terraform address
- State key
- Operator or automation identity
- Result

---

# Drift Evidence

Drift evidence should identify:

- Resource
- Expected state
- Observed state
- Source where known
- Risk classification
- Resolution

---

# Source-of-Truth Decision

Where live infrastructure and Terraform disagree, neither side is blindly
accepted.

The certified architecture determines the intended outcome.

---

# Reconciliation Decision

Reconciliation may result in:

- Terraform configuration updated
- Live infrastructure corrected
- Resource imported
- State repaired
- Resource retired
- Architectural exception documented

---

# Production Console Change

Manual Production Console change is exceptional.

Any permanent Production change must ultimately be reconciled with Terraform or
an explicitly approved external-management boundary.

---

# Drift Automation

Future automated drift detection may be implemented.

It must not automatically destroy or mutate Production merely because drift is
detected.

---

# Drift Remediation

Automatic drift remediation for destructive or privileged changes is prohibited
unless separately architected and approved.

---

# Deletion Boundary

Unknown, legacy, imported, or orphaned resources must not be deleted merely
because Terraform configuration does not contain them.

Deletion requires explicit evidence and authorization.

---

# Fail-Closed Requirement

Existing-resource governance must fail closed when:

- Ownership is unknown
- Environment is unknown
- Account is unknown
- Region is unknown
- State destination is ambiguous
- Import identity is incorrect
- Replacement risk is unresolved
- Data retention is unresolved
- Security dependency is unresolved

---

# Implementation Boundary

This section defines governance architecture only.

It does not yet:

- Run terraform import
- Run terraform state rm
- Run terraform state mv
- Import AWS resources
- Delete AWS resources
- Repair Terraform state
- Reconcile live drift
- Run Terraform apply

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

Future drift-monitoring automation may require Universal Runtime Registration
Standard assessment before runtime activation.

---

# Prohibited Practices

The following are prohibited:

- Blind recreation of existing AWS resources
- Unknown resources automatically destroyed
- Production resource imported into Development state
- Import without account/environment/region validation
- Broad ignore_changes used to hide security drift
- Emergency manual changes left unreconciled permanently
- Duplicate infrastructure created without discovery
- Data-bearing resources replaced without retention review
- Terraform state rm used merely to suppress plans
- Automatic destructive drift remediation without approved architecture
- Resource name treated as proof of ownership
- Security/audit infrastructure destroyed during Terraform adoption

---

# Canonical Decision Summary

Terraform must discover and classify existing infrastructure before adoption.

Drift must be investigated and reconciled.

Import must bind resource, account, environment, region, Terraform address, and
state correctly.

Unknown or destructive situations fail closed.

Terraform must never blindly recreate or destroy existing AWS infrastructure.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
