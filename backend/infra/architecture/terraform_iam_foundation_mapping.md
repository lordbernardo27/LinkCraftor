# LinkCraftor Terraform / IAM Foundation Mapping

Version: 1.0
Status: Canonical Implementation Mapping
Phase: Cloud Identity & Access Infrastructure
Section: 4.I.2 Terraform/IAM Foundation Mapping
Cloud Provider: Amazon Web Services
IaC Authority: Terraform

---

# Purpose

This document maps the certified LinkCraftor Cloud Identity & Access
architecture onto the certified Terraform architecture before live AWS IAM
implementation begins.

The mapping is reuse-first.

No duplicate Universal Runtime worker, trust engine, authorization engine, or
job execution system may be created.

---

# Governing Rule

Terraform manages the AWS cloud identity infrastructure.

The existing Universal Runtime remains authoritative for LinkCraftor runtime
job execution, worker authorization, execution grants, runtime permission
fencing, and worker lifecycle behavior.

AWS IAM must provide cloud identity and AWS-resource authorization around the
existing runtime.

AWS IAM must not replace the Universal Runtime authorization system.

---

# Identity Layers

## Layer 1 — Human Workforce Identity

Used for:

- Cloud administrators
- Engineers
- Operators
- Security personnel
- Emergency operators

Canonical direction:

- AWS IAM Identity Center
- Federated workforce access
- Temporary sessions

Long-lived IAM users are not the canonical workforce model.

---

## Layer 2 — Terraform Administrative Identity

Canonical roles:

- TerraformPlanRole
- TerraformApplyRole

Plan authority does not imply apply authority.

Universal Runtime workers must never receive TerraformApplyRole simply because
they execute jobs.

---

## Layer 3 — AWS Service / Workload Identity

AWS service and workload roles provide AWS-resource authority to LinkCraftor
services and runtime compute.

They do not replace LinkCraftor runtime identity or runtime authorization.

---

## Layer 4 — LinkCraftor Universal Runtime Identity

Existing authority:

backend/server/runtime/

Existing components include:

- operational trust
- signed execution grants
- worker identity validation
- service-to-service trust
- runtime authentication
- runtime authorization
- execution authorization
- privilege boundaries
- worker leasing
- worker heartbeat
- worker capacity
- worker registration
- Universal Runtime worker service

This layer must be REUSED.

No second worker runtime or parallel runtime identity system is permitted.

---

# Canonical Trust Flow

Human operator
    |
    v
AWS IAM Identity Center / federation
    |
    v
Approved AWS role
    |
    +--> TerraformPlanRole
    |
    +--> TerraformApplyRole
    |
    +--> Cloud administration role

AWS workload
    |
    v
AWS service/workload role
    |
    v
Existing LinkCraftor Universal Runtime trust boundary
    |
    v
Existing Universal Runtime worker
    |
    v
Existing runtime execution authorization

---

# Terraform Repository Mapping

Canonical root:

backend/infra/terraform/

Required implementation structure:

terraform/
|
+-- bootstrap/
+-- organization/
+-- modules/
|   +-- iam/
|   +-- identity_center/
|   +-- workload_identity/
|   +-- federation/
|   +-- security/
+-- environments/
|   +-- development/
|   +-- testing/
|   +-- staging/
|   +-- sandbox/
|   +-- production/
+-- shared/
+-- policies/
+-- scripts/
+-- tests/

Directory existence does not by itself certify live implementation.

---

# IAM Module Boundary

modules/iam owns reusable IAM role and policy primitives.

It may include:

- IAM roles
- Trust relationships
- Managed policy attachments
- Permission boundaries
- Session restrictions
- iam:PassRole controls

Production behavior must not be hardcoded into a generic reusable module.

---

# Terraform Plan Identity Mapping

Canonical role:

TerraformPlanRole

Purpose:

- Infrastructure discovery
- Terraform plan generation
- Read-oriented AWS access where practical
- Required Terraform state access

Planning does not authorize application.

---

# Terraform Apply Identity Mapping

Canonical role:

TerraformApplyRole

Purpose:

- Approved infrastructure mutation

Apply authority must be:

- Temporary
- Auditable
- Environment-scoped
- Account-scoped
- Approval-controlled
- Subject to SCP ceilings

Production apply authority remains separately controlled.

---

# Universal Runtime Workload Mapping

The existing Universal Runtime is reused.

Existing authoritative components include:

- ak6_operational_trust.py
- ak6_signed_execution_grants.py
- execution_authorization.py
- runtime_authorization.py
- service_to_service_trust.py
- worker_identity_validation.py
- universal_runtime_worker_service.py
- universal_runtime_worker_service_registration.py
- universal_runtime_worker_v1.py

