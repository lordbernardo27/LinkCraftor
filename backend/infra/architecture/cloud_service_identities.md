# LinkCraftor Cloud Service Identities

Version: 1.0
Status: Canonical
Phase: Cloud Identity & Access Infrastructure
Section: 4.1.4 Service Identities
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical non-human service-identity architecture for
LinkCraftor AWS infrastructure.

It establishes:

- What constitutes a service identity
- Service-identity ownership
- Separation from human and customer identity
- Relationship to AWS IAM roles
- Service-to-service trust
- Deployment and automation identities
- Runtime and worker identity boundaries
- Queue producer and consumer identities
- Credential and trust requirements
- Provisioning and deprovisioning
- Audit attribution
- Relationship to workload identity

This document defines the identity authority for non-human services.

Detailed workload credential acquisition and execution-environment identity are
governed by Phase 4.1.5 Workload Identity.

---

# Architectural Authorities

This architecture consumes and preserves:

- 4.1.1 Cloud Administrator Identity
- 4.1.2 IAM Role Architecture
- 4.1.3 Least-Privilege Model
- Identity / Access / Account Security Architecture
- Least-Privilege Principles
- Universal Runtime identity architecture
- Existing worker and queue identity architecture

This document must reuse existing identity authorities rather than create
parallel machine-identity systems.

---

# Canonical Definition

A service identity is a non-human principal representing a specific approved
software service, automation function, infrastructure component, runtime
component, or machine-operated responsibility.

Examples may include:

- Backend API
- Universal Runtime
- Runtime coordinator
- Worker
- Queue producer
- Queue consumer
- Scheduler
- Deployment automation
- Terraform execution
- Security automation
- Backup automation
- Notification service
- Monitoring service

A service identity represents the service responsibility.

It does not represent a customer.

It does not represent a human administrator.

---

# Principal Separation

LinkCraftor maintains separate principal classes:

1. Customer and product identities
2. Human workforce identities
3. Service identities
4. Workload execution identities

These classes may interact through approved trust contracts but must not be
collapsed into one universal identity.

---

# Customer Identity Boundary

Customer identity must remain separate from service identity.

A customer token, session, password, MFA credential, passkey, or recovery
credential must never become an AWS service identity.

A service identity must not be treated as a customer.

A customer must not receive the service identity's AWS credentials.

Customer authorization and AWS service authorization remain separate decisions.

---

# Human Identity Boundary

Human administrators and service identities must remain separately governed.

A human administrator credential must not become the production identity of:

- Backend services
- Workers
- Runtime jobs
- Queue consumers
- Queue producers
- Deployment automation
- Scheduled tasks

A service identity must not provide interactive human AWS Console access.

---

# Service Identity vs Workload Identity

Service identity defines the logical non-human principal.

Workload identity defines how an executing workload obtains and proves that
identity in its execution environment.

For example:

Backend API
→ logical service identity
→ approved workload identity mechanism
→ AWS IAM role
→ temporary AWS credentials

Phase 4.1.4 owns the logical service-identity model.

Phase 4.1.5 owns workload identity mechanisms and execution trust.

---

# Dedicated Identity Principle

Independent services should use dedicated identities where separate identity
materially improves isolation, attribution, or least privilege.

Unrelated services must not share a broad service identity merely for
convenience.

A dedicated identity should normally exist when services differ in:

- Responsibility
- AWS permissions
- Data access
- Queue access
- Environment
- Trust source
- Security sensitivity
- Operational ownership

---

# Canonical Service Identity Classes

Canonical service-identity classes include:

- BackendServiceIdentity
- UniversalRuntimeIdentity
- RuntimeCoordinatorIdentity
- WorkerIdentity
- QueueProducerIdentity
- QueueConsumerIdentity
- SchedulerIdentity
- DeploymentAutomationIdentity
- TerraformPlanIdentity
- TerraformApplyIdentity
- SecurityAutomationIdentity
- BackupAutomationIdentity
- NotificationServiceIdentity
- MonitoringServiceIdentity

The existence of a class does not require immediate provisioning.

Actual identities are created only when required by the owning service or
infrastructure phase.

---

# Backend Service Identity

Backend services must authenticate to AWS resources through their approved
service/workload identity.

Backend services must not:

- Use customer credentials as AWS credentials
- Use human administrator credentials
- Share unrestricted infrastructure credentials
- Receive unrelated worker or deployment permissions

Backend AWS access must follow the 4.1.3 Least-Privilege Model.

