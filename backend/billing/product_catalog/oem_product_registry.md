# OEM Product Registry

**Version:** 1.0.0

**Status:** Canonical

**Architecture Phase:** 2.1.6

**Last Updated:** 2026-08-01

---

# Purpose

The OEM Product Registry is the canonical registry for every LinkCraftor product, engine, API, SDK, deployment package or technology capability offered under an OEM agreement.

No LinkCraftor technology may be embedded, licensed, rebranded, distributed, privately deployed or commercially exposed as an OEM product unless it is registered through this registry and governed by an approved OEM agreement.

---

# Launch Status

OEM products are part of the future monetization roadmap.

They are not included in the initial LinkCraftor launch.

This registry defines the canonical architecture in advance and does not activate OEM sales, licensing or production availability.

---

# Registry Objectives

- Maintain one canonical OEM product inventory
- Assign unique OEM Product IDs
- Define licensable technology boundaries
- Separate OEM products from subscription plans
- Separate OEM products from Hyper Enterprise
- Support OEM contract mapping
- Support feature and service mapping
- Support deployment-model mapping
- Support licensing and usage controls
- Support pricing integration
- Support versioning and lifecycle management
- Protect LinkCraftor intellectual property
- Maintain complete auditability

---

# OEM Product Categories

The registry shall support:

- Intelligence Engine Products
- API Products
- SDK Products
- Embedded Runtime Products
- Private Deployment Products
- Dedicated Infrastructure Products
- White-Label Technology Products
- Data and Knowledge Products
- Enterprise Integration Products
- Future OEM Products

---

# Initial OEM Product Candidates

The following categories may become registered OEM products after formal review and approval:

- Internal Linking Engine
- Semantic Linking Engine
- External Authority Linking Engine
- Smart Phrase Extraction Engine
- Topic Cluster Engine
- Semantic Audit Engine
- Content Intelligence Engine
- Entity Intelligence Engine
- Approved API Bundles
- Approved SDK Bundles
- Embedded Runtime Services
- Dedicated Tenant Deployment
- Private Cloud Deployment
- Customer-Controlled Cloud Deployment
- On-Premises Deployment
- White-Label Technology Package

These are architecture candidates only and are not automatically approved for commercial licensing.

---

# OEM Product Record Requirements

Every registered OEM product shall include:

- OEM Product ID
- OEM Product Name
- Product Category
- Product Description
- Product Owner
- Associated Product ID
- Associated Service IDs
- Associated Feature IDs
- Associated Engine IDs
- Associated API Product IDs, where applicable
- Associated SDK IDs, where applicable
- License Model
- Permitted Deployment Models
- Permitted Use
- Prohibited Use
- Embedding Rights
- Distribution Rights
- White-Label Rights
- Reseller Rights
- Sub-Licensing Rights
- Source-Code Rights
- Modification Rights
- Geographic Availability
- Customer Scope
- Workspace Scope
- Usage Limits
- Action Unit Rules
- API Rules
- Infrastructure Requirements
- Security Requirements
- Support Level
- SLA Eligibility
- Pricing Association
- Contract Requirement
- Product Version
- Product Status
- Effective Date
- Retirement Date, where applicable
- Approval Authority

---

# OEM Product Identity Rules

- Every OEM product shall have one globally unique OEM Product ID.
- OEM Product IDs shall never be reused.
- OEM products shall reference canonical Product, Service and Feature IDs.
- OEM products shall not use subscription-plan IDs as OEM Product IDs.
- OEM product identity shall remain separate from enterprise plan identity.
- A commercial agreement shall reference the exact OEM Product ID and version.
- Product aliases shall not replace canonical identifiers.

---

# OEM Licensing Models

Registered OEM products may support one or more approved licensing models:

- Monthly License
- Annual License
- Multi-Year License
- Usage-Based License
- Action Unit License
- API Consumption License
- Per-Seat License
- Per-Customer License
- Per-Workspace License
- Per-Deployment License
- Revenue Share
- Minimum Commitment
- Volume Commitment
- Dedicated Infrastructure Fee
- Private Deployment Fee
- Professional Services Fee
- Hybrid License

