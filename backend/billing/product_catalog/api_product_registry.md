# API Product Registry

**Version:** 1.0.0

**Status:** Canonical

**Architecture Phase:** 2.1.4

**Last Updated:** 2026-08-01

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
- Support Action Unit accounting
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
- Content Intelligence APIs
- Analytics APIs
- Administration APIs
- Enterprise APIs
- OEM APIs
- Future APIs

---

# Initial API Products

| API Product | Monthly Access Fee | API AU Cost |
|---|---:|---:|
| Internal Linking API | $49 | 25 AU |
| External Linking API | $79 | 50 AU |
| Topic Cluster API | $99 | 100 AU |
| Semantic Audit API | $149 | 150 AU |
| Autonomous Intelligence API | $199 | 300 AU |

The API access fee and API Action Unit consumption are billed separately.

Approved API AU rate:

**1 API AU = $0.0005**

---

# Registry Record Requirements

Every API product shall include:

- API Product ID
- API Product Name
- Category
- Description
- Associated Service ID
- Associated Feature IDs
- Pricing Model
- Access Fee
- Action Unit Cost
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
- Action Unit Accounting
- Subscription Entitlements

---

# Enforcement Boundary

This document defines the canonical registry only.

It does not:

- process API requests
- authenticate users
- authorize requests
- consume Action Units
- create runtime jobs
- execute workers
- create queues

Those responsibilities belong to the API runtime infrastructure.

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

Future executable API product services shall undergo independent URRS assessment before implementation.

---

# Governance Rules

- Every API product shall have a unique API Product ID.
- API products shall reference registered services and features.
- API pricing shall reference the Pricing Engine.
- Action Unit pricing shall remain configuration-driven.
- Changes shall be version-controlled.
- Historical records shall remain traceable.
- Deprecated API products shall not be deleted.

---

# Architecture Status

Status: Approved API Product Registry

Implementation Status: Pending

Production Status: Not Implemented

---

End of API Product Registry
