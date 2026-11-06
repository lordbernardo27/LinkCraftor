# LinkCraftor Cloud Environment Account Isolation

Version: 1.0
Status: Canonical
Phase: Cloud Organization & Environment Isolation
Section: 2.3 Environment Account Isolation
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS environment account-isolation
architecture for LinkCraftor.

It establishes separate account boundaries for:

- Development
- Testing
- Staging
- Sandbox
- Production

Supporting Security, Log Archive, Network, Shared Services, and Deployment
accounts remain separately governed.

---

# Core Rule

Production must remain isolated from lower environments.

Development, Testing, Staging, Sandbox, and Production must not share the same
AWS account.

---

# Development Isolation

DEVELOPMENT hosts development workloads only.

Development identities must not automatically access Production.

Development resources must not become dependencies that Production requires for
normal operation unless explicitly architected through an approved shared
service.

---

# Testing Isolation

TESTING hosts automated, integration, and failure-testing workloads.

Testing credentials must not automatically operate in Production.

Production customer credentials must not be used as test identities.

---

# Staging Isolation

STAGING provides a controlled pre-production environment.

Staging must approximate Production where useful without becoming Production.

Production secrets and unrestricted customer data must not automatically be
copied to Staging.

---

# Sandbox Isolation

SANDBOX is experimentation space.

Sandbox must have:

- No unrestricted Production data
- No Production credentials
- No Production secrets
- No implicit Production trust
- Strict cost controls
- Appropriate lifecycle controls

---

# Production Isolation

PRODUCTION is the customer-facing environment.

Production must have:

- Separate AWS account
- Separate IAM assignments
- Separate workload identities
- Separate temporary credentials
- Separate secrets
- Separate deployment authority
- Separate audit evidence
- Separate production trust

---

# Human Access Separation

Human access must remain environment-specific.

Development access does not imply:

- Testing access
- Staging access
- Production access

Production human access must be separately assigned.

---

# Service Identity Separation

Service identities must remain scoped to their approved environment.

A Development service identity must not automatically operate in Production.

Production service identities must be separately provisioned.

---

# Workload Identity Separation

Workload identities must remain environment-specific.

A lower-environment workload must not assume a Production role unless an
explicit approved architecture permits a narrowly scoped interaction.

---

# Temporary Credential Separation

Temporary credentials must remain environment-scoped.

Development sessions must not be reused in Production.

Production sessions require independently approved role assignment or workload
trust.

---

# Privileged Access Separation

Privileged Production authority must be independently granted.

Development, Testing, and Staging privileged access must not imply Production
privilege.

---

# CI/CD Separation

Non-production CI/CD authority must not deploy to Production.

Production deployment requires dedicated approved Production deployment
identity.

Repository membership alone must not grant Production deployment authority.

---

# Terraform Separation

Terraform execution must preserve account and environment boundaries.

Development Terraform credentials must not automatically mutate Production.

Production Terraform execution requires independently approved authority.

---

# Data Isolation

Production customer data must not freely flow into lower environments.

Use where appropriate:

- Synthetic datasets
- Sanitized datasets
- Masked datasets
- Minimized approved production-derived data

Shared databases between Development, Staging, and Production are prohibited.

---

# Secret Isolation

Environment secrets must remain separate.

Production secrets must not be reused in lower environments as the normal model.

---

# KMS Isolation

Lower-environment identities must not automatically decrypt Production data.

Production encryption-key policies must preserve account and environment
boundaries.

---

# Storage Isolation

Production storage must not become general development or testing storage.

Lower environments require separately governed storage.

---

# Queue Isolation

Queues and asynchronous infrastructure must preserve environment identity and
authorization boundaries.

A lower-environment worker must not consume Production jobs unless explicitly
authorized by an approved architecture.

---

# Runtime Isolation

Universal Runtime authorization and AWS environment authorization remain separate.

A runtime-authorized worker does not automatically obtain Production AWS
authority.

AWS Production credentials do not automatically authorize arbitrary runtime
execution.

---

# Network Isolation

Network connectivity does not imply IAM trust.

Even where environments share approved network connectivity, identity and
authorization boundaries remain mandatory.

---

# Cross-Environment Access

Any legitimate cross-environment access must be:

- Explicit
- Narrowly scoped
- Auditable
- Justified
- Reviewable
- Revocable

