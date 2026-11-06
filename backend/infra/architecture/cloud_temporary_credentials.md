# LinkCraftor Cloud Temporary Credentials

Version: 1.0
Status: Canonical
Phase: Cloud Identity & Access Infrastructure
Section: 4.1.6 Temporary Credentials
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS temporary-credential architecture for
LinkCraftor.

It governs short-lived AWS credentials used by:

- Human workforce administrators
- IAM Identity Center sessions
- AWS role assumption
- Service identities
- Workload identities
- CI/CD systems
- Terraform automation
- Universal Runtime workloads
- Cross-account access
- Emergency access where separately authorized

This document does not define customer authentication tokens.

Customer identity and AWS temporary credentials remain separate identity planes.

---

# Architectural Authorities

This architecture consumes and preserves:

- 4.1.1 Cloud Administrator Identity
- 4.1.2 IAM Role Architecture
- 4.1.3 Least-Privilege Model
- 4.1.4 Service Identities
- 4.1.5 Workload Identity
- Identity / Access / Account Security Architecture
- Least-Privilege Principles
- Universal Runtime trust architecture

This document specializes those authorities for AWS temporary credential use.

---

# Core Rule

Normal AWS access must use temporary, attributable, scoped credentials wherever
AWS provides an approved mechanism.

Long-lived static AWS access keys must not become the default access model for:

- Humans
- Services
- Workloads
- Deployment systems
- Automation
- Universal Runtime workers

---

# Credential Classes

Canonical temporary credential classes include:

1. Human workforce sessions
2. Service/workload role sessions
3. CI/CD federation sessions
4. Terraform execution sessions
5. Cross-account sessions
6. Emergency sessions

Each class must have its own trust, scope, lifetime, and audit requirements.

---

# Human Workforce Sessions

Human AWS access must normally flow through AWS IAM Identity Center or another
approved workforce federation mechanism.

Canonical flow:

Named human identity
→ strong authentication
→ approved permission set
→ approved AWS account
→ temporary AWS role session

Human administrators must not receive permanent AWS access keys merely for
routine convenience.

---

# MFA

MFA must be enforced according to the privilege and identity architecture.

Privileged administrative access should require strong MFA.

Where AWS session trust conditions support MFA context, it may be used as an
additional authorization condition.

Customer MFA credentials must never become AWS workforce MFA credentials.

---

# Service and Workload Sessions

Service and workload identities must use AWS-managed or short-lived role
credentials where supported.

Canonical flow:

Approved service identity
→ approved workload identity
→ IAM role
→ STS or AWS-managed credential delivery
→ short-lived credentials

Static service access keys must not become the normal workload mechanism.

---

# STS Role Sessions

AWS STS is the canonical mechanism where explicit role assumption is required.

Role assumption must validate:

- Trusted principal
- Approved role
- Account
- Environment
- Trust conditions
- Session duration
- Session identity
- Permission scope

A successful AssumeRole operation must not exceed the authority of the assumed
role or applicable policy boundaries.

---

# Session Duration

Temporary credentials must have bounded lifetime.

Session duration must reflect:

- Human vs workload use
- Privilege level
- Production sensitivity
- Operational need
- AWS service capabilities
- Recovery requirements
- Automation duration

No session should be longer than necessary for its approved purpose.

---

# Human Session Duration

Human administrator sessions should use shorter duration for higher privilege.

Examples of factors requiring shorter sessions include:

- Production administration
- Security administration
- Organization administration
- Emergency access
- Sensitive data infrastructure
- Key-management operations

Routine read-only access may have a longer duration than privileged mutation
access where appropriate.

Exact values may be finalized during implementation once AWS account and
permission-set infrastructure exists.

---

# Workload Credential Duration

Workload credentials should use the lifetime automatically managed by the
approved AWS workload identity mechanism where possible.

A workload must not persist temporary AWS credentials beyond their intended
session lifetime.

Applications should refresh credentials through the approved provider
mechanism rather than manually copying session credentials.

---

# Renewal

Credential renewal must occur through the approved identity mechanism.

Renewal must not silently transform a temporary credential into a permanent one.

Human session renewal must require the authentication and authorization state
required by the workforce identity architecture.

Workload renewal must occur through the workload's approved credential provider.

---

# Re-Assumption

When an STS role session expires, a new session must be obtained through a fresh
approved trust evaluation.

Expired credentials must not be extended locally.

A workload or human principal must not alter expiration timestamps or reuse
expired credentials.

---

# Session Naming

Where AWS supports role-session naming, session names must support attribution.

Session naming should allow identification of the acting principal without
exposing secrets.

Potential components include:

- Principal identifier
- Service identity
- Workload identifier
- Deployment context
- Environment
- Correlation identifier

Session naming conventions must be deterministic where practical.

---

