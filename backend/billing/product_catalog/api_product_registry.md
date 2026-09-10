# API Product Registry

**Version:** 1.1.0

**Status:** Canonical

**Architecture Phase:** 2.1.4

**Last Updated:** 2026-09-10

---

# Purpose

The API Product Registry is the canonical registry for every API product offered by LinkCraftor.

No API product may be published, subscribed to, billed or exposed unless it is registered through this registry.

---

# Registry Objectives

- Maintain one canonical API product inventory
- Assign unique API Product IDs
- Support API lifecycle management
- Support billing integration
- Support usage metering integration
- Support entitlement mapping
- Support authentication and authorization mapping
- Support pricing integration
- Support version control
- Support auditability

---

# API Product Categories

The registry shall support:

- Internal Linking APIs
- Semantic Linking APIs
- External Linking APIs
- Unified Linking APIs
- Content Intelligence APIs
- Analytics APIs
- Administration APIs
- Enterprise APIs
- OEM APIs
- Future APIs

---

# Initial API Products

The initial LinkCraftor API product family consists of:

- Internal Linking API
- Semantic Linking API
- External Linking API

A future Unified Linking API may orchestrate Internal Linking, Semantic Linking and External Linking through a unified product interface.

The Unified Linking API shall not receive final pricing or metering rules until its runtime consumption model has been benchmarked and approved.

---

# API Access Architecture

API product registration is separate from API access eligibility and API usage billing.

Subscription API access eligibility begins at the Business plan and above.

Starter and Pro do not receive subscription API access eligibility.

Business, Enterprise, Growth Enterprise, Scale Enterprise and Hyper Enterprise may receive API platform eligibility according to the canonical API Feature Mapping and subscription entitlement architecture.

Standalone API-only access for non-subscribers is governed by the Pricing Engine.

API access pricing shall not be duplicated in this registry.

---

# API Usage Metering Status

Exact API usage package quantities, prices, per-request consumption values, Action Unit equivalents and final API metering units are intentionally not defined here.

These values remain suspended pending real API consumption benchmarking.

The final API metering architecture shall be referenced by this registry once approved.

---

# Registry Record Requirements

Every API product shall include:

- API Product ID
- API Product Name
- Category
- Description
- Associated Service ID
- Associated Feature IDs
- Pricing Model Reference
- Access Eligibility Reference
- Usage Metering Policy Reference
- Authentication Method
- Authorization Policy
- Endpoint Group
- Version
- Status
- Effective Date
- Retirement Date (if applicable)

---

# API Product Lifecycle

- Draft
- Review
- Approved
- Active
- Deprecated
- Retired

---

# Dependencies

This registry depends on:

- Product Registry
- Service Registry
- Feature Registry
- API Feature Mapping
- Pricing Engine
- API Metering Architecture
- Subscription Entitlements

---

# Enforcement Boundary

This document defines the canonical registry only.

It does not:

- process API requests
- authenticate users
- authorize requests
- meter billable API usage
- deduct usage balances
- create runtime jobs
- execute workers
- create queues

Those responsibilities belong to the API runtime and billing infrastructure.

---

# Runtime Eligibility

Current Component:

API Product Registry document

Runtime Eligible:

No

Reason:

This is a canonical architecture definition.

Current URRS Requirement:

Not Applicable

Future executable API product loaders, entitlement services, access-control components, API metering services and runtime API infrastructure shall undergo independent URRS assessment before implementation.

---

# Governance Rules

- Every API product shall have a unique API Product ID.
- API products shall reference registered services and features.
- API pricing shall reference the Pricing Engine.
- API access eligibility shall reference the canonical entitlement architecture.
- API usage metering shall reference the approved API metering architecture.
- Commercial values shall not be duplicated in this registry.
- Changes shall be version-controlled.
- Historical records shall remain traceable.
- Deprecated API products shall not be deleted.
- Exact API consumption values shall remain undefined until approved benchmarking is complete.

---

# Architecture Status

Status: Approved API Product Registry

Implementation Status: Pending

Runtime Eligibility: Not Runtime Eligible

URRS Requirement: Not Applicable

Production Status: Not Implemented

---

End of API Product Registry
