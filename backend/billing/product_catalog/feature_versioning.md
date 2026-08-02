# Feature Versioning

**Version:** 1.0.0
**Status:** Canonical
**Architecture Phase:** 2.1.3.8
**Last Updated:** 2026-08-01

---

# Purpose

The Feature Versioning framework defines how LinkCraftor features, entitlements, limits, mappings and availability rules are versioned, activated, deprecated and retired.

No feature definition or mapping may change without a new traceable version.

---

# Versioning Objectives

- Preserve feature history
- Prevent silent entitlement changes
- Support backward compatibility
- Support controlled releases
- Support rollback
- Preserve billing and contract traceability
- Support safe plan evolution
- Support audit and certification

---

# Versioned Artifacts

- Core Feature Registry records
- Feature Availability Matrix records
- Plan Feature Mapping records
- Batch Upload Limits
- API Feature Mapping records
- Enterprise Feature Mapping records
- OEM Feature Mapping records
- Trial feature rules
- Feature usage limits
- Contract-specific overrides
- Deprecation and retirement rules

---

# Version Format

Feature artifacts shall use Semantic Versioning:

**MAJOR.MINOR.PATCH**

- Major: breaking entitlement or feature changes
- Minor: backward-compatible additions
- Patch: non-breaking corrections

---

# Feature Version Record Requirements

Every version record shall include:

- Version Record ID
- Feature ID
- Previous Version
- New Version
- Change Type
- Change Summary
- Change Reason
- Affected Products
- Affected Plans
- Affected Services
- Entitlement Impact
- Billing Impact
- Migration Requirement
- Compatibility Status
- Effective Date
- Expiration Date, where applicable
- Rollback Version
- Approval Authority
- Change Request ID
- Certification Reference
- Created At
- Created By

---

# Version States

- Draft
- Review
- Approved
- Scheduled
- Active
- Superseded
- Deprecated
- Retired
- Rejected
- Rolled Back

---

# Effective-Date Rules

- Every approved version shall have an effective date.
- Future versions shall not activate early.
- Historical versions shall remain immutable and traceable.
- Expired versions shall not be deleted.
- Contract-specific mappings may retain older versions.
- Upgrades and downgrades shall use the version active at entitlement activation.

---

# Backward Compatibility

Every change shall be classified as:

- Fully Backward Compatible
- Conditionally Compatible
- Migration Required
- Breaking Change
- Contract Exception Required

Breaking changes require a major version, impact assessment, migration plan, rollback plan and certification.

---

# Deprecation and Retirement

- Deprecated features shall define a replacement and migration path.
- Retired features shall not be assigned to new customers.
- Retired Feature IDs shall never be reused.
- Historical billing and entitlement records shall remain preserved.
- Retirement shall not delete audit evidence.

---

# Mapping Version Rules

The following mappings shall be versioned independently:

- Feature Definition Version
- Plan Mapping Version
- API Mapping Version
- Enterprise Mapping Version
- OEM Mapping Version
- Trial Mapping Version
- Limit Configuration Version

A change to one mapping shall not silently modify another.

---

# Batch Upload Limit Versioning

| Plan | Maximum Documents Per Batch |
|---|---:|
| Starter | 10 |
| Pro | 50 |
| Business | 200 |
| Enterprise | 1,000 |
| Growth Enterprise | 2,000 |
| Scale Enterprise | 3,000 |
| Hyper Enterprise | 5,000 |

Every limit change shall record the previous limit, new limit, effective date, entitlement impact, trial impact and approval record.

---

# API, Enterprise and OEM Versioning

- API consumers shall not be moved silently to breaking versions.
- Enterprise contract overrides shall remain preserved.
- Canonical plan changes shall not overwrite contractual entitlements.
- OEM rights shall never expand automatically because of a feature-version change.

---

# Change Control

Every version change shall follow:

1. Change request
2. Impact assessment
3. Dependency assessment
4. Billing and entitlement assessment
5. Contract and security assessment
6. Approval
7. Version creation
8. Testing
9. Verification
10. Certification
11. Scheduled activation
12. Monitoring
13. Post-activation review

---

# Rollback Rules

- Every activatable version shall define a rollback target.
- Rollback shall preserve billing, entitlement and contract integrity.
- Rollback shall generate a new auditable event.
- The failed version shall remain historically traceable.

---

# Dependencies

- Product Registry
- Service Registry
- Feature Registry
- Core Feature Registry
- Feature Availability Matrix
- Plan Feature Mapping
- API Feature Mapping
- Enterprise Feature Mapping
- OEM Feature Mapping
- Billing Versioning
- Billing Change Management
- Product Lifecycle Management
- Subscription Entitlements
- Enterprise Contracts
- OEM Agreements
- Audit Infrastructure

---

# Enforcement Boundary

This document defines feature-versioning rules only.

Executable activation, migration and rollback belong to future configuration, entitlement and runtime infrastructure.

This document does not create jobs, workers, queues, migrations, entitlement changes or billing adjustments.

---

# Runtime Eligibility

**Current Component:** Feature Versioning document

**Runtime Eligible:** No

**Reason:** Canonical versioning and change-control definition only

**URRS Requirement:** Not applicable

---

# Governance Rules

- Versions shall never be changed in place after activation.
- Historical versions shall remain immutable.
- Breaking changes require a major version.
- Feature IDs shall never be reused.
- Contract rights shall not be silently altered.
- Rollbacks shall remain auditable.
- Versions shall be certified before production activation.

---

# Architecture Status

Status: Approved Feature Versioning

Implementation Status: Architecture Defined

Runtime Eligibility: Not Runtime Eligible

URRS Requirement: Not Applicable

Production Status: Not Implemented

---

End of Feature Versioning
