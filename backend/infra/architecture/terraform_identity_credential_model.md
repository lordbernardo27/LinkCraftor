# LinkCraftor Terraform Identity & Credential Model

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.8 Terraform Identity & Credential Model
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical identity and credential model used by
Terraform.

Terraform must operate through attributable, temporary, environment-scoped AWS
authority.

Long-lived shared AWS credentials are not the normal Terraform model.

---

# Architectural Authorities

This architecture consumes and preserves:

- 3.4 Provider & Account Targeting Architecture
- 3.7 Plan / Apply Separation
- Phase 4 Cloud Administrator Identity
- Phase 4 IAM Role Architecture
- Phase 4 Least-Privilege Model
- Phase 4 Temporary Credentials
- Phase 4 Privileged Access
- Phase 4 Cross-Environment Restrictions

---

# Core Rule

Terraform identities must be separate, attributable, temporary, and scoped.

Terraform credentials must not become universal AWS administrator credentials.

---

# Canonical Terraform Identity Classes

Canonical Terraform identity classes include:

- TerraformPlanIdentity
- TerraformApplyIdentity

Their corresponding AWS role classes include:

- TerraformPlanRole
- TerraformApplyRole

---

# Human-Initiated Terraform

Human-triggered Terraform operations must begin from an approved workforce
identity.

Human users must not rely on shared IAM users or shared static access keys.

---

# Automation-Initiated Terraform

CI/CD or automation may invoke Terraform through approved workload federation.

The automation identity must remain distinct from human administrator identity.

---

# Temporary Credentials

Terraform must use temporary AWS credentials.

Approved mechanisms may include:

- IAM Identity Center-backed role sessions
- STS AssumeRole
- OIDC federation
- Approved CI/CD workload federation

Exact mechanism is selected during implementation.

---

# Static Credential Restriction

Terraform must not routinely rely on:

- Hardcoded AWS access keys
- Shared access-key files
- Embedded secret keys
- Credentials committed to Git
- Long-lived Production access keys

---

# TerraformPlanIdentity

TerraformPlanIdentity must receive only the permissions required to calculate
approved plans.

It should have read-oriented authority where possible.

---

# TerraformApplyIdentity

TerraformApplyIdentity may receive the additional mutation permissions necessary
for approved infrastructure changes.

It must remain bounded by:

- Account
- Environment
- Region
- Role
- SCP
- Permissions boundaries where used
- Resource policies
- KMS policies

---

# Production Terraform Identity

Production Terraform authority must be separately provisioned.

Non-production Terraform identity must not automatically apply to Production.

---

# Organization Terraform Identity

Organization-level Terraform requires dedicated authority appropriate for:

- AWS Organizations
- OUs
- SCPs
- Account governance
- Delegated administration

Organization mutation authority must not be ordinary application deployment
authority.

---

# Security Terraform Identity

Terraform affecting SECURITY account infrastructure requires explicitly approved
security-account authority.

---

# Log Archive Terraform Identity

Terraform affecting LOG-ARCHIVE must preserve evidence-protection boundaries.

---

# Network Terraform Identity

Terraform affecting NETWORK infrastructure requires dedicated network authority.

Network authority must not automatically grant Production application authority.

---

# Deployment Terraform Identity

DEPLOYMENT may host or initiate approved Terraform automation.

Deployment-account identity does not itself grant destination-account mutation.

Destination trust remains required.

---

# Role Assumption

Terraform may assume destination roles through approved STS trust.

Both source permission and destination trust are required.

---

# Credential Chain

Credential resolution must be deterministic.

Production Terraform must not silently fall back to:

- Developer credentials
- Shared local profiles
- Development credentials
- Anonymous credentials
- Embedded keys

---

# AWS Profiles

Local AWS profiles may be used for controlled development or administration
where approved.

Profile names must not be treated as sufficient security validation.

Effective account and role must still be verified.

---

# Environment Variables

AWS credential environment variables must not become persistent shared
Production secrets.

If used temporarily, they must be handled securely and cleared appropriately.

---

# CI/CD Federation

CI/CD should use short-lived federation rather than stored AWS secrets where
supported.

Federation trust must constrain approved:

- Repository
- Workflow
- Branch or release context where appropriate
- Environment
- Role
- Account

---

# OIDC Trust

OIDC trust must validate relevant claims.

Broad wildcard federation into Production is prohibited.

---

# Session Attribution

