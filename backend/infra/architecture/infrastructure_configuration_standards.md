# LinkCraftor Infrastructure Configuration Standards

Version: 1.0
Status: Canonical
Phase: Cloud Infrastructure Architecture
Section: 1.1.8 Infrastructure Configuration Standards
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical configuration standards for LinkCraftor
cloud infrastructure.

It establishes how infrastructure configuration is authored, parameterized,
validated, reviewed, versioned, secured, applied, and recovered.

The standard separates architecture decisions from executable Infrastructure as
Code and separates infrastructure configuration from application runtime
configuration.

---

# Configuration Principles

LinkCraftor infrastructure configuration must be:

- Declarative where practical
- Version-controlled
- Reviewable
- Reproducible
- Environment-aware
- Region-aware
- Secure by default
- Parameterized
- Validated before deployment
- Traceable to architecture
- Recoverable
- Resistant to configuration drift
- Free of embedded secrets
- Free of unnecessary application coupling

Manual configuration must not become the authoritative source of truth for
managed cloud infrastructure.

---

# Configuration Authority

The configuration authority hierarchy is:

Cloud Infrastructure Architecture
→ Canonical architecture decisions
→ Infrastructure Configuration Standards
→ Infrastructure as Code definitions
→ Environment-specific parameterization
→ Deployment pipeline
→ AWS resources

Architecture defines what is permitted.

Infrastructure as Code defines how approved infrastructure is declared.

Environment configuration supplies approved environment-specific values.

Deployment automation applies the approved configuration.

AWS console state is not the canonical source of truth.

---

# Canonical Infrastructure as Code Strategy

Terraform is the canonical primary Infrastructure as Code mechanism for
LinkCraftor AWS infrastructure.

Terraform shall be used to define managed cloud infrastructure where technically
appropriate.

Terraform configuration must be organized through:

- Root modules
- Reusable modules
- Environment entry points
- Variables
- Locals
- Outputs
- Provider configuration
- Backend configuration
- Validation rules

Infrastructure configuration must not be duplicated independently across
multiple environments when a reusable module can express the same architecture.

---

# Canonical Configuration Repository

Canonical infrastructure root:

backend/infra/

The configuration model may use:

backend/infra/
├── architecture/
├── terraform/
├── environments/
├── modules/
├── policies/
├── scripts/
├── security/
├── templates/
├── tests/
└── evidence/

The exact implementation may evolve through approved architecture changes.

Existing files must not be moved or deleted solely for cosmetic conformity.

---

# Environment Configuration

Canonical environments:

- development
- testing
- staging
- production
- sandbox
- shared
- security

Each environment must have explicit configuration boundaries.

Production configuration must not silently inherit unsafe development or
testing defaults.

Environment-specific values may include:

- Environment identifier
- AWS account reference
- AWS Region
- Region code
- RegionRole
- Availability Zone mapping
- Network ranges
- Resource capacity
- Scaling parameters
- Logging levels
- Backup settings
- Retention settings
- Feature enablement
- Service endpoints
- Deployment controls

Environment-specific configuration must remain compatible with the canonical
architecture.

---

# Region Configuration

Canonical regional configuration:

Primary production:
- Region: eu-west-1
- Region code: euw1
- RegionRole: primary

Disaster recovery:
- Region: us-east-1
- Region code: use1
- RegionRole: disaster-recovery

Future African expansion:
- Region: af-south-1
- Region code: afs1
- RegionRole: future

Global resources:
- RegionRole: global

The obsolete Frankfurt Region must not be introduced as a current canonical
configuration value.

The value "secondary" must not be used as a canonical RegionRole.

---

# Availability Zone Configuration

Architecture-level logical Availability Zone identifiers:

- AZ-A
- AZ-B
- AZ-C

Infrastructure naming may use:

- az-a
- az-b
- az-c

Logical Availability Zone identifiers must be mapped through Infrastructure as
Code to actual AWS Availability Zone identities.

Application code must not hard-code physical AWS Availability Zone letter
suffixes.

Production in the primary Region must support the approved multi-AZ strategy.

The disaster-recovery Region does not automatically require a full active
three-AZ production footprint before an approved DR topology requires it.

---

# Configuration Variables

Infrastructure configuration should use explicit typed variables.

Typical canonical variables include:

- project_name
- environment
- aws_account_id_reference
- region
- region_code
- region_role
- availability_zones
- platform_domain
- service_name
- resource_role
- qualifier
- criticality
- data_classification
- owner
- cost_center
- lifecycle

Variables must have clear ownership and purpose.

Variables must not be created merely to hide unexplained constants.

---

# Defaults

Defaults are permitted only when the default is:

- Safe
- Non-secret
- Architecture-approved
- Appropriate across intended consumers
- Explicitly documented

Production-critical settings must not rely on hidden or unsafe defaults.

A default suitable for development must not automatically become the production
default.

---

# Configuration Validation

Infrastructure configuration must be validated before deployment.

Validation may include:

