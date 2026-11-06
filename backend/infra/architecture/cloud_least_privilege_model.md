# LinkCraftor Cloud Least-Privilege Model

Version: 1.0
Status: Canonical
Phase: Cloud Identity & Access Infrastructure
Section: 4.1.3 Least-Privilege Model
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS-specific least-privilege model for
LinkCraftor.

It translates the already-approved LinkCraftor Least-Privilege Principles into
AWS IAM permission design.

This document governs:

- Human workforce permission sets
- IAM roles
- Deployment roles
- Automation roles
- Service roles
- Workload roles
- Cross-account permissions
- Resource-based permissions
- Permissions boundaries
- Service Control Policy interaction
- Permission review and reduction

This document does not replace the canonical security-wide Least-Privilege
Principles.

It specializes those principles for AWS implementation.

---

# Architectural Authorities

This architecture consumes and preserves:

- 4.1.1 Cloud Administrator Identity
- 4.1.2 IAM Role Architecture
- Cloud Resource Organization
- Cloud Naming Standards
- Infrastructure Configuration Standards
- Least-Privilege Principles
- Separation-of-Duties Principles
- Identity / Access / Account Security Architecture

Where this document is more specific about AWS IAM permission construction, it
governs that AWS-specific scope.

---

# Core Least-Privilege Rule

Every AWS permission grant must be no broader than required for the approved
principal, action, resource, account, environment, region, and operational
purpose.

Permission design must answer:

1. Who is the principal?
2. What AWS action is required?
3. Which resource is required?
4. Which account is required?
5. Which environment is required?
6. Which region is required?
7. Under which conditions is access valid?
8. For how long is access required?
9. How is the permission reviewed?
10. How is excessive permission removed?

---

# Default-Deny Model

AWS access must operate from a default-deny posture.

No principal receives AWS permission unless an approved policy path grants it.

Absence of an explicit grant means access is denied.

Where risk requires stronger protection, explicit deny controls may be used.

---

# Action Scope

IAM policies must grant only the AWS actions required for the approved
responsibility.

Broad action families such as:

- `service:*`
- `*`

must not be used routinely when specific actions can reasonably be identified.

Read-only tasks should receive read/list/describe actions rather than mutation
actions.

Mutation authority must be granted only when required.

Administrative actions must be separately justified.

---

# Resource Scope

Permissions must be restricted to specific resources wherever the AWS service
supports resource-level permissions.

Resource scope may include:

- Exact ARN
- Resource family
- Environment-specific resource
- Service-specific resource
- Account-specific resource
- Region-specific resource
- Approved tagged resource set

Wildcard resource scope must not be used where narrower resource scope is
reasonably supported.

---

# Wildcard Permission Policy

Wildcard permissions require explicit justification.

The following are high-risk:

- `Action: "*"`
- `Resource: "*"`
- Broad `service:*`
- Wildcard principals
- Wildcard cross-account trust

Wildcard use is permitted only when:

- AWS technically requires it, or
- The required operation cannot be reasonably expressed more narrowly

and the risk is reduced through other controls such as:

- Conditions
- SCPs
- Permissions boundaries
- Account isolation
- Session restrictions
- Explicit denies
- Monitoring
- Short-lived access

Routine use of wildcard privileges is prohibited.

---

# Condition Scope

IAM conditions must be used where they materially reduce permission scope.

Potential condition dimensions include:

- Principal identity
- Principal ARN
- Principal tag
- Resource tag
- Request tag
- AWS account
- AWS organization
- Region
- Source ARN
- Source account
- Service
- OIDC issuer
- Repository
- Branch
- Environment
- Session context
- MFA presence where applicable

Condition keys must be validated against the AWS service and action being
authorized.

---

# Tag-Based Authorization

Tag-based authorization may be used where appropriate.

Tags used for authorization must come from trusted infrastructure governance.

Potential authorization tags include:

- Project
- Environment
- PlatformDomain
- Service
- Criticality
- RegionRole
- Owner

A principal must not be able to grant itself broader access merely by modifying
authorization-relevant tags.

Tag mutation and tag-based authorization must therefore be governed together.

---

# Account Scope

Permissions must be scoped to approved AWS accounts.

A principal authorized in one AWS account is not automatically authorized in
another.

Account-specific assignments must preserve:

- Management isolation
- Security isolation
- Log Archive isolation
- Network isolation
- Shared Services isolation
- Deployment isolation
- Development isolation
- Testing isolation
- Staging isolation
- Production isolation
- Sandbox isolation

