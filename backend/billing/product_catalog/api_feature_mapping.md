# API Feature Mapping

**Version:** 1.1.0
**Status:** Canonical
**Architecture Phase:** 2.1.3.5
**Last Updated:** 2026-09-10

---

# Purpose

The API Feature Mapping defines the canonical relationship between LinkCraftor features, subscription plans, standalone API access and registered API products.

No LinkCraftor feature may be exposed through an API unless its API availability is registered through this mapping.

This document defines API feature eligibility and mapping only.

API access pricing, API usage package pricing and API consumption values are owned by the Pricing Engine and shall not be duplicated here.

---

# API Access Eligibility

Subscription API access begins with the Business plan.

| Plan | API Access |
|---|---|
| Starter | Unavailable |
| Pro | Unavailable |
| Business | Available |
| Enterprise | Available |
| Growth Enterprise | Available |
| Scale Enterprise | Available |
| Hyper Enterprise | Available |

Business through Hyper Enterprise receive API platform eligibility through their subscription entitlement.

API usage remains separately metered and billed according to the canonical API usage architecture.

---

# Standalone API Access

Non-subscribers may obtain standalone API platform access.

Standalone API access pricing is defined canonically by the Pricing Engine and shall not be duplicated in this mapping.

Standalone API access does not itself grant unlimited usage.

API usage packages, metering units and consumption values shall be governed separately by the canonical API pricing and metering architecture.

---

# Initial API Products

The initial canonical API product scope is:

- Internal Linking API
- Semantic Linking API
- External Linking API

A future Unified Linking API may orchestrate Internal Linking, Semantic Linking and External Linking capabilities.

Unified Linking API pricing and usage metering are not finalized.

Canonical API Product IDs shall be provided by Phase 2.1.4 — API Product Registry.

---

# API Metering Status

Exact API usage package quantities, prices, Action Unit consumption values and per-request metering rules are currently suspended pending real API consumption benchmarking.

This mapping shall therefore not define:

- Fixed API Action Units per request
- API usage package quantities
- API usage package prices
- API-specific AU conversion rates
- Unified API consumption values

These values shall be introduced only after benchmarking and approval.

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
- Metering Policy Reference
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
- Pro shall not receive API access.
- Business through Hyper Enterprise shall receive API platform eligibility.
- API usage shall be separately metered.
- API usage shall follow the canonical API usage and billing architecture.
- API access shall not bypass feature or plan restrictions.
- API access shall not bypass workspace isolation.
- API requests shall reference registered API Product IDs and Feature IDs.
- API credentials shall be revocable and auditable.
- Historical mappings shall remain traceable.
- Plan upgrades shall activate newly eligible API features after entitlement activation.
- Plan downgrades shall remove unavailable API features at the effective downgrade time.

---

# Standalone API Rules

- Standalone API access shall use the canonical standalone API platform-access entitlement.
- Standalone access pricing shall be owned by the Pricing Engine.
- API usage charges shall remain separate from API access charges.
- Standalone API access shall not imply unlimited usage.
- API products shall remain independently entitlement-controlled.
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
- API Metering
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
- Consume usage units
- Grant access directly
- Perform runtime authorization
- Produce runtime failures or recovery actions

---

# Runtime Eligibility

**Current Component:** API Feature Mapping document
**Runtime Eligible:** No
**Reason:** Canonical configuration and architecture definition only
**URRS Requirement:** Not applicable

Any future executable API entitlement validator, usage-metering component or API access-control component shall receive a separate runtime and URRS assessment.

---

# Governance Rules

- API mappings shall be configuration-driven.
- API mappings shall not be hard-coded into endpoints.
- Every mapping shall reference canonical identifiers.
- Pricing values shall not be duplicated in this mapping.
- Metering values shall not be duplicated until benchmarked and approved.
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
