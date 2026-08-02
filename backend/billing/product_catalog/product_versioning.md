# Product Versioning

**Version:** 1.0.0

**Status:** Canonical

**Architecture Phase:** 2.1.7

**Last Updated:** 2026-08-01

---

# Purpose

The Product Versioning framework defines how LinkCraftor products, product records, product mappings, commercial terms and lifecycle changes are versioned and preserved.

No registered product may be changed in place after activation.

Every material product change shall create a new traceable product version.

---

# Versioning Objectives

- Preserve complete product history
- Prevent silent product-definition changes
- Protect customer entitlements
- Protect enterprise and OEM contract rights
- Support backward compatibility
- Support controlled product releases
- Support safe migrations
- Support rollback
- Preserve billing reproducibility
- Maintain auditability
- Support product retirement
- Prevent Product ID reuse

---

# Versioned Product Types

Product versioning applies to:

- Subscription Plans
- API Products
- Marketplace Products
- OEM Products
- Add-On Products
- Professional Services Products
- Training Products
- Usage Products
- Top-Up Products
- Enterprise Products
- Future Products

---

# Versioned Product Artifacts

The following artifacts shall be independently versioned:

- Product definition
- Product name
- Product category
- Product description
- Billing model
- Pricing association
- Feature mapping
- Service mapping
- Plan mapping
- Availability
- Geographic availability
- Currency availability
- Trial eligibility
- Usage limits
- Batch upload limits
- API eligibility
- Enterprise eligibility
- OEM eligibility
- Marketplace eligibility
- Contract requirements
- Lifecycle status
- Effective date
- Retirement date

A change to one artifact shall not silently modify unrelated product artifacts.

---

# Version Format

Product versions shall use Semantic Versioning:

**MAJOR.MINOR.PATCH**

Examples:

- 1.0.0
- 1.1.0
- 1.1.1
- 2.0.0

---

# Major Version Rules

A major version increment is required when a change:

- Removes a product capability
- Breaks an existing entitlement
- Changes product identity
- Replaces the billing model
- Requires customer migration
- Changes contract interpretation
- Removes plan availability
- Makes incompatible limit changes
- Replaces a product architecture
- Changes API contracts incompatibly
- Changes OEM licensing boundaries incompatibly

Example:

**1.4.2 to 2.0.0**

---

# Minor Version Rules

A minor version increment is required when a change:

- Adds backward-compatible capabilities
- Adds a new feature mapping
- Adds a new service mapping
- Adds new regional availability
- Adds new currency support
- Adds optional entitlements
- Adds compatible product metadata
- Expands availability without breaking existing customers
- Adds a new compatible API version
- Adds an approved deployment option

Example:

**1.4.2 to 1.5.0**

---

# Patch Version Rules

A patch version increment is required when a change:

- Corrects product metadata
- Fixes documentation
- Corrects a non-breaking configuration defect
- Repairs a validation rule without changing intended access
- Corrects inaccurate descriptions
- Adds audit clarification
- Fixes non-breaking references

Example:

**1.4.2 to 1.4.3**

---

# Product Version Record Requirements

Every product version record shall include:

- Product Version Record ID
- Product ID
- Product Name
- Product Category
- Previous Version
- New Version
- Change Type
- Change Summary
- Change Reason
- Affected Services
- Affected Features
- Affected Plans
- Affected APIs
- Affected Marketplace Listings
- Affected Enterprise Contracts
- Affected OEM Agreements
- Pricing Impact
- Billing Impact
- Entitlement Impact
- Contract Impact
- Migration Requirement
- Backward Compatibility Status
- Effective Date
- Expiration Date, where applicable
- Activation Status
- Rollback Version
- Approval Authority
- Change Request ID
- Certification Reference
- Created At
- Created By

---

# Product Version States

Every product version shall use one of these states:

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

Only an approved or scheduled version may become active.

---

# Effective-Date Rules

