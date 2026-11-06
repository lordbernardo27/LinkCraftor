# LinkCraftor Cloud Privileged Access

Version: 1.0
Status: Canonical
Phase: Cloud Identity & Access Infrastructure
Section: 4.1.7 Privileged Access
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS privileged-access architecture for
LinkCraftor.

It governs elevated human access to AWS administration and sensitive cloud
operations.

This architecture covers:

- Privileged eligibility
- Privileged request and approval
- Step-up authentication
- Strong MFA
- Temporary elevated sessions
- Production privileged access
- Organization administration
- Security administration
- Network and data administration
- Sensitive IAM operations
- Privilege escalation prevention
- `iam:PassRole`
- Just-in-time access
- Standing privilege minimization
- Separation of duties
- Dual control where required
- Audit attribution
- Access review
- Revocation
- Emergency-access boundary

Emergency break-glass access itself is governed separately by Phase 4.1.9.

---

# Architectural Authorities

This architecture consumes and preserves:

- 4.1.1 Cloud Administrator Identity
- 4.1.2 IAM Role Architecture
- 4.1.3 Least-Privilege Model
- 4.1.4 Service Identities
- 4.1.5 Workload Identity
- 4.1.6 Temporary Credentials
- Separation-of-Duties Principles
- Least-Privilege Principles
- Identity / Access / Account Security Architecture

This document specializes those authorities for AWS privileged access.

---

# Privileged Access Definition

Privileged access is elevated AWS access capable of materially changing:

- Organization configuration
- IAM configuration
- Security controls
- Production systems
- Network controls
- Data infrastructure
- Encryption and key configuration
- Deployment controls
- Recovery configuration
- Cross-account trust
- Audit configuration
- Other security-sensitive cloud state

Privileged access must not be treated as routine baseline access.

---

# Core Rule

Privileged AWS access must be:

- Explicit
- Individually attributable
- Least-privileged
- Time-bounded
- Strongly authenticated
- Independently authorized where required
- Audited
- Reviewable
- Revocable

Standing unrestricted privilege must be minimized.

---

# Privileged Role Classes

Privileged role classes include:

- OrganizationAdministrator
- CloudPlatformAdministrator
- SecurityAdministrator
- DeploymentAdministrator
- ProductionAdministrator
- NetworkAdministrator
- DataInfrastructureAdministrator
- EmergencyAdministrator

These roles remain governed by 4.1.2 IAM Role Architecture.

The existence of a role does not imply automatic assignment.

---

# Privileged Eligibility

A person must be explicitly eligible for a privileged role before privileged
access may be granted.

Eligibility must consider:

- Job responsibility
- Current need
- Environment
- Role ownership
- Separation of duties
- Security requirements
- Required training or approval where applicable

Privileged eligibility must be revocable.

---

# Request Model

Privileged access should require an explicit request where the access is not
already justified as narrowly scoped standing operational authority.

A privileged request should identify:

- Requester
- Requested role
- AWS account
- Environment
- Purpose
- Required duration
- Requested scope
- Related ticket, incident, deployment, or change where applicable

---

# Approval

High-risk privileged access must require approval appropriate to the risk.

Approval must be independent from the requester where separation of duties
requires it.

Self-approval must not be the normal model for high-risk privilege.

Approval does not itself execute the privileged action.

---

# Separation of Duties

Privileged architecture must preserve separation among:

- Request
- Approval
- Execution
- Audit review
- Security review

One person should not automatically control every stage of a high-risk action.

Critical IAM, production, security, and recovery actions may require stronger
duty separation.

---

# Dual Control

Dual control may be required for critical operations.

Examples may include:

- High-risk production changes
- Organization-wide IAM changes
- Security-boundary changes
- Audit-control changes
- Destructive data operations
- Key-management changes
- High-impact recovery operations

Exact dual-control requirements may be finalized by the owning security and
operations architecture.

---

# Strong Authentication

Privileged access requires authentication appropriate to the risk.

Strong MFA is mandatory for privileged administrative access.

Higher-risk administration should prefer phishing-resistant authentication where
available and approved.

Customer authentication factors must not be reused as AWS workforce
administrator credentials.

---

# Step-Up Authentication

A privileged action may require step-up authentication before execution.

Step-up must provide stronger or more recent authentication evidence.

Successful step-up does not bypass authorization.

After step-up, the privileged request must still receive a valid authorization
decision.

---

# Assurance

Privileged operations must use the assurance level required by the Identity
Security Architecture.

Critical operations may require higher assurance such as AAL3-equivalent
operator controls where defined by that architecture.

AWS privileged-access architecture must consume, not redefine, the product
identity assurance model.

---

# Temporary Privileged Sessions

Privileged access must use temporary AWS sessions.

A privileged session must not become a permanent identity.

Privileged session duration should be shorter for higher-risk roles.

4.1.6 Temporary Credentials governs session mechanics and lifetime architecture.

---

# Standing Privilege

Standing privileged access must be minimized.

