# LinkCraftor Cloud Cross-Environment Restrictions

Version: 1.0
Status: Canonical
Phase: Cloud Identity & Access Infrastructure
Section: 4.1.8 Cross-Environment Restrictions
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS cross-environment identity and access
restrictions for LinkCraftor.

It governs how human identities, service identities, workload identities,
temporary credentials, privileged access, CI/CD identities, Terraform identities,
and cross-account trust are separated across environments.

This architecture does not create the AWS accounts themselves.

Phase 2 owns account and environment isolation.

This phase defines the IAM and identity restrictions that must operate across
those account and environment boundaries.

---

# Architectural Authorities

This architecture consumes and preserves:

- 4.1.1 Cloud Administrator Identity
- 4.1.2 IAM Role Architecture
- 4.1.3 Least-Privilege Model
- 4.1.4 Service Identities
- 4.1.5 Workload Identity
- 4.1.6 Temporary Credentials
- 4.1.7 Privileged Access
- Cloud Resource Organization
- Cloud Foundation Certification
- Separation-of-Duties Principles
- Least-Privilege Principles
- Identity / Access / Account Security Architecture

---

# Canonical Environments

Canonical operating environments include:

- Development
- Testing
- Staging
- Sandbox
- Production

Supporting infrastructure domains include:

- Security
- Log Archive
- Network
- Shared Services
- Deployment

Each environment or infrastructure domain must maintain distinct trust and
authorization boundaries appropriate to its purpose.

---

# Core Rule

Access to one environment must not silently authorize another environment.

In particular:

- Development does not imply Testing
- Development does not imply Staging
- Development does not imply Production
- Testing does not imply Staging
- Testing does not imply Production
- Staging does not imply Production
- Sandbox does not imply Production
- Shared Services does not imply unrestricted Production
- Security administration does not imply unrestricted Production application access

Production access always requires independent authorization.

---

# Human Identity Separation

Human AWS access must be environment-specific.

A human permission assignment valid for one environment must not automatically
grant access to another.

Production human access must be separately assigned.

Human users must not receive one broad role merely because they operate across
multiple environments.

---

# Permission-Set Separation

IAM Identity Center permission sets must support environment-specific assignment.

Where the same functional role exists across environments, the assignments and
effective permissions must remain independently governable.

Examples:

- DevelopmentAdministrator
- TestingAdministrator
- StagingAdministrator
- ProductionAdministrator

Equivalent naming may be finalized during implementation, but environment
separation must be preserved.

---

# Production Access Boundary

Production access must be independently authorized.

Production access must not be inherited from:

- Development roles
- Testing roles
- Staging roles
- Sandbox roles
- Repository membership
- CI/CD repository permissions
- Customer product authority
- Generic organization membership

Production access must be:

- Explicit
- Individually attributable
- Justified
- Audited
- Reviewable
- Revocable

---

# Service Identity Separation

Service identities must remain environment-specific where they access
environment-specific resources.

A development service identity must not automatically operate in production.

A testing service identity must not automatically operate in staging or
production.

A staging service identity must not automatically operate in production.

Production service identities must be separately provisioned and trusted.

---

# Workload Identity Separation

Workload identities must remain environment-specific.

A development workload identity must not automatically assume a production role.

A production workload must use independently approved workload trust.

Runtime worker identity does not automatically authorize cross-environment AWS
resource access.

---

# Temporary Credential Separation

Temporary credentials inherit the scope of the approved environment role.

A temporary session issued for Development must not be reused for Production.

A workload session issued for Testing must not silently operate in Staging or
Production.

Production sessions require independently approved trust and role assignment.

---

# Privileged Access Separation

Privileged access remains environment-specific.

Production privileged access requires separate authorization.

Development privileged authority must not automatically grant:

- Production IAM administration
- Production network administration
- Production data administration
- Production runtime administration
- Production security administration

Cross-environment privileged access requires explicit assignment.

---

# Sandbox Boundary

Sandbox is isolated experimentation space.

Sandbox identities must not receive access to:

- Production customer data
- Production databases
- Production secrets
- Production runtime
- Production workers
- Production encryption keys
- Production administrative roles

Sandbox access must not be used as a shortcut into Production.

---

# Shared Services Boundary

Shared Services may support multiple environments but must not become an
uncontrolled bridge between them.

Shared Services identities must be explicitly scoped.

Shared Services access to Production requires approved trust and narrowly scoped
permissions.

Shared infrastructure must not provide implicit Production authority.

---

# Security Account Boundary

Security accounts and security identities must remain separately controlled.

Security visibility does not automatically imply unrestricted mutation authority
over Production workloads.

