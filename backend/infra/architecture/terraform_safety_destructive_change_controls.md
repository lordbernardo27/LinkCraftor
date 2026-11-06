# LinkCraftor Terraform Safety & Destructive-Change Controls

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.10 Terraform Safety & Destructive-Change Controls
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical Terraform safety controls that protect
LinkCraftor infrastructure against accidental deletion, replacement, privilege
escalation, wrong-target execution, unsafe drift remediation, and uncontrolled
Production mutation.

---

# Architectural Authorities

This architecture consumes and preserves:

- 3.1 Terraform Authority & Source-of-Truth Model
- 3.3 Terraform State & Backend Architecture
- 3.4 Provider & Account Targeting Architecture
- 3.5 Environment Configuration Model
- 3.6 Module Boundaries & Reuse Rules
- 3.7 Plan / Apply Separation
- 3.8 Terraform Identity & Credential Model
- 3.9 Drift, Import & Existing-Resource Governance
- Phase 4 Privileged Access
- Phase 4 Emergency Cloud Access

---

# Core Rule

Destructive or privilege-expanding Terraform changes must not proceed silently.

High-risk changes require explicit evidence, validation, and authorization.

---

# Destructive Change Definition

A destructive change includes Terraform actions that may:

- Delete infrastructure
- Replace infrastructure
- Recreate infrastructure
- Destroy data-bearing resources
- Disable security controls
- Remove logging
- Remove encryption
- Revoke recovery capability
- Break networking
- Change trust boundaries
- Reduce availability
- Remove backup capability
- Destroy state or state protection

---

# Privilege-Expanding Change Definition

Privilege-expanding changes include:

- Broader IAM permissions
- Broader trust policies
- Broader resource policies
- Broader KMS permissions
- Wildcard principals
- Expanded iam:PassRole
- Cross-account access expansion
- Production access expansion
- Security-control bypass

These changes require security-sensitive review even when they are not
technically destructive.

---

# Plan Action Review

Terraform plans must be inspected for:

- create
- update
- replace
- destroy
- recreate
- unknown or deferred values affecting security

Destruction count alone is insufficient.

Replacement may be more dangerous than deletion where data or identity is
involved.

---

# Production Destructive Changes

Any Production plan containing destruction or replacement must receive
heightened review.

Production destructive change must not proceed merely because terraform plan
completed successfully.

---

# Organization-Level Changes

Terraform changes affecting:

- AWS Organizations
- Organizational Units
- SCPs
- Account placement
- Delegated administrators

require heightened governance because they may affect multiple accounts.

---

# IAM Safety

Terraform IAM changes must be reviewed for:

- Privilege escalation
- Wildcard actions
- Wildcard resources
- Wildcard trust
- PassRole expansion
- Cross-account trust expansion
- Removal of permissions boundaries
- New administrative roles

---

# KMS Safety

KMS changes require heightened review.

Unsafe KMS modification may:

- Lock out data
- Break services
- Destroy recoverability
- Expand decrypt authority

KMS key deletion or disabling must not occur casually.

---

# State Safety

Terraform state must not be:

- Deleted casually
- Replaced without backup/recovery evidence
- Manually edited without controlled procedure
- Moved between environments without validation

---

# prevent_destroy

Terraform lifecycle `prevent_destroy` may be used for critical resources where
appropriate.

It should be considered for resources such as:

- Production databases
- Critical state infrastructure
- Log archives
- Backup infrastructure
- Security-critical resources
- Long-lived encryption resources

It must not be used blindly as a substitute for governance.

---

# create_before_destroy

`create_before_destroy` may be used where replacement can be made safely.

It must not be assumed safe for all resource types.

Cost, naming collisions, quotas, and dependency behavior must be considered.

---

# replace_triggered_by

Replacement triggers must be explicit and reviewed.

They must not cause broad hidden replacement cascades.

---

# lifecycle Ignore Boundary

`ignore_changes` must not hide:

- Security drift
- IAM drift
- Encryption drift
- Public-access changes
- Production trust changes
- Critical logging changes

---

# Resource Deletion Protection

Where AWS services provide native deletion protection, Production use should be
considered according to the resource type.

Examples may include:

- Databases
- Load balancers where applicable
- Backup vaults
- Critical storage or recovery resources

Terraform lifecycle controls and AWS-native controls may both be used.

---

# Data-Bearing Resource Safety

Data-bearing resources require heightened protection.

Examples include:

- S3 buckets
- Databases
- EBS volumes
- File systems
- Backup vaults

Destruction or replacement requires retention and recovery review.

---

# Backup Verification Before Destruction

Where a resource contains critical data, required backup or recovery evidence
must exist before approved destruction.

A backup assumption without evidence is insufficient.

---

# S3 Safety

Critical S3 resources must not be destroyed while containing required data.

