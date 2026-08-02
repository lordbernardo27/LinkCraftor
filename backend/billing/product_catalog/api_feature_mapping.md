# API Feature Mapping

**Version:** 1.0.0  
**Status:** Canonical  
**Architecture Phase:** 2.1.3.5  
**Last Updated:** 2026-08-01

---

# Purpose

The API Feature Mapping defines the canonical relationship between LinkCraftor features, subscription plans, standalone API products and API access entitlements.

No LinkCraftor feature may be exposed through an API unless its API availability is registered through this mapping.

---

# API Access Eligibility

API access is available beginning with the Pro plan.

| Plan | API Access |
|---|---|
| Starter | Unavailable |
| Pro | Available |
| Business | Available |
| Enterprise | Available |
| Growth Enterprise | Available |
| Scale Enterprise | Available |
| Hyper Enterprise | Available |

API access inside a subscription plan remains subject to:

- Registered API products
- Feature entitlements
- Authentication and authorization
- Action Unit availability
- Rate limits
- Usage limits
- Contract restrictions
- Workspace isolation

---

# Standalone API Products

The initial standalone API products are:

| API Product | Monthly Access Fee | Action Units Per Request |
|---|---:|---:|
| Internal Linking API | $49 | 25 AU |
| External Linking API | $79 | 50 AU |
| Topic Cluster API | $99 | 100 AU |
| Semantic Audit API | $149 | 150 AU |
| Autonomous Intelligence API | $199 | 300 AU |

Standalone API customers pay:

**API access fee + actual API AU consumption**

The approved API consumption rate is:

**1 API AU = $0.0005**

---

# API Mapping Requirements

Every API feature mapping shall include:

- Mapping ID
- API Product ID
- Feature ID
- Service ID
- Endpoint ID
- Eligible Plans
- Standalone Availability
- Entitlement Type
- Authentication Requirement
- Authorization Requirement
- Action Unit Cost
- Rate Limit
- Usage Limit
- Workspace Scope
- Enterprise Override
- OEM Availability
- Version
- Effective Date
- Expiration Date, where applicable
- Approval Status

---

# API Availability States

Each API feature mapping shall use one of these states:

- Included
- Limited
- Standalone
- Contract Only
- Enterprise Only
- OEM Only
- Restricted
- Unavailable
- Deprecated
- Retired

---

# Subscription API Rules

- Starter shall not receive API access.
- Pro through Hyper Enterprise shall receive API access entitlement.
- API usage shall consume Action Units.
- Application-plan API usage shall use the customer's available plan AU and approved top-ups.
- API access shall not bypass feature or plan restrictions.
- API access shall not bypass workspace isolation.
- API requests shall reference registered API Product IDs and Feature IDs.
- API credentials shall be revocable and auditable.
- Historical mappings shall remain traceable.
- Plan upgrades shall activate newly eligible API features after entitlement activation.
- Plan downgrades shall remove unavailable API features at the effective downgrade time.

---

# Standalone API Rules

- Standalone developers may subscribe to individual API products.
- Each API product shall have an independent access fee.
- No fixed AU allocation is attached to the access fee.
- Consumption shall be billed using actual API AU usage.
- Different APIs may consume different AU amounts.
- API access fees and API consumption charges shall remain separate.
- Developers subscribing to one API shall not automatically receive access to other APIs.
- Enterprise and OEM agreements may define custom API mappings.
- All standalone API activity shall be metered and auditable.

---

# API Feature Mapping Dependencies

This mapping depends on:

- Product Registry
- Service Registry
- Feature Registry
- Core Feature Registry
- Feature Availability Matrix
- Plan Feature Mapping
- API Product Registry
- Pricing Engine
- Subscription Entitlements
- Action Unit Accounting
- API Authentication
- API Authorization
- Workspace Isolation

The API Product Registry is scheduled for Phase 2.1.4 and shall provide the canonical API Product IDs referenced by this mapping.

---

# Enforcement Boundary

This document defines API feature availability and mapping rules only.

Executable enforcement belongs to the API authentication, authorization, entitlement, metering and usage-control infrastructure.

This definition document does not:

- Process API requests
- Create jobs
- Start workers
- Create queues
- Consume Action Units
- Grant access directly
- Perform runtime authorization
- Produce runtime failures or recovery actions

---

# Runtime Eligibility

**Current Component:** API Feature Mapping document  
**Runtime Eligible:** No  
**Reason:** Canonical configuration and architecture definition only  
**URRS Requirement:** Not applicable

Any future executable API entitlement validator shall be scanned separately when its dependent API and runtime infrastructure are ready.

---

# Governance Rules

- API mappings shall be configuration-driven.
- API mappings shall not be hard-coded into endpoints.
- Every mapping shall reference canonical identifiers.
- Changes shall be version-controlled.
- Changes shall be reviewed and approved.
- Changes shall generate audit records.
- Deprecated mappings shall remain historically traceable.
- API access shall follow least-privilege principles.
- API feature access shall preserve workspace and customer isolation.

---

# Architecture Status

Status: Approved API Feature Mapping

Implementation Status: Architecture Defined

Runtime Eligibility: Not Runtime Eligible

URRS Requirement: Not Applicable

Production Status: Not Implemented

---

End of API Feature Mapping
