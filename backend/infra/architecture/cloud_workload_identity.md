# LinkCraftor Cloud Workload Identity

Version: 1.0
Status: Canonical
Phase: Cloud Identity & Access Infrastructure
Section: 4.1.5 Workload Identity
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS workload-identity architecture for
LinkCraftor.

It defines how an executing non-human workload proves and obtains the service
identity defined by Phase 4.1.4.

This architecture covers:

- AWS workload principals
- Execution-environment identity
- IAM-role attachment
- STS role assumption
- OIDC workload federation
- ECS task roles
- EC2 instance profiles
- Lambda execution roles
- CI/CD workload identity
- Universal Runtime workload identity
- Trusted issuer integration
- Workload/service identity mapping
- Environment and account isolation
- Credential acquisition
- Trust verification
- Runtime integration boundaries
- Audit attribution

This architecture does not create a new runtime worker identity authority.

Existing Universal Runtime identity, signed-grant, lease, replay, revocation,
queue, and handler authorization controls remain authoritative.

---

# Architectural Authorities

This architecture consumes and preserves:

- 4.1.1 Cloud Administrator Identity
- 4.1.2 IAM Role Architecture
- 4.1.3 Least-Privilege Model
- 4.1.4 Service Identities
- Existing Universal Runtime worker identity validation
- Existing AK.6 signed execution grants
- Existing AK.6 authoritative persisted lease
- Existing AK.6 operational trust
- Existing queue-claim authorization
- Existing handler/stage binding
- Existing Universal Job submission architecture

This document must integrate with those systems rather than duplicate them.

---

# Workload Identity Definition

A workload identity is the verifiable identity of an executing software
workload.

It answers:

"Which approved workload instance is currently executing?"

Workload identity is distinct from:

- Customer identity
- Human workforce identity
- Logical service identity
- Application authorization
- Job authorization

A workload identity implements the logical service identity defined by 4.1.4.

---

# Service Identity Relationship

Phase 4.1.4 defines the logical service principal.

Phase 4.1.5 defines how an executing workload proves that principal.

Canonical relationship:

Logical service identity
→ approved execution environment
→ workload identity mechanism
→ IAM role
→ temporary AWS credentials
→ approved AWS resource access

---

# Existing Universal Runtime Authority

Universal Runtime already contains authoritative runtime trust controls.

These include:

- Worker identity validation
- Worker/job assignment binding
- Execution binding
- Persisted queue claim verification
- Authoritative worker lease
- Signed execution grants
- Trusted issuer verification
- Machine-pinned verifier key
- Windows worker SID validation
- Durable replay protection
- Revocation enforcement
- Queue claim gating
- Handler/stage binding
- Fail-closed execution

These controls must be reused.

Cloud workload identity must not create a second runtime identity or execution
authorization system.

---

# Runtime Trust Boundary

AWS workload identity and Universal Runtime trust solve different layers.

AWS workload identity answers:

"Which AWS workload principal is executing?"

Universal Runtime trust answers:

"Is this worker authorized to execute this specific job, stage, handler, and
lease?"

Both must succeed for protected runtime execution where both apply.

AWS IAM authorization alone must not authorize a Universal Runtime job.

Universal Runtime authorization alone must not grant arbitrary AWS permissions.

---

# Workload Identity Principle

Every AWS workload must use an identity mechanism appropriate to its execution
environment.

A workload must not depend on:

- Human credentials
- Customer credentials
- Shared administrator credentials
- Permanent embedded access keys
- Caller-supplied identity claims
- Network location alone

---

# Canonical AWS Workload Identity Mechanisms

Approved workload identity mechanisms may include:

- ECS task roles
- EC2 instance profiles
- Lambda execution roles
- AWS STS AssumeRole
- OIDC workload federation
- Approved CI/CD federation
- Other AWS-native workload identity mechanisms approved later

The mechanism used must match the actual deployment architecture.

No workload identity mechanism is provisioned merely because it appears in this
architecture.