Terraform sessions should remain attributable.

Where supported and useful, controls may include:

- SourceIdentity
- Session name
- Trusted session tags
- CI/CD job identity

---

# Session Tags

Session tags used for authorization must come from trusted sources.

Self-assigned tags must not increase privilege.

---

# Session Duration

Terraform sessions must have bounded duration.

Higher-risk Production and organization-level authority should use appropriately
short sessions.

Exact durations will be selected during implementation.

---

# Credential Renewal

Credential expiration must not be bypassed through undocumented persistent keys.

Long operations must use approved renewal or reauthentication mechanisms.

---

# State Access Credentials

Access to Terraform state and authority to mutate AWS resources remain distinct.

A Terraform identity may require both, but each permission must be explicitly
granted.

---

# KMS Access

Terraform identity must receive only KMS authority required for its scope.

State encryption or resource encryption does not justify broad KMS
administration.

---

# iam:PassRole

Terraform apply identity may require iam:PassRole for specific managed
infrastructure.

PassRole must be limited to approved roles.

Unrestricted PassRole is prohibited.

---

# Role Creation Boundary

Authority to create IAM roles must be limited and reviewed.

Terraform must not be able to create arbitrary privileged roles beyond approved
architecture.

---

# Trust Policy Mutation

Terraform authority to modify trust policies is security-sensitive.

Production and organization trust changes require stronger review.

---

# Permissions Boundary Interaction

Where permissions boundaries are used, Terraform must not bypass or remove them
without approved authority.

---

# SCP Interaction

Terraform roles remain subject to applicable SCP ceilings.

Terraform role permissions cannot override SCP explicit denies.

---

# Root User Boundary

AWS root credentials must not be used for normal Terraform execution.

Any exceptional root-required action must remain outside normal Terraform
credential flow and follow emergency governance.

---

# Customer Identity Separation

LinkCraftor customer identity is not Terraform cloud authority.

Customer authentication credentials must never become AWS Terraform credentials.

---

# Universal Runtime Separation

Universal Runtime worker identity is not Terraform administrative identity.

Runtime workers must not gain TerraformApplyRole merely because they execute
LinkCraftor jobs.

---

# Credential Storage

Terraform credentials must not be stored in:

- Source code
- Terraform files
- tfvars
- Terraform state intentionally
- Logs
- Queue payloads
- Documentation
- Browser storage
- Runtime job payloads

---

# Credential Logging

Scripts and pipelines must avoid printing AWS secrets or tokens.

Sensitive environment variables must be masked where supported.

---

# Revocation

Terraform access must be revocable.

Revocation must not depend solely on credential expiration.

---

# Access Review

Terraform roles and assignments must be periodically reviewed.

Review should determine:

- Is the identity still required?
- Is plan authority sufficient?
- Is apply authority still justified?
- Is Production access still required?
- Can permissions be reduced?

---

# Emergency Terraform Access

Emergency Terraform access is governed by Phase 4.1.9.

Emergency access must remain temporary, attributable, and audited.

---

# Fail-Closed Requirement

Terraform credential resolution must fail closed when:

- Identity is unknown
- Required role cannot be assumed
- Account does not match
- Environment does not match
- Production authority is absent
- Session is expired
- Federation claims are invalid
- Credential source is ambiguous

---

# Implementation Boundary

This section defines identity architecture only.

It does not yet:

- Create TerraformPlanRole
- Create TerraformApplyRole
- Configure OIDC federation
- Configure IAM Identity Center assignments
- Configure trust policies
- Issue AWS sessions
- Store credentials
- Execute Terraform
- Modify AWS infrastructure

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Shared Terraform AWS user
- Long-lived Production Terraform access key
- Credentials committed to Git
- Production Terraform falling back to Development credentials
- TerraformApplyRole granted to Universal Runtime workers
- Customer credentials used as AWS Terraform credentials
- Broad wildcard OIDC trust into Production
- Self-assigned session tags increasing privilege
- Unrestricted iam:PassRole
- Root credentials used for normal Terraform
- Terraform credentials printed to logs
- State access treated as unrestricted infrastructure authority

---

# Canonical Decision Summary

Terraform uses approved temporary AWS identity.

Planning and application use separately governable identity classes.

Production Terraform authority is independently provisioned.

Human, automation, customer, runtime, and Terraform identities remain distinct.

Long-lived shared AWS credentials are prohibited as the normal model.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
