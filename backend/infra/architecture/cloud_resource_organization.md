# LinkCraftor Cloud Resource Organization

Version: 1.0
Status: Canonical
Phase: Cloud Infrastructure Architecture
Section: 1.1.6 Cloud Resource Organization
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical organization of LinkCraftor cloud accounts,
organizational units, environments, resources, ownership boundaries, and
infrastructure repositories.

It establishes the structural foundation for secure isolation, governance,
cost allocation, operational ownership, and future enterprise expansion.

---

# Organization Model

LinkCraftor shall use AWS Organizations as the canonical account-governance
foundation.

The architecture shall support:

- Central organizational governance
- Separate AWS accounts by responsibility
- Environment isolation
- Security isolation
- Log and audit isolation
- Shared service management
- Cost allocation
- Service Control Policies
- Future enterprise and regional expansion

The production environment must not share an AWS account with development,
testing, or personal experimentation.

---

# Management Account

Canonical account role:

LINKCRAFTOR-MANAGEMENT

Purpose:

- AWS Organizations administration
- Consolidated billing
- Organizational Unit management
- Service Control Policy management
- Account creation and governance
- Organization-wide policy administration

Restrictions:

- No application workloads
- No customer data
- No production compute
- No routine engineering activity
- No shared administrative credentials

The management account must be used only for organization-level governance.

---

# Canonical Organizational Units

The AWS Organization shall support the following logical Organizational Units.

## Security OU

Purpose:

- Security monitoring
- Audit evidence
- Central logging
- Security tooling
- Threat detection
- Compliance infrastructure

Canonical member accounts:

- LINKCRAFTOR-SECURITY
- LINKCRAFTOR-LOG-ARCHIVE

## Infrastructure OU

Purpose:

- Shared networking
- Shared services
- Infrastructure tooling
- CI/CD support
- Artifact infrastructure
- Operational tooling

Canonical member accounts:

- LINKCRAFTOR-NETWORK
- LINKCRAFTOR-SHARED-SERVICES
- LINKCRAFTOR-DEPLOYMENT

## Non-Production OU

Purpose:

- Development
- Testing
- Staging
- Sandbox experimentation

Canonical member accounts:

- LINKCRAFTOR-DEVELOPMENT
- LINKCRAFTOR-TESTING
- LINKCRAFTOR-STAGING
- LINKCRAFTOR-SANDBOX

## Production OU

Purpose:

- Customer-facing production infrastructure
- Production databases
- Production runtime
- Production workers
- Production storage
- Production monitoring

Canonical member accounts:

- LINKCRAFTOR-PRODUCTION

Additional production accounts may later be created by:

- Region
- Workload class
- Data classification
- Enterprise isolation requirement
- Regulatory boundary
- White-label deployment
- Dedicated customer requirement

## Suspended OU

Purpose:

- Disabled accounts
- Decommissioned accounts
- Quarantined accounts
- Accounts pending investigation

No active workloads may run in the Suspended OU.

---

# Canonical AWS Account Structure

## LINKCRAFTOR-MANAGEMENT

Responsibilities:

- AWS Organizations
- Consolidated billing
- Service Control Policies
- Account lifecycle
- Organization governance

## LINKCRAFTOR-SECURITY

Responsibilities:

- Security Hub
- GuardDuty administration
- Inspector administration
- IAM Access Analyzer
- Security operations
- Security evidence aggregation

## LINKCRAFTOR-LOG-ARCHIVE

Responsibilities:

- Central CloudTrail logs
- Central configuration logs
- Security audit logs
- Immutable log retention
- Cross-account evidence storage

## LINKCRAFTOR-NETWORK

Responsibilities:

- Shared network architecture
- Transit connectivity
- DNS integration
- Network inspection
- Future regional network coordination

## LINKCRAFTOR-SHARED-SERVICES

Responsibilities:

- Shared operational services
- Central observability components
- Shared artifact services
- Approved internal tooling
- Shared automation

## LINKCRAFTOR-DEPLOYMENT

Responsibilities:

- CI/CD execution
- Infrastructure provisioning
- Deployment roles
- Artifact promotion
- Controlled environment access

## LINKCRAFTOR-DEVELOPMENT

Responsibilities:

- Cloud-based development workloads
- Early infrastructure validation
- Developer integration testing
- Non-production experimentation

## LINKCRAFTOR-TESTING

Responsibilities:

- Automated testing
- Integration testing
- Load-test preparation
- Failure testing
- Infrastructure validation

## LINKCRAFTOR-STAGING

Responsibilities:

- Production-like validation
- Release-candidate deployment
- Pre-production certification
- Deployment rehearsal
- Recovery rehearsal

## LINKCRAFTOR-PRODUCTION

Responsibilities:

- Customer-facing application
- Production APIs
- Production databases
- Production object storage
- Universal Runtime workloads
- Worker fleets
- Upload infrastructure
- Queue infrastructure
- Production observability

## LINKCRAFTOR-SANDBOX

Responsibilities:

- Temporary experiments
- Proofs of concept
- Training
- Isolated evaluation

Sandbox resources must have strict budgets, expiration controls, and no access
to production data.

---

# Environment Isolation Rules

Each environment must have independent:

- AWS accounts
- IAM roles
- VPCs
- Subnets
- Security groups
- Secrets
- Encryption keys
- Databases
- Storage
- Queues
- Runtime workers
- Logging
- Monitoring
- Budgets
- Deployment permissions

Production resources must not be shared with lower environments unless a
specific managed shared service has been formally approved.

Production data must not be copied into lower environments without approved
sanitization, masking, governance, and audit controls.

---

# Resource Hierarchy

The canonical resource hierarchy is:

AWS Organization
→ Organizational Unit
→ AWS Account
→ AWS Region
→ Environment
→ Platform Domain
→ Service
→ Resource Type
→ Individual Resource

Example:

LinkCraftor Organization
→ Production OU
→ LINKCRAFTOR-PRODUCTION
→ eu-west-1
→ production
→ universal-runtime
→ queue-service
→ Amazon SQS Queue
→ production universal-runtime primary queue

---

# Platform Domain Organization

Cloud resources shall be grouped logically by platform domain.

Canonical domains include:

- frontend
- backend-api
- identity
- workspace
- upload
- connected-domain
- universal-runtime
- worker-fleet
- queue
- storage
- database
- cache
- observability
- security
- billing
- supportops
- notification
- api
- plugin
- ai
- deployment
- backup
- disaster-recovery
- owner-control-tower

New platform domains require architecture approval.

---

# Infrastructure Repository Organization

The canonical local infrastructure root is:

backend/infra/

Required top-level structure:

backend/infra/
├── architecture/
├── docker/
├── terraform/
├── environments/
├── modules/
├── policies/
├── scripts/
├── security/
├── templates/
├── tests/
└── evidence/

Current folders may remain until their migration is approved.

No existing infrastructure file should be moved or deleted solely because this
document is created.

---

# Canonical Infrastructure Directory Responsibilities

## architecture

Contains:

- Cloud architecture decisions
- Strategies
- Standards
- Policies
- Certifications
- Architecture boundary documents

## docker

Contains:

- Dockerfiles
- Container runtime configuration
- Image build configuration

## terraform

Contains:

- Terraform root modules
- Provider configuration
- Backend state configuration
- Account and environment entry points

## environments

Contains environment-specific configuration for:

- development
- testing
- staging
- production

Secrets must not be stored in this folder.

## modules

Contains reusable Infrastructure as Code modules.

## policies

Contains:

- IAM policies
- Service Control Policies
- Resource policies
- Governance policies

## scripts

Contains controlled infrastructure automation scripts.

## security

Contains cloud-security infrastructure configuration.

## templates

Contains approved reusable infrastructure templates.

## tests

Contains infrastructure validation and policy tests.

## evidence

Contains generated certification and verification evidence.

Runtime-generated production evidence should be stored in approved cloud
storage rather than committed directly to source control.

---

# Resource Ownership

Every cloud resource must have a designated owner.

Required ownership dimensions:

- Business owner
- Technical owner
- Operational owner
- Security owner
- Cost owner
- Data owner where applicable

A resource without an assigned owner is non-compliant.

---

# Mandatory Resource Metadata

Every supported AWS resource must include metadata where the AWS service
supports tagging.

Canonical required tags:

- Project
- Environment
- PlatformDomain
- Service
- Owner
- ManagedBy
- CostCenter
- DataClassification
- Criticality
- RegionRole
- Lifecycle
- Repository
- CreatedBy

Canonical values:

Project=LinkCraftor

ManagedBy=Terraform

Environment must be one of:

- development
- testing
- staging
- production
- sandbox
- shared
- security

RegionRole must be one of:

- primary
- secondary
- disaster-recovery
- future
- global

