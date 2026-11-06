# LinkCraftor Cloud Production Isolation

Version: 1.0
Status: Canonical
Phase: Cloud Organization & Environment Isolation
Section: 2.5 Production Isolation
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS Production isolation architecture for
LinkCraftor.

PRODUCTION is a distinct security, identity, data, deployment, and operational
boundary.

---

# Architectural Authorities

This architecture consumes and preserves:

- Cloud Resource Organization
- 2.1 AWS Organization & Account Structure
- 2.2 Organizational Units
- 2.3 Environment Account Isolation
- 2.4 Shared Infrastructure Account Separation
- Phase 4 Cloud Identity & Access Infrastructure

---

# Core Rule

Production must remain independently governed from all lower environments.

Production authority must never be implied by access to another environment.

---

# Production Account

PRODUCTION is the canonical customer-facing Production AWS account.

It hosts or will host approved Production resources such as:

- Production APIs
- Production workloads
- Production databases
- Production object storage
- Production workers
- Production queues
- Production secrets
- Production observability components

Detailed service implementation belongs to later phases.

---

# Separate Account Boundary

Production must use a separate AWS account from:

- Development
- Testing
- Staging
- Sandbox

Production must not share an account with personal experimentation.

---

# Human Access Isolation

Production human access must be separately assigned.

The following must not automatically grant Production access:

- Development access
- Testing access
- Staging access
- Sandbox access
- Repository membership
- Customer product authority
- Generic AWS Organization membership

---

# Privileged Production Access

Production privileged access must be independently authorized.

ProductionAdministrator must remain distinct from:

- Development administrators
- Testing administrators
- Staging administrators
- Security administrators
- Network administrators
- Data administrators
- Emergency administrators

Role combination requires explicit justification.

---

# Workload Isolation

Production workloads require Production-specific workload identity and trust.

Development, Testing, or Staging workload identities must not automatically
operate in Production.

---

# Service Identity Isolation

Production service identities must be separately provisioned and governed.

A lower-environment service identity must not silently become a Production
service identity.

---

# Credential Isolation

Production credentials must remain distinct.

Lower-environment:

- Access keys
- Temporary sessions
- Role credentials
- Tokens
- Deployment credentials

must not automatically operate in Production.

---

# Secret Isolation

Production secrets must remain separately governed.

Development, Testing, Staging, and Sandbox must not reuse Production secrets as
the normal operating model.

---

# Data Isolation

Production customer data must remain protected from uncontrolled use in lower
environments.

Production data must not be copied into lower environments without an approved
process.

Approved alternatives may include:

- Synthetic data
- Masked data
- Sanitized data
- Minimized approved Production-derived data

---

# Database Isolation

Production databases must not be shared with Development, Testing, Staging, or
Sandbox.

Lower environments require their own approved database resources.

---

# Storage Isolation

Production object storage must not become ordinary Development or Testing
storage.

Production buckets and objects require Production-specific authorization.

---

# Queue Isolation

Production queues must not be automatically consumable by lower-environment
workers.

Production consumers require approved Production runtime and AWS authority.

---

# Runtime Isolation

Universal Runtime authorization does not automatically grant Production AWS
authority.

AWS Production credentials do not automatically authorize arbitrary Universal
Runtime execution.

Both authorization layers must remain independently enforceable.

---

# Deployment Isolation

Production deployment authority must remain independent from non-production
deployment authority.

Approved promotion path:

Development
→ Testing
→ Staging
→ Production

Artifacts may be promoted.

Credentials and identities are not promoted.

---

# Production CI/CD

Production CI/CD must use separately approved deployment identity.

A non-production CI/CD identity must not deploy to Production.

Repository membership alone must not grant Production deployment authority.

---

# Terraform Production Authority

Terraform mutation of Production requires separately approved Production
authority.

Development or non-production Terraform credentials must not mutate Production.

Terraform plan and apply authority must remain separately governable where
required.

---

# Network Isolation

Network connectivity to Production does not imply application or IAM authority.

Production network access must be explicitly approved.

Connectivity should be constrained by later networking architecture.

---

# Security Account Relationship

SECURITY may inspect or administer approved security capabilities affecting
Production.

Security visibility does not automatically grant unrestricted Production
application mutation authority.

---

# Log Archive Relationship

Production control-plane evidence must be delivered to independently governed
central evidence infrastructure where later implemented.

Production administrators must not be able to silently erase the only
authoritative audit copy.

---

# Shared Services Relationship

Production may consume explicitly approved Shared Services.

Shared Services must not become an unrestricted administrative path into
Production.

---

# Deployment Account Relationship

DEPLOYMENT may assume approved Production deployment authority.

The destination Production role and source Deployment identity must both be
explicitly governed.

---

# Production KMS Boundary

Production encryption authority must be separately governed.

Lower-environment identities must not automatically decrypt Production data.

---

# Production Root Boundary

Production root-user authority is exceptional.

Root must not be used for routine Production administration.

Emergency/root controls are governed by Phase 4.1.9 Emergency Cloud Access.

---

# Production Failure Containment

Failure or compromise in:

- Development
- Testing
- Staging
- Sandbox

must not automatically compromise Production.

Lower environments must not retain unrestricted Production authority.

---

# Production Trust Boundary

Every Production trust path must be explicit.

Trust may include:

- Human role assignment
- Workload trust
- CI/CD federation
- Cross-account role trust
- Resource policy
- KMS policy
- Service principal

Implicit trust is prohibited.

---

# Production Audit Attribution

Production administrative actions must be attributable.

Evidence should identify:

- Principal
- Role
- Session
- Source account
- Environment
- Region
- API action
- Resource
- Timestamp
- Result

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Production Access Review

Production access must be periodically reviewable.

Review should determine:

- Is access still required?
- Is privilege still appropriate?
- Is Production authority separately justified?
- Is any dormant privilege present?
- Can the role be reduced?
- Should the assignment be removed?

---

# Fail-Closed Requirement

Production access must fail closed when:

- Production authorization is absent
- Trust is missing
- Principal is unknown
- Role assignment is invalid
- Credential environment is wrong
- Workload identity is untrusted
- Session is expired
- Required approval is absent

---

# Terraform and IaC Boundary

Production account configuration, trust, roles, policies, and guardrails must
ultimately be represented through approved Terraform/IaC where applicable.

Phase 3 owns the Terraform implementation foundation.

---

# Implementation Boundary

This section defines architecture only.

It does not yet:

- Create Production resources
- Create Production IAM roles
- Create Production deployment roles
- Configure Production databases
- Configure Production storage
- Configure Production queues
- Configure Production KMS
- Configure Production networking
- Issue Production workload credentials
- Deploy Production workloads

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Production sharing an AWS account with lower environments
- Development authority automatically granting Production access
- Testing authority automatically granting Production access
- Staging authority automatically granting Production access
- Shared lower-environment and Production credentials
- Shared lower-environment and Production secrets
- Shared lower-environment and Production databases
- Non-production CI/CD deploying directly to Production
- Lower-environment Terraform credentials mutating Production
- Lower-environment workers consuming Production jobs automatically
- Production root used for routine administration
- Production audit evidence controlled only by Production administrators
- Repository membership treated as Production authorization

---

# Canonical Decision Summary

Production is an independently governed AWS security boundary.

Production human access, workload identity, service identity, credentials,
secrets, data, deployment authority, Terraform authority, encryption authority,
and audit evidence must remain separately controlled.

No lower environment automatically grants Production authority.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