---

# ECS Task Roles

If LinkCraftor workloads execute on ECS, each workload should use an appropriate
ECS task role.

The task role represents the workload's AWS identity.

The ECS execution role and application task role must remain distinguishable.

Application permissions belong to the task role.

Infrastructure needed by the ECS agent or task startup belongs to the execution
role where AWS requires it.

Unrelated services must not share one broad task role.

---

# EC2 Instance Profiles

If a workload executes directly on EC2, AWS permissions should be delivered
through an approved instance profile and IAM role.

Static AWS access keys must not be installed on the instance as the normal
workload identity model.

Instance roles must remain narrowly scoped.

Where multiple workloads on one host require materially different permissions,
the architecture must avoid using one overly broad instance role as a substitute
for workload isolation.

---

# Lambda Execution Roles

If LinkCraftor workloads execute in AWS Lambda, each Lambda workload or related
workload family must use an approved execution role.

Lambda execution roles must contain only the permissions required by the
function.

One Lambda function must not inherit unrelated runtime, deployment, queue,
storage, or administrative authority.

---

# STS Role Assumption

AWS STS may be used where a workload must assume an approved IAM role.

AssumeRole trust must identify the approved principal.

STS assumption must not allow:

- Uncontrolled cross-account access
- Privilege escalation
- Human-to-workload identity substitution
- Workload-to-human permission substitution

Detailed temporary credential lifetime and session architecture is governed by
4.1.6.

---

# OIDC Workload Federation

OIDC federation may be used for approved external workload identity sources.

Examples may include:

- CI/CD systems
- Approved deployment automation
- Other trusted workload platforms

OIDC trust must validate:

- Issuer
- Audience
- Subject
- Repository or workload identity where applicable
- Environment
- Approved branch or deployment context where applicable

Wildcard federation trust is prohibited.

---

# CI/CD Workload Identity

CI/CD pipelines must use dedicated workload identity.

Repository access alone must not grant AWS authority.

Approved CI/CD identity must map through an explicit trust contract to an AWS
deployment role.

Production deployment identity must be independently governed from
non-production deployment identity.

---

# Universal Runtime Workload Identity

Universal Runtime workers must retain their existing runtime identity authority.

AWS workload identity must map the running worker environment to an approved AWS
service identity without replacing:

- Worker identity validation
- Signed execution grants
- Queue claims
- Lease validation
- Runtime job authorization
- Handler authorization
- Replay protection
- Revocation

The AWS layer supplies cloud resource identity.

The runtime layer supplies runtime execution authority.

---

# Worker Operating-System Identity

Where the worker runs on Windows, the existing Windows worker principal and SID
validation remain authoritative for the runtime trust layer.

AWS workload identity must not weaken that validation.

If the worker later moves to an AWS-native compute platform, the runtime
architecture must explicitly define how the platform workload identity maps to
the existing trusted worker identity model.

No silent migration of trust is permitted.

---

# Trusted Issuer Integration

Production workload trust requires a separately trusted issuer where the
existing runtime grant architecture requires externally issued grants.

The issuer must remain outside the worker's authority.

The worker must not:

- Generate its own production signing key
- Authorize its own workload identity
- Modify its protected trust root
- Replace its pinned issuer key
- Issue its own execution grant

Issuer provisioning must be handled through approved deployment/IAM/security
controls.

---

# Issuer Key Protection

Trusted issuer public verification material must be protected.

Existing runtime machine-pinned trust requirements remain authoritative.

A workload must not accept an issuer key merely because it was supplied through:

- Job metadata
- Environment input controlled by the workload
- Queue payload
- Caller parameter
- User input
- Untrusted configuration

Protected trust configuration must be provisioned independently.

---

# Job and Stage Binding

AWS workload identity must not weaken existing job/stage binding.

A valid AWS role does not authorize execution of any arbitrary Universal Runtime
job.

Existing runtime controls must continue to enforce:

- Job identity
- Workspace identity
- Stage identity
- Handler identity
- Worker identity
- Execution identity

---

# Lease Binding

Protected runtime execution must continue to enforce the authoritative persisted
worker lease.

AWS identity does not replace lease validation.

The active worker must match the stored:

- Worker ID
- Worker instance identity
- Lease owner
- Lease ID
- Lease validity window

---

# Replay Protection

Existing runtime nonce and grant replay protection remains authoritative.

AWS credential validity does not make a replayed execution grant valid.

Replay-safe execution must preserve:

- Single-use execution semantics where required
- Durable grant state
- Revocation state
- Lease binding
- Job binding

---

# Revocation

Workload identity must support revocation at both relevant layers.

AWS-layer revocation may include:

- Trust-policy removal
- Role disablement
- Federation removal
- Credential/session expiry
- Deployment identity disablement

Runtime-layer revocation remains responsible for:

- Grant revocation
- Runtime worker trust
- Execution authorization
- Lease validity
- Runtime trust state

One layer must not silently bypass revocation in the other.

---

# Queue Claim Boundary

Queue claims remain governed by existing Universal Runtime queue authorization.

AWS queue permissions alone must not imply permission to claim or execute every
runtime job.

The runtime queue-claim gate and existing authorization logic remain mandatory.

---

# Handler Authorization Boundary

Existing handler and canonical stage binding remain authoritative.

Possession of AWS credentials must not allow a workload to invoke an arbitrary
pipeline handler.

The requested handler must continue to match the job's canonical stage and
registered execution scope.

---

# Fail-Closed Requirement

Workload identity must fail closed.

Protected execution must be denied when required trust cannot be proven.

Failure cases include:

- Missing workload identity
- Invalid IAM trust
- Untrusted issuer
- Invalid worker identity
- Missing signed grant
- Invalid signature
- Expired grant
- Replay
- Revoked grant
- Job mismatch
- Stage mismatch
- Handler mismatch
- Worker mismatch
- Missing lease
- Lease mismatch
- Expired lease
- Invalid execution environment

---

# Credential Acquisition

Workloads must acquire AWS credentials from approved workload identity
mechanisms.

Preferred pattern:

Trusted workload environment
→ approved IAM role
→ AWS STS or AWS-managed credential delivery
→ short-lived AWS credentials

Long-lived embedded access keys must not become the normal workload mechanism.

Detailed credential lifetime and renewal rules are governed by 4.1.6.

---

# Credential Provider Chain

AWS SDK credential provider chains may be used only when their sources are
understood and constrained.

Production workloads must not accidentally fall back to:

- Developer credentials
- Local user profiles
- Shared personal credentials
- Unapproved environment credentials
- Arbitrary static access keys

The production workload credential source must be deterministic and documented.

---

# Environment Isolation

Workload identities must remain environment specific.

Development workload identity must not automatically operate in:

- Testing
- Staging
- Production

Testing identity must not automatically operate in production.

Production workload identity must be separately provisioned and trusted.

---

# Account Isolation

Workload identity must respect AWS account boundaries.

A workload identity valid in one account does not automatically gain authority
in another.

Cross-account workload identity requires explicit trust on both sides.

---

# Region Scope

Where meaningful, workload identity permissions should remain constrained to the
approved region.

Canonical regions remain:

- eu-west-1 — primary
- us-east-1 — disaster-recovery
- af-south-1 — future

DR workload capability does not imply unrestricted normal production operation
in the DR region.

---

# Least Privilege

All workload identities must comply with 4.1.3 Least-Privilege Model.

A workload receives only:

- Required actions
- Required resources
- Required account
- Required environment
- Required region
- Required trust conditions

Workload identity does not justify broad AdministratorAccess.

---

# Service Identity Mapping

Every workload identity must map to an approved service identity defined by
4.1.4.

The mapping must identify:

- Logical service
- Execution environment
- AWS role
- Environment
- Account
- Trust source
- Required permissions
- Runtime authority where applicable

