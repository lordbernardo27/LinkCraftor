# Feature Availability Matrix

**Version:** 1.0.0
**Status:** Canonical
**Architecture Phase:** 2.1.3.2
**Last Updated:** 2026-07-26

---

# Purpose

The Feature Availability Matrix defines how registered LinkCraftor features are assigned, restricted and made available across subscription plans, trials, API products, enterprise packages and OEM offerings.

No feature shall be exposed to a customer unless its availability is defined through this matrix.

---

# Availability States

Each feature-plan relationship shall use one of the following states:

- Included
- Limited
- Trial Limited
- Add-On
- Contract Only
- API Only
- OEM Only
- Marketplace Only
- Unavailable
- Deprecated

---

# Supported Plans

- Starter
- Pro
- Business
- Enterprise
- Growth Enterprise
- Scale Enterprise
- Hyper Enterprise

---

# Trial Eligibility

| Plan | Trial Availability |
|---|---|
| Starter | 7-Day Free Trial |
| Pro | 7-Day Free Trial |
| Business | Unavailable |
| Enterprise | Unavailable |
| Growth Enterprise | Unavailable |
| Scale Enterprise | Unavailable |
| Hyper Enterprise | Unavailable |

Trial users receive selected-plan feature access subject to trial-specific document, AU and batch limits.

---

# Canonical Batch Upload Availability

| Plan | Maximum Documents Per Batch |
|---|---:|
| Starter | 10 |
| Pro | 50 |
| Business | 200 |
| Enterprise | 1,000 |
| Growth Enterprise | 2,000 |
| Scale Enterprise | 3,000 |
| Hyper Enterprise | 5,000 |

---

# Matrix Record Requirements

Every feature availability record shall include:

- Feature ID
- Plan ID
- Availability State
- Entitlement Type
- Usage Limit
- Batch Limit, where applicable
- Trial Availability
- API Availability
- Enterprise Availability
- OEM Availability
- Add-On Eligibility
- Effective Date
- Expiration Date, where applicable
- Configuration Version
- Approval Status

---

# Availability Rules

- Features shall reference registered Feature IDs.
- Plans shall reference registered Product IDs.
- Availability shall be configuration-driven.
- Trial access shall never override trial restrictions.
- Higher plan access shall not be assumed automatically.
- Enterprise and OEM access may require contract-specific mappings.
- Changes shall be version-controlled and auditable.
- Deprecated mappings shall remain historically traceable.

---

# Enforcement Boundary

This document defines canonical availability rules.

Actual customer access shall be enforced by the entitlement and authorization infrastructure.

This stage does not execute customer requests or runtime jobs.

---

# Architecture Status

Status: Approved Feature Availability Matrix

Implementation Status: Pending

Runtime Eligibility: Not Runtime Eligible

URRS Requirement: Not Applicable

Production Status: Not Implemented

---

End of Feature Availability Matrix
