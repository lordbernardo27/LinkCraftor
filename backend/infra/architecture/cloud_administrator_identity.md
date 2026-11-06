# LinkCraftor Cloud Administrator Identity

Version: 1.0
Status: Canonical
Phase: Cloud Identity & Access Infrastructure
Section: 4.1.1 Cloud Administrator Identity
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical human administrator identity architecture
for access to LinkCraftor AWS infrastructure.

It establishes who may act as a cloud administrator, how human cloud
administrators authenticate, how administrative identity remains separate from
LinkCraftor customer identity, and the security boundaries that later IAM,
privileged-access, production-access, emergency-access, and workload-identity
architecture must preserve.

This document does not define customer login, customer sessions, workspace
authorization, customer MFA, account recovery, or customer passkey policy.

Those remain governed by the LinkCraftor Identity / Access / Account Security
Architecture.

---

# Architectural Boundary

LinkCraftor maintains separate identity planes.

## LinkCraftor Identity Plane

The LinkCraftor Identity Plane governs:

- Customer authentication
- Workspace identity
- Workspace membership
- Product authorization
- Customer sessions
- Customer MFA
- Customer passkeys
- Customer account recovery
- Product operators where governed by LinkCraftor application identity

## AWS IAM / Workforce Plane

The AWS IAM / Workforce Plane governs:

- AWS Console access
- AWS administrative access
- Infrastructure administration
- AWS deployment administration
- Security administration
- AWS account administration
- AWS organization administration
- AWS resource administration
- Cloud control-plane permissions

The same natural person may have identities in both planes, but those identities,
sessions, permissions, credentials, and audit records must remain separately
governed.

---

# Canonical Decision

Human AWS administration shall use a centrally governed workforce identity model.

AWS IAM Identity Center is the canonical AWS workforce-access entry point for
normal human administrative access.

Human administrators shall not use customer credentials to obtain AWS access.

Customer authentication must never become an AWS administrative authentication
mechanism.

AWS administrative authentication must never become the LinkCraftor customer
authentication authority.

---

# AWS IAM Identity Center

AWS IAM Identity Center shall be the canonical workforce-access broker for normal
human access across the LinkCraftor AWS organization.

It shall provide the controlled path for:

- Founder cloud administration
- Authorized engineering access
- Security administration
- Deployment administration
- Read-only infrastructure access
- Audit access
- Future approved operations personnel

Direct standalone IAM users must not become the default human workforce-access
model.

---

# Named Human Identities

Every normal human AWS administrator must use an individually attributable
identity.

Shared administrator identities are prohibited.

Shared console credentials are prohibited.

Shared administrator passwords are prohibited.

Administrative actions must be attributable to the specific human actor who
performed them.

A team name, department name, generic account, shared mailbox, or common
credential must not replace individual administrator identity.

---

# Human vs Workload Identity

Human administrator identity and workload identity are different principal
classes.

Human administrators authenticate as workforce principals.

Applications, workers, deployment systems, automation, and infrastructure
components authenticate through approved workload or service identities.

A human administrator must not operate production workloads using a personal
long-lived access key.

A workload must not depend on a human administrator's interactive AWS session as
its production identity.

Detailed workload identity is governed by Phase 4.1.5.

---

# Customer Identity Separation

A LinkCraftor customer identity is not:

- An AWS IAM user
- An AWS IAM role
- An AWS IAM group
- An AWS access key
- An AWS workforce administrator
- An AWS Console identity

Customer passwords, MFA secrets, passkeys, recovery credentials, and product
sessions must never be accepted as AWS administrative credentials.

AWS infrastructure permissions must never be inferred directly from a customer's
LinkCraftor workspace role.

---

# Employee and Customer Dual Identity

A person may simultaneously be:

- A LinkCraftor customer
- A LinkCraftor employee
- An engineer
- An approved infrastructure administrator

Those roles do not create one universal identity.

