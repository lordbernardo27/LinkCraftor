# LinkCraftor Cloud Naming Standards

Version: 1.0
Status: Canonical
Phase: Cloud Infrastructure Architecture
Section: 1.1.7 Cloud Naming Standards
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical naming standards for LinkCraftor cloud
infrastructure.

It governs human-readable identifiers, Infrastructure as Code names, AWS
resource names, environment codes, Region codes, platform-domain names,
resource roles, qualifiers, account names, and display names.

The objective is to provide consistent, predictable, auditable, portable, and
automation-safe infrastructure naming without embedding unnecessary AWS
implementation details into application code.

---

# Naming Principles

All LinkCraftor cloud names must follow these principles:

- Predictable
- Deterministic
- Human-readable
- Machine-readable
- Environment-aware
- Region-aware where required
- Platform-domain-aware
- Service-aware
- Compatible with AWS service naming constraints
- Compatible with Terraform
- Stable across deployment cycles
- Free of secrets and sensitive data
- Free of personal names unless formally approved
- Free of arbitrary or unexplained abbreviations

Names must communicate resource purpose without requiring access to source code
to understand what the resource represents.

---

# Canonical Project Identity

Canonical product name:

LinkCraftor

Canonical architecture identifier:

LINKCRAFTOR

Canonical lowercase infrastructure prefix:

linkcraftor

Canonical project tag:

Project=LinkCraftor

The spelling "LinkCraftor" must be preserved for product and architecture
identity.

Lowercase "linkcraftor" shall be used where AWS resource naming rules or
canonical infrastructure patterns require lowercase names.

---

# Canonical Environment Names

Canonical environment names:

- development
- testing
- staging
- production
- sandbox
- shared
- security

Canonical short environment codes:

- development → dev
- testing → test
- staging → stage
- production → prod
- sandbox → sandbox
- shared → shared
- security → security

Short codes may be used in physical resource names where shorter identifiers are
required.

Full environment names remain canonical for metadata and architecture
documentation.

Environment codes must not create ambiguity.

---

# Canonical AWS Account Names

Canonical AWS account role names:

- LINKCRAFTOR-MANAGEMENT
- LINKCRAFTOR-SECURITY
- LINKCRAFTOR-LOG-ARCHIVE
- LINKCRAFTOR-NETWORK
- LINKCRAFTOR-SHARED-SERVICES
- LINKCRAFTOR-DEPLOYMENT
- LINKCRAFTOR-DEVELOPMENT
- LINKCRAFTOR-TESTING
- LINKCRAFTOR-STAGING
- LINKCRAFTOR-PRODUCTION
- LINKCRAFTOR-SANDBOX

These are architecture-level account role identifiers.

Actual AWS account IDs must not be embedded in naming standards, application
code, public documentation, or source-controlled configuration.

---

# Canonical Region Names and Codes

Approved canonical Regions:

## Primary Production Region

AWS Region:

eu-west-1

Name:

Europe (Ireland)

Canonical short code:

euw1

RegionRole:

primary

## Disaster-Recovery Region

AWS Region:

us-east-1

Name:

US East (N. Virginia)

Canonical short code:

use1

RegionRole:

disaster-recovery

## Future African Region

AWS Region:

af-south-1

Name:

Africa (Cape Town)

Canonical short code:

afs1

RegionRole:

future

## Global Scope

Resources that are architecturally global may use:

global

RegionRole:

global

The former Frankfurt Region and code are not canonical.

The following must not be introduced as current LinkCraftor canonical values:

- eu-central-1
- Europe (Frankfurt)
- euc1

A future Region must receive an approved canonical short code before use.

---

# Canonical RegionRole Values

RegionRole must use one of:

- primary
- disaster-recovery
- future
- global

The value "secondary" is not canonical.

RegionRole represents operational responsibility, not simply numerical order.

---

# Canonical Platform Domain Names

Approved platform-domain identifiers:

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

New platform-domain identifiers require architecture approval.

Platform-domain names must use lowercase kebab-case unless an AWS service
requires a different format.

---

# Canonical Resource Naming Formula

Default resource naming formula:

linkcraftor-{environment}-{platform-domain}-{service}-{resource-role}

Example:

linkcraftor-prod-universal-runtime-queue-primary

Where Region identification is required:

linkcraftor-{environment}-{region}-{platform-domain}-{service}-{resource-role}

Example:

linkcraftor-prod-euw1-universal-runtime-worker-primary

Where an additional qualifier is required:

linkcraftor-{environment}-{region}-{platform-domain}-{service}-{resource-role}-{qualifier}

Example:

linkcraftor-prod-euw1-backend-api-service-primary-v1

The shortest valid canonical form should be preferred.

Optional components must not be added where they provide no operational value.

---

