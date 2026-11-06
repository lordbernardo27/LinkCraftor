# LinkCraftor Cloud Emergency Access

Version: 1.0
Status: Canonical
Phase: Cloud Identity & Access Infrastructure
Section: 4.1.9 Emergency Cloud Access
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS emergency and break-glass access
architecture for LinkCraftor.

It governs exceptional access used when normal administrative access is
unavailable, insufficient, or unsafe during a critical incident, recovery
event, security containment action, or cloud-control failure.

Emergency access is not routine privileged access.

Routine privileged access is governed by Phase 4.1.7.

---

# Architectural Authorities

This architecture consumes and preserves:

- 4.1.1 Cloud Administrator Identity
- 4.1.2 IAM Role Architecture
- 4.1.3 Least-Privilege Model
- 4.1.6 Temporary Credentials
- 4.1.7 Privileged Access
- 4.1.8 Cross-Environment Restrictions
- Separation-of-Duties Principles
- Least-Privilege Principles
- Identity / Access / Account Security Architecture

---

# Emergency Access Definition

Emergency access is exceptional cloud authority used only for:

- Active security incidents
- Critical service recovery
- Identity-provider failure
- IAM or federation failure
- Production containment
- Recovery from administrator lockout
- Critical infrastructure restoration
- Security-control restoration
- Disaster-recovery activation where required

Emergency access must not be used for:

- Routine administration
- Convenience
- Ordinary deployment
- Normal production maintenance
- Avoiding standard approval
- Avoiding privileged-access controls

---

# Core Rule

Emergency authority must be:

- Exceptional
- Temporary
- Narrowly scoped
- Strongly authenticated
- Explicitly activated
- Approved according to risk
- Individually attributable
- Continuously monitored where feasible
- Audited
- Revocable
- Automatically expiring where supported
- Reviewed after use

Emergency access must never silently become standing administrator authority.

---

# EmergencyAdministrator

EmergencyAdministrator is the canonical emergency privileged role class.

It exists only for approved break-glass, containment, recovery, or critical
restoration scenarios.

EmergencyAdministrator must not be used for routine operations.

Assignment or activation must be separately governed from normal privileged
roles.

---

# Root Account Boundary

AWS root user access is separate from EmergencyAdministrator access.

The root user is not the normal break-glass mechanism.

Root access must be reserved for AWS operations that specifically require root
authority or for extraordinary account-recovery circumstances where no safer
approved mechanism is available.

Routine incident response must use EmergencyAdministrator or another approved
narrow emergency role rather than root.

---

# Root Credential Protection

AWS root credentials must receive exceptional protection.

Requirements include:

- Strong MFA
- No routine root access keys
- Restricted credential custody
- No shared casual use
- Separate recovery procedure
- Alerting on root use
- CloudTrail evidence where AWS records the action
- Post-use review

Root credentials must not be embedded in automation, source code, scripts,
CI/CD, or runtime workloads.

---

# Root MFA

Root accounts must use strong MFA.

Phishing-resistant or hardware-backed MFA should be preferred where supported
and operationally approved.

Root MFA must remain independent from customer authentication.

---

# Emergency Authentication

Emergency access requires strong workforce authentication.

Where available and approved, higher-assurance or phishing-resistant
authentication should be used.

Customer passwords, customer MFA, passkeys, recovery credentials, or customer
sessions must never become AWS emergency credentials.

---

# Explicit Activation

Emergency access must require explicit activation.

Emergency authority must not remain permanently active merely because the user
is eligible.

Activation should record:

- Principal
- Emergency role
- AWS account
- Environment
- Reason
- Incident identifier
- Requested scope
- Activation time
- Intended duration
- Approval evidence where required

---

# Approval Model

Emergency approval depends on whether the action is restrictive or
risk-increasing.

Risk-increasing emergency actions should require independent approval or dual
approval where required.

Self-approval must not become the normal emergency model.

---

# Immediate Containment Exception

Where immediate containment is necessary to prevent ongoing or imminent harm, an
approved responder may activate a pre-authorized restrictive control before
secondary approval where the governing incident policy permits it.

Such containment must be:

- Restrictive rather than privilege-expanding where possible
- Pre-authorized
- Audited
- Time-bounded
- Followed by secondary review
- Associated with an incident

This exception must not become a shortcut for ordinary privilege escalation.

---

# Dual Control

Dual control may be required for high-risk emergency actions.

Examples include:

- Organization-wide IAM mutation
- Disabling security controls
- Root-account recovery
- Destructive production actions
- KMS key-policy changes
- Major SCP changes
- Audit-control mutation
- Broad recovery actions

The applicable owning architecture may impose stronger approval requirements.

---

# Temporary Emergency Sessions

Emergency AWS access must use temporary sessions where technically possible.

Emergency sessions must have bounded lifetime.

Higher-risk emergency roles should use particularly short session durations.

4.1.6 Temporary Credentials governs session mechanics.

---

# Limited Lifetime