The person's customer identity and AWS workforce identity must remain separately:

- Authenticated
- Authorized
- Sessioned
- Audited
- Revoked
- Governed

Compromise of one identity plane must not automatically compromise the other.

---

# Administrator Categories

The architecture recognizes separate administrator responsibility classes.

These may include:

- Organization Administrator
- Cloud Platform Administrator
- Security Administrator
- Deployment Administrator
- Production Administrator
- Network Administrator
- Data Infrastructure Administrator
- Read-Only Operator
- Auditor
- Emergency Administrator

These responsibility classes do not automatically grant permissions.

Detailed IAM role architecture is owned by Phase 4.1.2.

---

# Organization Administrator

Organization-level administration must be exceptionally restricted.

The AWS Organizations management account is a governance account, not an
application workload account.

Organization administration may include:

- AWS Organizations governance
- Account lifecycle governance
- Organizational Unit governance
- Service Control Policy governance
- IAM Identity Center administration
- Organization-level security configuration

Organization Administrator authority must not automatically provide unrestricted
routine production application administration.

---

# Management Account Boundary

The AWS Organizations management account must remain dedicated to
organization-level governance.

Production application workloads must not run in the management account.

Normal application engineering activity must not require routine management
account administrator access.

Access to the management account must be more restrictive than ordinary
non-production administration.

---

# Root User Protection

AWS root users are exceptional identities.

Root-user access must not be used for routine cloud administration.

Root users must be protected through:

- Strong authentication
- MFA
- Secure recovery controls
- Restricted access
- Controlled credential custody
- Audit visibility
- Emergency-use procedures

Root access must be limited to tasks that genuinely require the root user or to
approved recovery circumstances.

Root credentials must never be shared as an ordinary administrator credential.

Root access is not a substitute for IAM Identity Center or delegated
administrator roles.

Detailed emergency access is governed by Phase 4.1.9.

---

# Authentication Assurance

Cloud administrators must use strong workforce authentication.

Administrative authentication must require MFA appropriate to the privilege
level.

Higher-risk administrative access should use phishing-resistant authentication
where supported and operationally appropriate.

Administrative authentication requirements must not be weakened merely for
convenience.

The detailed authenticator implementation may be aligned with approved
enterprise/workforce identity capabilities without merging customer identity and
AWS workforce identity.

---

# Administrative Sessions

Normal human AWS access shall use temporary authenticated sessions.

Permanent administrative credentials are prohibited as the normal access model.

Administrative sessions must be:

- Time bounded
- Individually attributable
- Revocable
- Auditable
- Role scoped
- Environment aware

Detailed temporary-credential architecture is governed by Phase 4.1.6.

---

# Permanent Access Keys

Permanent administrator AWS access keys are prohibited.

Human administrators must not receive long-lived AWS access keys merely to avoid
interactive workforce authentication.

Exceptions, if ever required by an externally imposed technical constraint, must
be:

- Explicitly approved
- Narrowly scoped
- Time constrained where technically possible
- Monitored
- Rotated
- Documented
- Removed when no longer required

An exception must not silently become the standard administrator-access model.

---

# Role Assumption

Authentication establishes the human workforce principal.

Authorization to administer AWS resources shall be granted through approved roles
or permission-set assignments.

Authentication alone does not grant unrestricted AWS authority.

A human identity may assume only roles explicitly authorized for:

- The person's function
- The intended AWS account
- The intended environment
- The intended administrative purpose

Detailed role architecture is governed by Phase 4.1.2.

---

# Least Privilege Boundary

Cloud administrator access is subject to least privilege.

An administrator must receive only the permissions required for the approved
administrative responsibility.

Administrator identity does not imply universal AWS AdministratorAccess.

Detailed least-privilege architecture is governed by Phase 4.1.3.

---

# Production Administration

Production access must be independently authorized.

Development access must not imply production access.

Testing access must not imply production access.

Staging access must not imply production access.