- Every approved product version shall have an effective date.
- Future product versions shall not activate before the effective date.
- Historical versions shall remain immutable and traceable.
- Expired product versions shall not be deleted.
- Only one default active version may exist unless parallel compatibility is approved.
- Contract-specific customers may remain on older versions where contractually required.
- New subscriptions shall use the active eligible version.
- Product upgrades shall use the active version at entitlement activation.
- Product downgrades shall use the version active at the effective downgrade time.

---

# Product Identity Rules

- Product IDs shall remain permanent.
- Product IDs shall never be reused.
- A product version change shall not create a new Product ID unless the product identity materially changes.
- A materially different commercial product shall receive a new Product ID.
- Product aliases shall never replace canonical Product IDs.
- Historical records shall reference the exact Product ID and version used.
- Subscription, API, Marketplace and OEM Product IDs shall remain separate.

---

# Backward Compatibility Classification

Every product change shall be classified as:

- Fully Backward Compatible
- Conditionally Compatible
- Migration Required
- Breaking Change
- Contract Exception Required
- Regulatory Exception Required

Breaking changes shall require:

- Major version increment
- Impact assessment
- Migration plan
- Rollback plan
- Billing reconciliation plan
- Entitlement review
- Contract review
- Customer communication, where applicable
- Certification before activation

---

# Subscription Product Versioning

Subscription product versions shall preserve:

- Plan identity
- Monthly price association
- Annual price association
- Trial eligibility
- Included document allowance
- Included Action Units
- Batch upload limit
- Feature availability
- API eligibility
- Team entitlement
- Enterprise entitlement
- Upgrade rules
- Downgrade rules

A new subscription version shall not silently alter an active customer's contractual rights.

---

# API Product Versioning

API product versions shall preserve:

- API Product ID
- API product name
- Endpoint group
- Request contract
- Response contract
- Authentication method
- Authorization policy
- API access fee
- Action Unit cost
- Rate limit
- Usage limit
- Deprecation date
- Retirement date
- Compatibility status

API customers shall not be silently migrated to breaking versions.

---

# Marketplace Product Versioning

Marketplace product versions shall preserve:

- Marketplace Product ID
- Seller ID
- Publisher
- Listing version
- Pricing model
- Commission model
- Revenue-share model
- Feature mapping
- Entitlement mapping
- Approval status
- Publication status
- Effective date
- Retirement date

Marketplace version changes shall not silently change seller or buyer financial terms.

---

# OEM Product Versioning

OEM product versions shall preserve:

- OEM Product ID
- Licensed engines
- Licensed services
- Licensed features
- Permitted use
- Prohibited use
- Embedding rights
- Distribution rights
- White-label rights
- Reseller rights
- Source-code rights
- Modification rights
- Deployment rights
- Geographic scope
- Usage limits
- Contract association
- Effective date
- Renewal terms

OEM product changes shall never expand licensing rights automatically.

---

# Pricing Association Versioning

Product definitions and pricing records shall remain independently versioned.

A product version shall reference:

- Pricing Version ID
- Currency Version
- Regional Pricing Version
- Promotional Pricing Version, where applicable
- Enterprise Pricing Version, where applicable
- OEM Pricing Version, where applicable
- Marketplace Pricing Version, where applicable
- Effective Date

Changing pricing shall not overwrite the historical product version used for prior billing.

---

# Product Deprecation Rules

A product may enter deprecation when:

- It is being replaced
- It is no longer commercially supported
- It creates security or compliance risk
- It conflicts with a newer architecture
- It is no longer operationally viable
- It is contractually retired
- It is no longer strategically supported

Every product deprecation record shall include:

- Deprecation date
- Replacement product
- Migration path
- Affected customers
- Affected contracts
- Affected integrations
- Support period
- Final retirement date
- Exceptions
- Rollback availability

---

# Product Retirement Rules

