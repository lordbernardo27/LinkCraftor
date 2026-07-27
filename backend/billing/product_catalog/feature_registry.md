# Feature Registry

**Version:** 1.0.0
**Status:** Canonical
**Architecture Phase:** 2.1.3
**Last Updated:** 2026-07-26

---

# Purpose

The Feature Registry is the canonical registry for every product capability offered by LinkCraftor.

No feature may be assigned to a subscription plan, API product, enterprise package, OEM agreement or marketplace product unless it is registered through this framework.

---

# Registry Objectives

- Maintain one canonical feature inventory
- Assign unique feature identifiers
- Map features to products and services
- Map features to subscription plans
- Control feature availability
- Define feature limits and entitlements
- Support feature versioning
- Support lifecycle governance
- Prevent inconsistent plan definitions
- Enable auditable billing integration

---

# Feature Registry Components

The Feature Registry includes:

- Core Feature Registry
- Feature Availability Matrix
- Plan Feature Mapping
- Batch Upload Limits
- API Feature Mapping
- Enterprise Feature Mapping
- OEM Feature Mapping
- Feature Versioning
- Feature Registry Certification

---

# Feature Requirements

Every registered feature shall include:

- Feature ID
- Feature Name
- Feature Description
- Feature Category
- Owning Product
- Owning Service
- Eligible Plans
- Entitlement Type
- Usage Limit
- Batch Limit, where applicable
- API Availability
- Enterprise Availability
- OEM Availability
- Feature Version
- Feature Status
- Effective Date
- Retirement Date, where applicable

---

# Canonical Batch Upload Limits

| Plan | Maximum Documents Per Batch |
|---|---:|
| Starter | 10 |
| Pro | 50 |
| Business | 200 |
| Enterprise | 1,000 |
| Growth Enterprise | 2,000 |
| Scale Enterprise | 3,000 |
| Hyper Enterprise | 5,000 |

These are per-batch limits and are separate from total plan document allowances.

---

# Feature Lifecycle

- Draft
- Review
- Approved
- Active
- Restricted
- Deprecated
- Retired

---

# Governance Rules

- Feature definitions shall be configuration-driven.
- Plan assignments shall reference registered Feature IDs.
- Feature limits shall not be duplicated across unrelated services.
- Changes shall be version-controlled and audited.
- Deprecated features shall remain traceable.
- Feature access shall be enforced through the entitlement architecture.
- Runtime execution is not performed by this registry document.

---

# Architecture Status

Status: Approved Feature Registry

Implementation Status: Pending

Runtime Eligibility: Not Runtime Eligible

URRS Requirement: Not Applicable

Production Status: Not Implemented

---

End of Feature Registry
