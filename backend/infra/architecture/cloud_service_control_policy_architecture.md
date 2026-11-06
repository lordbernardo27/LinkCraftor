# LinkCraftor Cloud Service Control Policy Architecture

Version: 1.0
Status: Canonical
Phase: Cloud Organization & Environment Isolation
Section: 2.7 Service Control Policy Architecture
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical Service Control Policy architecture for the
LinkCraftor AWS Organization.

SCPs provide organization-level permission guardrails.

They define maximum available authority.

They do not grant IAM permissions.

---

# Architectural Authorities

This architecture consumes and preserves:

- 2.1 AWS Organization & Account Structure
- 2.2 Organizational Units
- 2.3 Environment Account Isolation
- 2.4 Shared Infrastructure Account Separation
- 2.5 Production Isolation
- 2.6 Cross-Account Trust Boundaries
- Phase 4 Least-Privilege Model
- Phase 4 Cross-Environment Restrictions

---

# Core Rule

Service Control Policies are permission ceilings.

SCPs do not create permissions.

A principal must still receive authorization from IAM or another applicable
AWS permission mechanism.

---

# SCP Evaluation Boundary

Effective AWS authority may be constrained by:

- IAM identity policies
- Permission sets
- Role policies
- Session policies
- Permissions boundaries
- Resource policies
- KMS policies
- Trust policies
- Service Control Policies

An SCP can reduce effective authority.

An SCP cannot independently grant authority.

---

# Attachment Levels

SCPs may be attached at:

- Organization Root
- Organizational Unit
- Individual account

Attachment location must reflect governance intent.

---

# Root-Level Guardrails

Root-level SCPs should contain only controls that are intended to apply broadly
across the LinkCraftor AWS Organization.

Root policies must not unnecessarily block required legitimate service
operation.

---

# Security OU Guardrails

Security OU controls should protect:

- SECURITY
- LOG-ARCHIVE

Potential protections may include restrictions against:

- Disabling required audit services
- Destroying protected evidence
- Weakening centralized security services
- Unauthorized account movement
- Unauthorized region use

Exact implementation will be finalized in Terraform.

---

# Infrastructure OU Guardrails

Infrastructure OU controls apply to:

- NETWORK
- SHARED-SERVICES
- DEPLOYMENT

Guardrails should preserve:

- Network responsibility boundaries
- Shared-services trust restrictions
- Deployment isolation
- Protection against uncontrolled Production authority

---

# Non-Production OU Guardrails

Non-Production OU contains:

- DEVELOPMENT
- TESTING
- STAGING
- SANDBOX

Guardrails must prevent lower environments from silently obtaining Production
authority.

Non-Production may retain broader experimentation rights where safe, but not
rights that bypass Production isolation.

---

# Production OU Guardrails

Production OU receives stronger protective controls appropriate to
customer-facing infrastructure.

Potential protections may include:

- Restriction of unauthorized region use
- Restriction of security-service disablement
- Protection of logging
- Protection of critical IAM boundaries
- Protection of Production data services
- Protection against unauthorized account movement
- Restriction of lower-environment trust

---

# Management Account Boundary

SCP behavior in the AWS Organizations management account differs from member
accounts according to AWS semantics.

Management-account security must therefore not rely only on SCPs.

Root-user protection, workforce identity, MFA, least privilege, and governance
remain mandatory.

---

# Deny Strategy

Explicit Deny may be used for high-confidence prohibited actions.

Deny controls should be:

- Intentional
- Tested
- Documented
- Narrow enough to avoid accidental platform failure
- Version-controlled
- Reviewable

---

# Allow-List Strategy

Where an allow-list SCP strategy is adopted, it must be deliberately designed.

Allow-list strategies may create operational complexity and must not be adopted
casually.

The initial implementation approach must be validated during Phase 3.

---

# Region Guardrail Relationship

Region restrictions are governed further by Phase 2.8.

SCPs may enforce regional boundaries where appropriate.

