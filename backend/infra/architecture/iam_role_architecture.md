# LinkCraftor IAM Role Architecture

Version: 1.0
Status: Canonical
Phase: Cloud Identity & Access Infrastructure
Section: 4.1.2 IAM Role Architecture
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS IAM role and AWS IAM Identity Center
permission-set architecture for LinkCraftor.

It defines:

- Role and permission-set classes
- Human workforce role taxonomy
- Deployment and automation role taxonomy
- Workload/service role boundaries
- Trust-policy boundaries
- Cross-account role rules
- Production-role separation
- Read-only and audit-role separation
- Role naming and lifecycle requirements
- Separation-of-duties boundaries
- Relationship to least-privilege implementation

This document defines role architecture.

It does not define the complete detailed AWS permissions for every role.

Detailed permission minimization is governed by Phase 4.1.3 Least-Privilege
Model.

---

# Architectural Authorities

This architecture consumes and preserves:

- 4.1.1 Cloud Administrator Identity
- Cloud Resource Organization
- Cloud Naming Standards
- Infrastructure Configuration Standards
- Least-Privilege Principles
- Separation-of-Duties Principles
- Identity / Access / Account Security Architecture

This document must not create a competing customer authorization model.

AWS IAM remains responsible for AWS workforce and workload authorization.

LinkCraftor application authorization remains responsible for LinkCraftor
product and workspace authorization.

---

# Principal Classes

LinkCraftor recognizes three primary AWS principal classes:

1. Human workforce principals
2. Deployment and automation principals
3. Workload and service principals

These principal classes must remain separately governed.

A human principal must not be used as a production workload identity.

A workload principal must not be used as a human console identity.

A deployment principal must not silently become a general human administrator
identity.

---

# Human Workforce Permission Sets

Normal human AWS access through AWS IAM Identity Center shall use approved
permission sets.

Canonical human permission-set classes are:

- OrganizationAdministrator
- CloudPlatformAdministrator
- SecurityAdministrator
- DeploymentAdministrator
- ProductionAdministrator
- NetworkAdministrator
- DataInfrastructureAdministrator
- ReadOnlyOperator
- Auditor
- EmergencyAdministrator

These are responsibility classes.

They do not imply unrestricted AdministratorAccess.

Each permission set must be scoped by:

- AWS account
- Environment
- Responsibility
- Required privilege
- Approved session boundary
- Security controls

---

# OrganizationAdministrator

OrganizationAdministrator is the highest routine organization-governance
responsibility class.

It may govern:

- AWS Organizations
- Organizational Units
- Account lifecycle
- Service Control Policies
- Delegated organization administration
- IAM Identity Center organization-level configuration

It must not automatically receive unrestricted routine production application
administration.

It must not be the normal role used for application engineering.

Management-account access must remain more restricted than ordinary
non-production administration.

---

# CloudPlatformAdministrator

CloudPlatformAdministrator governs shared infrastructure and platform-level AWS
resources within explicitly assigned accounts.

It may include responsibility for:

- Compute infrastructure
- Shared services
- Platform configuration
- General infrastructure operations
- Approved infrastructure troubleshooting

It must not automatically grant:

- Organization-level governance
- Security administration
- Production data administration
- Unrestricted IAM administration
- Emergency access

---

# SecurityAdministrator

SecurityAdministrator governs approved AWS security controls.

Potential responsibility includes:

- Security Hub
- GuardDuty
- IAM security controls
- Access Analyzer
- Security findings
- KMS governance where approved
- Security configuration
- Security investigation

SecurityAdministrator must not automatically grant:

- General application administration
- Unrestricted production data access
- Organization administration
- Routine deployment authority

Security administrators must not be able to silently erase required audit
evidence of their own actions.

---

# DeploymentAdministrator

DeploymentAdministrator governs approved deployment and release operations.

It may authorize or operate approved deployment mechanisms.

It must remain distinct from:

- Source-code identity
- Human production administration
- Workload runtime identity
- Organization administration

A DeploymentAdministrator must not automatically receive unrestricted
production-console administration.

Deployment execution should use approved deployment roles rather than broad
human AWS permissions.

---

# ProductionAdministrator

ProductionAdministrator governs explicitly authorized production
administration.

ProductionAdministrator must:

- Be separately assigned
- Be auditable
- Be environment scoped
- Use strong workforce authentication
- Use temporary sessions
- Follow privileged-access controls where required