Emergency sessions must automatically expire where supported.

Emergency access must not require manual cleanup as its only expiry mechanism.

Extensions must require a new approval or explicit re-authorization where
appropriate.

---

# Scope Restriction

Emergency access must be narrowly scoped to the problem being resolved.

Scope may be constrained by:

- AWS account
- Environment
- Region
- Role
- Resource
- Service
- Action
- Session duration
- Incident context

Emergency authority must not automatically include all Production, Security,
Network, Data, and Organization privileges.

---

# Production Emergency Access

Production emergency access requires explicit Production authority.

Development, Testing, Staging, Sandbox, or Shared Services access does not imply
Production emergency authority.

Production emergency sessions must be independently attributable and audited.

---

# Security Account Emergency Access

Emergency access to Security or Log Archive accounts must remain separately
governed.

Emergency responders must not be able to silently erase evidence of their own
activity.

Security-account emergency authority does not automatically grant unrestricted
Production mutation authority.

---

# Cross-Account Emergency Access

Cross-account emergency access requires explicit trust.

Emergency access in one account must not automatically provide emergency access
in another.

Cross-account emergency roles must identify approved source principals and
destination authority.

---

# Organization Emergency Access

Organization-level emergency authority is exceptionally sensitive.

Organization-wide changes should require elevated approval, strong
authentication, narrow session duration, and complete audit evidence.

Emergency organization access must not become routine cloud administration.

---

# Recovery Access

Recovery privilege must remain separate from ordinary Production administration.

Recovery authority may include:

- Restoring critical infrastructure
- Restoring identity access
- Recovering failed security controls
- Activating DR capability
- Restoring required configuration

Recovery access must end when the recovery need ends.

---

# Disaster-Recovery Boundary

DR activation does not automatically authorize unrestricted normal Production
operation.

Emergency DR access must follow approved recovery procedures.

The use of us-east-1 as the disaster-recovery region does not itself grant
emergency authority.

---

# Privilege Escalation Boundary

Emergency access must not permit uncontrolled privilege escalation.

High-risk operations include:

- IAM policy mutation
- Role creation
- Trust-policy mutation
- Permissions-boundary mutation
- SCP mutation
- `iam:PassRole`
- KMS policy mutation
- Federation mutation
- Audit-control mutation

These actions must remain explicitly governed.

---

# iam:PassRole Emergency Boundary

Emergency `iam:PassRole` authority must remain narrowly scoped.

Wildcard PassRole over all roles must not become the standard emergency model.

Where broader authority is temporarily unavoidable, it must be separately
approved, time-bounded, audited, and removed after the event.

---

# Security-Control Changes

Emergency access must not silently weaken fundamental security boundaries.

Changes affecting:

- CloudTrail
- Log retention
- Security monitoring
- IAM trust
- MFA
- SCPs
- KMS
- Security Hub
- GuardDuty
- Security Lake
- SIEM integration
- Event routing

must produce explicit evidence and review.

---

# Audit Preservation

Emergency administrators must not be able to silently erase required evidence.

Emergency activity must remain independently reviewable.

Audit evidence must survive the incident where technically possible.

---

# Audit Attribution

Every emergency AWS action must be attributable.

Evidence should identify:

- Human principal
- Emergency role
- Session
- Source identity where available
- AWS account
- Environment
- Region
- Incident identifier
- API action
- Resource
- Timestamp
- Result

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Notification

Emergency activation should generate immediate notification to appropriate
security, operations, or owner authorities.

Notification should identify:

- Who activated emergency access
- Which account
- Which environment
- Why
- Incident identifier
- Time of activation

Notifications must not contain credentials or session secrets.

---

# Continuous Monitoring

Emergency sessions should receive enhanced monitoring.

Monitoring may include:

- CloudTrail activity review
- Security-event correlation
- High-risk API detection
- Session-duration monitoring
- Unexpected region activity
- Unexpected resource scope
- Attempts to disable security controls

---

# Revocation

Emergency access must be revocable.

Revocation may include:

- Removing role assignment
- Removing permission-set assignment
- Blocking role assumption
- Changing role trust
- Disabling federation
- Restricting policy
- Ending eligibility
- Incident containment

Revocation must not rely solely on waiting for long credential expiration.

---

# Automatic Expiry

Emergency eligibility or session activation should automatically expire where
supported.

Emergency authority must not survive indefinitely after the incident.

---

# Return to Normal Access

After the emergency condition ends:

1. Emergency access must be revoked or allowed to expire.
2. Normal administrative access must resume.
3. Temporary emergency trust changes must be removed.
4. Temporary policies must be reverted.
5. Emergency credentials or sessions must not remain active.
6. Evidence must be preserved.

---

# Post-Event Review

Every material use of emergency access must receive post-event review.

Review must determine:

- Why emergency access was required
- Whether normal access failed
- Whether activation was justified
- Whether scope was appropriate
- Whether approval requirements were satisfied
- Whether any unexpected actions occurred
- Whether all emergency authority was removed
- Whether architecture or runbooks require correction

