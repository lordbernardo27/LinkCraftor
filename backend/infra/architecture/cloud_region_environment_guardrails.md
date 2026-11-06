# LinkCraftor Cloud Region & Environment Guardrails

Version: 1.0
Status: Canonical
Phase: Cloud Organization & Environment Isolation
Section: 2.8 Region / Environment Guardrails
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS regional and environment guardrails for
LinkCraftor.

It preserves the approved regional architecture while preventing unauthorized
deployment, data movement, identity use, and service activation across regions
and environments.

---

# Architectural Authorities

This architecture consumes and preserves:

- Cloud Foundation Certification
- Cloud Resource Organization
- 2.3 Environment Account Isolation
- 2.5 Production Isolation
- 2.6 Cross-Account Trust Boundaries
- 2.7 Service Control Policy Architecture
- Phase 4 Cross-Environment Restrictions

---

# Canonical Regions

The canonical AWS regions are:

- eu-west-1 — Ireland — Primary
- us-east-1 — N. Virginia — Disaster Recovery
- af-south-1 — Cape Town — Future

Canonical codes:

- euw1
- use1
- afs1

Canonical RegionRole values:

- primary
- disaster-recovery
- future

The term secondary is noncanonical.

---

# Primary Region

eu-west-1 is the normal Production-serving region at launch.

Normal Production deployment should target eu-west-1 unless another approved
architecture explicitly authorizes otherwise.

---

# Disaster-Recovery Region

us-east-1 is the controlled disaster-recovery region.

It may support:

- Backup
- Recovery
- Replication
- DR readiness
- Controlled failover
- Recovery testing

It is not the default normal active-serving Production region.

---

# Future Region

af-south-1 is reserved for future use.

Its inclusion in architecture does not authorize immediate Production
deployment.

Activation requires a later approved implementation decision.

---

# Region Allowlist

Infrastructure must use approved regions only.

Unauthorized region deployment must be denied or detected according to the
service and implementation mechanism.

---

# Global AWS Services

Some AWS services are global or have global control-plane characteristics.

Region guardrails must not incorrectly block required global services.

Examples may include:

- IAM
- AWS Organizations
- Route 53
- CloudFront
- IAM Identity Center
- Other AWS global services

Actual service behavior must be validated during implementation.

---

# Production Regional Boundary

Normal Production workloads must not silently deploy outside approved Production
regions.

Production deployment authority must preserve regional restrictions.

---

# Development Regional Boundary

Development may use only approved regions unless an explicitly approved test
requires otherwise.

Experimental regional use must not weaken Production controls.

---

# Testing Regional Boundary

Testing must remain within approved test regions.

Testing activity must not silently create Production-grade infrastructure in
unapproved regions.

---

# Staging Regional Boundary

Staging should remain aligned with Production regional architecture where
appropriate for validation.

Staging must not itself become an unauthorized Production region.

---

# Sandbox Regional Boundary

Sandbox experimentation must remain region-governed.

Sandbox experimentation in an unapproved region requires explicit approval.

Sandbox use must not create hidden long-lived infrastructure.

---

# Environment Guardrail Rule

Environment identity and region authorization are separate controls.

A principal authorized for Development does not gain Production authority merely
because both resources are in eu-west-1.

Likewise, being authorized for a region does not grant access to every
environment in that region.

---

# Region and Account Interaction

Region controls do not replace AWS account isolation.

Account isolation remains mandatory even when environments operate in the same
region.

---

# Region and Identity Interaction

IAM roles and workload identities should be restricted to approved regional
scope where technically appropriate.

Region conditions may be used where supported and safe.

---

# aws:RequestedRegion Boundary

`aws:RequestedRegion` may be used in IAM or SCP conditions where appropriate.

Its semantics must be validated for each AWS service, especially global
services.

It must not be applied blindly.

---

# Cross-Region Data Movement

Production data movement between regions must be explicitly authorized.

Cross-region replication does not automatically imply unrestricted read or write
access.

---

# Production Data Residency

Data residency requirements must be considered before enabling regional
replication or processing.