Canonical region roles remain:

- eu-west-1 — primary
- us-east-1 — disaster-recovery
- af-south-1 — future

---

# Security Service Protection

SCPs may later help protect approved security capabilities from unauthorized
disablement.

Examples may include:

- CloudTrail
- GuardDuty
- Security Hub
- AWS Config
- Security Lake
- Centralized logging
- Approved security automation

Actual services must be finalized in their owning phases.

---

# Log Protection

SCP architecture should support protection against unauthorized deletion or
disablement of centralized audit controls.

Production administrators must not be able to silently erase authoritative
central evidence.

---

# IAM Protection

SCPs may restrict high-risk IAM or organization actions.

Potential high-risk actions include:

- Organization mutation
- SCP mutation
- Unauthorized account movement
- IAM privilege escalation
- Trust-policy changes
- Unrestricted iam:PassRole
- Unauthorized federation modification

SCPs complement rather than replace IAM least privilege.

---

# KMS Protection

SCPs may provide organization-level restrictions related to approved KMS
operations where appropriate.

KMS key policies remain independently authoritative for key access.

---

# Production Protection

Production guardrails should prevent lower-environment or unauthorized
principals from weakening Production protections.

SCP architecture must support independent Production governance.

---

# Account Movement Protection

Movement of accounts between OUs is security-sensitive.

SCP architecture should support protection against unauthorized movement into
weaker policy boundaries.

---

# Delegated Administration Boundary

Delegated AWS service administration must not bypass SCP intent.

Delegated administrators remain subject to their approved account and role
boundaries.

---

# Break-Glass Relationship

Emergency Cloud Access does not automatically bypass SCPs.

If an emergency procedure requires an SCP change, that change must be:

- Explicit
- Approved according to emergency policy
- Audited
- Temporary where possible
- Restored after the incident
- Reviewed afterward

---

# Testing Requirement

Every SCP must be tested before Production attachment.

Testing should include:

- Positive allowed behavior
- Negative denied behavior
- AWS service dependencies
- Automation dependencies
- Recovery path
- Terraform execution compatibility

---

# Rollout Strategy

SCP rollout should progress through controlled stages.

Conceptual progression:

Development
→ Testing
→ Staging
→ Production

Security-critical policies may follow a dedicated validation path where required.

---

# Change Control

SCP changes are security-sensitive.

Changes require:

- Version control
- Review
- Approval appropriate to risk
- Testing
- Evidence
- Rollback plan

---

# Audit Attribution

SCP creation, modification, attachment, and deletion must be attributable.

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Fail-Closed Principle

Where an SCP protects a critical security boundary, failure to validate required
conditions should result in denial where technically appropriate.

Guardrails must not silently fail open.

---

# Terraform and IaC Boundary

SCP definitions and attachments must ultimately be represented through approved
Terraform/IaC.

Phase 3 owns the Terraform implementation foundation.

Manual Console configuration must not become the authoritative SCP source.

---

# Implementation Boundary

This section defines architecture only.

It does not yet:

- Create SCPs
- Attach SCPs
- Modify Organization Root policy
- Modify OU policy
- Modify account-level SCP attachment
- Disable AWS services
- Change Production permissions

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- SCPs treated as permission grants
- Untested SCP attachment to Production
- Broad Deny policies without impact analysis
- Production SCP changes without rollback planning
- Lower-environment policies weakening Production protections
- Emergency SCP changes becoming permanent accidentally
- Manual Console SCP state becoming authoritative
- SCP design replacing IAM least privilege
- Security controls relying exclusively on SCPs

---

# Canonical Decision Summary

LinkCraftor shall use Service Control Policies as organization-level permission
ceilings and governance guardrails.

SCPs will reinforce environment, account, region, Production, security, logging,
and privilege boundaries.

They will not grant permissions and will not replace IAM least privilege.

All implementation will be controlled through Phase 3 Terraform/IaC.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