---

# Incident Association

Emergency access should be associated with an incident, recovery, or emergency
change record where operational systems support it.

Emergency access without a recorded reason must be considered exceptional and
reviewed.

---

# Testing

Emergency access must be tested periodically without creating uncontrolled
Production risk.

Tests should validate:

- Authentication
- MFA
- Activation
- Approval
- Role assumption
- Audit logging
- Notification
- Revocation
- Expiration
- Recovery from lockout

Testing must use controlled procedures.

---

# Credential Storage

Emergency credentials must not be stored in:

- Source code
- Repository files
- CI/CD variables unless explicitly designed for approved emergency custody
- Queue messages
- Application logs
- Documentation
- Container images
- Browser storage
- Runtime configuration

Credential custody must use approved secure mechanisms.

---

# Customer Identity Boundary

Customer identity remains outside the AWS emergency-access plane.

Product ownership, workspace ownership, or customer administrator status must
not grant AWS emergency authority.

AWS emergency credentials must never be accepted as LinkCraftor customer login
credentials.

---

# Workload Boundary

Workers, backend services, CI/CD systems, Terraform automation, and other machine
identities must not assume EmergencyAdministrator merely because an incident
exists.

Machine emergency authority, if ever required, must be separately designed and
approved.

Human emergency roles must not be reused by workloads.

---

# Fail-Closed Emergency Access

Emergency access must fail closed when required controls cannot be verified.

Denial conditions include:

- Unknown principal
- Failed strong authentication
- Failed MFA
- Missing eligibility
- Missing required approval
- Invalid emergency role
- Wrong AWS account
- Wrong environment
- Expired session
- Revoked access
- Invalid trust
- Unapproved privilege escalation

---

# Emergency Access Lifecycle

Canonical lifecycle:

Emergency detected
→ Normal access evaluated
→ Emergency access requested
→ Eligibility verified
→ Approval obtained where required
→ Strong authentication
→ Explicit activation
→ Temporary emergency session
→ Recovery / containment action
→ Continuous audit
→ Revocation / expiry
→ Return to normal access
→ Post-event review

---

# Terraform and IaC Boundary

Emergency roles, permission sets, trust policies, alerting configuration, and
related controls must ultimately be represented through approved Terraform/IaC
where applicable.

Phase 3 owns the Terraform implementation foundation.

Manual AWS Console configuration must not become authoritative emergency-access
architecture.

---

# Implementation Boundary

This phase defines architecture only.

It does not yet:

- Create EmergencyAdministrator roles
- Configure break-glass permission sets
- Configure root-account custody
- Configure root MFA
- Configure emergency approval workflows
- Configure emergency alerts
- Configure emergency session duration
- Configure emergency cross-account trust
- Activate emergency access
- Perform root recovery
- Perform Production break-glass access

Those actions require later implementation gates.

---

# Runtime Eligibility

This document is an architecture and governance artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future automated emergency-access monitoring, stale emergency-role detection,
activation review, break-glass validation, or compliance jobs may require
Universal Runtime Registration Standard assessment.

---

# Phase Dependencies

4.1.9 defines emergency cloud access.

4.1.10 certifies Phase 4 architecture only after implementation dependencies are
satisfied.

Phase 2 must provide AWS account and environment isolation.

Phase 3 must provide Terraform/IaC implementation.

Later observability, incident-response, recovery, and operations phases must
implement monitoring and operational procedures.

Final Phase 4 certification remains deferred until those implementation
dependencies exist.

---

# Prohibited Practices

The following are prohibited:

- EmergencyAdministrator used for routine administration
- Root user used as routine administrator
- Permanent break-glass sessions
- Emergency access without attribution
- Shared emergency identities
- Customer credentials used for emergency AWS access
- Human emergency credentials used by workloads
- Unbounded emergency session duration
- Self-approved high-risk emergency action where independent approval is required
- Emergency access used to avoid normal privileged-access controls
- Emergency administrator silently expanding authority
- Unrestricted emergency `iam:PassRole`
- Emergency administrator silently deleting audit evidence
- Root access keys used for automation
- Root credentials embedded in scripts
- Emergency access remaining active after the incident
- Temporary emergency trust changes left permanently in place
- Manual Console emergency configuration becoming authoritative state

---

# Canonical Decision Summary

LinkCraftor emergency AWS access shall remain exceptional, temporary, narrowly
scoped, strongly authenticated, explicitly activated, approved according to
risk, fully attributable, auditable, revocable, and subject to post-event
review.

EmergencyAdministrator is separate from routine privileged access.

AWS root user access is even more exceptional and is not the normal break-glass
mechanism.

Emergency Production access must be independently authorized.

Emergency authority must expire or be revoked after the incident.

Audit evidence must be preserved.

Phase 2 and Phase 3 provide the account-isolation and Terraform foundations
required for implementation.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