---

# Universal Runtime Identity

Universal Runtime maintains its existing canonical identity authority.

Cloud IAM must integrate with that authority rather than replace it.

Universal Runtime service identity must remain distinct from:

- Human administrators
- Customer identities
- CI/CD deployment identity
- Generic backend identity

Runtime jobs and handlers must receive only the AWS permissions required for
their approved runtime responsibilities.

---

# Runtime Coordinator Identity

The runtime coordinator must have an independently identifiable service identity
where its responsibility differs from workers or handlers.

Coordinator permissions must not automatically include every worker permission.

Coordinator authority must remain bounded to its approved orchestration and
coordination responsibility.

---

# Worker Identity

Workers must use non-human service/workload identities.

A worker must not execute under:

- Human administrator credentials
- Customer credentials
- Shared unrestricted AWS credentials
- Deployment administrator identity

Worker AWS access must be scoped to the resources required by that worker.

Existing worker identity architecture remains authoritative and must be reused.

---

# Queue Producer Identity

A queue producer identity should receive only permissions required to publish to
approved queues or messaging destinations.

Producer identity must not automatically receive:

- Queue consumption
- Queue deletion
- Queue administration
- Worker administration

---

# Queue Consumer Identity

A queue consumer identity should receive only permissions required for approved
consumption behavior.

Typical permissions may include:

- Receive approved messages
- Delete successfully processed messages
- Extend visibility where required

Queue consumer identity must not automatically receive queue-administration
authority.

---

# Scheduler Identity

Schedulers must use dedicated service identity where they invoke workloads,
jobs, events, or automation.

Scheduler permissions must be limited to approved scheduling and invocation
responsibilities.

A scheduler must not become a general-purpose infrastructure administrator.

---

# Deployment Automation Identity

Deployment automation must use a dedicated machine identity.

Deployment identity must remain separate from:

- Human deployment administrators
- Human production administrators
- Runtime identities
- Customer identities

GitHub or another source-control identity may establish federation into an
approved deployment identity, but repository access alone must not constitute
AWS deployment authority.

---

# Terraform Plan Identity

Terraform planning must use an approved service/deployment identity.

TerraformPlanIdentity should receive only the permissions necessary for approved
plan, state-read, and infrastructure-inspection operations.

Planning authority must not silently grant apply authority.

---

# Terraform Apply Identity

Terraform apply operations must use a separately governed service/deployment
identity.

TerraformApplyIdentity may receive approved mutation permissions necessary for
infrastructure changes.

Production apply identity requires stronger control than non-production apply
identity.

---

# Security Automation Identity

Security automation must use a dedicated service identity.

Its permissions must be limited to specifically approved:

- Security inspection
- Security response
- Security configuration
- Finding processing
- Remediation operations

Security automation identity must not become general cloud administrator
identity.

---

# Backup Automation Identity

Backup and recovery automation must use service identity separate from ordinary
application workloads where appropriate.

Backup identity may require:

- Backup creation
- Snapshot operations
- Retention operations
- Replication operations
- Recovery operations

Backup identity must not automatically gain unrestricted production application
authority.

---

# Notification Service Identity

Notification services must use only the permissions required for approved
notification channels and destinations.

Notification identity must not receive unrelated infrastructure or customer-data
authority.

---

# Monitoring Service Identity

Monitoring and observability services must use dedicated service identities where
required.

Monitoring identity should normally prefer read and telemetry permissions over
mutation authority.

Security-sensitive monitoring actions require explicit authorization.

---

# AWS IAM Relationship

AWS IAM remains authoritative for AWS permissions assigned to service identities.

A service identity may be represented through an approved IAM role or other
approved AWS-native identity mechanism.

Service identity does not itself imply permission.

Permissions are granted through the approved IAM role/policy architecture.

---

# Trust Establishment

Every service identity must have an explicit trust basis.

Trust may be established through approved mechanisms such as:

- AWS service principal
- AWS workload role
- AWS STS role assumption
- OIDC federation
- Approved CI/CD federation
- Runtime workload identity
- Account-specific trust
- Resource-specific trust

Trust must not rely merely on network location or the claim that a caller is
internal.

---

# Trust Policy Requirements

Trust policies must identify the approved principal or trust source.

Uncontrolled wildcard principals are prohibited.

Trust policy conditions should be used where appropriate to constrain:

- Account
- Organization
- Service
- Source ARN
- Source account
- OIDC issuer
- Repository
- Branch
- Environment
- Session context