---

# Environment Scope

Environment least privilege is mandatory.

Development access must not imply testing, staging, or production access.

Testing access must not imply staging or production access.

Staging access must not imply production access.

Production access must be independently assigned and justified.

Environment scope must be reflected through:

- Account assignment
- IAM role
- Permission set
- Policy resources
- Trust relationship
- Session controls
- Tags where used

---

# Region Scope

Permissions should be region constrained where the AWS service and operation
permit meaningful region restriction.

The canonical regional model is:

- eu-west-1 — primary
- us-east-1 — disaster-recovery
- af-south-1 — future

Access to the disaster-recovery region does not automatically imply normal
production-operation authority there.

Future-region authorization must not be granted merely because the region exists
in architecture.

Global AWS services are governed separately where region conditions do not
apply.

---

# Human Workforce Permission Ceilings

Each human permission set must have a defined maximum authority boundary.

Human permission sets must not rely on unrestricted AdministratorAccess as the
routine model.

The permission ceiling for each responsibility class must reflect its purpose.

Examples:

- ReadOnlyOperator — observation only
- Auditor — audit/compliance evidence only
- NetworkAdministrator — network administration only
- SecurityAdministrator — security administration only
- ProductionAdministrator — approved production operations only
- OrganizationAdministrator — organization governance only

A role name does not itself grant authority.

The attached IAM policies define actual permission.

---

# ReadOnlyOperator Least Privilege

ReadOnlyOperator must not receive mutation authority except where a narrowly
approved diagnostic action genuinely requires it.

Read-only access should prefer:

- Get
- List
- Describe
- View

operations.

Sensitive secret values, credentials, private keys, or customer data must not
be exposed simply because a user has read-only infrastructure access.

---

# Auditor Least Privilege

Auditor should receive only the evidence required for approved audit,
compliance, security, or governance review.

Auditor should normally be non-mutating.

Auditor must not automatically receive:

- IAM mutation
- Infrastructure mutation
- Production deployment
- Secret-value access
- Key administration
- Data modification

---

# SecurityAdministrator Least Privilege

SecurityAdministrator permissions must be restricted to approved security
functions.

Security administration must not automatically include:

- General production modification
- Unrestricted customer-data access
- Deployment authority
- Organization administration
- Audit-log deletion

Security evidence must remain protected from unilateral deletion.

---

# ProductionAdministrator Least Privilege

ProductionAdministrator must receive only the production permissions required
for approved production operations.

Production administration must not imply:

- Organization administration
- Security administration
- unrestricted IAM administration
- unrestricted database content access
- unrestricted backup deletion
- emergency authority

Production access must remain individually attributable and auditable.

---

# Deployment Least Privilege

Deployment roles must receive only the permissions necessary to deploy approved
resources.

Planning and apply authority must remain distinct where practical.

TerraformPlanRole should primarily receive permissions necessary for:

- State/read operations
- Resource inspection
- Plan generation

TerraformApplyRole may receive mutation permissions required by approved
infrastructure changes.

CI/CD deployment roles must not become general-purpose administrator roles.

---

# Service and Workload Least Privilege

Each service or workload identity must receive only the AWS permissions required
for its operational responsibility.

A backend API role must not automatically receive worker permissions.

A worker role must not automatically receive deployment permissions.

A queue consumer role must not automatically receive queue-administration
permissions.

A storage reader must not automatically receive storage deletion authority.

A database client must not automatically receive database-administration
authority.

---

# Universal Runtime Least Privilege

Universal Runtime identities must remain narrowly scoped.

Runtime jobs, workers, coordinators, queues, and handlers must use their
existing canonical identity architecture.

AWS permissions must be granted only as required by their runtime function.

Universal Runtime identities must not receive human workforce permission sets.

Cloud IAM must not duplicate or replace existing Universal Runtime authorization
contracts.

---

# Queue and Worker Least Privilege

Queue producers and queue consumers should have distinct permissions where
appropriate.

Typical separation includes:

Producer:
- Send messages

Consumer:
- Receive messages
- Delete successfully processed messages
- Extend visibility where required

Queue administration must remain separate from routine producer/consumer
permissions.

Worker permissions must be specific to the resources required by that worker.

---

# Storage Least Privilege

Storage permissions must distinguish:

- Read
- Write
- Delete
- List
- Administration
- Lifecycle management
- Replication
- Backup/recovery

A workload that needs object reads must not automatically receive object deletion
or bucket administration.

Sensitive storage resources require narrower scopes and stronger controls.

