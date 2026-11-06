# LinkCraftor Terraform Provider & Account Targeting Architecture

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.4 Provider & Account Targeting Architecture
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines how Terraform targets AWS accounts and regions safely.

Provider configuration must make the destination account, region, role, and
environment explicit.

Terraform must never silently default to Production.

---

# Architectural Authorities

This architecture consumes and preserves:

- Phase 2 certified AWS account architecture
- 3.1 Terraform Authority & Source-of-Truth Model
- 3.2 Terraform Repository & Module Structure
- 3.3 Terraform State & Backend Architecture
- Phase 4 IAM Role Architecture
- Phase 4 Temporary Credentials
- Phase 4 Cross-Environment Restrictions

---

# Core Rule

Terraform provider targeting must be explicit.

Terraform must know:

- AWS account
- Environment
- Region
- Role
- Execution identity

before infrastructure mutation is permitted.

---

# Canonical AWS Accounts

Terraform must preserve the canonical accounts:

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

Account targeting must use stable technical identifiers once AWS account IDs
exist.

Display names alone must not become the sole target authority.

---

# Canonical Regions

Canonical regions remain:

- eu-west-1 — primary
- us-east-1 — disaster-recovery
- af-south-1 — future

RegionRole values are:

- primary
- disaster-recovery
- future

The value secondary is noncanonical.

---

# Provider Configuration

Provider configuration must declare intended AWS region.

Where role assumption is required, provider configuration must also identify
the intended target role.

Provider configuration must not contain long-lived credentials.

---

# Default Provider Boundary

A default AWS provider may exist only where its scope is unambiguous.

The default provider must never create a path where an omitted provider alias
silently targets Production.

Modules capable of operating across accounts or regions must use explicit
provider passing.

---

# Provider Aliases

Provider aliases must be meaningful and deterministic.

Examples may represent:

- Account
- Environment
- Region
- Control-plane responsibility

Aliases such as generic "aws2" or "other" are prohibited where they obscure
target identity.

---

# Production Provider

Production provider configuration must be separately defined.

Production provider configuration must not reuse Development authority.

Production targeting must require an approved Production role.

---

# Non-Production Providers

Development, Testing, Staging, and Sandbox provider configurations must remain
separate.

Access to one provider configuration must not imply access to another.

---

# Organization Provider

AWS Organizations-level Terraform must use an approved management or delegated
administration provider.

Organization provider authority must not be used for ordinary workload
infrastructure.

---

# Security Provider

SECURITY account provider authority must remain scoped to approved security
functions.

Security provider configuration must not automatically grant Production
application authority.

---

# Log Archive Provider

LOG-ARCHIVE provider authority must remain focused on audit and evidence
infrastructure.

Ordinary workload deployment identities must not receive unrestricted Log Archive
administration.

---

# Network Provider

NETWORK provider authority must remain distinct from application, IAM, and data
administration.

Network reachability does not imply resource authorization.

---

# Shared Services Provider

SHARED-SERVICES provider configuration must not become a universal bridge to
Production.

Cross-account Production access requires explicit destination trust.

---

# Deployment Provider

DEPLOYMENT may use provider configurations that assume approved destination
deployment roles.

Production deployment roles must remain separate from non-production roles.

---

# Role Assumption

Cross-account provider targeting should use approved temporary role assumption.

The provider must not rely on shared static access keys.

---

# Terraform Execution Identity

Provider targeting and Terraform execution identity are separate concepts.

The execution identity may run from:

- Human administrative session
- CI/CD federation
- Terraform automation role

but destination account authority must still be explicit.

---

# Account Validation

Terraform must validate that the authenticated account matches the intended
target.

An unexpected account must cause execution to stop.

---

# Region Validation

Terraform must validate that the selected region is allowed for the target
environment and workload purpose.

Unknown or unauthorized region selection must fail closed.

---

# Production Validation

Before Production mutation, Terraform must confirm:

- Environment is Production
- Account is PRODUCTION
- Intended Production role is active
- Region is approved
- Backend state is Production state
- Configuration is Production configuration

Any mismatch must stop execution.

---

# Environment / Account Binding

Each environment must map to its approved AWS account.

Canonical bindings include:

- development → DEVELOPMENT
- testing → TESTING
- staging → STAGING
- sandbox → SANDBOX
- production → PRODUCTION

Supporting infrastructure accounts use their own explicit bindings.

---

# Region / Environment Binding

Environment does not automatically define region.

Environment and region remain separate configuration dimensions.

Production may use:

- eu-west-1 for normal primary operation
- us-east-1 for approved DR use

af-south-1 remains future until activated.

---

# Provider Passing to Modules

Reusable modules must not instantiate hidden provider configuration.

Root compositions should pass providers explicitly where required.

This keeps account and region targeting visible.

---

# Cross-Region Provider Use

Resources spanning approved regions must use explicit aliased providers.

Cross-region configuration must not depend on implicit provider inheritance.

---

# Cross-Account Provider Use

Cross-account operations must use explicit provider aliases and explicit trust.

Organization membership alone is insufficient.

---

# aws_caller_identity Validation

Terraform may use AWS caller-identity data to validate the effective account ID.

Account validation must compare actual identity against approved configuration.

---

# Partition Boundary

The canonical initial AWS partition is:

aws

Other AWS partitions must not be targeted without explicit architecture approval.

---

# Credentials Boundary

Provider configuration must not contain:

- Access key ID
- Secret access key
- Session token
- Long-lived static credentials

Credentials must be obtained through approved identity mechanisms.

---

# Backend / Provider Separation

Terraform backend authority and provider authority are distinct.

Access to state does not imply permission to mutate AWS resources.

Permission to mutate AWS resources does not automatically imply state access.

---

# CI/CD Targeting

CI/CD must bind deployment workflow to intended:

- Repository
- Environment
- Account
- Region
- Role

Production workflows must not allow arbitrary account substitution.

---

# Fail-Closed Requirement

Terraform targeting must fail closed when:

- Account cannot be validated
- Region cannot be validated
- Environment is unknown
- Role is missing
- Production identity is absent
- Provider alias is ambiguous
- Backend and target environment disagree
- Target account differs from approved account

---

# Implementation Boundary

This section defines provider targeting architecture only.

It does not yet:

- Configure providers.tf
- Create IAM roles
- Assume AWS roles
- Authenticate to AWS
- Execute terraform init
- Execute terraform plan
- Execute terraform apply
- Modify live AWS resources

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Unknown provider defaulting to Production
- Hidden account targeting
- Hidden region targeting
- Production provider using Development credentials
- Static credentials embedded in provider blocks
- Generic ambiguous provider aliases
- Modules silently creating their own ungoverned providers
- Cross-account operations without explicit trust
- Region authorization treated as environment authorization
- Backend access treated as AWS resource authority
- AWS resource authority treated as state access
- Arbitrary CI/CD Production account substitution

---

# Canonical Decision Summary

Terraform provider configuration must make account, environment, region, role,
and execution identity explicit.

Production targeting is independently validated.

Provider aliases must clearly identify intended account and region.

Unknown target state must never fall through to Production.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
