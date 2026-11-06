# LinkCraftor Terraform Testing & Validation

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.11 Terraform Testing & Validation
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical testing and validation architecture for
LinkCraftor Terraform.

Terraform configuration must be validated before infrastructure mutation.

Testing must cover syntax, structure, targeting, security, plan behavior,
modules, policy, and environment isolation.

---

# Architectural Authorities

This architecture consumes and preserves:

- 3.1 Terraform Authority & Source-of-Truth Model
- 3.2 Terraform Repository & Module Structure
- 3.3 Terraform State & Backend Architecture
- 3.4 Provider & Account Targeting Architecture
- 3.5 Environment Configuration Model
- 3.6 Module Boundaries & Reuse Rules
- 3.7 Plan / Apply Separation
- 3.8 Terraform Identity & Credential Model
- 3.9 Drift, Import & Existing-Resource Governance
- 3.10 Terraform Safety & Destructive-Change Controls

---

# Core Rule

Terraform must pass required validation before apply.

Successful syntax validation alone does not prove infrastructure safety.

---

# Validation Layers

The canonical validation model includes:

1. Formatting validation
2. Initialization validation
3. Terraform syntax/configuration validation
4. Variable validation
5. Provider/account targeting validation
6. Environment validation
7. State/backend validation
8. Module validation
9. Security/static analysis
10. Plan validation
11. Destructive-change review
12. Integration validation where appropriate

---

# terraform fmt

Terraform files must pass formatting checks.

Formatting consistency supports reviewability.

Formatting does not prove semantic correctness.

---

# terraform init

Initialization validates provider/module/backend preparation.

Init must not be treated as permission to apply.

Backend initialization must use the intended environment/state context.

---

# terraform validate

`terraform validate` must be part of normal Terraform validation.

It checks configuration consistency but does not prove:

- AWS permissions
- Correct live account
- Correct live region
- Security correctness
- Safe Production behavior

Additional validation remains required.

---

# Variable Validation

Security-sensitive variables should use Terraform validation where practical.

Examples include:

- Environment
- Region
- RegionRole
- Account class
- Production flags
- Allowed CIDRs
- Naming constraints

---

# Environment Validation

Testing must confirm that:

- Development targets DEVELOPMENT
- Testing targets TESTING
- Staging targets STAGING
- Sandbox targets SANDBOX
- Production targets PRODUCTION

---

# Account Validation

Once AWS account IDs exist, tests must validate canonical account-to-ID
mappings.

A wrong account must fail validation.

---

# Region Validation

Tests must preserve canonical regions:

- eu-west-1 — primary
- us-east-1 — disaster-recovery
- af-south-1 — future

The RegionRole value secondary must not be accepted.

---

# Production Region Validation

Testing must confirm:

- eu-west-1 is normal Production-serving region
- us-east-1 is DR-controlled
- af-south-1 remains future until activated

---

# Backend Validation

Tests must verify that:

- Environment uses correct backend
- State key is correct
- Production uses Production state
- Development cannot write Production state
- Organization state remains separately protected

---

# Provider Validation

Tests must verify:

- Explicit provider targeting
- Expected account
- Expected region
- Expected role
- No hidden Production fallback
- No static credentials embedded in provider configuration

---

# Caller Identity Validation

When connected to AWS during approved implementation testing, effective caller
identity should be verified before mutation.

Wrong identity must stop execution.

---

# Module Validation

Reusable modules must be tested independently where practical.

Tests should verify:

- Required inputs
- Safe defaults
- Outputs
- Provider behavior
- Validation rules
- Environment neutrality
- Production protections

---

# Module Reuse Testing

A reusable module used in multiple environments should demonstrate that reuse
does not merge:

- Accounts
- State
- Credentials
- Secrets
- Data
- Trust

---

# Negative Testing

Testing must include failure scenarios.

Examples include:

- Unknown environment
- Wrong account
- Wrong region
- Missing role
- Missing state configuration
- Invalid RegionRole
- Production with Development credentials
- Unauthorized cross-account trust
- Invalid destructive approval context

---

# Fail-Closed Testing

Fail-closed controls must be tested deliberately.

A safety rule that exists only in documentation is not implementation evidence.

---

# Static Analysis

Terraform static analysis should be used where appropriate.

Static analysis may identify:

- Public exposure
- Weak encryption
- IAM risk
- Missing logging
- Unsafe network rules
- Security misconfiguration

Exact tooling will be selected during implementation.

---

# Security Scanning

Terraform configuration should be scanned for security-sensitive issues before
Production apply.

Security scanning complements but does not replace architecture review.

---

# Secret Scanning

Source control and CI/CD should detect committed secrets.

Terraform files, tfvars, scripts, and generated artifacts must not contain
embedded AWS secrets.

---

# Policy Testing

Policy-oriented validation may be used for:

- IAM policies
- SCPs
- Resource policies
- KMS policies

Testing should verify expected allows and expected denies where practical.

---

# SCP Testing

SCP testing must include:

- Intended allowed operations
- Intended denied operations
- Emergency/recovery considerations
- Service dependencies
- Production lockout risk

---

# IAM Testing

IAM testing should verify:

- Least privilege
- Trust relationships
- PassRole restrictions
- Environment scope
- Cross-account boundaries
- Production isolation

---

# Plan Validation

Terraform plan is a primary validation artifact.

Plan review must identify:

- Resources added
- Resources changed
- Resources replaced
- Resources destroyed
- Security-sensitive policy changes
- Cross-account changes
- Region changes
- State-sensitive implications