Development, testing, staging, or sandbox access must not imply
ProductionAdministrator access.

General engineering membership must not automatically grant this role.

---

# NetworkAdministrator

NetworkAdministrator governs approved AWS network infrastructure.

Potential scope includes:

- VPC configuration
- Route tables
- Subnets
- Network security controls
- VPC endpoints
- Approved connectivity
- DNS/network infrastructure where assigned

NetworkAdministrator must not automatically receive:

- Application-data access
- Production database administration
- Organization administration
- IAM administration

---

# DataInfrastructureAdministrator

DataInfrastructureAdministrator governs approved infrastructure-level data
services.

Potential responsibility includes:

- RDS infrastructure administration
- Backup infrastructure
- Storage infrastructure
- Database-service configuration
- Approved recovery operations

This role does not automatically authorize unrestricted access to application or
customer data.

Infrastructure administration and data-content access must remain separate where
technically possible.

---

# ReadOnlyOperator

ReadOnlyOperator provides approved observation access without mutation authority.

It may support:

- Infrastructure inspection
- Troubleshooting
- Health review
- Configuration review
- Capacity review

It must not silently receive mutation permissions.

Read-only access remains:

- Authenticated
- Authorized
- Logged
- Account scoped
- Environment scoped

---

# Auditor

Auditor provides access to approved governance, security, compliance, and audit
evidence.

Auditor should normally be non-mutating.

Potential scope includes:

- CloudTrail review
- Security findings
- Configuration evidence
- Access-review evidence
- Infrastructure inventory
- Compliance evidence

Auditor must not silently become SecurityAdministrator or
ProductionAdministrator.

---

# EmergencyAdministrator

EmergencyAdministrator is not a routine permission set.

EmergencyAdministrator exists only for approved break-glass or recovery
circumstances.

It must be:

- Separately controlled
- Strongly authenticated
- Narrowly activated
- Time limited
- Monitored
- Audited
- Reviewed after use

Detailed emergency architecture is governed by Phase 4.1.9.

---

# Human Permission-Set Assignment Model

Human access shall use:

Human workforce identity
→ IAM Identity Center
→ Approved permission set
→ Approved AWS account
→ Temporary role session

A permission-set assignment must identify:

- Workforce principal
- Permission set
- AWS account
- Environment
- Business or technical justification
- Approval authority
- Effective date
- Expiration or review requirement where applicable

---

# No Universal Human Administrator

LinkCraftor must not rely on a single universal human administrator permission
set for all AWS administration.

Universal AWS AdministratorAccess must not become the standard operating model.

Where broad emergency authority exists, it belongs to the separately controlled
EmergencyAdministrator path.

---

# Deployment and Automation Roles

Deployment and automation must use dedicated machine roles.

Canonical classes include:

- TerraformPlanRole
- TerraformApplyRole
- CICDDeploymentRole
- SecurityAutomationRole

These roles are non-human operational identities unless explicitly documented
otherwise.

They must not use customer credentials or human interactive sessions as their
production identity.

---

# TerraformPlanRole

TerraformPlanRole shall support approved read/plan operations necessary to
produce infrastructure change plans.

It should normally have less authority than TerraformApplyRole.

Planning authority must not silently imply deployment authority.

---

# TerraformApplyRole

TerraformApplyRole shall execute approved infrastructure changes.

It must be:

- Restricted to approved deployment workflows
- Account scoped
- Environment scoped
- Auditable
- Temporarily assumed
- Protected from unauthorized interactive use

Production TerraformApplyRole access must receive stronger control than
non-production apply access.

---

# CICDDeploymentRole

CICDDeploymentRole shall represent approved CI/CD deployment automation.

It must use approved workload federation or temporary credentials.

It must not require permanent human AWS access keys.

Repository membership alone must not authorize assumption of the deployment
role.

The deployment trust relationship must identify the approved CI/CD source and
conditions.

---

# SecurityAutomationRole

SecurityAutomationRole may perform approved security-response or
security-management automation.

It must be limited to specifically approved security actions.

Security automation must not silently become a general infrastructure
administrator.

---

# Workload and Service Roles

Application and infrastructure workloads shall use dedicated service or workload
roles.

Examples include:

- Backend API role
- Universal Runtime role
- Worker role
- Queue producer role
- Queue consumer role
- Storage-access role
- Database-access role
- Notification role
- Backup role
- Monitoring role