Security administration and Production administration must remain separable where
required.

---

# Network Account Boundary

Network identities may manage approved network infrastructure.

Network authority must not automatically grant application, database, runtime, or
IAM administration within Production.

Cross-account network operations must use explicit trust and role assignment.

---

# Deployment Account Boundary

Deployment systems must use dedicated deployment identities.

Non-production deployment authority must not automatically imply production
deployment authority.

Production deployment must require separately approved deployment trust.

Repository membership alone does not grant production deployment authority.

---

# CI/CD Environment Separation

CI/CD identities must be environment-specific or explicitly constrained by
trusted environment conditions.

A non-production CI/CD identity must not deploy to Production.

Production deployment federation should validate trusted context such as:

- Repository
- Branch or release context
- Environment
- Workflow
- Approved deployment role

Wildcard production federation trust is prohibited.

---

# Terraform Environment Separation

Terraform execution must preserve environment-specific authority.

TerraformPlanRole and TerraformApplyRole must not become universal
cross-environment roles by default.

Production Terraform execution requires independently approved production
authority.

Terraform state and backend permissions must preserve environment boundaries.

---

# Cross-Account Trust

Cross-account access must require explicit trust.

Both sides must agree:

- Source principal
- Destination role
- Account
- Environment
- Required actions
- Trust conditions

No account may trust another merely because both belong to the same AWS
Organization.

---

# Trust Policy Restrictions

Trust policies must prevent uncontrolled cross-environment role assumption.

Trust may be constrained by:

- Principal ARN
- AWS account
- Organization identifier where appropriate
- Environment tags
- OIDC claims
- Source identity
- Session tags
- External ID where required
- Service principal
- Approved deployment context

Wildcard trust that bridges environments is prohibited.

---

# SCP Boundary

Service Control Policies may provide organization-level maximum-permission
guardrails.

SCPs do not grant permissions.

SCPs may be used later to deny prohibited cross-environment behaviors.

Examples may include:

- Restricting Production mutation from lower environments
- Protecting security/logging accounts
- Restricting unauthorized regions
- Preventing prohibited account-level actions

Detailed SCP implementation belongs to Phase 2 and Phase 3.

---

# Resource Policy Boundary

Resource policies must not bypass environment IAM restrictions.

S3, KMS, SQS, SNS, Secrets Manager, and other resource policies must not create
uncontrolled lower-to-production trust.

Cross-environment resource access requires explicit authorization.

---

# Data Separation

Production data must not be copied into lower environments without an approved,
controlled process.

Development, Testing, Staging, and Sandbox must not receive unrestricted
production customer data.

Shared databases between lower environments and Production are prohibited.

Data masking, synthetic data, or approved sanitized datasets should be used where
appropriate.

---

# Secret Separation

Secrets must remain environment-specific.

Development secrets must not be Production secrets.

Testing and Staging must not reuse Production secrets unless an explicitly
approved exceptional architecture requires it.

Production secret access requires Production workload or human authority.

---

# KMS Separation

Encryption-key access must remain environment-specific where appropriate.

Lower-environment identities must not automatically decrypt Production data.

KMS key policies must preserve account and environment boundaries.

---

# Queue and Runtime Separation

Universal Runtime authorization remains separate from AWS environment
authorization.

A worker authorized to execute a runtime job does not automatically gain access
to Production AWS resources.

Likewise, AWS Production credentials do not automatically authorize arbitrary
runtime jobs.

Both controls must succeed where both apply.

---

# Environment Promotion

Promotion between environments must be controlled.

Promotion should move approved artifacts or configuration through a governed
path.

Promotion must not be implemented by reusing lower-environment credentials in a
higher environment.

Canonical concept:

Development
→ Testing
→ Staging
→ Production

Each promotion boundary requires the authority appropriate to the target
environment.

---

# Artifact Promotion

Artifacts may be promoted across environments after validation.

Identity and credentials are not promoted as artifacts.

Production deployment must use Production deployment identity.

---

# Identity Configuration Separation

Identity-provider configuration must remain environment-specific.

Development, Testing, Staging, and Production should use separate:

- Client identifiers
- Credentials
- Callback URIs
- Issuer allowlists
- Audiences
- Scopes
- Session namespaces

Cross-environment token acceptance is prohibited.

---

# Token Boundary

An identity token issued for one environment must not be accepted as authority
for another environment unless an explicit, approved architecture defines such a
relationship.

Wildcard audiences are prohibited.

Cross-environment token acceptance is prohibited.

---

# Production Data in Lower Environments

Real production customer data must not become the default test or development
dataset.

Any production-derived data used outside Production must follow approved data
classification, minimization, sanitization, privacy, and security controls.