---

# Plan Exit Behavior

Automation may use Terraform plan exit behavior to distinguish:

- Error
- No changes
- Changes present

The workflow must still inspect change risk.

---

# Plan JSON Analysis

Machine-readable plan output may be used for automated policy checks.

Automation may identify:

- Destruction
- Replacement
- Public exposure
- IAM expansion
- KMS changes
- Production-sensitive modifications

---

# Destructive Change Testing

Plans containing destroy or replace actions must trigger 3.10 controls.

---

# Test Fixtures

Modules may use safe fixtures for test scenarios.

Test fixtures must not include real Production secrets or uncontrolled
Production data.

---

# Sandbox Testing

SANDBOX may be used for controlled infrastructure experiments.

Sandbox use must still obey:

- Region guardrails
- Cost controls
- No Production credentials
- No Production data
- No Production trust

---

# Development Testing

Development should be the primary environment for early infrastructure
validation.

---

# Testing Environment

TESTING may validate automation, policy, module, integration, and infrastructure
behavior.

---

# Staging Validation

STAGING should provide the strongest pre-Production validation where practical.

Staging should approximate Production architecture without sharing Production:

- Account
- Credentials
- State
- Secrets
- Data authority

---

# Production Validation

Production validation must occur before and after approved apply.

Pre-apply validation proves the intended target and plan.

Post-apply validation confirms the expected infrastructure result.

---

# Post-Apply Validation

After apply, validation may include:

- Resource existence
- Correct account
- Correct region
- Correct configuration
- Logging enabled
- Encryption enabled
- Health status
- Expected trust
- Expected access restrictions

---

# Drift Validation

Periodic plan or approved drift detection may verify that infrastructure remains
aligned with Terraform.

---

# Existing Resource Testing

Before importing existing resources, validation must confirm:

- Resource identity
- Ownership
- Account
- Region
- Environment
- State destination
- Terraform address

---

# Import Validation

After import, a plan must determine whether Terraform intends unexpected
changes.

Unexpected replacement or deletion must stop progression.

---

# State Testing

Backend/state controls should be validated for:

- Access
- Isolation
- Versioning
- Encryption
- Public-access prevention
- Locking
- Recovery

---

# Recovery Testing

Terraform state recovery procedures should be tested under controlled conditions.

Recovery testing must not endanger Production state.

---

# CI/CD Validation Gates

CI/CD should enforce required checks before apply.

Potential gates include:

- fmt
- validate
- static analysis
- security scanning
- secret scanning
- plan
- destructive-change detection
- approval

---

# Required Check Failure

A required validation failure must block apply.

Warnings may require review depending on severity.

---

# Test Evidence

Validation evidence should record:

- Terraform version
- Provider versions
- Source revision
- Environment
- Account
- Region
- Backend/state
- Tests executed
- Results
- Plan summary
- Reviewer where required

---

# Repeatability

Tests should be reproducible where practical.

One-time manual validation must not become the only proof of long-term
infrastructure correctness.

---

# Test Isolation

Tests must not unintentionally mutate Production.

Tests requiring live AWS resources must use approved accounts and environments.

---

# Cost Safety

Infrastructure testing must consider resource cost.

Tests should clean up disposable resources through approved procedures.

---

# Test Cleanup

Cleanup must be explicit.

Automated cleanup must not destroy shared or Production resources.

---

# Version Upgrade Testing

Terraform and provider upgrades require validation before Production adoption.

Testing should identify:

- Plan changes
- Provider behavior changes
- State migration requirements
- Deprecated features
- Breaking changes

---

# Module Upgrade Testing

Module changes must be tested against known consumers where practical.

Production-impacting module upgrades require stronger review.

---

# Regression Testing

Infrastructure fixes should add regression tests where practical.

Repeated safety failures should not rely only on operator memory.

---

# Certification Evidence

Phase 3 certification must rely on actual verification evidence.

Architecture files alone are not sufficient to claim live Terraform or AWS
implementation.

---

# Fail-Closed Requirement

Validation must fail closed when:

- Required check fails
- Target environment is unknown
- Account cannot be verified
- Region is invalid
- State binding is wrong
- Provider identity is wrong
- Required approval is absent
- Destructive risk is unresolved
- Security scan has blocking findings

---

# Implementation Boundary

This section defines testing architecture only.

It does not yet:

- Install Terraform
- Run terraform init
- Run terraform validate
- Run terraform plan
- Configure scanners
- Configure CI/CD
- Apply AWS infrastructure
- Create live test resources

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

Future scheduled drift or compliance testing may require Universal Runtime
Registration Standard assessment before runtime activation.

---

# Prohibited Practices

The following are prohibited:

- Syntax validation treated as full certification
- Required failed check ignored for Production
- Production testing using Development credentials
- Test automation mutating Production unexpectedly
- Real Production secrets embedded in fixtures
- Import accepted without post-import plan
- Static analysis replacing architecture review entirely
- CI/CD apply proceeding after blocking test failure
- Cleanup destroying shared resources
- Terraform/provider upgrades reaching Production without validation
- Architecture-only evidence represented as live implementation evidence

---

# Canonical Decision Summary

Terraform configuration must pass layered validation before apply.

Testing covers formatting, syntax, variables, providers, accounts, environments,
regions, state, modules, security, policies, plans, destructive changes,
imports, and post-apply behavior.

Production apply is blocked when required validation fails.

Phase 3 certification must distinguish architecture certification from live AWS
implementation evidence.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
