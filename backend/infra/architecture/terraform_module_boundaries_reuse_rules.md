# LinkCraftor Terraform Module Boundaries & Reuse Rules

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.6 Module Boundaries & Reuse Rules
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical boundaries for reusable Terraform modules.

Modules must maximize safe reuse without collapsing account, environment,
security, or infrastructure responsibility boundaries.

---

# Core Rule

Terraform modules are reusable implementation units.

Modules must not become hidden governance authorities.

Root compositions determine approved account, environment, provider, region,
state, and security context.

---

# Module Responsibility

Each module should represent a cohesive infrastructure responsibility.

Examples may later include:

- VPC
- Subnet
- IAM role
- KMS key
- S3 bucket
- SQS queue
- ECS service
- Load balancer
- Database
- Monitoring component

A module should not mix unrelated infrastructure merely for convenience.

---

# Root Module vs Reusable Module

Reusable modules define infrastructure building blocks.

Root modules compose those building blocks for:

- Account
- Environment
- Region
- Governance scope

Root modules own target context.

Reusable modules must not secretly select target context.

---

# Provider Boundary

Reusable child modules must not define ungoverned provider configurations.

Provider configuration should generally be owned by the root composition and
passed explicitly where required.

---

# Account Boundary

Modules must not hardcode AWS Account IDs.

Account identity must come from canonical configuration.

Exceptions require explicit architecture approval.

---

# Environment Boundary

Modules must not hardcode Production behavior as the default.

Environment-specific behavior must be explicit through validated inputs.

---

# Region Boundary

Modules must not silently assume a region where region is security or
availability relevant.

Regional behavior must be explicit.

---

# Production Boundary

A reusable module may support Production, but it must not create Production
authority.

Production targeting and authorization remain root-level responsibilities.

---

# Security Boundary

Modules must not weaken:

- IAM boundaries
- Account isolation
- Environment isolation
- Region restrictions
- Encryption requirements
- Logging requirements
- State boundaries

Module convenience must never override security architecture.

---

# Module Inputs

Inputs should be:

- Explicit
- Typed
- Validated
- Documented
- Minimal
- Security-aware

Avoid broad unstructured maps for security-critical behavior where typed
variables provide stronger validation.

---

# Required Context Inputs

Modules may require explicit context such as:

- Environment
- Account class
- Region
- RegionRole
- Application
- Owner
- Tags

However, these values must not be blindly trusted for authorization.

---

# Module Outputs

Modules should expose only outputs required by consumers.

Sensitive outputs must be marked sensitive.

Modules must not expose credentials or secret values unnecessarily.

---

# Naming

Module resource naming should use approved naming inputs.

Names must remain deterministic where practical.

Module naming must not become the sole source of environment identity.

---

# Tagging

Modules should apply required governance tags where appropriate.

Core tags should not be removable accidentally by ordinary module callers.

---

# Module Defaults

Defaults must be safe.

A default must never:

- Select Production
- Enable public access
- Disable encryption
- Disable logging
- Permit wildcard trust
- Create destructive behavior
- Enable unrestricted cross-account access

---

# Optional Features

Optional module features must be disabled by default when they materially
increase privilege, exposure, cost, or blast radius.

---

# Public Exposure

Modules creating internet-accessible resources must require explicit
configuration.

Public access must never result from an accidental default.

---

# Encryption

Modules handling data should enable approved encryption defaults where
applicable.

Callers must not be able to disable required Production encryption casually.

---

# IAM Module Rules

IAM modules must not create universal administrator roles by default.

IAM modules must support:

- Explicit trust
- Least privilege
- Environment scope
- Account scope
- Region conditions where appropriate

---

# iam:PassRole Boundary

Modules granting iam:PassRole must restrict passable roles deliberately.

Wildcard PassRole must not be a generic module default.

---

# Resource Policy Rules

Modules generating resource policies must avoid broad principals by default.

