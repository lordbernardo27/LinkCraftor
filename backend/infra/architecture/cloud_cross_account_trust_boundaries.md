# LinkCraftor Cloud Cross-Account Trust Boundaries

Version: 1.0
Status: Canonical
Phase: Cloud Organization & Environment Isolation
Section: 2.6 Cross-Account Trust Boundaries
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical cross-account trust architecture for the
LinkCraftor AWS Organization.

It governs how principals and services in one AWS account may obtain authority
in another AWS account.

---

# Architectural Authorities

This architecture consumes and preserves:

- 2.1 AWS Organization & Account Structure
- 2.2 Organizational Units
- 2.3 Environment Account Isolation
- 2.4 Shared Infrastructure Account Separation
- 2.5 Production Isolation
- Phase 4 IAM Role Architecture
- Phase 4 Temporary Credentials
- Phase 4 Cross-Environment Restrictions

---

# Core Rule

Cross-account access requires explicit trust.

AWS Organization membership alone does not grant cross-account authority.

---

# Two-Sided Authorization

Cross-account role assumption requires both:

1. Source-side permission to assume the destination role.
2. Destination-side trust permitting the source principal.

One side alone is insufficient.

---

# Source Principal

The source principal must be explicitly identifiable.

Potential source principals include:

- IAM Identity Center-backed human roles
- AWS IAM roles
- Approved workload roles
- Deployment roles
- Security automation roles
- Terraform roles
- Approved AWS service principals

Shared anonymous trust is prohibited.

---

# Destination Role

The destination account must expose an explicitly approved role or resource
policy.

A destination must not rely on broad implicit trust.

---

# Account Scope

Cross-account trust must identify the approved source and destination account
boundaries.

Trust across every account in the organization must not be granted merely for
convenience.

---

# Environment Scope

Cross-account trust must preserve environment separation.

Non-production principals must not automatically receive Production authority.

Production trust requires independent authorization.

---

# Human Cross-Account Access

Human cross-account access must remain attributable.

Human users must access destination authority through approved role assumption or
approved workforce mechanisms.

Shared static credentials are prohibited.

---

# Workload Cross-Account Access

Workloads must use approved workload identity.

A Development workload identity must not automatically assume a Production
destination role.

Production workload trust must be separately provisioned.

---

# Deployment Cross-Account Access

DEPLOYMENT may access environment accounts only through explicitly approved
deployment roles.

Production deployment trust must be separately governed from non-production
deployment trust.

---

# Security Cross-Account Access

SECURITY may receive approved cross-account security authority.

Security visibility must be distinguishable from mutation authority.

Security roles should receive only the permissions required for their security
function.

---

# Log Archive Cross-Account Access

LOG-ARCHIVE may receive approved log-delivery or evidence-ingestion access.

Workload accounts may deliver evidence without receiving destructive Log Archive
administration.

---

# Network Cross-Account Access

NETWORK may receive approved networking authority.

Network trust must not automatically grant application, database, IAM, or
customer-data authority.

---

# Shared Services Cross-Account Access

SHARED-SERVICES cross-account relationships must be explicitly scoped.

Shared Services must not become a universal trust hub.

---

# Production Cross-Account Trust

Production cross-account trust requires stronger control.

Every Production trust relationship must identify:

- Source principal
- Source account
- Destination role or resource
- Required actions
- Environment
- Session controls
- Approval basis

---

# IAM Role Trust Policies

IAM trust policies must use explicit principals and conditions where appropriate.

Potential conditions may include:

- Principal ARN
- Source account
- AWS Organization ID
- OIDC claims
- Environment tags
- SourceIdentity
- Session tags
- External ID
- Service-specific conditions

Organization ID alone must not be treated as sufficient authorization for
sensitive access.

---

# Wildcard Principal Boundary

Wildcard principals must not be used for sensitive cross-account trust unless a
specific AWS service architecture requires them and compensating conditions make
the trust appropriately constrained.

Unrestricted wildcard Production trust is prohibited.

---

# External ID

External ID must be used where required for approved third-party cross-account
access patterns.

External ID does not replace principal validation or least privilege.

---

# SourceIdentity

AWS STS SourceIdentity should be used where supported and beneficial to preserve
attribution across role assumptions.

A caller must not spoof another principal's source identity.

---

# Session Tags

Session tags may carry approved cross-account attribution or authorization
context.

Tags used for authorization must originate from trusted sources.

Self-assigned tags must not increase privilege.

---

# Temporary Credentials

Cross-account role assumption must use temporary credentials.

