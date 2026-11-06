# LinkCraftor Terraform Environment Configuration Model

Version: 1.0
Status: Canonical
Phase: Infrastructure as Code
Section: 3.5 Environment Configuration Model
Cloud Provider: Amazon Web Services
IaC Technology: Terraform
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical Terraform configuration model for
LinkCraftor environments.

Environment configuration must remain explicit, reviewable, validated, and
isolated.

---

# Core Rule

Terraform environment selection must be explicit.

Unknown configuration must not default to Production.

---

# Canonical Environments

Canonical application environments are:

- development
- testing
- staging
- sandbox
- production

Supporting infrastructure accounts remain separately configured.

---

# Environment to Account Mapping

Canonical environment mappings are:

development
→ DEVELOPMENT

testing
→ TESTING

staging
→ STAGING

sandbox
→ SANDBOX

production
→ PRODUCTION

---

# Supporting Account Configuration

The following accounts are not ordinary application environments:

- LINKCRAFTOR-MANAGEMENT
- SECURITY
- LOG-ARCHIVE
- NETWORK
- SHARED-SERVICES
- DEPLOYMENT

Their Terraform compositions must be separately classified.

---

# Configuration Sources

Environment configuration may be composed from approved inputs such as:

- Terraform variables
- Locals
- Non-secret tfvars
- Environment metadata
- CI/CD environment configuration
- Account registry data
- Approved module inputs

No single source may silently override security-critical identity.

---

# Environment Metadata

Configuration should identify:

- Environment name
- AWS account ID
- Canonical account name
- Allowed regions
- Primary region
- DR region where applicable
- Environment class
- Production flag
- State key
- Provider alias
- Terraform role
- Tags

---

# Stable Environment Identity

Environment identity must not depend solely on a directory name.

Terraform should validate environment metadata against target account and
provider identity.

---

# Production Flag

Production state must not be inferred casually.

Where a Production flag exists, it must be derived from canonical environment
configuration.

A user-provided arbitrary boolean must not independently create Production
authority.

---

# Configuration Layering

Configuration may use layered composition.

A safe conceptual order may include:

1. Global defaults
2. Account-class configuration
3. Environment configuration
4. Region configuration
5. Workload/module configuration

Later layers must not bypass security invariants.

---

# Global Defaults

Global defaults may define safe non-sensitive values.

Global defaults must not include:

- Production credentials
- Production secrets
- Production account authority
- Unsafe destructive settings

---

# Environment Overrides

Environment overrides may modify approved workload settings.

Overrides must not bypass:

- Account isolation
- Region controls
- IAM restrictions
- State boundaries
- Production approval requirements

---

# Region Configuration

Region configuration must be explicit.

Canonical regions are:

- eu-west-1
- us-east-1
- af-south-1

Environment configuration must identify which regions are actually authorized.

---

# Production Region Configuration

Production normal-serving region:

- eu-west-1

Production DR region:

- us-east-1

Future region:

- af-south-1

The future region must not become active merely by being listed.

---

# Environment Variable Files

If tfvars files are used, they must contain non-secret configuration only.

Secrets must not be committed in tfvars.

---

# Secret Configuration

Secrets must come from approved external secret mechanisms.

Environment config must reference secret locations or identifiers rather than
hardcode secret material.

---

# Tagging Configuration

Environment metadata should drive approved infrastructure tags.

Potential tags include:

- Environment
- AccountClass
- RegionRole
- ManagedBy
- Application
- Owner
- CostCenter

Tags support governance but are not the only security boundary.

---

# Naming Configuration

Resource naming should derive from canonical environment and regional metadata.

Naming must remain deterministic where practical.

Naming must not be the sole authority for account or environment identity.

---

# Production Configuration Isolation

Production configuration must be stored and loaded separately from
non-production configuration.

Development workflows must not automatically load Production variable files.

---

# Sandbox Configuration

Sandbox configuration should support experimentation while preserving:

- Cost controls
- Region restrictions
- No Production credentials
- No Production data
- No Production trust

---

# Staging Configuration

Staging should approximate Production configuration where useful.

It must still maintain separate:

- Account
- Credentials
- Secrets
- State
- Workload identity
- Data

---

# Testing Configuration

Testing configuration may enable test-specific resources.

Test configuration must not reuse unrestricted Production authority.

---

# Development Configuration

Development configuration should support engineering workflows without
requiring Production permissions.

---

# Configuration Validation

Environment configuration must be validated before plan or apply.

Validation should detect:

- Unknown environment
- Unknown account
- Wrong account binding
- Unauthorized region
- Invalid Production flag
- Wrong backend state
- Invalid state key
- Missing required metadata

---

# Account ID Validation

Once AWS accounts exist, configuration must bind canonical account names to
actual AWS Account IDs.

Account IDs should be maintained in an approved canonical registry or
configuration source.

---

# RegionRole Validation

Canonical RegionRole values are:

- primary
- disaster-recovery
- future

The value secondary is prohibited.

---

# State Key Binding

Environment configuration must identify or derive the correct Terraform state
boundary.

Production configuration must never point to Development state.

---

# Provider Binding

Environment configuration must identify the intended provider alias or provider
configuration.

Provider binding and account validation must agree.

---

# Terraform Role Binding

Environment configuration must identify the approved Terraform execution role
where applicable.

Production must use Production-authorized Terraform authority.

---

# CI/CD Environment Binding

CI/CD environment selection must map to the same canonical environment model.

Pipeline names alone must not be trusted without account and role validation.

---

# Immutable Security Invariants

Environment configuration must never override core invariants such as:

- Production separate account
- Production separate state
- Production separate credentials
- Approved regions
- Explicit cross-account trust
- No hidden Production fallback

---

# Configuration Drift

If configuration files differ from certified architecture, the discrepancy must
be treated as architecture/configuration drift.

Terraform must not silently accept the conflict.

---

# Fail-Closed Requirement

Environment configuration must fail closed when:

- Environment is missing
- Environment is unknown
- Account mapping is missing
- Account mapping is incorrect
- Region is unauthorized
- State binding is ambiguous
- Production configuration is incomplete
- Required role binding is absent

---

# Implementation Boundary

This section defines configuration architecture only.

It does not yet:

- Create tfvars files
- Create live account mappings
- Configure AWS providers
- Configure CI/CD variables
- Configure Production credentials
- Run Terraform
- Change AWS resources

---

# Runtime Eligibility

Runtime Eligibility:

Not Runtime Eligible / N/A

---

# Prohibited Practices

The following are prohibited:

- Unknown environment defaulting to Production
- Production selected only through arbitrary boolean input
- Production config automatically loaded by Development
- Secrets stored in committed tfvars
- Environment inferred only from directory name
- Account identity inferred only from account display name
- Production state path reused by lower environments
- RegionRole value secondary
- CI/CD environment name treated as sufficient authorization
- Environment config overriding security invariants

---

# Canonical Decision Summary

LinkCraftor Terraform environment configuration must bind environment, account,
region, state, provider, and Terraform role explicitly.

Production configuration remains isolated and independently validated.

Unknown or conflicting configuration must fail closed.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