- Terraform type constraints
- Variable validation
- Preconditions
- Policy checks
- Naming validation
- Tag validation
- Region validation
- Environment validation
- Network-range validation
- Resource-capacity validation
- Security-policy validation
- Required-value checks

Invalid configuration must fail before production deployment where technically
possible.

---

# Sensitive Configuration

Secrets and sensitive values must not be committed into Infrastructure as Code
source files, architecture documents, repository configuration, or plaintext
environment files.

Sensitive values include:

- Passwords
- API secrets
- Private keys
- OAuth client secrets
- Database credentials
- Signing secrets
- Tokens
- Encryption material
- Recovery credentials

Approved secret-storage mechanisms may include:

- AWS Secrets Manager
- AWS Systems Manager Parameter Store where appropriate
- AWS KMS-protected secret workflows

Secret-storage selection and lifecycle requirements are governed by the
Secrets, Keys & Certificate Infrastructure architecture.

---

# Configuration vs Secrets

Infrastructure configuration and secrets are separate concerns.

Example:

Allowed configuration:
database_port = 5432

Sensitive configuration:
database_password

The first may exist in approved Infrastructure as Code configuration.

The second must be retrieved from an approved secret-management mechanism.

---

# Application Configuration Boundary

Application configuration and infrastructure configuration must not be mixed
without a defined interface.

Application engines must not independently hard-code:

- AWS account IDs
- AWS Regions
- Availability Zone letters
- VPC IDs
- Subnet IDs
- Security Group IDs
- Secret values
- Resource ARNs
- Queue URLs
- Bucket names
- Database endpoints
- IAM role ARNs

where those values should be supplied through configuration, discovery,
deployment outputs, or a managed infrastructure contract.

Application code may consume approved configuration but must not become the
authority for cloud infrastructure topology.

---

# Infrastructure Configuration Outputs

Infrastructure as Code may expose approved outputs to dependent systems.

Examples include:

- Service endpoints
- Queue identifiers
- Bucket identifiers
- Database endpoints
- IAM role references
- Network identifiers
- Runtime configuration references

Outputs must expose only the information required by authorized consumers.

Sensitive outputs must be protected and must not be printed into logs or public
deployment output.

---

# Environment Isolation

Configuration must preserve environment isolation.

Development, testing, staging, sandbox, and production must not share mutable
configuration state in a way that permits accidental cross-environment changes.

Production configuration must require explicit production context.

Cross-environment references require architecture and security approval.

Production secrets must never be reused as development or testing secrets.

---

# AWS Account Boundary

Infrastructure configuration must target the approved AWS account for the
intended environment and responsibility.

Account selection must be explicit or deterministically derived from approved
deployment context.

A production deployment must fail if the effective AWS account does not match
the approved production boundary.

Application developers must not manually switch account identifiers inside
application source code.

---

# Terraform State

Terraform state must be treated as sensitive operational infrastructure data.

Terraform state must:

- Use an approved remote backend
- Be encrypted at rest
- Use access controls
- Support state locking where available
- Be isolated by approved environment or deployment boundary
- Be protected from unauthorized deletion
- Be recoverable
- Be auditable
- Avoid public exposure

Local state must not be used as the authoritative production state.

Production and non-production must not share the same Terraform state boundary
unless explicitly approved.

Detailed state backend implementation is owned by Phase 3 — Infrastructure as
Code.

---

# State Locking

Terraform state operations must use locking or another approved concurrency
control where supported.

Concurrent infrastructure changes must not be allowed to corrupt authoritative
state.

Lock override or forced unlock procedures must be controlled and auditable.

---

# Provider Configuration

Terraform provider configuration must be centralized and parameterized.

Provider configuration must use approved:

- AWS account context
- Region
- Role assumption
- Credential mechanism
- Default tags where appropriate

Long-lived static AWS credentials must not be embedded in provider files.

Provider configuration must support temporary credentials and approved workload
or deployment identities.

---

# Module Standards

Reusable Terraform modules must:

- Have a defined responsibility
- Use explicit inputs
- Expose intentional outputs
- Validate critical inputs
- Avoid hidden cross-environment dependencies
- Follow Cloud Naming Standards
- Apply required resource metadata where supported
- Avoid embedded secrets
- Avoid unnecessary provider duplication
- Be version-controlled
- Be testable
- Be reviewable

Modules must not silently create unrelated infrastructure outside their declared
responsibility.

---

# Naming and Metadata Integration

Infrastructure configuration must comply with:

- Cloud Resource Organization
- Cloud Naming Standards
- Region Strategy
- Availability Zone Strategy

Physical resource names must be generated through the approved naming standard.

Required metadata and tags must be applied where supported.

The configuration layer must not invent a conflicting naming or tagging model.

---

# Configuration Change Control

Infrastructure configuration changes must be version-controlled.

Normal change workflow:

1. Proposed change
2. Architecture compatibility review where required
3. Source-control change
4. Automated validation
5. Terraform plan or equivalent preview
6. Human or policy approval where required
7. Controlled deployment
8. Post-deployment validation
9. Evidence capture

