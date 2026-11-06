# LinkCraftor Cloud Account Lifecycle & Governance Boundaries

Version: 1.0
Status: Canonical
Phase: Cloud Organization & Environment Isolation
Section: 2.9 Account Lifecycle & Governance Boundaries
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical lifecycle and governance boundaries for
LinkCraftor AWS accounts.

It governs how accounts are:

- Proposed
- Approved
- Created
- Classified
- Assigned
- Secured
- Operated
- Reviewed
- Restricted
- Suspended
- Retired
- Closed

---

# Architectural Authorities

This architecture consumes and preserves:

- 2.1 AWS Organization & Account Structure
- 2.2 Organizational Units
- 2.3 Environment Account Isolation
- 2.4 Shared Infrastructure Account Separation
- 2.5 Production Isolation
- 2.6 Cross-Account Trust Boundaries
- 2.7 Service Control Policy Architecture
- 2.8 Region / Environment Guardrails

---

# Core Rule

No AWS account may exist as an unmanaged, unowned, or unclassified LinkCraftor
cloud environment.

Every account must have a defined lifecycle and governance status.

---

# Canonical Account Lifecycle

Canonical lifecycle:

Proposed
→ Approved
→ Provisioned
→ Classified
→ Baseline Secured
→ Active
→ Reviewed
→ Restricted / Suspended
→ Retired
→ Closed

Not every account must pass through every exceptional state.

---

# Proposed State

An account proposal must identify:

- Business purpose
- Technical purpose
- Environment
- Owner
- Security owner
- Expected region usage
- Expected data classification
- Expected cost responsibility
- Expected trust relationships

---

# Approval State

Account creation requires approval appropriate to the account's risk.

Production, Security, Log Archive, Network, and other sensitive accounts require
stronger governance than ordinary experimentation accounts.

---

# Provisioning

AWS account creation must occur through an approved organization-level process.

Manual unmanaged account creation must not become the normal model.

---

# Account Classification

Every account must have an authoritative classification.

Examples include:

- Management
- Security
- Log Archive
- Network
- Shared Services
- Deployment
- Development
- Testing
- Staging
- Sandbox
- Production

---

# Environment Classification

Environment classification must not be inferred only from an account name.

Canonical metadata or configuration must identify the account's environment and
purpose.

---

# Account Ownership

Every account requires:

- Business owner
- Technical owner
- Security responsibility
- Billing responsibility
- Administrative path

Unowned accounts are prohibited.

---

# Root User Governance

Each AWS account root user must be governed.

Root-user requirements include:

- Strong MFA
- No normal root access keys
- Exceptional-use policy
- Secure credential custody
- Root-use monitoring
- Recovery procedure

Routine administration must use workforce identities and roles.

---

# Contact Information

AWS account contact and alternate-contact information must remain current.

Where applicable, accounts should maintain approved:

- Security contact
- Billing contact
- Operations contact

---

# Billing Attribution

Every AWS account must have clear cost attribution.

Billing responsibility does not grant administrative authority.

Detailed cost-management architecture belongs to later FinOps phases.

---

# OU Placement

Every member account must be assigned to an approved Organizational Unit.

Permanent unclassified placement at the organization root is prohibited.

---

# SCP Baseline

Each account must receive the SCP baseline appropriate to its OU and risk.

SCP attachment does not replace IAM authorization.

---

# Region Baseline

Each account must receive approved regional restrictions appropriate to its
purpose.

Production regional rules must remain stronger than uncontrolled experimentation.

---

# Logging Baseline

Every active account must participate in the approved audit/evidence architecture.

Control-plane activity must remain auditable.

Detailed centralized logging implementation belongs to later phases.

---

# Security Baseline

Every account must participate in approved security monitoring and governance
appropriate to its role.

Security baseline implementation will be finalized in later security and
observability phases.

---

# Identity Baseline

Human access must use approved workforce identity.

Service and workload access must use approved service/workload identity.

Root and static long-lived credentials must not be normal administration
mechanisms.

---

# Cross-Account Trust Registration

Cross-account trust must be known and reviewable.

Unregistered hidden trust relationships are prohibited.

---

# Production Account Governance

Production accounts require stronger controls.

Production governance must include:

- Independent access authorization
- Production-specific workload trust
- Strong logging
- Security monitoring
- Controlled deployment
- Approved regions
- Data protection
- Periodic access review

---

# Security Account Governance

Security accounts require protection against unauthorized mutation and evidence
tampering.

Security administrators must not automatically control every other cloud
function.

---

# Log Archive Governance

Log Archive accounts must prioritize durability and evidence independence.

Ordinary workload administrators must not possess unrestricted destructive log
authority.

---

# Network Account Governance

Network accounts must preserve separation between connectivity administration
and application/data/IAM authority.

---

# Shared Services Governance

Shared Services accounts must not become universal administrative trust hubs.

Every shared service must have a defined purpose and consumer boundary.

---

# Deployment Account Governance

Deployment accounts must preserve separation between non-production and
Production deployment authority.

---

# Development Governance

Development accounts may allow controlled experimentation.

Development flexibility must not bypass Production protection.

---

# Testing Governance

Testing accounts must support automated validation without using uncontrolled
Production authority or credentials.

---

# Staging Governance

Staging accounts should approximate Production where useful while remaining
separate in identity, credentials, data, and authority.

---

# Sandbox Governance

Sandbox accounts require:

- Strong cost controls
- Expiration or cleanup discipline
- No unrestricted Production data
- No Production credentials
- No implicit Production trust

---

# Account Review

Every account must be periodically reviewed.

Review should verify:

- Account is still needed
- Owner is current
- Security owner is current
- OU placement is correct
- SCP baseline is correct
- Region usage is correct
- Trust relationships remain required
- Logging remains active
- Security baseline remains active
- Costs remain attributable

---

# Dormant Account Handling

Unused accounts must not remain indefinitely active without review.

Dormant accounts should be:

- Investigated
- Restricted where appropriate
- Cleaned up
- Retired if no longer required

---

# Restriction State

An account may enter Restricted state due to:

- Security incident
- Governance violation
- Ownership uncertainty
- Excessive risk
- Unexpected cost
- Unauthorized region use
- Unapproved cross-account trust

Restrictions must be auditable.

---

# Suspension State

Suspension may be used where the account must cease normal operation pending
review or recovery.

Suspension must not destroy required evidence.

---

# Account Retirement

Retirement requires a controlled process.

Retirement should address:

- Data retention
- Backups
- Secrets
- KMS dependencies
- DNS dependencies
- Network dependencies
- IAM trust
- Cross-account roles
- Logs
- Billing
- Legal retention
- Production dependencies

---

# Production Retirement

Production account retirement is exceptionally sensitive.

Production must not be retired until:

- Workloads are migrated or terminated
- Customer data handling is resolved
- Recovery requirements are satisfied
- Audit evidence is preserved
- DNS and external dependencies are resolved
- Cross-account trust is removed safely

---

# Account Closure

Account closure is the terminal lifecycle state.

Closure must be explicitly approved.

Closure must not be used as an informal cleanup shortcut.

---

# Account Reuse Boundary

Closed or retired account identity must not be casually reused for a different
environment or purpose.

New purpose should normally receive a new appropriately governed account.

---

# Account Naming

Canonical account names must remain controlled.

Renaming must not break environment or governance identity.

Machine logic should not rely solely on display names where stable identifiers
are available.

---

# Account IDs

AWS Account IDs are authoritative technical identifiers once accounts exist.

Account IDs must not be treated as secrets.

They must, however, be correctly mapped to canonical account purpose.

---

# Metadata Registry

A canonical registry should eventually record:

- AWS Account ID
- Canonical account name
- Account classification
- OU
- Environment
- Owner
- Security owner
- Regions
- Status
- Creation date
- Retirement status
- Trust relationships

Implementation belongs to later governance and IaC work.

---

# Change Management

Material account governance changes require controlled change management.

Examples include:

- OU movement
- SCP changes
- Production classification changes
- Region changes
- Trust changes
- Delegated-administrator changes
- Account retirement

---

# Delegated Administrator Governance

Delegated AWS service administrators must be explicitly registered and
reviewable.

Delegated administration must not silently create universal authority.

---

# Account Vending Boundary

If automated account vending is adopted later, it must enforce this canonical
governance model.

Automation must not create unmanaged accounts.

---

# Control Tower Boundary

AWS Control Tower may be evaluated later as an implementation mechanism.

It is not currently assumed as the canonical authority merely by being an AWS
service.

The architecture remains implementation-mechanism independent until explicitly
approved.

---

# Incident Governance

Accounts involved in security incidents may require temporary restriction,
credential revocation, trust removal, or emergency access.

Incident controls must preserve evidence.

---

# Audit Attribution

Account lifecycle changes must be attributable.

Examples include:

- Account creation
- OU movement
- SCP changes
- Trust changes
- Delegated-administrator changes
- Suspension
- Retirement
- Closure

AWS CloudTrail remains the canonical AWS control-plane audit source where the
relevant operation is recorded.

---

# Fail-Closed Requirement

Governance operations must fail closed where required ownership, authorization,
or classification cannot be validated.

High-risk account changes must not proceed from unknown state.

---

# Terraform and IaC Boundary

Account metadata, OU placement, SCP attachments, account governance mappings, and
related controls must ultimately be represented through approved Terraform/IaC
where supported and appropriate.

Phase 3 owns the Terraform implementation foundation.

---

# Implementation Boundary

This section defines architecture only.

It does not yet:

- Create AWS accounts
- Close AWS accounts
- Move accounts between OUs
- Configure account contacts
- Configure root MFA
- Configure SCPs
- Configure security services
- Configure logging
- Create account registry infrastructure
- Enable Control Tower
- Enable automated account vending

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

Future account-governance monitoring or drift-detection jobs may require
Universal Runtime Registration Standard assessment.

---

# Prohibited Practices

The following are prohibited:

- Unowned AWS accounts
- Unclassified AWS accounts
- Permanent unmanaged accounts at Organization Root
- Root user used for routine administration
- Dormant accounts remaining indefinitely without review
- Account closure without dependency review
- Production account closure without controlled retirement
- Retired account casually reused for a different environment
- Hidden cross-account trust
- Account naming treated as the only authoritative identity
- Automated account vending without governance controls
- AWS Control Tower assumed mandatory without explicit approval
- Account lifecycle changes without auditability

---

# Canonical Decision Summary

Every LinkCraftor AWS account shall have a defined owner, purpose, classification,
OU placement, region boundary, security baseline, logging baseline, identity
baseline, cost attribution, lifecycle status, and review process.

Accounts shall progress through controlled lifecycle states from proposal through
closure.

No unmanaged or unowned AWS account is permitted.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