The applicable model shall be defined through OEM Pricing and the approved OEM agreement.

---

# OEM Deployment Models

An OEM product may be approved for one or more deployment models:

- Shared LinkCraftor Cloud
- Dedicated Tenant
- Dedicated Infrastructure
- Private Cloud Deployment
- Customer-Controlled Cloud Deployment
- Regional Deployment
- On-Premises Deployment
- Hybrid Deployment

Deployment eligibility shall be explicitly recorded for each OEM product.

No deployment model shall be inferred automatically from an enterprise subscription.

---

# Default OEM Rights

Unless explicitly approved and registered:

| Right | Default Status |
|---|---|
| Embed LinkCraftor technology | Unavailable |
| Rebrand LinkCraftor technology | Unavailable |
| Resell LinkCraftor technology | Unavailable |
| Sub-license LinkCraftor technology | Unavailable |
| Modify LinkCraftor technology | Unavailable |
| Access source code | Unavailable |
| Access model weights | Unavailable |
| Access proprietary datasets | Unavailable |
| Private deployment | Contract Only |
| Dedicated infrastructure | Contract Only |
| API use | Contract Only |
| SDK use | Contract Only |
| White-label use | Contract Only |
| Trademark use | Unavailable |
| Claim ownership | Prohibited |

Rights not expressly granted shall remain prohibited.

---

# OEM Product Lifecycle

Each OEM product shall use one of the following lifecycle states:

- Proposed
- Draft
- Review
- Approved
- Contract Ready
- Active
- Restricted
- Suspended
- Deprecated
- Retired
- Rejected

Only products in the Active state may be commercially licensed.

---

# Lifecycle Rules

- Proposed products shall not be sold.
- Draft products shall remain internal.
- Review products shall require architecture, security, legal and financial assessment.
- Approved products shall still require pricing and contract readiness.
- Contract Ready products may be offered only through approved sales processes.
- Active products may be licensed through approved OEM agreements.
- Suspended products shall not accept new activations.
- Deprecated products shall define a migration path.
- Retired products shall not be assigned to new agreements.
- Historical product records shall never be deleted.

---

# OEM Contract Mapping

Every active OEM product shall be mapped to an approved OEM agreement before customer access is activated.

The contract mapping shall identify:

- OEM Customer ID
- OEM Product ID
- OEM Product Version
- Contract ID
- Licensed Features
- Licensed Services
- Licensed Engines
- Permitted Deployment
- Permitted Use
- Prohibited Use
- Usage Limits
- Action Unit Terms
- API Terms
- Infrastructure Assignment
- Support Level
- SLA
- Pricing Terms
- Revenue Share, where applicable
- Effective Date
- Expiration Date
- Renewal Terms
- Suspension Conditions
- Termination Conditions

---

# OEM Product and Enterprise Separation

- Enterprise subscriptions do not automatically include OEM products.
- Growth Enterprise does not automatically include OEM products.
- Scale Enterprise does not automatically include OEM products.
- Hyper Enterprise does not automatically include OEM products.
- White-label reporting does not automatically grant OEM rights.
- Reseller rights do not automatically grant OEM rights.
- API access does not automatically grant embedding or redistribution rights.
- OEM licensing shall remain a separate product, contract and pricing domain.

---

# OEM Product and API Separation

- An API Product ID is not automatically an OEM Product ID.
- Standalone API access does not grant redistribution rights.
- OEM API products require explicit OEM registration.
- API resale requires explicit contractual permission.
- API white-label rights require explicit contractual permission.
- API authentication, authorization and metering remain mandatory.
- OEM API consumption may use custom pricing or Action Unit terms.
- OEM API credentials shall remain isolated and revocable.

---

# OEM Product and Marketplace Separation

- Marketplace listing does not grant OEM licensing rights.
- Marketplace sellers may not redistribute LinkCraftor technology without an OEM agreement.
- OEM products shall not be published in the Marketplace automatically.
- Any marketplace distribution of an OEM product requires separate approval.
- Marketplace commissions and OEM licensing fees shall remain separate.