General engineering membership must not automatically grant production
administrator authority.

Production AWS administration must use workforce authentication independent of
customer authentication.

Production administrative actions must be auditable.

Detailed cross-environment restrictions are governed by Phase 4.1.8.

---

# Security Administration

Security administration must be distinguishable from general platform
administration where separation of duties requires it.

Security responsibilities may include:

- IAM security configuration
- Security monitoring
- Security service administration
- Key-management governance
- Security findings
- Security-policy controls
- Security investigation

Possession of Security Administrator authority must not automatically mean
unrestricted application-data access.

---

# Read-Only and Audit Access

Where a task requires observation rather than modification, administrators should
use read-only or audit-oriented access.

Audit access should permit inspection of approved infrastructure and security
evidence without silently granting mutation authority.

Read-only access must still be:

- Authenticated
- Authorized
- Attributable
- Logged
- Environment scoped

---

# Privileged Access

Highly privileged administrative access must receive additional controls.

These may include:

- Stronger authentication
- Explicit approval
- Shorter sessions
- Restricted role assumption
- Additional logging
- Step-up controls
- Just-in-time access where later adopted
- Post-use review

Detailed privileged-access architecture is governed by Phase 4.1.7.

---

# Emergency Administrator Boundary

Emergency or break-glass access must remain separate from routine administrator
access.

Emergency access must not become a permanent general production administrator
role.

Emergency mechanisms must be:

- Restricted
- Monitored
- Recoverable
- Audited
- Tested
- Used only under approved emergency conditions

Detailed emergency cloud access is governed by Phase 4.1.9.

---

# Environment Isolation

Cloud administrator identity architecture must preserve environment isolation.

Development, testing, staging, sandbox, shared, security, and production access
must remain distinguishable.

Administrative access to one environment must not silently authorize access to
another environment.

Cross-environment administrator authority requires explicit architecture and
security approval.

Detailed environment/account implementation is dependent on Phase 2.

---

# Account Isolation

Cloud administrator authorization shall align with the canonical AWS account
model defined by Cloud Resource Organization.

The canonical AWS organization includes distinct account boundaries for:

- Management
- Security
- Log Archive
- Network
- Shared Services
- Deployment
- Development
- Testing
- Staging
- Production
- Sandbox

A single workforce identity may receive different permissions in different
accounts, but those permissions must remain explicit and independently
governable.

---

# Logging and Attribution

Administrative AWS activity must produce auditable evidence.

AWS CloudTrail is the canonical AWS API/control-plane audit source approved by
the Cloud Service Portfolio.

Administrative audit evidence must make it possible to determine, where
available:

- Acting workforce identity
- Assumed role or permission set
- AWS account
- Environment
- Session
- API action
- Resource
- Timestamp
- Result
- Relevant source context

Administrative logging must not depend exclusively on self-reported application
logs.

---

# Audit Protection

Administrators must not routinely be able to erase the evidence required to
audit their own privileged activity.

Audit-log protection, security-log ownership, and separation-of-duties controls
must be preserved by later IAM and logging implementation.

---

# Provisioning

Cloud administrator access must be explicitly provisioned.

Administrative authority must not arise automatically from:

- Customer signup
- Workspace ownership
- Subscription level
- Source-code repository membership alone
- Employee status alone
- Email-domain possession alone
- Plugin ownership
- Application administrator status alone

Approved access must map the human workforce principal to approved AWS
administrative roles or permission sets.

---

# Deprovisioning

Administrative access must be removed when:

- Employment or engagement ends
- Administrative responsibility ends
- Authorization expires
- Security requires suspension
- The identity is compromised
- The role assignment is no longer justified

Deprovisioning must remove AWS workforce access without depending on termination
of the person's customer identity.

---

# Credential Compromise

If a cloud administrator identity is suspected of compromise:

- Administrative access must be capable of suspension
- Active sessions must be capable of revocation where supported
- Related credentials must be invalidated where applicable
- Audit evidence must be preserved
- Security investigation must be initiated
- Production access must fail closed where required

Compromise of a customer identity must not automatically compromise AWS
administrator access.

Compromise of AWS administrator identity must not automatically grant access to
customer authentication secrets.

---

# Source-Control and Deployment Boundary

GitHub or other source-control identity is not automatically AWS administrator
identity.

CI/CD systems shall use their own approved deployment/workload identities.

A developer's repository access must not silently provide production AWS Console
administrator access.

Deployment identity is further governed by:

- Phase 4.1.4 Service Identities
- Phase 4.1.5 Workload Identity
- Phase 4.1.6 Temporary Credentials
- Phase 14 Deployment & Release Infrastructure

---

# Universal Runtime Boundary

Universal Runtime worker identities and cloud administrator identities are
different principal classes.

A Universal Runtime worker must not execute AWS infrastructure administration
using a human administrator credential.

A cloud administrator must not become the runtime identity of application
workers.

Existing Universal Runtime worker, queue, orchestration, and workload identity
architecture must be reused rather than duplicated.

---

# Relationship to Identity Security Architecture

This document consumes and preserves the Identity / Access / Account Security
Architecture boundary between:

- LinkCraftor customer/operator identity
- AWS workforce identity
- AWS workload identity

It does not replace the Identity Security Architecture.

It does not create:

- Customer authentication
- Customer authorization
- Customer MFA policy
- Customer passkey policy
- Customer recovery policy
- Customer session-management authority

No shadow authentication authority is introduced by this architecture.

---

# Phase Dependencies

4.1.1 establishes the human cloud-administrator identity model.

Later Phase 4 components own:

- 4.1.2 IAM Role Architecture
- 4.1.3 Least-Privilege Model
- 4.1.4 Service Identities
- 4.1.5 Workload Identity
- 4.1.6 Temporary Credentials
- 4.1.7 Privileged Access
- 4.1.8 Cross-Environment Restrictions
- 4.1.9 Emergency Cloud Access
- 4.1.10 Cloud Identity & Access Certification

Phase 2 must later provide the implemented AWS account/environment boundaries.

Phase 3 must later provide the Terraform/IaC implementation foundation.

Therefore 4.1.1 may be architecturally approved now, but Phase 4 final
implementation certification remains deferred until required Phase 2 and Phase 3
dependencies exist.

---

# Prohibited Practices

The following are prohibited:

- Shared routine AWS administrator identities
- Shared routine AWS administrator passwords
- Customer credentials used for AWS administration
- AWS IAM used as LinkCraftor customer authentication
- Permanent administrator access keys as the normal human-access model
- Routine root-user administration
- Automatic production access from development access
- Automatic AWS administration from workspace ownership
- Automatic AWS administration from application Administrator role
- Human credentials used as workload identity
- Workload credentials used as customer login
- Unattributable privileged AWS sessions
- Emergency access becoming routine administrator access
- Source-control access silently becoming AWS administrator access

---

# Runtime Eligibility

This document is an architecture and governance artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Later executable identity validation, privileged-session validation,
access-review, IAM compliance, or cloud-access certification jobs may require
Universal Runtime Registration Standard assessment.

---

# Canonical Decision Summary

LinkCraftor shall use a separate, centrally governed AWS workforce identity model
for human cloud administration.

Normal human AWS administration shall use AWS IAM Identity Center and temporary,
individually attributable administrative sessions.

Customer identity and AWS administrator identity remain separate authorities.

Shared administrator identities and permanent routine administrator access keys
are prohibited.

Production administrator access must be separately authorized and audited.

Root identities are exceptional and must not be used for routine administration.

Detailed permissions, workload identities, temporary credentials, privileged
access, cross-environment controls, and emergency access are owned by later
Phase 4 components.

Phase 4 final implementation certification remains dependent on Phase 2 and
Phase 3 implementation foundations.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