Lifecycle must be one of:

- permanent
- managed
- temporary
- experimental
- deprecated
- decommissioning

---

# Cost Allocation Boundaries

Cloud resources must support cost allocation by:

- AWS account
- Environment
- Platform domain
- Service
- Region
- Workload
- Tenant where technically supported
- Workspace where technically supported
- Pipeline where technically supported

Shared infrastructure costs must have a documented allocation method.

---

# Shared Resource Rules

Shared resources may be used only when sharing:

- Does not weaken environment isolation
- Does not expose production data
- Does not create uncontrolled cross-account access
- Has a defined owner
- Has cost-allocation rules
- Has monitoring
- Has recovery procedures
- Has documented consumers

Shared databases between development, staging, and production are prohibited.

---

# Production Resource Boundaries

Production resources must:

- Exist only in approved production accounts
- Use approved Regions
- Use approved Availability Zones
- Be managed through Infrastructure as Code
- Have monitoring and alerting
- Have backup and recovery controls where applicable
- Have approved IAM access
- Have required tags
- Have cost controls
- Have documented ownership

Manual production resource creation is prohibited unless an emergency procedure
authorizes it and the resource is subsequently imported into Infrastructure as
Code.

---

# Account Access Rules

Human access must use:

- Named identities
- AWS IAM Identity Center
- Temporary sessions
- Multi-factor authentication
- Least privilege
- Auditable role assumption

Permanent administrator access keys are prohibited.

Application workloads must use service roles or workload identities rather than
human credentials.

---

# Account Lifecycle

Each AWS account must have a documented lifecycle:

1. Request
2. Approval
3. Provisioning
4. Baseline configuration
5. Security enrollment
6. Logging enrollment
7. Budget assignment
8. Operational activation
9. Periodic review
10. Suspension
11. Decommissioning
12. Evidence retention

Accounts must not be deleted without confirming data retention, backup, audit,
billing, legal, and recovery requirements.

---

# Resource Lifecycle

Each resource must support a controlled lifecycle:

1. Architecture approval
2. Infrastructure definition
3. Security review
4. Cost review
5. Deployment
6. Validation
7. Monitoring
8. Maintenance
9. Versioning
10. Deprecation
11. Decommissioning
12. Evidence retention

Temporary resources must have expiration controls.

---

# Service Control Policy Readiness

The organization must support future Service Control Policies for:

- Prohibiting unauthorized Regions
- Preventing security-service disablement
- Restricting root-user actions
- Blocking unapproved public storage
- Preventing CloudTrail removal
- Enforcing approved account boundaries
- Restricting unmanaged production resources
- Preventing use of prohibited AWS services
- Protecting log archive accounts
- Protecting security accounts

Actual Service Control Policies will be created during the governance and
security implementation phases.

---

# Expansion Strategy

The account structure must support future:

- Multi-region production
- Dedicated enterprise accounts
- White-label deployments
- Regulated customer environments
- Dedicated customer data boundaries
- Regional data-residency accounts
- Acquisition integration
- Additional LinkCraftor products
- Marketplace operations
- OEM infrastructure

Expansion must preserve centralized governance and isolation.

---

# Prohibited Practices

LinkCraftor must not:

- Run production inside the management account.
- Combine all environments into one AWS account.
- Store customer production data in sandbox accounts.
- Share production databases with non-production environments.
- Create unmanaged AWS accounts.
- Create ownerless resources.
- Use untagged production resources where tagging is supported.
- Use personal AWS accounts for LinkCraftor infrastructure.
- Use shared administrator credentials.
- Bypass organization-level logging or security enrollment.
- Create arbitrary account structures without architecture approval.

---

# Runtime Eligibility

This Cloud Resource Organization document is an architecture and governance
artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future executable account-provisioning workflows, tag-compliance scans,
resource-inventory scans, account-baseline jobs, drift scans, and certification
operations may require Universal Runtime Registration Standard assessment.

---

# Canonical Decision

LinkCraftor shall adopt:

- AWS Organizations
- A dedicated management account
- Separate security and log archive accounts
- Separate infrastructure and deployment accounts
- Separate development, testing, staging, sandbox, and production accounts
- Environment-specific resource isolation
- Centralized governance
- Mandatory ownership and tagging
- Infrastructure as Code management
- Expansion readiness for regions, enterprises, and white-label deployments

Specific AWS account IDs must not be stored in this document.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