Organization-wide trust requires explicit justification.

---

# KMS Module Rules

KMS modules must make key policy ownership explicit.

Cross-account KMS trust must be deliberately configured.

---

# Networking Module Rules

Networking modules may create connectivity.

They must not imply IAM authorization.

Network modules must preserve environment and account boundaries.

---

# Storage Module Rules

Storage modules must support:

- Encryption
- Public-access blocking where applicable
- Lifecycle controls
- Logging where required
- Environment isolation

Production storage must not default to public exposure.

---

# Queue Module Rules

Queue modules must support explicit producers and consumers.

Environment boundaries must be preserved.

Lower-environment workers must not automatically gain Production queue access.

---

# Compute Module Rules

Compute modules must accept approved workload identity rather than create
uncontrolled embedded credentials.

---

# Database Module Rules

Database modules must preserve environment isolation.

Production databases must not be shared with lower environments.

---

# Module Composition

Modules may compose other modules where responsibility remains clear.

Deep module nesting should be avoided when it obscures ownership or debugging.

---

# Circular Dependencies

Circular module dependencies are prohibited.

Cross-account and cross-environment dependencies must remain explicit.

---

# Duplicate Module Rule

Before creating a new module, existing modules must be reviewed.

Duplicate modules for the same responsibility should not be created without
clear justification.

---

# Module Version Control

Reusable modules must be version-controlled in Git.

Changes affecting multiple environments require impact review.

---

# Breaking Changes

Breaking module changes require:

- Explicit identification
- Consumer impact analysis
- Migration path
- Testing
- Production review where applicable

---

# Module Testing

Reusable modules should eventually support:

- terraform validate
- terraform fmt
- plan-based validation
- module tests
- static analysis
- policy checks

Detailed testing architecture is governed by 3.11.

---

# Environment Parity

Reuse should encourage consistency between environments.

Parity does not mean sharing credentials, state, data, or account authority.

---

# Production Reuse

The same reusable module may be used by Development and Production when safe.

The resulting resources remain separately instantiated through separate:

- Accounts
- Providers
- State
- Configuration
- Credentials

---

# Module Ownership

Every reusable module should have a defined infrastructure responsibility and
maintainer/owner.

Unowned modules must not become critical Production dependencies.

---

# Deprecation

Deprecated modules must be clearly identified.

Consumers should migrate through a controlled path.

Deprecated modules must not remain hidden long-term infrastructure dependencies.

---

# Module Removal

Module removal must not automatically destroy live resources.

Removal from configuration must be evaluated for destructive consequences.

---

# Security Review Trigger

Module changes require stronger review when they affect:

- IAM
- KMS
- Network exposure
- Public access
- Production
- Cross-account trust
- Logging
- Security services
- Data protection

---

# Fail-Closed Requirement

Module use must fail closed when:

- Required environment context is absent
- Required account context is absent
- Region context is invalid
- Security-critical input is invalid
- Production-specific protections are missing

---

# Implementation Boundary

This section defines module governance architecture only.

It does not yet:

- Create Terraform modules
- Deploy resources
- Configure providers
- Configure IAM
- Run Terraform
- Change AWS infrastructure

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Modules silently targeting Production
- Hardcoded AWS account IDs in generic modules
- Hidden provider creation
- Public exposure enabled by unsafe defaults
- Encryption disabled by unsafe defaults
- Wildcard IAM trust as module default
- Wildcard iam:PassRole as module default
- Module convenience bypassing account isolation
- Modules sharing Production and Development state
- Duplicate modules without review
- Removal of modules causing unreviewed destruction
- Unowned critical Production modules

---

# Canonical Decision Summary

Reusable Terraform modules must remain account-, environment-, and region-neutral
unless their purpose explicitly requires otherwise.

Root compositions provide target context.

Modules must use safe defaults, explicit inputs, strong validation, and
least-privilege behavior.

Reuse must never weaken Production isolation or cloud governance.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