# Resource Role Naming

Resource-role values describe what the resource does.

Examples include:

- primary
- replica
- standby
- worker
- api
- frontend
- runtime
- queue
- dead-letter
- cache
- database
- upload
- archive
- backup
- logs
- deployment
- monitoring
- internal
- public
- private
- ingress
- egress

Resource roles must be meaningful and stable.

Generic names such as:

- resource1
- thing
- server
- test123
- temp123
- new
- final
- final2

are prohibited for managed cloud infrastructure.

---

# Qualifier Rules

Qualifiers may represent:

- version
- shard
- tenant boundary
- workload class
- sequence
- recovery tier
- purpose subtype

Qualifiers must be deterministic.

Random suffixes may be used only where:

1. The AWS service requires global uniqueness.
2. Infrastructure as Code generates or manages the suffix.
3. The stable logical resource identity remains discoverable through tags and
   architecture metadata.

Random suffixes must not be manually invented as part of the canonical naming
scheme.

---

# Display Names vs Physical Resource Names

A human-facing display name and a physical AWS resource name are separate
concepts.

Example display name:

Main LinkCraftor Production

Canonical architecture identifier:

LINKCRAFTOR-PRODUCTION

Example physical infrastructure name:

linkcraftor-prod-euw1-backend-api-service-primary

Human-facing names may use spaces and title case.

Physical names must follow AWS service constraints and the applicable canonical
formula.

Display names must not replace required tags or canonical identifiers.

---

# Tags vs Names

Resource names provide operational readability.

Tags provide authoritative metadata.

A physical resource name must not be treated as the only source of truth for:

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

Those values remain governed by the Cloud Resource Organization metadata model.

Names and tags must agree where they represent the same dimension.

---

# AWS Service-Specific Naming Rules

AWS services impose different character, case, length, and uniqueness
requirements.

The canonical LinkCraftor naming formula must therefore be adapted without
changing its semantic meaning.

---

# Amazon S3 Bucket Naming

S3 bucket names must:

- Use lowercase letters where required
- Use digits and hyphens where valid
- Avoid uppercase characters
- Avoid underscores
- Satisfy AWS global uniqueness requirements
- Avoid embedding secrets, account IDs, customer-sensitive information, or
  personal data

Example:

linkcraftor-prod-euw1-storage-uploads-primary

If a uniqueness suffix is required, it must be generated and managed through
Infrastructure as Code.

---

# Amazon ECS Naming

ECS cluster and service names should preserve:

- Project
- Environment
- Platform domain
- Service
- Role

Examples:

linkcraftor-prod-euw1-universal-runtime-cluster-primary

linkcraftor-prod-euw1-backend-api-service-primary

---

# Amazon RDS Naming

Database infrastructure names must identify:

- Environment
- Region where appropriate
- Database service or workload
- Resource role

Example:

linkcraftor-prod-euw1-database-app-primary

Secrets, credentials, database passwords, tenant names, or customer-sensitive
identifiers must not appear in database infrastructure names.

---

# Amazon SQS Naming

Queue names must identify:

- Environment
- Platform domain or workload
- Queue purpose
- Role

Examples:

linkcraftor-prod-euw1-universal-runtime-queue-primary

linkcraftor-prod-euw1-universal-runtime-queue-dead-letter

Dead-letter queues should use the canonical resource role:

dead-letter

rather than arbitrary abbreviations unless a service-specific limit requires a
shorter approved form.

---

# Amazon SNS Naming

Topic names must follow the same environment, platform-domain, service, and role
principles.

Example:

linkcraftor-prod-euw1-notification-events-primary

---

# VPC Naming

VPC names must clearly identify environment and Region.

Example:

linkcraftor-prod-euw1-network-vpc-primary

Where a dedicated workload VPC exists, include the relevant platform domain or
workload qualifier.

---

# Subnet Naming

Subnet names must identify:

- Environment
- Region
- Logical Availability Zone
- Subnet class

Canonical logical Availability Zone identifiers:

- az-a
- az-b
- az-c

Examples:

linkcraftor-prod-euw1-az-a-network-subnet-public

linkcraftor-prod-euw1-az-a-network-subnet-private-app

linkcraftor-prod-euw1-az-a-network-subnet-private-runtime

linkcraftor-prod-euw1-az-a-network-subnet-private-data

Physical AWS Availability Zone letter suffixes must not become architecture
identifiers.

---

# Security Group Naming

Security group names should identify the protected workload or access role.

Examples:

linkcraftor-prod-euw1-backend-api-sg-app

linkcraftor-prod-euw1-database-sg-data

Rules must not rely on a human-readable security-group name as the security
boundary.

---

# IAM Role Naming

IAM role names must identify:

- Project
- Environment or scope
- Platform domain or service
- Role purpose