The exact set is created only when required by the owning infrastructure phase.

Workload roles must follow Phase 4.1.5 Workload Identity.

---

# Role-per-Service Principle

A single shared workload role should not be reused across unrelated services when
separate roles materially improve security isolation.

Roles should align with:

- Service responsibility
- Environment
- Account
- Required AWS actions
- Required resource scope
- Trust principal

Broad shared application roles are prohibited where a narrower role can
reasonably be used.

---

# Trust Policy Architecture

Every assumable IAM role must have an explicit trust relationship.

Trust policies must identify the approved principal class.

Trust must not be granted merely because a principal exists inside the same AWS
organization.

A trust policy must avoid uncontrolled wildcard principals.

Trust relationships should use approved conditions where appropriate.

Potential trust constraints include:

- AWS account
- AWS organization
- Identity Center assignment
- OIDC issuer
- Repository
- Branch/environment
- Service principal
- Source ARN
- Source account
- Session conditions

Detailed implementation belongs to Phase 3 and later service phases.

---

# Role Assumption

AWS role assumption must be explicit and auditable.

A role may be assumed only by a principal authorized by its trust policy and
corresponding access architecture.

Role chaining must not be used to bypass environment, account, or privilege
boundaries.

A lower-privilege role must not silently self-escalate into a higher-privilege
role.

---

# Cross-Account Role Architecture

Cross-account access must be explicitly designed.

Cross-account access must identify:

- Source principal
- Source account
- Destination account
- Destination role
- Purpose
- Environment
- Trust conditions
- Required permissions
- Audit requirements

Uncontrolled cross-account trust is prohibited.

Production cross-account roles must receive stricter controls than ordinary
non-production access.

---

# Account Assignment

Human permission sets shall be assigned independently per AWS account.

Possession of a permission set in one account does not automatically grant the
same permission set in another account.

For example:

Development CloudPlatformAdministrator

does not imply:

Production CloudPlatformAdministrator.

Account assignments remain independently governable.

---

# Environment Boundary

Role architecture must preserve:

- Development isolation
- Testing isolation
- Staging isolation
- Sandbox isolation
- Shared-services isolation
- Security isolation
- Production isolation

Role names, assignments, policies, trust relationships, and session controls must
not erase these environment boundaries.

Detailed cross-environment restrictions are governed by Phase 4.1.8.

---

# Production Role Boundary

Production-capable roles must be separately identifiable.

Production access must be explicitly granted.

Production roles must not be inferred from:

- Employment
- Engineering team membership
- Repository access
- Development AWS access
- Testing AWS access
- Staging AWS access
- Application administrator role
- Workspace ownership

---

# Separation of Duties

Role design must preserve separation of duties.

Potential conflicting authority combinations must be reviewed.

Examples include:

- IAM administration + privileged-access approval
- Security administration + audit deletion
- Deployment approval + unrestricted production modification
- Production administration + independent audit review
- Backup administration + unrestricted backup deletion
- Emergency-access activation + sole post-event review

The exact conflict matrix may be refined during 4.1.7 and later governance
phases.

---

# Permissions Boundaries

IAM permissions boundaries may be used where appropriate to limit the maximum
permissions of delegated IAM roles or automation.

Permissions boundaries do not replace:

- Identity-based policies
- Resource-based policies
- Service Control Policies
- Trust policies
- Least-privilege review

Their use must be intentional and documented.

---

# Service Control Policy Boundary

AWS Organizations Service Control Policies define organization/account-level
maximum permission boundaries.

SCPs do not grant permissions.

A role must still receive explicit IAM permissions.

A permissive IAM policy cannot override an SCP deny.

SCP architecture belongs primarily to cloud organization/governance
implementation, but IAM role design must respect it.

---

# AdministratorAccess Boundary

AWS managed policy AdministratorAccess must not be the default policy for human
or workload roles.

Its use, if ever required, must be:

- Explicitly justified
- Narrowly assigned
- Reviewed
- Time constrained where possible
- Audited
- Subject to privileged-access governance

Emergency broad authority belongs to the controlled emergency path, not routine
administration.

---

# Permission-Set Naming

Human permission-set names must identify the responsibility class clearly.

Recommended canonical logical names:

- LinkCraftor-OrganizationAdministrator
- LinkCraftor-CloudPlatformAdministrator
- LinkCraftor-SecurityAdministrator
- LinkCraftor-DeploymentAdministrator
- LinkCraftor-ProductionAdministrator
- LinkCraftor-NetworkAdministrator
- LinkCraftor-DataInfrastructureAdministrator
- LinkCraftor-ReadOnlyOperator
- LinkCraftor-Auditor
- LinkCraftor-EmergencyAdministrator

Physical naming must remain compatible with Cloud Naming Standards.

---

# IAM Role Naming

IAM role naming must follow Cloud Naming Standards.

Role names must identify, where applicable:

- Project
- Environment
- Platform domain
- Service
- Role purpose

Naming does not replace policy, trust, least-privilege, or session review.

---

# Role Lifecycle

Every IAM role or permission set must have an accountable lifecycle.

Lifecycle stages may include:

- Proposed
- Approved
- Provisioned
- Active
- Restricted
- Deprecated
- Retired

Unused or unjustified roles must not remain indefinitely active.

---

# Access Review

Human permission-set assignments and privileged roles must be reviewable.

Review should determine:

- Is the principal still authorized?
- Is the role still required?
- Is the account assignment still required?
- Is production access still justified?
- Is the privilege level still appropriate?
- Are conflicting roles present?
- Has the role been used?

Later governance phases may automate access-review evidence.

---

# Deprovisioning

When authorization ends:

- Human permission-set assignment must be removed
- Role assumption must cease
- Temporary sessions should be invalidated where supported
- Related access evidence must be preserved

Deprovisioning one role must not require deletion of unrelated identities.

---

# Auditability

Role activity must be attributable through approved AWS audit mechanisms.

Audit evidence should identify:

- Principal
- Permission set or role
- AWS account
- Session
- Assumed role
- API action
- Resource
- Timestamp
- Result

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Source-Control Boundary

GitHub identity is not AWS IAM role authority.

Repository permission does not itself authorize:

- Production AWS administration
- IAM administration
- Terraform apply
- Security administration

CI/CD access must be mapped through approved deployment identity and trust
contracts.

---

# Universal Runtime Boundary

Universal Runtime identities must use workload/service roles.

Universal Runtime workers must not assume human workforce permission sets.

Human administrators must not become the runtime identity of workers.

Existing Universal Runtime worker and queue identity architecture must be reused.

---

# Runtime Eligibility

This architecture document is not executable infrastructure.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future IAM compliance, access-review, trust-policy, role-lifecycle, or
permission-set validation jobs may require Universal Runtime Registration
Standard assessment.

---

# Phase Dependencies

4.1.2 defines the canonical IAM role and permission-set architecture.

Phase 4.1.3 defines detailed least-privilege permission policy.

Phase 4.1.4 defines service identities.

Phase 4.1.5 defines workload identities.

Phase 4.1.6 defines temporary credential architecture.

Phase 4.1.7 defines privileged-access controls.

Phase 4.1.8 defines detailed cross-environment restrictions.

Phase 4.1.9 defines emergency-access architecture.

Phase 2 must provide the implemented AWS account/environment boundaries.

Phase 3 must provide Terraform/IaC implementation.

Final Phase 4 certification remains deferred until those implementation
dependencies are available.

---

# Prohibited Practices

The following are prohibited:

- One universal routine human administrator role
- Shared human administrator accounts
- Customer identity used as AWS role authority
- Workload roles used as human console identities
- Human identities used as production workload roles
- Development access automatically granting production access
- Repository access automatically granting AWS administration
- Uncontrolled wildcard trust
- Uncontrolled cross-account role assumption
- Permanent human access keys as the standard access model
- Role chaining used to bypass privilege boundaries
- Routine AdministratorAccess as the default AWS role policy
- Emergency administrator authority used for routine operations
- Workload roles shared broadly across unrelated services without justification
- IAM roles that cannot be attributed to an owning responsibility

---

# Canonical Decision Summary

LinkCraftor shall use explicit AWS IAM role and IAM Identity Center permission-set
architecture.

Human workforce access shall use responsibility-specific permission sets.

Deployment, automation, and workloads shall use separate machine identities and
IAM roles.

Permission-set assignment shall be account specific.

Production access shall be independently assigned.

Cross-account trust shall be explicit.

Trust policies shall be narrowly controlled.

Broad universal AdministratorAccess shall not be the routine operating model.

Detailed permissions remain governed by the 4.1.3 Least-Privilege Model.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