---

# Service-to-Service Authentication

Service-to-service communication must authenticate the calling service where the
target operation requires authenticated identity.

Internal network location does not independently prove service identity.

Service-to-service authorization must evaluate the approved identity and
required operation.

One service must not trust another solely because both are LinkCraftor services.

---

# Service Authorization Boundary

Service identity answers:

"Which trusted machine/service is acting?"

Application authorization separately answers:

"Is this service permitted to perform this application operation?"

AWS IAM authorization answers:

"May this AWS principal access this AWS resource?"

Those authorities must remain distinguishable.

---

# Temporary Credential Requirement

Service identities should use short-lived or automatically managed credentials
where the AWS execution model supports them.

Long-lived static AWS credentials must not become the normal service identity
mechanism.

Detailed temporary-credential architecture is governed by Phase 4.1.6.

---

# Static Credential Restriction

Long-lived access keys and secrets for services are strongly restricted.

They may be used only when no approved temporary or managed identity mechanism
reasonably supports the required integration.

Any exception must be:

- Explicitly approved
- Narrowly scoped
- Protected
- Rotated
- Monitored
- Documented
- Removed when no longer required

---

# Credential Storage

Service credentials must not be embedded in:

- Source code
- Repository files
- Container images
- Browser code
- Frontend bundles
- Logs
- Queue payloads
- Documentation
- Plaintext configuration

Approved secret-management mechanisms must be used where credentials must be
stored.

---

# Identity Ownership

Every service identity must have an accountable owner.

Ownership must identify the architecture or service responsible for:

- Permission requirements
- Trust relationship
- Credential mechanism
- Rotation
- Review
- Incident response
- Decommissioning

An identity without an accountable owner must not remain active indefinitely.

---

# Account and Environment Scope

Service identities must remain scoped to approved AWS accounts and environments.

A development service identity must not automatically operate in production.

A testing identity must not automatically operate in staging or production.

A production service identity must be separately provisioned and governed.

Cross-account service identity requires explicit trust architecture.

---

# Region Scope

Service identities should be region-aware where the AWS service and operation
require regional scope.

The canonical regional model remains:

- eu-west-1 — primary
- us-east-1 — disaster-recovery
- af-south-1 — future

DR identity capability does not automatically authorize normal production
operation in the DR region.

---

# Least Privilege

Every service identity must comply with 4.1.3 Least-Privilege Model.

A service identity must receive only:

- Required actions
- Required resources
- Required accounts
- Required environments
- Required regions
- Required conditions

Service identity creation must not be used as justification for broad
permissions.

---

# Role-Per-Service Boundary

Broad shared service roles are prohibited where a narrower identity can
reasonably provide meaningful isolation.

Services with materially different trust or permission requirements should use
separate roles.

Shared identities require explicit justification.

---

# Privilege Escalation Boundary

Service identities must not be able to silently increase their own authority.

High-risk permissions include:

- IAM policy modification
- Role trust modification
- `iam:PassRole`
- Permission-set modification
- KMS policy modification
- Infrastructure deployment with stronger roles

Such permissions require explicit architecture and security review.

---

# Identity Lifecycle

Every service identity must have a lifecycle.

Canonical lifecycle:

Proposed
→ Approved
→ Provisioned
→ Active
→ Reviewed
→ Restricted / Rotated
→ Deprecated
→ Retired

Identity lifecycle must be traceable to the owning service.

---

# Provisioning

A service identity may be provisioned only for an approved service or automation
responsibility.

Provisioning must define:

- Identity name
- Owner
- Service
- Environment
- AWS account
- Trust source
- IAM role
- Required permissions
- Credential mechanism
- Logging requirements

---

# Rotation

Where service identity includes rotatable credential material, rotation must be
supported.

Rotation must not require uncontrolled manual distribution of credentials.

Managed or automatically rotated credentials are preferred where available.

---

# Revocation

Service identity access must be revocable.

Revocation may occur when:

- Service is retired
- Identity is compromised
- Trust source is compromised
- Permissions are no longer required
- Environment is retired
- Deployment mechanism changes
- Security requires containment

Revocation must preserve audit evidence.

---

# Deprovisioning

Retired service identities must be removed or disabled.

Deprovisioning should address:

- IAM role
- Trust relationship
- Credentials
- Secrets
- Resource policies
- Queue permissions
- Storage permissions
- Database access
- Monitoring dependencies
- Related configuration