AWS IAM does not supersede these controls.

---

# Worker Activation Boundary

This mapping does not:

- activate a worker
- provision operational worker identity
- provision the live trusted issuer
- authorize queued jobs
- change existing worker trust
- claim live authorization
- start a second worker service

Worker activation remains independently governed.

---

# Workforce Identity Boundary

AWS workforce/admin identity is distinct from:

- LinkCraftor customer identity
- service identity
- workload identity
- Universal Runtime worker identity
- TerraformApplyRole

---

# Service Identity Boundary

Each service receives only the AWS permissions required for its workload.

A generic all-services administrative role is prohibited.

---

# Cross-Environment Mapping

Development, Testing, Staging, Sandbox, and Production remain separate AWS
account boundaries.

Production credentials must not be fallback credentials for non-Production
execution.

Non-Production identities must not silently assume Production authority.

---

# Cross-Account Trust Mapping

Cross-account trust must explicitly identify:

- Source principal
- Destination role
- Account
- Environment
- Purpose
- Session restrictions
- Auditability

AWS Organizations membership alone does not authorize cross-account role
assumption.

---

# SCP Relationship

AWS Organizations SCPs remain permission ceilings.

SCPs do not grant IAM permissions.

---

# Temporary Credential Mapping

Canonical access mechanisms include:

- IAM Identity Center sessions
- STS AssumeRole
- OIDC workload federation

Static long-lived AWS access keys are not the canonical identity model.

---

# Credential Storage Boundary

AWS secret credentials must not be embedded in:

- Terraform source
- tfvars
- Python source
- PowerShell source
- Git repositories
- Runtime job payloads
- Queue messages
- Browser storage
- Architecture documents

Environment-variable names such as AWS_ACCESS_KEY_ID are not themselves secret
credentials.

Literal credential values require separate remediation.

---

# Static Credential Review Rule

Repository findings must distinguish:

1. Environment-variable reference
2. Placeholder/example
3. Test fixture
4. Actual secret value

A textual reference alone must not be classified as a leaked credential.

Secret values must never be written into architecture or verification evidence.

---

# Terraform State Boundary

Terraform state access is separate from AWS mutation authority.

Development Terraform identity must not automatically receive Production state
access.

---

# Reuse Classification

REUSE:

- Existing Universal Runtime
- Existing runtime worker
- Existing runtime trust
- Existing signed execution grants
- Existing runtime authorization
- Existing execution authorization
- Existing service-to-service trust
- Existing worker identity validation
- Existing Cloud IAM architecture
- Existing Phase 2 AWS organization architecture
- Existing Phase 3 Terraform architecture

---

# Extend Classification

EXTEND:

- Existing Universal Runtime with AWS workload identity boundary
- Existing service identity architecture with AWS roles
- Existing IAM architecture with Terraform resources
- Terraform Plan/Apply architecture with IAM roles
- Temporary credential architecture with AWS federation
- Environment boundaries with provider/account role binding
- SCP architecture with Terraform implementation

---

# Retire Classification

No existing canonical Universal Runtime component is approved for retirement.

No duplicate worker, runtime authorization engine, or parallel execution system
will be created.

---

# Missing Implementation

Still missing:

- backend/infra/terraform/
- Terraform bootstrap implementation
- Remote backend implementation
- AWS provider implementation
- Account bindings
- TerraformPlanRole
- TerraformApplyRole
- Workforce/admin AWS role implementation
- AWS service roles
- AWS workload identity
- Federation
- Privileged access implementation
- Cross-environment enforcement
- Emergency cloud access
- Live authorization evidence

---

# Implementation Order

1. Terraform implementation root
2. Bootstrap/state foundation
3. Provider/account bindings
4. Workforce/admin identity
5. Terraform Plan/Apply identities
6. Service identities
7. Workload identity integration
8. Federation/temporary credentials
9. Privileged access
10. Cross-environment enforcement
11. Emergency access
12. Live authorization tests
13. Phase 4.1.10 certification

---

# Implementation Boundary

This mapping creates no live AWS or IAM resources.

It does not create:

- AWS accounts
- IAM roles
- IAM policies
- OIDC providers
- Identity Center assignments
- Terraform state
- Runtime workers

---

# Runtime Eligibility

Not Runtime Eligible / N/A

---

# Canonical Decision

The existing Universal Runtime remains authoritative.

Terraform will implement the AWS cloud identity layer around the existing
runtime.

AWS IAM and LinkCraftor runtime identity are distinct but integrated security
layers.

No duplicate Universal Runtime implementation is permitted.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL IMPLEMENTATION MAPPING