Long-lived static shared credentials must not become the normal cross-account
mechanism.

---

# Role Chaining

Role chaining must be deliberately governed.

A principal must not gain broader authority merely by traversing multiple roles.

Chained sessions remain constrained by applicable AWS session-duration and
permission rules.

---

# Permission Ceiling

Cross-account sessions remain constrained by all applicable permission layers:

- Source permissions
- Destination role permissions
- Session policies
- Permissions boundaries
- SCPs
- Resource policies
- KMS policies
- Trust conditions

Cross-account access never expands authority beyond those limits.

---

# Resource Policies

Cross-account resource policies must remain explicit and least-privileged.

Applicable services may include:

- S3
- KMS
- SQS
- SNS
- Secrets Manager
- EventBridge
- ECR
- Other approved AWS services

Resource policies must not create accidental organization-wide trust.

---

# KMS Cross-Account Trust

KMS cross-account use requires explicit key policy and IAM authorization where
required by AWS.

Production encryption keys must not automatically trust lower environments.

---

# Cross-Account Data Access

Cross-account data access must be explicitly justified.

Access to an account does not automatically mean access to every dataset within
that account.

Data-security rules remain independently enforceable.

---

# Cross-Account Secret Access

Secrets must not become organization-wide merely because accounts share an AWS
Organization.

Cross-account secret access requires explicit policy.

---

# Cross-Account Network Access

Network connectivity does not create IAM trust.

A reachable resource remains protected by its IAM, resource-policy, application,
and data authorization controls.

---

# Cross-Account Runtime Boundary

Universal Runtime authority remains separate from AWS cross-account authority.

A worker authorized to execute a job does not automatically receive destination
AWS account access.

Destination AWS access does not automatically authorize runtime execution.

---

# Privilege Escalation Prevention

Cross-account trust must not create indirect privilege-escalation paths.

High-risk pathways include:

- `iam:PassRole`
- Trust-policy mutation
- Role creation
- Permissions-boundary mutation
- Resource-policy mutation
- KMS policy mutation
- Session-tag abuse
- OIDC claim abuse

These pathways require explicit control.

---

# Cross-Account Emergency Access

Emergency cross-account access remains governed by Phase 4.1.9 Emergency Cloud
Access.

Emergency authority in one account must not automatically propagate to another.

---

# Audit Attribution

Cross-account activity must be attributable across both source and destination
contexts.

Evidence should identify:

- Source principal
- Source account
- Destination account
- Destination role
- Session
- Source identity where available
- API action
- Resource
- Timestamp
- Result

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Trust Review

Cross-account trust relationships must be periodically reviewable.

Review should determine:

- Is the source still valid?
- Is the destination role still required?
- Is Production access still justified?
- Can the scope be reduced?
- Are trust conditions still appropriate?
- Is the relationship still actively used?

Unused trust should be removed.

---

# Fail-Closed Requirement

Cross-account access must fail closed when:

- Source principal is unknown
- Source permission is absent
- Destination trust is absent
- Destination role is invalid
- Environment authorization is absent
- Required condition is missing
- Session is expired
- Source identity is invalid
- Required approval is absent

---

# Terraform and IaC Boundary

Cross-account roles, trust policies, resource policies, and related conditions
must ultimately be represented through approved Terraform/IaC where applicable.

Phase 3 owns the Terraform implementation foundation.

---

# Implementation Boundary

This section defines architecture only.

It does not yet:

- Configure IAM trust policies
- Create cross-account roles
- Configure resource policies
- Configure KMS cross-account access
- Configure STS SourceIdentity
- Configure session tags
- Configure Production deployment trust
- Configure security delegated access
- Issue cross-account sessions

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Organization membership treated as cross-account permission
- Shared static cross-account credentials
- Wildcard Production trust
- Non-production identities automatically trusted in Production
- Shared human access keys
- Universal cross-account workload identities
- Shared Services used as an unrestricted trust hub
- Network connectivity treated as authorization
- Security visibility automatically granting Production mutation
- Session tags used for self-escalation
- Unrestricted cross-account `iam:PassRole`
- Resource policies creating uncontrolled organization-wide access
- Emergency authority automatically propagating between accounts

---

# Canonical Decision Summary

Cross-account access within LinkCraftor must use explicit two-sided trust.

Source permission and destination trust are both required.

Production cross-account relationships require independent authorization.

Human, workload, deployment, security, networking, logging, shared-service, and
emergency trust paths remain separately governed.

Organization membership alone never grants cross-account authority.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