Implicit cross-environment access is prohibited.

---

# Production Promotion

Approved artifacts may be promoted through:

Development
→ Testing
→ Staging
→ Production

Credentials and identities are not promoted.

Production deployment must use Production authority.

---

# Production Failure Isolation

Failure in Development, Testing, Staging, or Sandbox should not automatically
compromise Production.

Lower environments must not hold credentials that permit unrestricted Production
control.

---

# Security and Logging Independence

Security and Log Archive services must remain independently governed from
ordinary environment accounts.

Production administrators must not be able to silently erase centralized audit
evidence.

---

# Shared Services Boundary

Shared Services may support multiple environments.

Shared Services must not become an uncontrolled privilege bridge.

Production access from Shared Services must use explicit trust.

---

# Network Boundary

NETWORK may provide central networking capabilities.

Network authority must not automatically imply Production application, database,
IAM, or data authority.

---

# Deployment Boundary

DEPLOYMENT governs approved deployment capability.

Production deployment authority must remain separately controlled from
non-production deployment authority.

---

# Fail-Closed Requirement

Cross-environment access must fail closed.

Access must be denied when:

- Source environment is unknown
- Target environment is unknown
- Trust is absent
- Production authorization is absent
- Role assignment is missing
- Credential scope is wrong
- Workload trust is invalid
- Required approval is absent

---

# Audit Attribution

Environment-crossing actions must be attributable.

Evidence should identify:

- Principal
- Source account
- Target account
- Source environment
- Target environment
- Role
- Session
- API action
- Resource
- Result
- Timestamp

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Terraform and IaC Boundary

Account-level environment isolation, IAM trust, resource policy, and related
guardrails must ultimately be represented through approved Terraform/IaC where
applicable.

Phase 3 owns the Terraform implementation foundation.

---

# Implementation Boundary

This section defines architecture only.

It does not yet:

- Create environment AWS accounts
- Move accounts into OUs
- Configure SCPs
- Configure IAM trust
- Configure cross-account roles
- Create environment networks
- Create environment databases
- Create environment secrets
- Deploy Production workloads

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Phase Dependencies

2.1 defines canonical account structure.

2.2 defines Organizational Units.

2.3 defines environment account isolation.

Phase 3 provides Terraform/IaC implementation.

Phase 4 identity architecture defines IAM rules that operate across these
boundaries.

---

# Prohibited Practices

The following are prohibited:

- Development and Production sharing one AWS account
- Testing and Production sharing one AWS account
- Staging and Production sharing one AWS account
- Sandbox and Production sharing one AWS account
- Development credentials controlling Production
- Testing credentials controlling Production
- Staging credentials controlling Production
- Shared Production and lower-environment secrets
- Shared lower-environment and Production databases
- Non-production CI/CD identity deploying to Production
- Lower-environment Terraform authority mutating Production
- Network connectivity treated as identity authorization
- Lower-environment workers automatically consuming Production jobs
- Production audit evidence controlled only by Production administrators

---

# Canonical Decision Summary

LinkCraftor shall maintain separate AWS accounts for Development, Testing,
Staging, Sandbox, and Production.

Production is an independently governed security boundary.

Human identities, workload identities, service identities, credentials, secrets,
data, deployment authority, Terraform authority, and audit controls must preserve
that separation.

Supporting Security, Log Archive, Network, Shared Services, and Deployment
accounts remain separately governed.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL

---

# Simulation Lab Isolation Amendment

Status: CANONICAL

Simulation Lab is a dedicated pre-production environment.

Its purpose is controlled simulation of production-like conditions without
becoming Production.

Required isolation rules:

- Separate AWS account identity
- Separate Terraform environment root
- Separate Terraform state boundary
- Separate IAM roles
- Separate workload identities
- No Production credential reuse
- No silent cross-environment role assumption
- No direct Production customer traffic
- No automatic use of Production secrets
- No automatic use of Production customer data
- Synthetic or explicitly approved test datasets only by default
- Production-equivalent controls may be simulated without granting Production authority

Promotion relationship:

DEVELOPMENT
    |
    v
TESTING
    |
    v
STAGING
    |
    v
SIMULATION-LAB
    |
    v
PRODUCTION

SANDBOX remains outside the formal promotion chain and is used for isolated
experimentation.

Marker:
SIMULATION-LAB-ISOLATION-CANONICAL

