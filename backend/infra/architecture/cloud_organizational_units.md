# LinkCraftor Cloud Organizational Units

Version: 1.0
Status: Canonical
Phase: Cloud Organization & Environment Isolation
Section: 2.2 Organizational Units
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS Organizations Organizational Unit
architecture for LinkCraftor.

OUs provide governance groupings.

They do not themselves grant IAM permissions.

---

# Core Rule

Organizational Units are governance boundaries used for:

- Service Control Policies
- Account grouping
- Governance inheritance
- Security controls
- Environment separation
- Compliance controls

OU membership must not be treated as identity authorization.

---

# Canonical OU Structure

Canonical organization structure:

ROOT
├── Security OU
│   ├── SECURITY
│   └── LOG-ARCHIVE
│
├── Infrastructure OU
│   ├── NETWORK
│   ├── SHARED-SERVICES
│   └── DEPLOYMENT
│
├── Non-Production OU
│   ├── DEVELOPMENT
│   ├── TESTING
│   ├── STAGING
│   └── SANDBOX
│
└── Production OU
    └── PRODUCTION

LINKCRAFTOR-MANAGEMENT remains the Organizations management account and is not
treated as an ordinary member account.

---

# Security OU

Security OU contains:

- SECURITY
- LOG-ARCHIVE

Its controls should prioritize:

- Security-service protection
- Audit-evidence protection
- Restricted mutation
- Restricted account movement
- Restricted disabling of security controls

---

# Infrastructure OU

Infrastructure OU contains:

- NETWORK
- SHARED-SERVICES
- DEPLOYMENT

These accounts provide shared infrastructure capabilities.

Infrastructure OU membership must not imply unrestricted Production access.

---

# Non-Production OU

Non-Production OU contains:

- DEVELOPMENT
- TESTING
- STAGING
- SANDBOX

The OU must remain separate from Production.

Policies may be less restrictive than Production where experimentation requires
it, but may never create uncontrolled Production access.

---

# Production OU

Production OU contains:

- PRODUCTION

Production OU receives the strongest operational protection appropriate to
customer-facing workloads.

Production governance must not be weakened merely to simplify development.

---

# Management Account Boundary

The AWS Organizations management account remains outside normal workload OU
placement.

Its privileges must be tightly controlled.

Routine workloads must not execute there.

---

# OU Movement

Moving an account between OUs is a security-sensitive action.

Account movement must be:

- Explicit
- Authorized
- Audited
- Reviewed

Production accounts must not be moved into weaker governance boundaries without
approved change control.

---

# SCP Attachment

Service Control Policies may be attached at:

- Root
- OU
- Account

SCPs define permission ceilings.

They do not grant IAM authority.

Detailed SCP architecture is governed by Phase 2.7.

---

# Environment Isolation

OU structure reinforces but does not replace account isolation.

Development, Testing, Staging, Sandbox, and Production remain distinct accounts.

---

# Security Separation

Security and Log Archive accounts must not be placed under a weaker
Non-Production governance boundary.

---

# Production Separation

Production must not share the Non-Production OU.

Production must remain independently governable.

---

# Future Expansion

Future accounts may be introduced where justified.

Examples may include:

- Additional Production accounts
- Additional security accounts
- Regional specialized accounts
- Enterprise-specific infrastructure accounts

Any new account must be intentionally assigned to an approved OU.

---

# Account Placement Validation

Every member account must have an approved OU placement.

Unclassified accounts must not remain indefinitely at the organization root.

---

# Terraform and IaC Boundary

OU creation, account placement, and SCP attachment must ultimately be
represented through approved Terraform/IaC where supported.

Phase 3 owns the Terraform implementation foundation.

---

# Implementation Boundary

This section defines architecture only.

It does not yet:

- Create OUs
- Move AWS accounts
- Attach SCPs
- Create AWS accounts
- Change organization membership

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Production placed inside Non-Production OU
- Security accounts placed under Sandbox governance
- OU membership treated as IAM permission
- Account moves without authorization
- Production moved to weaker controls without approval
- Unclassified accounts permanently remaining at root
- SCPs treated as permission grants

---

# Canonical Decision Summary

LinkCraftor shall use four primary governance OUs:

- Security
- Infrastructure
- Non-Production
- Production

The OU structure provides policy inheritance and governance separation while AWS
accounts remain the primary environment isolation boundaries.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL

---

# Simulation Lab OU Amendment

Status: CANONICAL

The canonical Non-Production OU membership is:

Non-Production OU
├── DEVELOPMENT
├── TESTING
├── STAGING
├── SIMULATION-LAB
└── SANDBOX

Production remains isolated:

Production OU
└── PRODUCTION

Simulation Lab must inherit Non-Production organizational guardrails and must
not inherit Production authority merely because it is used for realistic
pre-production simulation.

Marker:
SIMULATION-LAB-NONPRODUCTION-OU

