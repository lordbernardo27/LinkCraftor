# LinkCraftor Terraform Plan / Apply Separation

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.7 Plan / Apply Separation
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical separation between Terraform planning and
Terraform infrastructure mutation.

A Terraform plan is evidence of proposed change.

A Terraform apply is authorization to mutate infrastructure.

The two are not equivalent.

---

# Architectural Authorities

This architecture consumes and preserves:

- 3.1 Terraform Authority & Source-of-Truth Model
- 3.2 Terraform Repository & Module Structure
- 3.3 Terraform State & Backend Architecture
- 3.4 Provider & Account Targeting Architecture
- 3.5 Environment Configuration Model
- 3.6 Module Boundaries & Reuse Rules
- Phase 4 IAM Role Architecture
- Phase 4 Temporary Credentials
- Phase 4 Privileged Access

---

# Core Rule

Plan authority does not imply apply authority.

Terraform planning and Terraform application must remain separately governable.

---

# Terraform Plan

Terraform plan evaluates the intended difference between:

- Terraform configuration
- Terraform state
- Live provider-visible infrastructure

Plan must not itself be treated as approval to change infrastructure.

---

# Terraform Apply

Terraform apply performs infrastructure mutation.

Apply therefore requires stronger authorization and control than plan.

---

# TerraformPlanRole

TerraformPlanRole is the canonical planning identity class.

Its authority should be limited to what is necessary to:

- Read required Terraform state
- Read required AWS infrastructure metadata
- Refresh provider-visible state where required
- Calculate proposed changes
- Produce plan evidence

TerraformPlanRole should not receive general infrastructure mutation authority.

---

# TerraformApplyRole

TerraformApplyRole is the canonical mutation identity class.

It may receive additional permissions required to apply approved changes.

Apply authority must remain:

- Environment-specific
- Account-specific
- Region-aware
- Auditable
- Revocable

---

# Production Separation

Production planning and Production application must remain independently
controlled.

A person or workflow able to generate a Production plan must not automatically
be permitted to apply it.

---

# Non-Production Separation

Development, Testing, Staging, and Sandbox may use less restrictive approval
flows where appropriate.

They still must preserve the distinction between observation/planning and
mutation.

---

# Saved Plan Artifact

Where a saved Terraform plan artifact is used, apply should execute the reviewed
plan artifact rather than silently regenerating a different plan.

Plan artifact handling must preserve:

- Target environment
- Target account
- Target region
- Configuration revision
- Provider context
- State lineage
- Plan identity

---

# Plan Freshness

A plan must not remain valid indefinitely.

A plan may become stale when:

- Terraform configuration changes
- State changes
- Provider-visible infrastructure changes
- Credentials or authorization context changes
- Provider versions change
- Module versions change

Stale plans must be regenerated.

---

# Source Revision Binding

Plan evidence should be bound to the source-control revision from which it was
generated.

An apply must not silently use code materially different from the reviewed plan.

---

# Backend Binding

Plan and apply must use the intended backend and state boundary.

A plan generated against Development state must not be applied against
Production state.

---

# Account Binding

Plan and apply must target the same approved AWS account.

Account substitution between plan and apply is prohibited.

---

# Environment Binding

Plan and apply must preserve the same canonical environment.

An artifact generated for Staging must not become a Production apply artifact.

---

# Region Binding

Plan and apply must preserve approved region targeting.

A plan for eu-west-1 must not silently apply to another region.

---

# Provider Binding

Provider identity and aliases must remain consistent between plan and apply.

Ambiguous provider substitution is prohibited.

---

# Approval Boundary

Approval requirements must reflect risk.

Production apply should require explicit approval appropriate to the change.

High-risk infrastructure changes may require additional reviewers.

---

# Separation of Duties

Where practical, sensitive Production changes should preserve separation between:

- Author
- Reviewer
- Approver
- Apply executor

A single person may perform multiple functions only where approved by the
privileged-access model and risk level.

---

# CI/CD Boundary

CI/CD may generate plans automatically.

Automatic plan generation must not automatically authorize Production apply.

Production apply must pass its independent authorization gate.

---

# Local Apply Boundary

Routine Production apply from unmanaged local developer terminals is prohibited.

Approved emergency or controlled administrative use must remain exceptional and
audited.

---

# Plan Evidence

Plan evidence should identify:

- Source revision
- Environment
- Account
- Region
- Backend/state
- Terraform version
- Provider versions
- Planned additions
- Planned changes
- Planned destructions

---

# Destructive Plan Escalation

Plans containing destruction or replacement require elevated review according to
3.10 Terraform Safety & Destructive-Change Controls.

---

# No-Change Plan

A no-change plan may provide evidence that configuration and live state are
aligned at that point in time.

It does not permanently certify absence of drift.

---

# Failed Plan

A failed plan must not be manually converted into an apply authorization.

The underlying error must be resolved.

---

# Apply Failure

A partially failed apply requires investigation before another apply is
attempted.

Operators must not blindly rerun until infrastructure and state are understood.

---

# State Locking

Apply must respect the canonical state-locking model from 3.3.

Failure to obtain the required lock must stop apply.

---

# Concurrent Apply Boundary

Concurrent applies against the same Terraform state are prohibited.

---

# Apply Logging

Terraform apply evidence must be retained sufficiently to identify:

- Who initiated it
- What source revision was used
- What plan was approved
- Which account/environment/region was targeted
- What result occurred

AWS CloudTrail provides independent AWS control-plane evidence.

---

# Emergency Apply

Emergency infrastructure mutation remains subject to emergency-access governance.

Emergency status must not silently disable:

- Account validation
- Environment validation
- Region validation
- State protection
- Audit logging

---

# Fail-Closed Requirement

Apply must fail closed when:

- Approved plan is absent where required
- Plan is stale
- Account differs
- Environment differs
- Region differs
- Backend differs
- Source revision differs materially
- Apply identity is unauthorized
- Production approval is absent
- Required state lock cannot be acquired

---

# Implementation Boundary

This section defines execution governance architecture only.

It does not yet:

- Create TerraformPlanRole
- Create TerraformApplyRole
- Configure CI/CD approval gates
- Generate live plans
- Execute terraform apply
- Mutate AWS infrastructure

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Plan authority treated as apply authority
- Production plan automatically applied without independent authorization
- Development plan applied to Production
- Account substitution after planning
- Region substitution after planning
- Backend/state substitution after planning
- Applying materially different code than reviewed
- Blind rerun after partially failed apply
- Concurrent applies against the same state
- Routine unmanaged local Production apply
- Stale plan treated as indefinitely valid
- Emergency mode disabling audit or target validation

---

# Canonical Decision Summary

Terraform plan and Terraform apply are separate control stages.

TerraformPlanRole provides planning authority.

TerraformApplyRole provides approved mutation authority.

Production apply requires independent validation and authorization.

Plan/account/environment/region/state/source context must remain consistent from
review through apply.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
