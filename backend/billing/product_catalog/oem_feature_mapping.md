# OEM Feature Mapping

**Version:** 1.0.0  
**Status:** Canonical  
**Architecture Phase:** 2.1.3.7  
**Last Updated:** 2026-08-01

---

# Purpose

The OEM Feature Mapping defines the canonical relationship between LinkCraftor intelligence engines, OEM agreements, embedded deployments, licensed capabilities and contract-specific OEM entitlements.

No third-party platform may embed, resell, expose or commercially use LinkCraftor technology under OEM terms unless the licensed features and rights are defined through this mapping and an approved OEM agreement.

---

# OEM Definition

OEM licensing allows an approved third-party company to embed one or more LinkCraftor engines, services or intelligence capabilities inside its own software, platform, application or commercial offering.

OEM licensing is separate from:

- Standard subscriptions
- Enterprise subscriptions
- Hyper Enterprise
- Standalone API subscriptions
- White-label reports
- White-label client portals
- Reseller rights
- Marketplace access

An Enterprise or Hyper Enterprise subscription does not automatically grant OEM rights.

---

# OEM Product Categories

OEM mappings may include:

- Internal Linking Engine
- Semantic Linking Engine
- External Authority Linking Engine
- Smart Phrase Extraction Engine
- Topic Cluster Engine
- Semantic Audit Engine
- Content Intelligence Engine
- Entity Intelligence Engine
- API Products
- SDK Products
- Embedded Runtime Services
- Private Deployment Products
- Dedicated Infrastructure Products
- White-Label Technology
- Future Intelligence Engines

---

# OEM Licensing Models

Approved OEM agreements may use one or more of the following models:

- Annual License Fee
- Monthly License Fee
- Usage-Based Licensing
- Action Unit Consumption
- API Consumption
- Per-Seat Licensing
- Per-Customer Licensing
- Per-Workspace Licensing
- Revenue Sharing
- Minimum Commitment
- Volume Commitment
- Dedicated Infrastructure Fee
- Private Deployment Fee
- Professional Services Fee
- Hybrid Licensing

---

# OEM Availability States

Each OEM feature mapping shall use one of these states:

- Licensed
- Limited
- Evaluation Only
- Contract Based
- Contract Only
- Usage Restricted
- Deployment Restricted
- Region Restricted
- Customer Restricted
- Workspace Restricted
- Suspended
- Unavailable
- Deprecated
- Retired

---

# OEM Mapping Requirements

Every OEM feature mapping shall include:

- Mapping ID
- OEM Customer ID
- Contract ID
- Product ID
- Feature ID
- Service ID
- Engine ID
- API Product ID, where applicable
- Deployment ID
- License Type
- Availability State
- Permitted Use
- Prohibited Use
- Distribution Rights
- Embedding Rights
- White-Label Rights
- Reseller Rights
- API Rights
- SDK Rights
- Source-Code Rights
- Modification Rights
- Sub-Licensing Rights
- Geographic Scope
- Customer Scope
- Workspace Scope
- Usage Limit
- Action Unit Limit
- API Rate Limit
- Infrastructure Assignment
- Support Level
- SLA Reference
- Revenue-Share Terms
- Minimum Commitment
- Effective Date
- Expiration Date
- Renewal Terms
- Version
- Approval Authority
- Status

---

# Default OEM Rights

Unless an approved OEM agreement states otherwise:

| Right | Default Status |
|---|---|
| Embed LinkCraftor engines | Unavailable |
| Rebrand LinkCraftor engines | Unavailable |
| Resell LinkCraftor technology | Unavailable |
| Sub-license LinkCraftor technology | Unavailable |
| Modify LinkCraftor engines | Unavailable |
| Access source code | Unavailable |
| Deploy privately | Contract Only |
| Use dedicated infrastructure | Contract Only |
| Use approved APIs | Contract Only |
| Use approved SDKs | Contract Only |
| White-label API responses | Contract Only |
| Use LinkCraftor trademarks | Unavailable |
| Claim ownership of LinkCraftor technology | Prohibited |

All rights must be granted explicitly.

---

# OEM Contract Rules

- Every OEM mapping shall reference an approved OEM agreement.
- OEM rights shall never be inferred from a subscription plan.
- Hyper Enterprise shall not automatically grant OEM rights.
- OEM agreements shall define exactly which engines and features are licensed.
- Rights not expressly granted shall remain prohibited.
- OEM customers shall not receive source-code access unless explicitly approved.
- OEM customers shall not modify licensed engines unless explicitly approved.
- OEM customers shall not sublicense LinkCraftor technology unless explicitly approved.
- OEM deployments shall preserve customer and workspace isolation.
- OEM usage shall remain metered and auditable.
- Contract limits shall be enforceable through entitlement and runtime infrastructure.
- Expired or suspended agreements shall disable OEM access.
- Historical mappings shall never be deleted.
- Contract amendments shall create new versioned records.
- OEM pricing shall remain separate from enterprise subscription pricing.