Production infrastructure changes must not be applied from unreviewed local
files.

---

# Pull Request Review

Infrastructure configuration changes should use pull-request review before
merging into protected branches.

Review should assess:

- Architecture compliance
- Security impact
- Environment impact
- Cost impact
- Data impact
- Availability impact
- Migration or replacement behavior
- Rollback capability

Emergency changes require a documented emergency process and later
reconciliation with Infrastructure as Code.

---

# Configuration Drift

Configuration drift occurs when deployed infrastructure differs from the
approved Infrastructure as Code state or approved architecture.

Drift may result from:

- Manual console changes
- Emergency changes
- Unmanaged scripts
- Incorrect automation
- Provider behavior
- External service changes

Drift must be detected, investigated, and reconciled.

Unapproved drift must not become the new source of truth merely because it
exists in AWS.

---

# Manual AWS Console Changes

Routine managed-infrastructure changes through the AWS console are prohibited
for production.

Console access may be used for:

- Investigation
- Read-only inspection
- Approved emergency action
- Explicitly approved exceptional operation

Any emergency configuration change must be:

1. Logged
2. Reviewed
3. Reconciled into Infrastructure as Code
4. Validated
5. Captured as evidence

---

# Configuration Versioning

Infrastructure configuration must be version-controlled through the approved
source-control platform.

Git history must provide traceability for configuration changes.

Configuration releases should be attributable to:

- Commit
- Pull request
- Deployment run
- Environment
- Approver where required
- Evidence

Architecture documents and executable configuration must remain distinguishable.

---

# Rollback and Recovery

Infrastructure changes must consider rollback before production deployment.

Rollback may use:

- Reversion of Infrastructure as Code
- Previous approved configuration
- Resource restoration
- Blue/green infrastructure
- Backup recovery
- Controlled replacement

Rollback strategy must account for resources where reverting configuration does
not automatically restore data or service state.

---

# Backup of Configuration

Source-controlled Infrastructure as Code provides the primary version history
for configuration definitions.

Additional backup requirements apply to:

- Terraform state
- Critical deployment metadata
- Recovery artifacts
- Security configuration
- Evidence

Backups must not expose secrets.

---

# Configuration Documentation

Configuration must be documented sufficiently to identify:

- Purpose
- Owner
- Environment applicability
- Region applicability
- Valid values
- Default behavior
- Security considerations
- Deployment impact
- Recovery implications

Critical configuration must not exist only as tribal knowledge.

---

# CI/CD Integration

Infrastructure configuration validation and deployment should integrate with the
approved CI/CD platform.

GitHub Actions is the approved external CI/CD mechanism where applicable.

CI/CD must not bypass:

- Environment boundaries
- Deployment approvals
- Credential controls
- Secret-management controls
- Terraform state controls
- Production change governance

---

# Configuration Evidence

Infrastructure changes should generate evidence appropriate to the risk and
environment.

Evidence may include:

- Validation output
- Terraform plan
- Approval record
- Deployment result
- Drift check
- Post-deployment verification
- Recovery test
- Change identifier

Generated evidence must follow approved retention and security controls.

---

# Prohibited Practices

LinkCraftor infrastructure configuration must not:

- Store secrets in source control
- Store passwords in Terraform variables files
- Store long-lived AWS access keys in provider configuration
- Treat the AWS console as the production source of truth
- Hard-code AWS account IDs in application engines
- Hard-code physical Availability Zone letters in application logic
- Use obsolete Frankfurt configuration as canonical
- Use "secondary" as a canonical RegionRole
- Share production Terraform state with unmanaged lower environments
- Allow unreviewed local production changes
- Silently inherit development defaults into production
- Create duplicate configuration authorities
- Allow configuration drift to become canonical without approval
- Expose sensitive Terraform outputs
- Bypass architecture, security, or deployment controls

---

# Runtime Eligibility

This Infrastructure Configuration Standards document is an architecture and
governance artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future executable configuration-validation jobs, drift-detection jobs,
compliance scans, Terraform-plan certification jobs, and configuration-baseline
checks may require Universal Runtime Registration Standard assessment.

---

# Canonical Decision

LinkCraftor shall adopt:

- Terraform as the primary Infrastructure as Code configuration mechanism
- Version-controlled infrastructure configuration
- Environment-specific parameterization
- Approved Region and RegionRole configuration
- Logical Availability Zone mapping
- Typed and validated configuration variables
- Approved secret-management separation
- Remote and protected Terraform state
- Controlled provider configuration
- Reusable Terraform modules
- Pull-request and deployment review
- Configuration drift detection and reconciliation
- Controlled emergency changes
- Explicit application/infrastructure configuration boundaries
- Architecture-aligned naming and metadata
- Recoverable configuration and state
- Evidence-backed production changes

AWS console state is not the canonical infrastructure configuration source of
truth.

Application engines must consume approved infrastructure configuration rather
than independently hard-coding AWS topology.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