# Source Identity

AWS STS SourceIdentity should be used where supported and beneficial for
persistent attribution across role assumption.

Source identity must represent an approved trusted principal attribute.

A caller must not be allowed to spoof another principal's source identity.

---

# Session Tags

Session tags may be used to carry approved authorization or attribution context.

Potential tags include:

- Environment
- Service
- Workload
- Project
- Deployment
- Principal type

Session tags used for authorization must originate from trusted sources.

A principal must not be able to self-assign tags that increase privilege.

---

# Session Policies

STS session policies may be used to reduce permissions below the role's maximum
authority.

Session policies must not be used to increase authority.

Effective authority remains constrained by all applicable AWS permission layers.

---

# Permission Ceiling

Temporary credentials never expand the permissions of the source architecture.

Effective permissions remain constrained by:

- Role permissions
- Session policies
- Permissions boundaries
- SCPs
- Resource policies
- KMS policies
- Trust-policy conditions

Temporary credential issuance does not imply unrestricted access.

---

# Credential Provider Chain

Production credential sources must be deterministic and documented.

Production workloads must not accidentally fall back to:

- Developer credentials
- Local AWS profiles
- Shared personal profiles
- Unapproved environment variables
- Hard-coded access keys
- Desktop user credentials

The intended credential provider must be explicit in architecture and deployment
configuration.

---

# Environment Isolation

Temporary credentials must remain environment specific.

Development sessions must not automatically grant:

- Testing access
- Staging access
- Production access

Production sessions require independently approved role assignment or workload
trust.

---

# Account Isolation

A session valid in one AWS account does not automatically authorize another
account.

Cross-account role assumption requires explicit:

- Source permission
- Destination trust
- Approved role
- Account scope
- Environment scope
- Session controls

---

# Region Scope

Temporary credentials inherit regional restrictions from the IAM policy and
role architecture.

Where applicable, session use may be constrained to approved regions.

Canonical regions remain:

- eu-west-1 — primary
- us-east-1 — disaster-recovery
- af-south-1 — future

---

# Cross-Account Sessions

Cross-account sessions must use approved role assumption.

Cross-account access must not use shared static credentials.

The destination role trust policy must explicitly identify the approved source
principal or trust boundary.

Production cross-account sessions require stronger review.

---

# CI/CD Temporary Credentials

CI/CD systems must obtain short-lived AWS credentials through approved
federation or role assumption.

Repository credentials must not themselves be AWS credentials.

Preferred model:

Approved CI/CD identity
→ OIDC or approved federation
→ AWS deployment role
→ temporary credentials

Production deployment sessions must be separately governed from
non-production sessions.

---

# Terraform Temporary Credentials

Terraform must use temporary credentials appropriate to the approved execution
environment.

TerraformPlanRole and TerraformApplyRole must remain separately governed.

Terraform must not require permanent human access keys.

Terraform credential acquisition must be compatible with Phase 3 IaC
architecture.

---

# Universal Runtime Temporary Credentials

Universal Runtime workloads must acquire AWS credentials through approved
workload identity.

AWS session credentials do not replace:

- Worker identity validation
- Signed execution grants
- Persisted leases
- Runtime authorization
- Queue authorization
- Handler authorization
- Replay protection
- Revocation

AWS credentials authorize AWS resource access.

Universal Runtime trust authorizes runtime execution.

---

# Credential Storage

Temporary AWS credentials must not be persisted unnecessarily.

Credentials must not be written into:

- Source code
- Repository files
- Logs
- Queue messages
- Browser storage
- Documentation
- Container images
- General telemetry

Where temporary credentials are cached by an AWS SDK or approved runtime
mechanism, the cache must remain protected and bounded by credential lifetime.

---

# Expiration

Expired credentials must fail closed.

Applications must not continue privileged operations after credential expiration.

Clock-skew handling must remain bounded and must not materially extend
credential validity.

---

# Revocation

Revocation must not depend solely on waiting for temporary credentials to expire.

Revocation mechanisms may include:

- Removing role assignment
- Removing permission-set assignment
- Changing role trust
- Disabling federation
- Restricting or deleting policies
- Revoking workload trust
- Blocking future role assumption
- Emergency containment controls

Existing issued AWS sessions may remain technically usable until their
expiration where AWS does not support immediate invalidation.

Architecture must therefore use appropriately short lifetimes for high-risk
sessions.

---

# Workload Revocation

Workload credential revocation must operate together with runtime revocation.

AWS revocation does not replace:

- Grant revocation
- Worker trust revocation
- Lease invalidation
- Queue claim controls
- Runtime execution controls

Both layers must remain independently enforceable.

---

# Rotation

Temporary credentials normally rotate through reissuance rather than manual
secret rotation.

Long-lived credential exceptions, where unavoidable and approved, remain subject
to separate rotation requirements.