---

# OEM API Rules

- OEM API access requires an approved OEM agreement.
- OEM API access shall not be granted through normal Pro-to-Hyper plan entitlement alone.
- API Product IDs shall reference the canonical API Product Registry.
- OEM API consumption may use Action Units, custom rate cards or contract pricing.
- OEM API limits may be customer-specific.
- OEM API credentials shall be isolated, revocable and auditable.
- API authentication and authorization shall remain mandatory.
- Workspace and tenant isolation shall not be bypassed.
- API resale rights shall require explicit contractual approval.
- API white-label rights shall require explicit contractual approval.

---

# OEM Deployment Models

Approved OEM deployment models may include:

- Shared LinkCraftor Cloud
- Dedicated Tenant
- Dedicated Infrastructure
- Private Cloud Deployment
- Customer-Controlled Cloud Deployment
- Regional Deployment
- On-Premises Deployment
- Hybrid Deployment

Each deployment model shall define:

- Infrastructure ownership
- Operational responsibility
- Security responsibility
- Data residency
- Backup responsibility
- Recovery responsibility
- Monitoring responsibility
- Support responsibility
- Upgrade responsibility
- Billing responsibility

---

# OEM Billing Rules

- OEM pricing shall use custom contract terms.
- OEM pricing shall not be inherited from Hyper Enterprise.
- License fees may be charged monthly, annually or multi-year.
- Usage charges may be billed separately.
- Dedicated infrastructure may be billed separately.
- Private deployment may be billed separately.
- Professional services may be billed separately.
- Revenue sharing may be included.
- Minimum annual commitments may be required.
- Overage pricing may be defined contractually.
- Taxes, currency and regional billing shall follow approved billing rules.
- OEM invoices shall reference the applicable contract and licensed products.

---

# OEM Compliance and Protection

OEM agreements and mappings shall protect:

- LinkCraftor intellectual property
- Proprietary algorithms
- Proprietary datasets
- Model weights
- Semantic graphs
- Entity graphs
- Source code
- Internal architecture
- Trade secrets
- Customer data
- Workspace data
- Usage data
- Billing data
- Security controls

Unauthorized copying, reverse engineering, redistribution, sublicensing or disclosure shall be prohibited unless explicitly permitted by contract.

---

# Dependencies

This mapping depends on:

- Product Registry
- Service Registry
- Feature Registry
- Core Feature Registry
- Feature Availability Matrix
- Plan Feature Mapping
- API Feature Mapping
- Enterprise Feature Mapping
- OEM Product Registry
- OEM Pricing
- Enterprise Contracts
- Subscription Entitlements
- Action Unit Accounting
- Usage Metering
- API Authentication
- API Authorization
- Workspace Isolation
- Infrastructure Assignment
- Audit Infrastructure

The OEM Product Registry is scheduled for Phase 2.1.6 and shall provide the canonical OEM Product IDs referenced by this mapping.

---

# Enforcement Boundary

This document defines OEM licensing rights, availability, restrictions and mapping rules only.

Executable enforcement belongs to:

- OEM Contract Validation
- OEM Entitlement Validation
- API Authentication
- API Authorization
- License Enforcement
- Usage Metering
- Action Unit Accounting
- Infrastructure Assignment
- Deployment Control
- Billing Enforcement
- Suspension and Revocation Control

This definition document does not:

- Activate OEM contracts
- Grant licensing rights directly
- Issue API credentials
- Deploy infrastructure
- Start runtime jobs
- Create workers
- Create queues
- Consume Action Units
- Process invoices
- Suspend licenses
- Revoke access
- Perform runtime authorization

---

# Runtime Eligibility

**Current Component:** OEM Feature Mapping document  
**Runtime Eligible:** No  
**Reason:** Canonical architecture, licensing and entitlement-definition document only  
**URRS Requirement:** Not applicable

Executable OEM contract, entitlement and license enforcement shall be scanned separately when the OEM Product, Contract, API and Runtime infrastructure is ready.

---

# Governance Rules

- OEM mappings shall be configuration-driven.
- OEM rights shall never be hard-coded.
- Every OEM mapping shall reference canonical identifiers.
- Every mapping shall reference an approved contract.
- Licensing rights shall use least privilege.
- Contract changes shall be version-controlled.
- Changes shall require formal approval.
- All activity shall be auditable.
- Historical records shall remain traceable.
- Customer, tenant and workspace isolation shall be preserved.
- OEM licensing shall remain separate from enterprise subscriptions.
- LinkCraftor intellectual property shall remain protected.
- Rights not expressly granted shall remain prohibited.

---

# Architecture Status

Status: Approved OEM Feature Mapping

Implementation Status: Architecture Defined

Runtime Eligibility: Not Runtime Eligible

URRS Requirement: Not Applicable

Production Status: Not Implemented

---

End of OEM Feature Mapping