---

# Intellectual Property Protection

Every OEM product shall preserve LinkCraftor ownership and protection of:

- Source code
- Proprietary algorithms
- Intelligence engines
- Model weights
- Proprietary datasets
- Semantic graphs
- Entity graphs
- Knowledge graphs
- Internal architecture
- Runtime infrastructure
- Security controls
- Trade secrets
- Product documentation
- Customer data
- Workspace data
- Usage data
- Billing data

Unauthorized copying, reverse engineering, disclosure, redistribution, modification or sublicensing shall be prohibited unless explicitly allowed by contract.

---

# Pricing Association

Every OEM product shall reference approved OEM Pricing.

OEM pricing may include:

- License fee
- Minimum annual commitment
- Usage pricing
- Action Unit pricing
- API pricing
- Deployment fee
- Dedicated infrastructure fee
- Private deployment fee
- Support fee
- Professional services fee
- Revenue share
- Overage pricing
- Renewal pricing
- Termination charges, where applicable

OEM pricing shall not be inherited automatically from subscription or enterprise pricing.

---

# Versioning Rules

- Every OEM product shall have a version.
- Breaking changes require a major version.
- Backward-compatible additions require a minor version.
- Non-breaking corrections require a patch version.
- Active contract versions shall remain traceable.
- Product changes shall not silently expand customer rights.
- Rights and restrictions shall be versioned independently where necessary.
- Deprecated versions shall remain available for contract and audit history.
- Retired OEM Product IDs shall never be reused.

---

# Dependencies

This registry depends on:

- Product Registry
- Service Registry
- Feature Registry
- Core Feature Registry
- Feature Availability Matrix
- Plan Feature Mapping
- API Feature Mapping
- Enterprise Feature Mapping
- OEM Feature Mapping
- API Product Registry
- Marketplace Product Registry
- Feature Registry Certification
- OEM Pricing
- Enterprise Contracts
- OEM Agreements
- Subscription Entitlements
- Action Unit Accounting
- Usage Metering
- API Authentication
- API Authorization
- Infrastructure Assignment
- Workspace Isolation
- Audit Infrastructure

---

# Enforcement Boundary

This document defines the canonical OEM product inventory and product-governance rules only.

Executable enforcement belongs to:

- OEM Contract Validation
- OEM Product Entitlement Validation
- License Enforcement
- API Authentication
- API Authorization
- Usage Metering
- Action Unit Accounting
- Deployment Control
- Infrastructure Assignment
- Billing Enforcement
- Suspension and Revocation Control
- Audit Infrastructure

This registry does not:

- activate OEM products
- create OEM contracts
- grant licenses
- issue credentials
- deploy infrastructure
- process API requests
- consume Action Units
- create runtime jobs
- start workers
- create queues
- process invoices
- suspend or revoke access

---

# Runtime Eligibility

Current Component:

OEM Product Registry document

Runtime Eligible:

No

Reason:

This is a canonical product-registry and licensing-definition document.

Current URRS Requirement:

Not Applicable

Executable OEM product provisioning, contract enforcement, entitlement validation and deployment services shall undergo separate URRS assessment before implementation.

---

# Governance Rules

- Every OEM product shall have a unique OEM Product ID.
- OEM products shall reference canonical products, services and features.
- Every active OEM product shall require an approved OEM agreement.
- OEM products shall remain separate from subscription plans.
- OEM products shall remain separate from Hyper Enterprise.
- OEM rights shall never be inferred.
- Pricing shall reference OEM Pricing.
- Rights and restrictions shall be configuration-driven.
- Product changes shall be version-controlled.
- Historical records shall remain immutable and traceable.
- Intellectual property protections shall remain mandatory.
- Customer, tenant and workspace isolation shall be preserved.
- Rights not expressly granted shall remain prohibited.

---

# Architecture Status

Status: Approved OEM Product Registry

Implementation Status: Architecture Defined

Runtime Eligibility: Not Runtime Eligible

URRS Requirement: Not Applicable

Launch Status: Future Monetization Roadmap

Production Status: Not Implemented

---

End of OEM Product Registry