- Retired products shall not be sold to new customers.
- Retired products shall not accept new subscriptions.
- Retired API products shall not accept new registrations.
- Retired Marketplace products shall not accept new purchases.
- Retired OEM products shall not be assigned to new agreements.
- Existing customers may remain temporarily only through approved migration or contract exceptions.
- Retired Product IDs shall never be reused.
- Historical billing and entitlement records shall remain preserved.
- Retirement shall not delete audit evidence.
- Replacement products shall receive their own canonical identity and version.

---

# Migration Rules

Every migration-required product version shall define:

- Source Product ID
- Source Product Version
- Target Product ID
- Target Product Version
- Eligible customers
- Excluded customers
- Entitlement transformation
- Pricing transformation
- Billing reconciliation
- Contract handling
- Data migration requirements
- Effective date
- Rollback conditions
- Customer communication
- Verification requirements
- Certification requirements

No migration shall be executed solely from this document.

---

# Change Control

Every product-version change shall follow:

1. Change request
2. Product impact assessment
3. Feature impact assessment
4. Service impact assessment
5. Pricing assessment
6. Billing assessment
7. Entitlement assessment
8. Contract assessment
9. Security and compliance assessment
10. Approval
11. Version creation
12. Testing
13. Verification
14. Certification
15. Scheduled activation
16. Monitoring
17. Post-activation review

---

# Rollback Rules

Every activatable product version shall define:

- Rollback eligibility
- Rollback target version
- Rollback conditions
- Product compatibility
- Feature compatibility
- Service compatibility
- Pricing compatibility
- Billing reconciliation
- Entitlement compatibility
- Contract compatibility
- Data compatibility
- Audit evidence requirements

Rollback shall generate a new auditable event.

Rollback shall not delete or overwrite the failed product version.

---

# Dependencies

This framework depends on:

- Product Registry
- Service Registry
- Feature Registry
- Feature Versioning
- API Product Registry
- Marketplace Product Registry
- OEM Product Registry
- Billing Versioning
- Billing Change Management
- Product Lifecycle Management
- Pricing Engine
- Subscription Entitlements
- Enterprise Contracts
- OEM Agreements
- Marketplace Agreements
- Audit Infrastructure

---

# Enforcement Boundary

This document defines product-versioning rules only.

Executable enforcement belongs to:

- Product Configuration Loader
- Product Version Activation Control
- Subscription Entitlement Infrastructure
- Product Migration Infrastructure
- API Version Routing
- Marketplace Listing Control
- OEM Contract Validation
- Rollback Control
- Billing Reconciliation
- Audit Infrastructure

This definition document does not:

- activate product versions
- migrate customers
- alter subscriptions
- change pricing directly
- modify entitlements
- route API traffic
- create runtime jobs
- start workers
- create queues
- process rollback
- process billing adjustments

---

# Runtime Eligibility

Current Component:

Product Versioning document

Runtime Eligible:

No

Reason:

This is a canonical versioning, governance and change-control definition.

Current URRS Requirement:

Not Applicable

Executable product activation, migration, rollback and reconciliation services shall undergo separate URRS assessment when their dependent runtime and product infrastructure are ready.

---

# Governance Rules

- Every product shall have a version.
- Active product versions shall never be modified in place.
- Historical versions shall remain immutable.
- Breaking changes shall require a major version.
- Product IDs shall never be reused.
- Contract rights shall not be silently altered.
- Pricing history shall remain reproducible.
- OEM rights shall not expand automatically.
- Marketplace financial terms shall not change silently.
- Rollbacks shall remain auditable.
- Product versions shall be certified before production activation.
- Customer, tenant and workspace isolation shall remain preserved.

---

# Architecture Status

Status: Approved Product Versioning

Implementation Status: Architecture Defined

Runtime Eligibility: Not Runtime Eligible

URRS Requirement: Not Applicable

Production Status: Not Implemented

---

End of Product Versioning