Retired identities must not remain silently usable.

---

# Compromise Response

If a service identity is suspected of compromise:

- Disable or restrict the identity where required
- Revoke or rotate credentials
- Invalidate trust where applicable
- Preserve CloudTrail and runtime evidence
- Determine affected resources
- Contain privilege escalation paths
- Restore through approved identity mechanisms

Compromise response must not require converting the service to a human
administrator identity.

---

# Audit Attribution

Service identity activity must be attributable through available AWS and runtime
evidence.

Audit evidence should identify:

- Service identity
- IAM role
- Workload/session identity
- AWS account
- Environment
- Region
- API action
- Resource
- Timestamp
- Result

AWS CloudTrail remains the canonical AWS control-plane audit source.

---

# Universal Runtime Boundary

Universal Runtime already has authoritative identity, worker, queue, and
orchestration contracts.

This architecture does not replace those contracts.

AWS cloud service identity must map approved runtime components to the AWS
permissions they need.

It must not create:

- A new runtime worker
- A duplicate queue identity
- A duplicate orchestration identity
- A second runtime authorization authority

Existing Universal Runtime identity architecture must be reused.

---

# Relationship to Workload Identity

Service identity identifies the logical service principal.

Phase 4.1.5 Workload Identity defines how that principal is established and
proven by an executing workload.

4.1.5 may define mechanisms such as:

- ECS task roles
- EC2 instance profiles
- Lambda execution roles
- OIDC workload federation
- STS role assumption
- Other approved AWS workload identity mechanisms

Those mechanisms must implement, not replace, the service identities defined
here.

---

# Relationship to Identity Security Architecture

This architecture preserves the existing Identity Security boundary.

Customer identities remain under the LinkCraftor Identity Plane.

AWS service/workload identities remain under AWS IAM and their canonical runtime
authorities.

No service identity may become:

- Customer login authority
- Customer session authority
- Customer recovery authority
- Customer MFA authority
- Customer workspace authorization authority

No shadow authentication authority is introduced.

---

# Terraform and IaC Boundary

Service-identity infrastructure should ultimately be represented through
approved Terraform/IaC where applicable.

Phase 3 owns the Terraform implementation foundation.

Manual AWS Console identity configuration must not become authoritative
infrastructure state.

---

# Runtime Eligibility

This document is an architecture and governance artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future automated service-identity review, trust validation, credential rotation,
identity inventory, or compliance jobs may require Universal Runtime
Registration Standard assessment.

---

# Phase Dependencies

4.1.4 defines logical service identities.

4.1.5 defines workload identity and execution trust.

4.1.6 defines temporary credentials.

4.1.7 defines privileged access.

4.1.8 defines cross-environment restrictions.

4.1.9 defines emergency cloud access.

Phase 2 must provide the implemented AWS account and environment boundaries.

Phase 3 must provide Terraform/IaC implementation.

Later compute, runtime, queue, storage, database, deployment, observability,
backup, and other infrastructure phases will provision their actual service
identities through this architecture.

Final Phase 4 certification remains deferred until required implementation
dependencies exist.

---

# Prohibited Practices

The following are prohibited:

- Customer identity used as AWS service identity
- Human administrator credentials used as production service identity
- Service identity used for human AWS Console administration
- One unrestricted identity shared across unrelated services
- Long-lived static AWS credentials as the normal service identity model
- Credentials embedded in source code
- Credentials embedded in images
- Credentials written to logs
- Credentials placed in queues
- Uncontrolled wildcard trust
- Service identities without accountable owners
- Development service identity automatically trusted in production
- Service identity silently self-escalating privileges
- Deployment identity becoming runtime identity
- Runtime identity becoming human administrator identity
- Cloud IAM duplicating Universal Runtime authorization
- Retired service identities remaining silently active

---

# Canonical Decision Summary

LinkCraftor shall use explicit, dedicated, non-human service identities for AWS
services, runtime components, workers, automation, deployment systems, and other
machine-operated responsibilities.

Service identity remains separate from customer identity and human workforce
identity.

Service identities shall map to approved AWS IAM roles and use narrowly scoped
permissions.

Temporary or managed credentials are preferred over long-lived static
credentials.

Service-to-service trust must be explicit.

Each service identity must have an owner, lifecycle, auditability, and revocation
path.

Existing Universal Runtime identity, worker, queue, and orchestration contracts
must be reused rather than duplicated.

Phase 4.1.5 will define how executing workloads prove and obtain these service
identities.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