Standing privilege is acceptable only where ongoing operational responsibility
requires it and the access remains:

- Narrowly scoped
- Individually assigned
- Reviewable
- Audited
- Revocable
- Appropriate to role

Broad standing administrator authority is prohibited as the default.

---

# Just-in-Time Privilege

Just-in-time privileged access may be adopted where supported and operationally
appropriate.

JIT access should:

- Activate only when needed
- Use approved eligibility
- Require approval where appropriate
- Produce a temporary session
- Expire automatically
- Preserve audit evidence

JIT must reduce standing privilege rather than create another privilege path.

---

# Production Privileged Access

Production privileged access must be independently authorized.

Development access must not imply production access.

Testing access must not imply production access.

Staging access must not imply production access.

Production access must be:

- Individually assigned
- Justified
- Time-bounded where appropriate
- Auditable
- Revocable

---

# Organization Administration

OrganizationAdministrator access is among the highest-risk authority classes.

It must not automatically include unrestricted application, data, or runtime
authority unless explicitly required.

Organization-level changes require elevated review and audit.

Routine administration should not use organization-wide authority where a
narrower role is sufficient.

---

# Security Administration

SecurityAdministrator access must remain separate from routine platform and
production administration where separation of duties requires it.

Security administrators must not be able to silently erase or disable required
security evidence.

Security administration must remain auditable.

---

# Production Administration

ProductionAdministrator access must be separately granted.

It must not be inherited from development or staging roles.

Production administration must not automatically imply:

- Organization administration
- Security administration
- Billing administration
- Audit-administration authority

---

# Deployment Administration

DeploymentAdministrator authority must remain separate from unrestricted
production administration where appropriate.

Deployment approval and deployment execution may require separation for
high-risk releases.

CI/CD workload identity remains separate from human deployment-administrator
identity.

---

# Network Administration

NetworkAdministrator authority must be limited to required networking
responsibilities.

Network administration must not automatically grant:

- Production application administration
- IAM administration
- Security-administration authority
- Data-administration authority

---

# Data Infrastructure Administration

DataInfrastructureAdministrator access must be limited to approved database,
storage, and data-infrastructure responsibilities.

Data infrastructure privilege must not automatically imply unrestricted access
to all customer data.

Data access remains separately governed by data-security architecture.

---

# AdministratorAccess Boundary

AWS managed policy `AdministratorAccess` must not become the routine privileged
access model.

Privileged roles must use explicit permission architecture.

Broad AdministratorAccess may exist only under separately governed exceptional
or emergency conditions where explicitly approved.

---

# PowerUserAccess Boundary

`PowerUserAccess` must not become a substitute for proper privileged-role design.

Broad managed policies require review and explicit justification.

---

# Privilege Escalation Prevention

Privileged roles must not silently expand their own authority.

High-risk escalation capabilities include:

- IAM policy mutation
- IAM role creation
- Trust-policy mutation
- Permission-set mutation
- Permissions-boundary mutation
- SCP mutation
- `iam:PassRole`
- KMS policy changes
- Deployment of stronger roles
- Modification of audit controls

Such actions require explicit scope and review.

---

# iam:PassRole

`iam:PassRole` must be narrowly scoped.

Wildcard `iam:PassRole` across all roles is prohibited except under separately
approved exceptional authority.

PassRole permissions must identify which roles may be passed and to which
services or workloads where practical.

---

# Sensitive IAM Operations

Sensitive IAM operations require elevated protection.

Examples include:

- Creating privileged users or roles
- Changing trust policies
- Modifying permission sets
- Changing MFA enforcement
- Creating access keys
- Modifying federation
- Changing SCPs
- Modifying permissions boundaries

These operations should receive stronger approval, authentication, and audit
controls.

---

# Session Duration

Privileged sessions must use shorter lifetimes than ordinary low-risk sessions
where appropriate.

Emergency, organization, security, and production mutation sessions should use
particularly constrained lifetimes.

Session duration architecture remains governed by 4.1.6.

---

# Session Revocation

Privileged sessions must be revocable where AWS supports the required controls.

Revocation may include:

- Removing role assignment
- Removing permission-set assignment
- Changing trust
- Disabling federation
- Restricting policy
- Blocking future assumption
- Emergency containment

Revocation must not depend solely on waiting for a long-lived session to expire.

---

# Access Review

Privileged assignments must be periodically reviewed.

Review must determine:

- Is the role still required?
- Is production access still justified?
- Is the scope still correct?
- Is the environment assignment correct?
- Is the user still eligible?
- Are any dormant privileges present?
- Should access be reduced or removed?

Unused or unjustified privilege must be removed.

---

# Privileged Activity Review

Privileged activity must be reviewable independently of the actor where
appropriate.

A privileged administrator must not be the sole authority over the audit record
of their own activity.

Security and audit reviewers must have appropriate evidence access.

---

# Audit Attribution

Every privileged AWS action must be attributable.

Audit evidence should include:

- Human principal
- Permission set
- IAM role
- Role session
- AWS account
- Environment
- Region
- Source identity where available
- Session name
- API action
- Resource
- Timestamp
- Result

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Audit Protection

Privileged users must not be able to silently erase required audit evidence.

Changes to:

- CloudTrail
- Log retention
- Security logging
- Audit storage
- Security Lake
- SIEM integrations
- Event routing

must be separately controlled where applicable.

---

# Environment Separation

Privileged access remains environment-specific.

Development privilege does not imply:

- Testing privilege
- Staging privilege
- Production privilege

Production privileged access must be separately authorized.

---

# Account Separation

Privileged access must respect AWS account boundaries.

Assignment in one AWS account must not silently grant privilege in another.

Cross-account privileged access requires explicit trust and assignment.

---

# Emergency Access Boundary

EmergencyAdministrator is not a routine privileged role.

Emergency or break-glass access is governed by 4.1.9 Emergency Cloud Access.

Routine administrative convenience must never justify emergency-role use.

---

# Customer Identity Boundary

Customer identity remains outside the AWS privileged-access plane.

A LinkCraftor customer, workspace owner, or product administrator must not gain
AWS privileged access merely because of product authority.

Customer MFA, passwords, passkeys, or sessions must never become AWS privileged
administrator credentials.

---

# Workload Boundary

Workload and service identities must not receive human privileged roles.

Workers, CI/CD, Terraform automation, and backend services must use their
approved machine identities.

Human privileged sessions must not be reused by workloads.

---

# Fail-Closed Privileged Access

Privileged access must fail closed when required conditions are not satisfied.

Denial conditions include:

- Missing authorization
- Missing approval
- Insufficient assurance
- Failed MFA
- Invalid role assignment
- Wrong AWS account
- Wrong environment
- Expired session
- Revoked eligibility
- Separation-of-duties conflict
- Invalid trust
- Unapproved privilege escalation

---

# Privileged Access Lifecycle

Canonical lifecycle:

Eligible
→ Requested
→ Approved
→ Strongly authenticated
→ Activated
→ Temporarily elevated
→ Audited
→ Expired / Revoked
→ Reviewed

Not every privileged role must use every step in exactly the same operational
form, but equivalent control objectives must be preserved.

---

# Terraform and IaC Boundary

Privileged role, permission-set, trust, and assignment configuration must
ultimately be represented through approved Terraform/IaC where applicable.

Phase 3 owns the Terraform implementation foundation.

Manual AWS Console changes must not become authoritative privileged-access
configuration.

---

# Implementation Boundary

This phase defines architecture only.

It does not yet:

- Create privileged IAM roles
- Create privileged permission sets
- Assign production administrators
- Configure JIT tooling
- Configure approval workflows
- Configure production access
- Configure organization-admin assignments
- Configure privileged session durations
- Create emergency roles
- Activate break-glass access

Those actions require later implementation gates.

---

# Runtime Eligibility

This document is an architecture and governance artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future automated privileged-access review, stale-role detection, approval
validation, privilege-escalation analysis, or compliance jobs may require
Universal Runtime Registration Standard assessment.

---

# Phase Dependencies

4.1.7 defines privileged access.

4.1.8 defines cross-environment restrictions.

4.1.9 defines emergency cloud access.

Phase 2 must provide account/environment isolation.

Phase 3 must provide Terraform/IaC implementation.

Later security, operations, deployment, and observability phases will implement
and monitor privileged-access controls.

Final Phase 4 certification remains deferred until those implementation
dependencies exist.

---

# Prohibited Practices

The following are prohibited:

- Routine universal AdministratorAccess
- Routine PowerUserAccess as privileged-role design
- Automatic production privilege from development access
- Automatic production privilege from staging access
- Shared privileged administrator identities
- Unattributable privileged sessions
- Permanent AWS access keys as normal privileged credentials
- Self-approved high-risk privilege where independent approval is required
- Privileged users silently expanding their own authority
- Unrestricted `iam:PassRole`
- Privileged users silently erasing required audit evidence
- Emergency administrator role used for routine operations
- Customer identity used as AWS privileged identity
- Human privileged credentials used by workloads
- Standing privilege without justification
- Privileged sessions without bounded lifetime
- Privileged access without review
- Manual console privilege becoming authoritative configuration

---

# Canonical Decision Summary

LinkCraftor privileged AWS access shall be explicit, individually attributable,
least-privileged, strongly authenticated, time-bounded, audited, reviewable, and
revocable.

Production privilege shall be independently authorized.

Standing privilege shall be minimized.

High-risk privileged assignments should require independent approval.

Step-up authentication and stronger assurance shall be used where the risk
requires them.

Routine AdministratorAccess and PowerUserAccess are prohibited as the standard
privileged model.

Privilege-escalation paths, including `iam:PassRole`, must be narrowly
controlled.

Emergency access remains separate and is governed by 4.1.9.

Phase 2 and Phase 3 will provide the account isolation and Terraform foundation
needed for implementation.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