---

# DR Boundary

The disaster-recovery region or capability does not create a separate lower
environment.

DR identity capability does not automatically authorize normal production
operations.

DR activation and access require separately governed recovery controls.

---

# Cross-Environment Session Restrictions

Temporary role sessions must remain bounded by the environment for which they
were issued.

Session tags or SourceIdentity must not be manipulated to falsely represent a
higher environment.

Environment escalation requires a new approved authorization path.

---

# Cross-Environment Privilege Escalation Prevention

A lower-environment principal must not gain Production authority through:

- `iam:PassRole`
- Role creation
- Trust-policy mutation
- Permissions-boundary mutation
- SCP mutation
- Resource-policy mutation
- OIDC claim abuse
- Session-tag manipulation
- Shared credentials
- Shared secrets
- Terraform state access
- Deployment automation

Such pathways must be explicitly prevented.

---

# Audit Attribution

Cross-environment activity must be attributable.

Audit evidence should identify:

- Principal
- Source environment
- Target environment
- Source account
- Target account
- Role
- Session
- API action
- Resource
- Timestamp
- Result

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Access Review

Cross-environment assignments must be reviewable.

Review must determine:

- Is the cross-environment access still required?
- Is Production access justified?
- Is the source principal still valid?
- Is destination trust still appropriate?
- Can the trust be reduced?
- Is any lower-environment role over-privileged?

Unneeded cross-environment trust must be removed.

---

# Fail-Closed Requirement

Cross-environment access must fail closed.

Access must be denied when:

- Environment is unknown
- Source principal is untrusted
- Destination trust is absent
- Role assignment is missing
- Production authorization is absent
- Token audience is wrong
- Session environment is wrong
- Workload trust is invalid
- Required approval is absent
- Cross-account trust is not explicit

---

# Terraform and IaC Boundary

Environment-specific IAM roles, trust policies, assignments, SCPs, resource
policies, and deployment identities must ultimately be represented through
approved Terraform/IaC where applicable.

Phase 3 owns the Terraform implementation foundation.

Manual AWS Console changes must not become authoritative cross-environment
configuration.

---

# Implementation Boundary

This phase defines architecture only.

It does not yet:

- Create environment-specific IAM roles
- Create production permission-set assignments
- Configure cross-account trust
- Configure SCPs
- Configure production OIDC trust
- Configure production resource policies
- Create environment-specific deployment roles
- Configure Terraform environment roles
- Move production data
- Activate production runtime access

Those actions require later implementation gates.

---

# Runtime Eligibility

This document is an architecture and governance artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future automated cross-environment trust validation, role-drift detection,
forbidden-trust detection, or compliance jobs may require Universal Runtime
Registration Standard assessment.

---

# Phase Dependencies

4.1.8 defines cross-environment identity restrictions.

4.1.9 defines emergency cloud access.

Phase 2 must implement AWS account and environment isolation.

Phase 3 must provide Terraform/IaC implementation.

Later deployment, data, networking, storage, compute, and operations phases will
enforce the relevant cross-environment controls.

Final Phase 4 certification remains deferred until those implementation
dependencies exist.

---

# Prohibited Practices

The following are prohibited:

- Development access automatically granting Production access
- Testing access automatically granting Production access
- Staging access automatically granting Production access
- Sandbox identity accessing Production data
- Shared Production and lower-environment credentials
- Shared Production and lower-environment secrets
- Cross-environment token acceptance
- Wildcard audiences across environments
- Wildcard cross-account trust
- Repository membership automatically granting Production access
- Non-production CI/CD identity deploying to Production
- Lower-environment workload identity trusted in Production
- Production customer data copied freely to lower environments
- Shared databases between Production and lower environments
- Lower-environment principals decrypting Production data without explicit approval
- Lower-environment `iam:PassRole` over Production roles
- Cross-environment trust through uncontrolled resource policies
- Manual Console configuration becoming authoritative environment policy

---

# Canonical Decision Summary

LinkCraftor shall maintain strict identity and authorization separation across
Development, Testing, Staging, Sandbox, Production, and supporting AWS accounts.

Production authority must always be independently granted.

Human, service, workload, temporary-session, privileged, CI/CD, and Terraform
identities must remain environment-scoped.

Cross-account and cross-environment trust must be explicit.

Cross-environment token acceptance is prohibited.

Production data, secrets, keys, workloads, and deployment authority must not
silently flow into lower environments.

Phase 2 provides the AWS account boundaries.

Phase 3 provides the Terraform implementation foundation.

This Phase 4.1.8 architecture defines the identity rules that must be enforced
across those boundaries.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