Temporary credential architecture must not normalize permanent access keys.

---

# Emergency Sessions

Emergency access credentials must remain temporary where technically possible.

Emergency access must be governed by 4.1.9 Emergency Cloud Access.

Break-glass authority must not become a standing permanent credential.

Emergency sessions require:

- Strong authentication
- Explicit activation
- Audit attribution
- Limited lifetime
- Post-event review

---

# Session Attribution

Temporary sessions must be attributable.

Audit evidence should allow correlation among:

- Human or workload principal
- IAM role
- Role session
- Source identity where used
- Session tags where used
- AWS account
- Environment
- Region
- API action
- Resource
- Timestamp
- Result

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Logging Restrictions

Temporary credentials themselves must never be logged.

Logs may record safe metadata such as:

- Role ARN
- Session ARN
- Principal identifier
- Source identity
- Session name
- Account
- Environment
- Correlation ID

Secret access key material and session tokens must never be logged.

---

# Credential Failure Behavior

Credential validation must fail closed.

Protected access must fail when credentials are:

- Missing
- Expired
- Invalid
- Untrusted
- Outside approved account
- Outside approved environment
- Outside approved role scope
- Outside approved session policy
- Obtained from an unapproved provider

---

# Static Credential Exceptions

Long-lived static credentials are strongly discouraged.

If an integration cannot support temporary credentials, any exception must be:

- Explicitly approved
- Narrowly scoped
- Documented
- Protected
- Rotated
- Monitored
- Time-bounded where possible
- Scheduled for removal when a temporary mechanism becomes available

Static credentials must never become the architecture default.

---

# Human / Workload Separation

Human and workload temporary sessions must remain distinct.

Human sessions must not be reused by:

- Workers
- Backend services
- CI/CD
- Terraform automation
- Runtime jobs

Workload sessions must not be reused as human interactive administrator sessions.

---

# Customer Identity Boundary

Customer sessions and customer authentication tokens are outside this
architecture.

Customer access tokens, passkeys, MFA credentials, passwords, and browser
sessions must never become AWS temporary credentials.

AWS temporary credentials must never be accepted as LinkCraftor customer login
credentials.

---

# Terraform and IaC Boundary

Temporary credential trust and role configuration must ultimately be represented
through approved Terraform/IaC where applicable.

Phase 3 owns the Terraform implementation foundation.

Manual console changes must not become authoritative configuration.

---

# Implementation Boundary

This phase defines architecture only.

It does not yet:

- Configure IAM Identity Center session duration
- Provision STS trust
- Create OIDC providers
- Assign role-session policies
- Configure production SourceIdentity
- Configure session tags
- Create emergency roles
- Issue production workload credentials
- Activate runtime workers

Those actions require later implementation gates.

---

# Runtime Eligibility

This document is an architecture and governance artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future automated credential-lifetime checks, session-policy validation, stale
credential detection, or compliance jobs may require Universal Runtime
Registration Standard assessment.

---

# Phase Dependencies

4.1.6 defines temporary AWS credential architecture.

4.1.7 defines privileged access.

4.1.8 defines cross-environment restrictions.

4.1.9 defines emergency cloud access.

Phase 2 must provide account/environment isolation.

Phase 3 must provide Terraform/IaC implementation.

Later workload, compute, deployment, and operations phases will implement the
actual session mechanisms.

Final Phase 4 certification remains deferred until those implementation
dependencies exist.

---

# Prohibited Practices

The following are prohibited:

- Permanent administrator AWS access keys as the normal human model
- Long-lived workload access keys as the normal service model
- Shared human AWS access keys
- Human sessions reused by workloads
- Workload sessions reused as human administrator sessions
- Customer credentials converted into AWS credentials
- AWS credentials accepted as customer login credentials
- Credentials written to logs
- Credentials embedded in source code
- Credentials embedded in container images
- Credentials placed in queue messages
- Uncontrolled cross-account role assumption
- Session tags that allow self-escalation
- Session policies used to expand authority
- Unapproved credential-provider fallback
- Expired credentials reused
- Temporary sessions treated as permanent identity
- Emergency credentials left permanently active

---

# Canonical Decision Summary

LinkCraftor shall use temporary AWS credentials as the normal access model for
human workforce and workload access.

Human administrators shall use temporary authenticated role sessions.

Workloads shall use AWS-managed or STS-issued temporary credentials through
approved workload identity.

Long-lived static access keys are prohibited as the normal model.

Credential lifetime must be bounded and appropriate to privilege.

Session identity, source identity, tags, and policies must remain controlled and
auditable.

Revocation must not rely solely on expiration.

Human, workload, customer, deployment, and emergency credential classes remain
separate.

Phase 3 and later implementation phases will encode and provision these controls.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