Examples:

linkcraftor-prod-universal-runtime-role-worker

linkcraftor-prod-deployment-role-ci

linkcraftor-security-role-auditor

IAM role naming does not replace IAM policy review, least privilege, workload
identity, trust-policy controls, or session controls.

---

# CloudWatch Naming

CloudWatch log groups, dashboards, alarms, and related resources should follow
the same project, environment, platform-domain, service, and role hierarchy
where the AWS service supports it.

Examples:

/linkcraftor/prod/backend-api/application

/linkcraftor/prod/universal-runtime/worker

Canonical slash-based hierarchy may be used for CloudWatch log groups.

---

# Infrastructure as Code Naming

Terraform is the canonical primary Infrastructure as Code implementation
strategy for LinkCraftor AWS infrastructure.

Terraform logical identifiers should:

- Be readable
- Be stable
- Avoid unnecessary coupling to physical resource names
- Use snake_case where appropriate for Terraform identifiers
- Preserve canonical environment, region, platform-domain, service, and role
  meaning

Example Terraform logical identifier:

aws_sqs_queue.universal_runtime_primary

Physical AWS resource name:

linkcraftor-prod-euw1-universal-runtime-queue-primary

Terraform logical resource names do not need to duplicate every physical-name
component.

---

# Terraform Variables

Infrastructure naming should be parameterized through variables such as:

project_name

environment

region

region_code

region_role

platform_domain

service_name

resource_role

qualifier

Names must be assembled centrally through reusable Terraform modules or naming
locals rather than independently constructed throughout the codebase.

---

# Naming Ownership

The Cloud Infrastructure Architecture owns the canonical naming standard.

Infrastructure as Code owns physical-resource name generation.

Cloud Resource Organization owns:

- Account structure
- Resource hierarchy
- Required metadata
- Required tags
- Ownership
- RegionRole vocabulary

Individual application engines must not independently invent AWS infrastructure
naming rules.

---

# Existing Resource Rule

Adoption of this naming standard does not automatically authorize renaming of
existing AWS resources.

Existing resources must not be renamed solely to achieve cosmetic conformity.

A rename may cause:

- Resource replacement
- Downtime
- Data migration
- DNS changes
- IAM reference changes
- Monitoring disruption
- State migration
- Terraform replacement
- Backup impact

Any existing-resource rename requires:

1. Impact analysis
2. Infrastructure plan
3. Security review
4. Data review where applicable
5. Downtime or migration review
6. Backup verification
7. Rollback plan
8. Architecture approval

Where safe renaming is not possible, the existing physical name may remain and
canonical metadata and tags must identify the resource correctly.

---

# Naming Migration Rule

Legacy names may remain during controlled migration.

A migration must document:

- Existing identifier
- New canonical identifier
- Resource type
- Environment
- Region
- Dependencies
- Replacement requirement
- Migration method
- Validation
- Rollback
- Evidence

Naming migrations must not be mixed casually with unrelated application
changes.

---

# Prohibited Practices

LinkCraftor cloud infrastructure must not:

- Use arbitrary resource names
- Use personal names for infrastructure without formal approval
- Embed passwords, secrets, tokens, account IDs, or confidential data in names
- Use the obsolete Frankfurt Region naming as canonical
- Use "secondary" as a canonical RegionRole
- Hard-code physical Availability Zone letters as architecture identities
- Use inconsistent environment abbreviations
- Invent unapproved Region short codes
- Create duplicate naming systems in separate teams
- Treat display names as authoritative metadata
- Rename live resources solely for cosmetic consistency
- Allow application code to depend on human-facing AWS resource names where a
  stable configuration or service-discovery mechanism should be used

---

# Runtime Eligibility

This Cloud Naming Standards document is an architecture and governance artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future executable naming-validation scanners, tag-to-name consistency checks,
Infrastructure as Code policy checks, migration validators, and certification
jobs may require Universal Runtime Registration Standard assessment.

---

# Canonical Decision

LinkCraftor shall use:

- LinkCraftor as the canonical project identity
- linkcraftor as the lowercase infrastructure prefix
- Approved full environment names and short environment codes
- euw1 for eu-west-1
- use1 for us-east-1
- afs1 for af-south-1
- primary, disaster-recovery, future, and global as canonical RegionRole values
- Lowercase kebab-case for general physical-resource naming where supported
- Stable platform-domain identifiers
- Deterministic resource-role identifiers
- Terraform-driven name generation
- Service-specific adaptation where AWS constraints require it
- Canonical metadata and tags in addition to physical names
- Controlled migration rather than automatic renaming of existing resources

The Frankfurt Region code euc1 is not canonical.

Specific AWS account IDs, secrets, tokens, customer-sensitive identifiers, and
personal data must not be embedded into resource names.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
