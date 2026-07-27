# Plan Feature Mapping

**Version:** 1.0.0
**Status:** Canonical
**Architecture Phase:** 2.1.3.3
**Last Updated:** 2026-07-26

---

# Purpose

The Plan Feature Mapping document defines the canonical relationship between LinkCraftor subscription plans and the features customers are entitled to use.

No subscription plan shall expose a feature unless the mapping is defined here.

---

# Objectives

- Maintain a single source of truth for plan entitlements
- Eliminate duplicated feature assignments
- Support billing and entitlement consistency
- Support future feature expansion
- Support enterprise customization
- Support API entitlement mapping
- Maintain complete auditability

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

# Mapping Requirements

Every mapping shall include:

- Mapping ID
- Plan ID
- Feature ID
- Availability Status
- Entitlement Type
- Usage Limits
- Batch Upload Limit
- Trial Eligibility
- API Availability
- Enterprise Override
- OEM Override
- Effective Date
- Expiration Date (if applicable)
- Version
- Approval Status

---

# Mapping Rules

- Every Plan ID shall reference the Product Registry.
- Every Feature ID shall reference the Core Feature Registry.
- Batch upload limits shall follow the canonical Feature Registry.
- Trial rules shall follow the Trial Pricing & Free Trial Rules.
- Plan changes shall be version controlled.
- Historical mappings shall never be deleted.
- Enterprise contracts may override default mappings.
- OEM agreements may define separate mappings.
- All mapping changes shall be auditable.

---

# Dependencies

This document depends on:

- Product Registry
- Service Registry
- Feature Registry
- Core Feature Registry
- Feature Availability Matrix
- Trial Pricing & Free Trial Rules

---

# Architecture Status

Status: Approved Plan Feature Mapping

Implementation Status: Pending

Runtime Eligibility: Not Runtime Eligible

URRS Requirement: Not Applicable

Production Status: Not Implemented

---

End of Plan Feature Mapping