---

# Database Least Privilege

AWS infrastructure permissions for database services must remain distinct from
database-engine authorization.

Permission to administer an RDS instance does not automatically authorize
application-level database access.

Database identities and grants must be governed by the owning database and data
architecture.

---

# Secrets Least Privilege

Access to Secrets Manager, Parameter Store secure values, and key material must
be narrowly scoped.

A workload must receive access only to secrets it actually requires.

Human infrastructure access must not automatically grant secret-value access.

Secret metadata access and secret-value access may be separated where useful.

---

# KMS Least Privilege

KMS permissions must distinguish:

- Key administration
- Key usage
- Encryption
- Decryption
- Grant management
- Policy management

Key administrators must not automatically receive permission to decrypt all data
protected by the key.

Workload key-use permissions must be constrained to approved keys and purposes.

---

# Network Least Privilege

Network administration must be limited to approved network resources and actions.

Application workloads must not receive network-control-plane permissions unless
required.

Security group use and security group administration should remain distinct
where practical.

---

# Backup and Recovery Least Privilege

Backup administration must be separated from routine workload permissions.

Recovery authority must not become unrestricted production administration.

Backup deletion requires stronger protection where the backup architecture
requires retention or immutability.

Recovery roles must be activated only for approved recovery purposes.

---

# Cross-Account Least Privilege

Cross-account access must grant the minimum required actions and destination
resources.

Both sides of the relationship matter:

- Source principal permission
- Destination trust policy

Cross-account trust must not rely on broad wildcard principals.

Production cross-account permissions require stronger review.

---

# Resource-Based Policy Least Privilege

Resource-based policies must follow the same least-privilege principles as
identity-based policies.

Examples include:

- S3 bucket policies
- KMS key policies
- SQS queue policies
- SNS topic policies
- Secrets Manager resource policies
- Lambda resource policies

Resource policies must not create access paths that bypass intended IAM role
restrictions.

---

# IAM Permissions Boundaries

Permissions boundaries may define the maximum authority available to delegated
roles.

A permissions boundary does not grant access.

The effective permission remains constrained by the intersection of applicable
permission layers.

Permissions boundaries are appropriate where delegation must occur without
allowing unrestricted privilege escalation.

---

# Service Control Policies

SCPs define the maximum permissions available inside affected AWS accounts or
organizational units.

SCPs do not grant permission.

IAM policies must remain least privilege even when an SCP already limits the
account.

Least privilege must not rely solely on organization-level denial.

---

# Explicit Deny Strategy

Explicit denies may be used for high-risk controls where deny semantics are
appropriate.

Potential examples include:

- Blocking unauthorized regions
- Blocking root-like destructive actions
- Protecting audit logs
- Preventing disabling security controls
- Preventing unapproved public exposure
- Blocking cross-environment access
- Protecting backup retention

Explicit deny design must account for operational recovery needs and must be
tested before production enforcement.

---

# Privilege Escalation Prevention

No role may grant itself broader permissions unless that behavior is explicitly
approved for the role's governance responsibility.

High-risk escalation paths include:

- `iam:PassRole`
- IAM policy attachment
- IAM policy creation
- Role trust modification
- Permission-set modification
- KMS policy modification
- Lambda or compute modification that can assume a stronger role
- CloudFormation or Terraform execution with broader authority

Permissions capable of indirect privilege escalation require special review.

---

# PassRole Controls

`iam:PassRole` must be narrowly scoped.

A principal may pass only approved roles to approved AWS services.

Wildcard `iam:PassRole` over all roles is prohibited except under separately
approved exceptional circumstances.

PassRole permissions must be reviewed together with the service permissions that
can consume the passed role.

---

# Managed Policy Use

AWS managed policies may be used only after review.

A managed policy must not be considered safe merely because AWS publishes it.

Broad managed policies such as AdministratorAccess or PowerUserAccess must not
be the default.

Customer-managed policies should be used when narrower scope or clearer control
is required.

---

# Inline vs Managed Policies

Policy form must be chosen intentionally.

Reusable managed policies may be appropriate for shared, well-defined
permission sets.

Inline policies may be appropriate when the permission belongs exclusively to
one role and reuse is not intended.

Policy reuse must not create unnecessary coupling between unrelated roles.

---

# Policy Composition

Effective AWS permission may result from multiple policy layers, including:

- Identity-based policies
- Resource-based policies
- Permissions boundaries
- Service Control Policies
- Session policies
- KMS key policies
- VPC endpoint policies where applicable