Actual legal and contractual residency requirements remain governed by the
appropriate privacy, security, and data architectures.

---

# DR Replication

Replication from eu-west-1 to us-east-1 must be purpose-specific.

Approved DR replication does not make us-east-1 a normal unrestricted Production
environment.

---

# DR Activation

DR activation requires an approved recovery or failover decision.

Identity capability in us-east-1 does not itself authorize failover.

---

# Return From DR

After DR use, return to normal Production operation must follow a controlled
recovery process.

Temporary emergency trust must not remain indefinitely.

---

# Future Cape Town Activation

Before af-south-1 becomes active, LinkCraftor must define:

- Workload purpose
- Data classification
- Production or non-production role
- Account usage
- Network architecture
- IAM trust
- Backup requirements
- Monitoring
- Cost model
- Compliance impact

---

# Regional Service Availability

Before relying on an AWS service in any canonical region, implementation must
confirm that the required feature is available in that region.

Architecture naming alone does not prove service availability.

---

# Regional Dependency Control

Production must not depend on an unapproved region for normal operation.

Cross-region dependencies must be documented.

---

# Regional Secret Boundary

Production secrets must not automatically replicate into every region.

Secret replication must be explicit and justified.

---

# Regional KMS Boundary

KMS keys are region-specific unless AWS provides a separately approved
multi-region architecture.

Encryption architecture must preserve approved regional boundaries.

---

# Regional Storage Boundary

Cross-region object replication must use explicitly approved destination,
encryption, retention, and access controls.

---

# Regional Database Boundary

Cross-region database replication must be explicitly architected.

DR database replicas must not become hidden normal write-primary systems without
approved failover.

---

# Regional Queue Boundary

Queue and event infrastructure must remain region-aware.

Cross-region event delivery must be explicit and auditable.

---

# Regional Runtime Boundary

Universal Runtime execution authority does not automatically authorize execution
against resources in every region.

AWS region authorization and runtime authorization remain separate.

---

# Regional Deployment Guardrail

CI/CD and Terraform must target approved regions.

Production pipelines must not silently deploy to arbitrary regions.

---

# Regional Tagging

Resources should carry approved environment and region-purpose metadata where
appropriate.

Tags may support governance but must not be the only security boundary.

---

# SCP Relationship

SCPs may enforce region restrictions where technically appropriate.

Exceptions for required global services must be deliberately handled.

---

# Monitoring

Unauthorized regional activity must be detectable.

Later observability phases should monitor:

- Resource creation in unapproved regions
- Unexpected API activity
- Cross-region data movement
- Unauthorized replication
- DR activation activity

---

# Audit Attribution

Regional control-plane actions must be attributable.

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Fail-Closed Requirement

Where regional restrictions are security-critical, access should fail closed
when approved regional context cannot be validated.

---

# Terraform and IaC Boundary

Region allowlists, provider configuration, SCP conditions, and environment
regional mappings must ultimately be represented through approved Terraform/IaC
where applicable.

Phase 3 owns implementation.

---

# Implementation Boundary

This section defines architecture only.

It does not yet:

- Attach region SCPs
- Configure AWS providers
- Deploy resources
- Configure DR replication
- Enable failover
- Activate Cape Town
- Move Production data
- Configure regional KMS
- Configure cross-region databases
- Configure cross-region storage

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Arbitrary Production deployment to unapproved regions
- Treating us-east-1 as default active Production
- Activating af-south-1 merely because it is architecturally reserved
- Production depending silently on an unapproved region
- Cross-region Production data movement without approval
- Blind use of aws:RequestedRegion without service validation
- Region authorization treated as environment authorization
- Lower-environment authority treated as Production authority
- DR identity capability automatically activating DR
- Temporary DR trust remaining permanently active
- Manual regional configuration becoming authoritative architecture

---

# Canonical Decision Summary

eu-west-1 is LinkCraftor's primary Production region.

us-east-1 is the controlled disaster-recovery region.

af-south-1 is reserved for future activation.

Regions and environments remain separate authorization dimensions.

Production, DR, data movement, identities, deployment, and Terraform must obey
approved regional guardrails.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