Terraform must not casually use force-destroy behavior for Production data.

---

# Database Safety

Production database destruction or replacement requires explicit review.

Where supported and appropriate, deletion protection and final snapshot
requirements should be used.

---

# Network Safety

Destructive changes to:

- VPCs
- Subnets
- Route tables
- Gateways
- Security groups
- Network ACLs
- Load-balancer dependencies

must consider service connectivity and blast radius.

---

# Security Service Safety

Terraform must not silently disable or destroy:

- CloudTrail
- Security monitoring
- Log delivery
- Detection infrastructure
- Audit storage
- Security evidence

---

# Production Access Safety

Terraform changes must not create hidden Production access paths.

Any new Production trust or access path must be explicit.

---

# Cross-Account Safety

Cross-account trust changes require:

- Source identification
- Destination identification
- Purpose
- Least privilege
- Review
- Auditability

---

# SCP Safety

SCP explicit deny may override administrative and emergency IAM permissions.

SCP changes must therefore be staged and tested carefully.

A careless SCP must not lock out required recovery paths.

---

# Wrong-Target Protection

Before apply, Terraform must validate:

- Environment
- Account
- Region
- Backend
- State
- Role
- Source revision

Wrong-target execution must fail closed.

---

# Production Confirmation

Production apply must require an explicit Production execution context.

It must not rely on an accidental current shell profile.

---

# Destructive Threshold

Automation may detect plans containing destructive actions.

Thresholds may trigger stronger approval.

Thresholds must not be used to permit "small" destructive changes automatically
when the affected resource is critical.

---

# Replacement Cascade

A plan that causes many dependent replacements must be treated as elevated risk.

The operator must understand dependency effects before apply.

---

# Terraform Target Flag

Routine use of `-target` is discouraged.

Targeted operations may bypass normal dependency evaluation.

Use requires a specific operational reason.

---

# Auto-Approve

`terraform apply -auto-approve` must not be the default Production workflow.

Automation may use noninteractive apply only after an independent approved gate
has already authorized the exact plan.

---

# Destroy Command

`terraform destroy` is highly privileged.

Routine Production use is prohibited.

Any approved destructive environment teardown must validate:

- Environment
- Account
- State
- Data retention
- Dependencies
- Backups
- Approval

---

# State Commands

Commands such as:

- terraform state rm
- terraform state mv
- terraform import
- terraform force-unlock

must follow their respective governance controls.

---

# Lock Bypass

State locking must not be bypassed casually.

If locking is unavailable, apply must stop unless an approved recovery procedure
explicitly authorizes intervention.

---

# Failed Apply Safety

A failed apply may leave partial infrastructure changes.

Operators must inspect:

- Terraform state
- AWS resources
- Error output
- Dependencies

before retrying.

---

# Rollback Boundary

Terraform rollback is not equivalent to application-code rollback.

Infrastructure rollback may itself be destructive.

Rollback must therefore be planned and validated.

---

# Emergency Changes

Emergency changes may accelerate approval but must not eliminate:

- Identity validation
- Account validation
- State protection
- Logging
- Evidence
- Post-event reconciliation

---

# Change Evidence

High-risk change evidence should identify:

- Plan artifact
- Source revision
- Environment
- Account
- Region
- State
- Reviewer
- Approval
- Destructive actions
- Privilege changes
- Backup/recovery evidence
- Final result

---

# Fail-Closed Requirement

Terraform apply must fail closed when:

- Target identity is ambiguous
- Environment mismatch exists
- Account mismatch exists
- Region mismatch exists
- State mismatch exists
- Destructive change lacks required approval
- Critical backup requirement is unresolved
- Privilege expansion is unreviewed
- Security-control removal is unreviewed
- Required lock cannot be acquired

---

# Implementation Boundary

This section defines safety architecture only.

It does not yet:

- Configure lifecycle blocks
- Enable AWS deletion protection
- Configure CI/CD gates
- Create backup policies
- Execute Terraform
- Delete AWS resources
- Replace AWS resources
- Modify Production

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Blind Production destroy
- Unreviewed replacement of data-bearing resources
- Production auto-approve as normal workflow
- Routine terraform destroy in Production
- force_destroy enabled casually on Production storage
- Broad ignore_changes hiding security drift
- Terraform target used as normal deployment strategy
- SCP changes applied without lockout review
- IAM privilege expansion without review
- KMS destructive change without recovery analysis
- Failed apply blindly rerun
- Wrong-target apply allowed to continue
- Emergency mode disabling auditability

---

# Canonical Decision Summary

Terraform destructive and privilege-expanding changes require heightened
controls.

Production changes must preserve identity, account, environment, region, state,
backup, recovery, and approval safety.

Critical resources may use Terraform lifecycle protections and AWS-native
deletion protections.

Unknown or unsafe destructive conditions fail closed.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
