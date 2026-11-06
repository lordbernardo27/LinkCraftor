# LinkCraftor Cloud Shared Infrastructure Account Separation

Version: 1.0
Status: Canonical
Phase: Cloud Organization & Environment Isolation
Section: 2.4 Security / Log / Network / Shared Services Separation
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical separation architecture for LinkCraftor's
shared infrastructure AWS accounts.

It governs:

- SECURITY
- LOG-ARCHIVE
- NETWORK
- SHARED-SERVICES
- DEPLOYMENT

These accounts perform different infrastructure responsibilities and must not
collapse into one universal administrative or workload boundary.

---

# Architectural Authorities

This architecture consumes and preserves:

- Cloud Resource Organization
- 2.1 AWS Organization & Account Structure
- 2.2 Organizational Units
- 2.3 Environment Account Isolation
- Phase 4 Cloud Identity & Access Infrastructure

---

# Core Rule

Security, logging, networking, shared services, and deployment responsibilities
must remain separately governed.

No supporting infrastructure account automatically gains unrestricted authority
over every other account or environment.

---

# Security Account

SECURITY is the dedicated security-services account.

It may host or administer approved capabilities such as:

- Security monitoring
- Security findings aggregation
- Threat detection
- Security automation
- Security posture management
- Compliance evidence processing
- Delegated security administration

Security visibility must not automatically grant unrestricted Production
application mutation authority.

---

# Security Administration Boundary

Security administrators must remain distinguishable from:

- Production administrators
- Network administrators
- Deployment administrators
- Data administrators
- Application administrators

Security authority must be least-privileged and auditable.

---

# Log Archive Account

LOG-ARCHIVE is the dedicated centralized evidence-preservation account.

It exists to receive and protect approved centralized logs and audit evidence.

Potential evidence may include:

- AWS CloudTrail
- Security findings
- Access logs
- Configuration evidence
- Security-event evidence
- Approved infrastructure logs

Detailed observability implementation belongs to later phases.

---

# Log Independence

Workload administrators must not be able to silently erase centralized evidence
of their own activity.

Production administrators must not control the sole copy of Production
control-plane audit evidence.

Security administrators must not automatically possess unrestricted audit
deletion authority.

---

# Log Write vs Delete Separation

Where technically practical:

- Workload accounts may deliver approved evidence
- Central logging systems may ingest evidence
- Ordinary workload administrators must not delete protected central evidence
- Destructive log administration must require separate authority

---

# Network Account

NETWORK is the dedicated centralized networking-governance account.

It may later host or govern approved capabilities such as:

- Shared network infrastructure
- Transit connectivity
- Central routing
- Network inspection
- Central DNS where approved
- Egress controls
- Connectivity infrastructure

Detailed networking architecture belongs to Phases 5 and 6.

---

# Network Authority Boundary

Network administration must not automatically grant:

- Production application administration
- Database administration
- Security administration
- IAM administration
- Customer-data access
- Deployment authority

Network connectivity creates reachability, not authorization.

---

# Shared Services Account

SHARED-SERVICES hosts approved common infrastructure used by more than one
environment or account.

Examples may later include:

- Shared tooling
- Approved build support
- Common operational services
- Centralized non-security infrastructure
- Shared internal platform services

A service is not placed in SHARED-SERVICES merely because more than one system
uses it.

---

# Shared Services Trust Boundary

SHARED-SERVICES must not become an uncontrolled bridge between environments.

Shared Services access to Production requires:

- Explicit trust
- Narrow permissions
- Approved identity
- Auditable sessions
- Environment-aware authorization

---

# Deployment Account

DEPLOYMENT hosts or governs approved deployment automation and release authority.

It remains separate from:

- Development
- Testing
- Staging
- Production
- Security
- Network administration

---

# Deployment Authority Boundary

Non-production deployment authority must not automatically grant Production
deployment authority.

Production deployment must use independently approved Production deployment
trust.

Repository membership alone must not create AWS Production deployment access.

---

# Account Compromise Containment

Compromise of one supporting account should not automatically compromise every
other account.

In particular:

- NETWORK compromise must not automatically grant Production IAM authority
- SHARED-SERVICES compromise must not automatically grant Production admin
- DEPLOYMENT compromise must not automatically grant Security admin
- SECURITY compromise must not automatically permit audit deletion
- Production compromise must not automatically permit LOG-ARCHIVE deletion

---

# Human Identity Separation

Human administrator assignments must reflect account responsibility.

A single person may legitimately hold multiple approved roles, but each role must
remain separately assigned, attributable, and reviewable.

---

# Workload Identity Separation

Security automation, logging systems, networking systems, shared services, and
deployment automation must use distinct workload/service identities appropriate
to their functions.

A universal cross-account machine identity is prohibited as the default model.

---

# Cross-Account Access

Access among supporting accounts requires explicit trust.

Organization membership alone is insufficient.

Cross-account roles must identify approved source and destination trust.

---

# Resource Policy Boundary

Resource policies must not bypass account responsibility boundaries.

Examples include policies for:

- S3
- KMS
- SQS
- SNS
- Secrets Manager
- EventBridge
- Other AWS resources

Broad organization-wide access must not be used merely for convenience.

---

# KMS Boundary

Encryption-key authority must remain scoped to the service and evidence model.

A Network administrator does not automatically receive Log Archive decryption
authority.

A Deployment administrator does not automatically receive unrestricted Security
key authority.

---

# Audit Attribution

Cross-account supporting-infrastructure actions must remain attributable.

Audit evidence should identify:

- Human or workload principal
- Source account
- Destination account
- IAM role
- Session
- API action
- Resource
- Timestamp
- Result

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Fail-Closed Requirement

Access must fail closed when:

- Source identity is unknown
- Destination trust is absent
- Required role assignment is absent
- Environment is unknown
- Account is outside approved scope
- Required security condition is absent
- Credential scope is invalid

---

# Terraform and IaC Boundary

Supporting account roles, trust relationships, resource policies, and account
controls must ultimately be represented through approved Terraform/IaC where
applicable.

Phase 3 owns the Terraform implementation foundation.

---

# Implementation Boundary

This section defines architecture only.

It does not yet:

- Create SECURITY resources
- Create LOG-ARCHIVE resources
- Create NETWORK resources
- Create SHARED-SERVICES resources
- Create DEPLOYMENT resources
- Configure delegated administrators
- Configure centralized CloudTrail
- Configure KMS keys
- Configure networking
- Configure cross-account roles
- Configure resource policies

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Security account treated as universal Production administrator
- Network account treated as universal IAM administrator
- Shared Services treated as unrestricted Production bridge
- Deployment account treated as unrestricted Production administrator
- Production administrators able to silently delete central audit evidence
- One universal machine identity spanning all supporting accounts
- Organization membership treated as cross-account permission
- Broad resource policies bypassing account boundaries
- Network reachability treated as authorization

---

# Canonical Decision Summary

SECURITY, LOG-ARCHIVE, NETWORK, SHARED-SERVICES, and DEPLOYMENT shall remain
separate AWS account responsibility boundaries.

Each account receives only the authority necessary for its function.

Cross-account access must be explicit, attributable, reviewable, and
least-privileged.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