Unowned workload identities are prohibited.

---

# Workload Identity Ownership

Every workload identity must have an accountable owner.

Ownership must cover:

- IAM trust
- Role mapping
- Runtime mapping
- Deployment mechanism
- Credential source
- Review
- Revocation
- Incident response
- Decommissioning

---

# Audit Attribution

Workload activity must be attributable.

Audit evidence should allow correlation among:

- Service identity
- Workload identity
- IAM role
- STS session where applicable
- AWS account
- Environment
- Region
- Worker identity
- Runtime job ID
- Execution ID
- Lease ID
- API action
- Resource
- Timestamp
- Result

AWS CloudTrail remains the canonical AWS control-plane audit source.

Runtime evidence remains authoritative for Universal Runtime execution history.

---

# Terraform and IaC Boundary

AWS workload identity configuration must ultimately be represented through
approved Terraform/IaC where applicable.

Phase 3 owns the Terraform implementation foundation.

Manual console configuration must not become the authoritative identity state.

---

# Implementation Boundary

This phase defines architecture only.

It does not yet:

- Create AWS IAM roles
- Create OIDC providers
- Provision ECS task roles
- Provision EC2 instance profiles
- Provision Lambda roles
- Configure production STS trust
- Provision runtime issuer infrastructure
- Change worker activation state
- Activate production queue claims
- Activate production handlers

Those actions require later approved implementation gates.

---

# Universal Runtime Activation Boundary

This architecture does not authorize production worker activation.

Existing Universal Runtime readiness and activation gates remain authoritative.

Cloud workload identity integration must be completed and verified before any
production activation that depends on it.

---

# Runtime Eligibility

This document is an architecture and governance artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future automated workload-identity validation, trust verification, role
inspection, or compliance jobs may require Universal Runtime Registration
Standard assessment.

---

# Phase Dependencies

4.1.5 defines workload identity and execution trust integration.

4.1.6 defines temporary credentials.

4.1.7 defines privileged access.

4.1.8 defines cross-environment restrictions.

4.1.9 defines emergency cloud access.

Phase 2 must provide implemented account/environment isolation.

Phase 3 must provide Terraform/IaC.

Later compute and deployment phases must select and provision the actual AWS
workload mechanisms.

Final Phase 4 certification remains deferred until those implementation
dependencies exist.

---

# Prohibited Practices

The following are prohibited:

- Creating a duplicate Universal Runtime worker identity authority
- Replacing signed execution grants with AWS IAM alone
- Replacing authoritative leases with AWS IAM alone
- Replacing queue authorization with AWS IAM alone
- Replacing handler/stage authorization with AWS IAM alone
- Worker-generated production signing keys
- Worker-issued production grants
- Caller-supplied trusted issuer
- Caller-supplied workload identity
- Human credentials used as workload identity
- Customer credentials used as workload identity
- Shared administrator credentials used by workloads
- Long-lived embedded access keys as normal workload credentials
- Development workload identity automatically trusted in production
- Repository membership automatically granting AWS production workload authority
- Wildcard OIDC federation trust
- Uncontrolled cross-account workload trust
- Runtime activation before required trust integration
- Manual AWS identity state becoming authoritative configuration

---

# Canonical Decision Summary

LinkCraftor workload identity shall implement, not replace, the service identity
architecture defined by 4.1.4.

AWS-native workload identity mechanisms may include ECS task roles, EC2 instance
profiles, Lambda execution roles, STS role assumption, and OIDC federation.

Actual mechanism selection depends on the final deployment architecture.

Existing Universal Runtime worker identity, signed grants, persisted leases,
replay protection, revocation, queue authorization, and handler/stage binding
remain authoritative.

AWS workload identity provides cloud-resource identity.

Universal Runtime provides runtime execution authority.

Production trust requires independently provisioned workload trust and issuer
controls.

Phase 4.1.6 will define the short-lived credential architecture used after
workload identity is established.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