Least-privilege review must evaluate the effective permission, not only a single
policy document in isolation.

---

# Access Analyzer

AWS IAM Access Analyzer is an approved supporting control.

It may be used to identify:

- External access
- Cross-account access
- Public access paths
- Unused access
- Policy findings
- Potentially excessive permissions

Access Analyzer findings must inform review but do not independently replace
architecture or security approval.

---

# Unused Permission Reduction

Unused permissions should be removed when evidence shows they are no longer
required.

Permission reduction must consider:

- Observed use
- Expected but infrequent operations
- Recovery requirements
- Deployment requirements
- Seasonal or scheduled operations
- Emergency requirements

Absence of recent use alone must not automatically remove a permission required
for legitimate rare events without review.

---

# Access Review

Least-privilege review must occur for:

- New permission sets
- New roles
- Material policy changes
- Production roles
- Privileged roles
- Cross-account access
- Emergency access
- High-risk service permissions

Review should confirm:

- Required actions
- Required resources
- Required conditions
- Required account
- Required environment
- Required region
- Escalation risk
- Data sensitivity
- Auditability

---

# Permission Reduction Lifecycle

Permission lifecycle follows:

Requested
→ Reviewed
→ Approved
→ Provisioned
→ Observed
→ Reassessed
→ Reduced / Retained / Removed

Permissions must not become permanent merely because they were once approved.

---

# Exceptions

Least-privilege exceptions must be formally controlled.

An exception must document:

- Reason
- Principal
- Permission
- Resource
- Account
- Environment
- Risk
- Compensating controls
- Approver
- Expiration or review date

Exceptions must not silently become the permanent baseline.

---

# Evidence

Least-privilege evidence should include, where applicable:

- IAM policy version
- Role or permission-set identity
- Account assignment
- Trust policy
- Permissions boundary
- SCP context
- Access Analyzer findings
- CloudTrail evidence
- Access-review decision
- Exception record

---

# Terraform and IaC Boundary

IAM policy implementation shall ultimately be represented through approved
Terraform/IaC where applicable.

Manual console policy changes must not become the authoritative infrastructure
state.

Phase 3 owns the Terraform implementation foundation.

This architecture defines the policy rules that Phase 3 must later encode.

---

# Universal Runtime Boundary

Future automated IAM-policy validation, access review, privilege-escalation
detection, or least-privilege certification may become executable operational
work.

Those jobs must be assessed under the Universal Runtime Registration Standard.

This architecture document itself is not runtime eligible.

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Phase Dependencies

4.1.3 defines the AWS-specific least-privilege permission model.

4.1.4 defines service identities.

4.1.5 defines workload identities.

4.1.6 defines temporary credential architecture.

4.1.7 defines privileged-access controls.

4.1.8 defines cross-environment restrictions.

4.1.9 defines emergency cloud access.

Phase 2 must provide the real AWS account and environment boundaries.

Phase 3 must implement these controls through Terraform/IaC.

Final Phase 4 certification remains deferred until the required implementation
dependencies exist.

---

# Prohibited Practices

The following are prohibited:

- Routine `Action: "*"`
- Routine `Resource: "*"` where narrower scope is supported
- Uncontrolled wildcard principals
- Routine AdministratorAccess
- Routine PowerUserAccess without review
- Development access automatically granting production access
- Human administrator permissions reused as workload permissions
- Workload permissions reused as human administrator permissions
- Unrestricted `iam:PassRole`
- Unreviewed privilege-escalation permissions
- Cross-account trust without explicit scope
- IAM policies used to bypass SCP or security boundaries
- Secret access granted merely because infrastructure access exists
- KMS key administration automatically granting decrypt access
- Read-only roles receiving silent mutation authority
- Permissions retained indefinitely without review
- Manual console policy state becoming authoritative infrastructure state

---

# Canonical Decision Summary

LinkCraftor AWS permissions shall follow explicit least privilege across actions,
resources, conditions, accounts, environments, regions, and principal classes.

Security-wide Least-Privilege Principles remain authoritative.

This architecture specializes those principles for AWS IAM.

Human, deployment, automation, service, and workload permissions remain
separately scoped.

Wildcard permissions, AdministratorAccess, PowerUserAccess, iam:PassRole,
cross-account trust, resource-based policies, and privilege-escalation paths
require explicit control.

Effective permission must be evaluated across all applicable AWS policy layers.

Permissions must be reviewable and reducible over time.

Phase 3 will later encode this model through Terraform/IaC.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
