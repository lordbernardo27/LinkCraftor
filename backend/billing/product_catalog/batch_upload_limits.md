# Batch Upload Limits

**Version:** 1.0.0
**Status:** Canonical
**Architecture Phase:** 2.1.3.4
**Last Updated:** 2026-07-26

---

# Purpose

This document defines the canonical maximum number of documents that a LinkCraftor customer may submit in a single upload batch under each subscription plan.

These limits are separate from the total document allowance included with each plan.

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

---

# Trial Batch Upload Limits

Starter and Pro are the only plans eligible for the seven-day free trial.

| Trial Plan | Maximum Documents Per Batch |
|---|---:|
| Starter Trial | 10 |
| Pro Trial | 50 |

Trial access remains subject to separate trial document and Action Unit limits.

---

# Limit Rules

- The limit applies to each individual batch submission.
- A batch exceeding the customer plan limit shall be rejected before processing.
- Partial acceptance of an oversized batch is not permitted by default.
- Batch limits shall be obtained from canonical configuration.
- Upload services shall not hard-code plan limits.
- Plan upgrades shall apply the new limit after entitlement activation.
- Plan downgrades shall apply the lower limit at the effective downgrade time.
- Enterprise contract overrides require an approved contract-specific entitlement.
- OEM limits require a separate approved OEM mapping.
- Every rejected oversized batch shall generate an auditable failure record.
- Limit changes shall be version-controlled and historically traceable.

---

# Enforcement Boundary

This document defines the canonical limits only.

Runtime enforcement shall be performed by the upload admission and entitlement validation infrastructure before a batch job is created.

The future enforcement component may require URRS assessment because it can create runtime decisions, failures, evidence and metrics.

---

# Dependencies

- Product Registry
- Feature Registry
- Feature Availability Matrix
- Plan Feature Mapping
- Trial Pricing & Free Trial Rules
- Subscription Entitlements
- Upload Admission Validation
- Universal Runtime Infrastructure

---

# Architecture Status

Status: Approved Batch Upload Limits

Implementation Status: Pending

Runtime Eligibility: Not Runtime Eligible

Future Enforcement Runtime Eligibility: Eligible for separate assessment

URRS Requirement: Not Applicable to this definition document

Production Status: Not Implemented

---

End of Batch Upload Limits
