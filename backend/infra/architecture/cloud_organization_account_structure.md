# LinkCraftor Cloud Organization & Account Structure

Version: 1.0
Status: Canonical
Phase: Cloud Organization & Environment Isolation
Section: 2.1 AWS Organization & Account Structure
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS Organization and account structure for
LinkCraftor.

It specializes and preserves the previously approved Cloud Resource Organization
architecture.

It does not replace that authority.

---

# Architectural Authorities

This architecture consumes and preserves:

- Cloud Foundation Certification
- Cloud Resource Organization
- Cloud Identity & Access Infrastructure
- Cross-Environment Restrictions
- Least-Privilege Model

---

# AWS Organizations

LinkCraftor shall use AWS Organizations as the authoritative account-governance
boundary.

The organization exists to provide:

- Account isolation
- Environment isolation
- Security separation
- Central governance
- Central billing
- Service Control Policy guardrails
- Delegated administration
- Cross-account trust boundaries
- Production protection

---

# Canonical Account Structure

The canonical AWS accounts are:

1. LINKCRAFTOR-MANAGEMENT
2. SECURITY
3. LOG-ARCHIVE
4. NETWORK
5. SHARED-SERVICES
6. DEPLOYMENT
7. DEVELOPMENT
8. TESTING
9. STAGING
10. SANDBOX
11. PRODUCTION

These account names are canonical.

---

# Management Account

LINKCRAFTOR-MANAGEMENT is the AWS Organizations management account.

It is responsible for organization-level governance.

It must not become the normal workload account.

Normal application workloads must not run in the management account.

Routine production compute must not run in the management account.

---

# Security Account

SECURITY is the dedicated security-services account.

It may host or govern approved centralized security capabilities.

Security authority must remain separate from ordinary application administration.

---

# Log Archive Account

LOG-ARCHIVE is the dedicated centralized audit and security-evidence account.

It exists to preserve durable audit evidence independently from ordinary
workload accounts.

Workload administrators must not be able to silently erase centralized evidence.

---

# Network Account

NETWORK is the dedicated central network-governance account.

Networking authority must remain separate from application, IAM, and data
administration where appropriate.

---

# Shared Services Account

SHARED-SERVICES hosts approved common infrastructure shared across environments.

Shared Services must not become an uncontrolled bridge into Production.

---

# Deployment Account

DEPLOYMENT hosts or governs approved deployment automation and deployment
authority.

Production deployment authority must remain separately controlled from
non-production deployment authority.

---

# Development Account

DEVELOPMENT is dedicated to development workloads.

Development identities and resources must not automatically gain Production
authority.

---

# Testing Account

TESTING is dedicated to automated and integration testing.

Testing authority must not automatically grant Staging or Production authority.

---

# Staging Account

STAGING is the pre-production environment.

Staging must remain separate from Production.

Production credentials, secrets, and unrestricted production data must not be
reused automatically in Staging.

---

# Sandbox Account

SANDBOX is dedicated experimentation space.

Sandbox must not contain unrestricted Production customer data.

Sandbox access must not imply Production access.

---

# Production Account

PRODUCTION is the customer-facing Production environment.

It must remain isolated from:

- Development
- Testing
- Staging
- Sandbox
- Personal experimentation

Production authority must be independently assigned.

---

# Account Ownership

Every AWS account must have:

- Defined purpose
- Account owner
- Security owner
- Billing attribution
- Environment classification
- Approved administrator path
- Audit coverage
- Lifecycle status

Unowned AWS accounts are prohibited.

---

# Account Boundary Rule

AWS accounts are security boundaries.

Membership in the AWS Organization does not by itself grant access between
accounts.

Cross-account access requires explicit trust and permission.

---

# Root User Boundary

Each AWS account retains an AWS root identity.

Root access is exceptional.

Root users must not be used for routine administration.

Root-account controls are governed further by Emergency Cloud Access.

---

# Billing Boundary

Centralized billing may be governed through the AWS Organizations management
account.

Billing centralization does not imply security or workload authority.

---

# Production Isolation

Production must remain independently governable from lower environments.

No lower-environment account may automatically administer Production.

---

# Region Relationship

Canonical regions remain:

- eu-west-1 — primary
- us-east-1 — disaster-recovery
- af-south-1 — future

Account structure and region structure are separate concepts.

A Production account may contain approved Production resources in more than one
region where the architecture authorizes it.

A separate account is not required merely because a region is used for DR.

---

# Cross-Account Access

Cross-account access must use explicit IAM trust.

No account receives access to another merely because both belong to the same AWS
Organization.

---

# Terraform and IaC Boundary

AWS Organizations, accounts, policies, and account-level governance must
ultimately be represented through approved Terraform/IaC where supported and
appropriate.

Phase 3 owns the Terraform implementation foundation.

---

# Implementation Boundary

This section defines architecture only.

It does not yet:

- Create AWS Organizations
- Create AWS accounts
- Move accounts
- Configure delegated administrators
- Configure SCPs
- Configure organization-wide services
- Configure billing
- Configure production roles

Those actions require later implementation gates.

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Production workloads in the management account
- Development and Production sharing one account
- Testing and Production sharing one account
- Sandbox and Production sharing one account
- Workloads silently crossing account boundaries
- Organization membership treated as access permission
- Root user used for routine administration
- Unowned AWS accounts
- Manual account structure becoming undocumented authoritative state

---

# Canonical Decision Summary

LinkCraftor shall use an eleven-account AWS Organization.

The management, security, logging, networking, shared-services, deployment,
development, testing, staging, sandbox, and production responsibilities remain
separately governed.

AWS account membership creates organizational membership only.

It does not create cross-account permission.

Production remains independently protected.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL

---

# Simulation Lab Account Amendment

Status: CANONICAL

The LinkCraftor AWS account inventory includes a dedicated Simulation Lab
environment account.

Canonical account name:

SIMULATION-LAB

Classification:

- Environment type: Non-Production
- Organizational Unit: Non-Production OU
- Production serving authority: NO
- Production customer traffic: NO
- Synthetic / simulation workload authority: YES
- Production credential fallback: PROHIBITED
- Production data dependency by default: PROHIBITED

Simulation Lab is distinct from:

- DEVELOPMENT
- TESTING
- STAGING
- SANDBOX
- PRODUCTION

The Simulation Lab account must not be implemented as an alias of STAGING.

Updated canonical environment account inventory:

- DEVELOPMENT
- TESTING
- STAGING
- SIMULATION-LAB
- SANDBOX
- PRODUCTION

Marker:
SIMULATION-LAB-CANONICAL-ACCOUNT

