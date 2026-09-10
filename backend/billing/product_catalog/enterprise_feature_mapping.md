# Enterprise Feature Mapping

**Version:** 1.1.0
**Status:** Canonical
**Architecture Phase:** 2.1.3.6
**Last Updated:** 2026-09-10

---

# Purpose

The Enterprise Feature Mapping defines the canonical relationship between LinkCraftor enterprise plans, enterprise-only capabilities, contract-specific entitlements and approved feature overrides.

No enterprise customer shall receive a feature, limit, entitlement or contract override unless it is defined through this mapping or an approved enterprise contract.

This document owns enterprise feature availability and override architecture only.

Commercial prices, document allowances, batch limits, Action Unit allowances and API usage prices shall remain owned by their respective canonical billing and entitlement components and shall not be duplicated here.

---

# Enterprise Plans

The canonical enterprise plan family is:

- Enterprise
- Growth Enterprise
- Scale Enterprise
- Hyper Enterprise

Plan pricing is owned by the Pricing Engine.

Plan document allowances are owned by the canonical subscription entitlement architecture.

Batch upload limits are owned by **Phase 2.1.3.4 — Batch Upload Limits**.

Included application Action Unit allowances are currently suspended pending real engine-consumption benchmarking and shall not be defined in this mapping.

Annual billing rules are owned by the Pricing Engine.

---

# Enterprise Trial Rules

Enterprise plans do not receive self-service free trials under the currently defined trial architecture.

| Plan | Free Trial |
|---|---|
| Enterprise | Unavailable |
| Growth Enterprise | Unavailable |
| Scale Enterprise | Unavailable |
| Hyper Enterprise | Unavailable |

Enterprise access begins through direct subscription, approved sales conversion or contract activation.

Final trial-commercial rules remain subject to the canonical Trial Pricing & Free Trial Rules.

---

# Enterprise Feature Categories

Enterprise mappings may include:

- Advanced Workspace Management
- Multi-Workspace Management
- Team Administration
- Role-Based Access Control
- Enterprise Audit Logs
- Advanced Reporting
- Priority Processing
- API Access
- Higher API Throughput
- Enterprise Support
- Service-Level Agreements
- Dedicated Onboarding
- Dedicated Account Management
- Custom Integrations
- Custom Workflow Automation
- Contract-Specific Limits
- Dedicated Infrastructure
- Private Deployment
- White-Label Reports
- White-Label Client Portals
- Reseller Rights
- OEM Eligibility
- Future Enterprise Capabilities

---

# Default Enterprise Availability

| Capability | Enterprise | Growth Enterprise | Scale Enterprise | Hyper Enterprise |
|---|---|---|---|---|
| API Access | Included | Included | Included | Included |
| Multi-Workspace Management | Included | Included | Included | Included |
| Advanced Reporting | Included | Included | Included | Included |
| Priority Support | Included | Included | Included | Included |
| Dedicated Account Management | Contract Based | Included | Included | Included |
| Custom Workflow Automation | Contract Based | Limited | Included | Included |
| Advanced Audit Logs | Included | Included | Included | Included |
| Dedicated Infrastructure | Contract Only | Contract Only | Optional | Available |
| Private Deployment | Contract Only | Contract Only | Contract Only | Contract Only |
| White-Label Reports | Available | Available | Available | Available |
| White-Label Client Portal | Contract Based | Available | Available | Available |
| Reseller Rights | Unavailable | Contract Based | Contract Based | Available |
| OEM Rights | Unavailable | Unavailable | Contract Only | Contract Only |

This table defines default feature availability only.

It does not define commercial prices, document allowances, workspace quantities, seat quantities, Action Unit allowances, batch limits or API usage prices.

Approved enterprise contracts may add, restrict or override specific entitlements.

---

# Mapping Requirements

Every enterprise feature mapping shall include:

- Mapping ID
- Customer ID
- Workspace ID
- Contract ID
- Plan ID
- Feature ID
- Service ID
- Availability State
- Entitlement Type
- Usage Limit Reference
- Batch Limit Reference
- API Access
- API Throughput Policy Reference
- Support Level
- SLA Reference
- Infrastructure Assignment
- White-Label Rights
- Reseller Rights
- OEM Eligibility
- Override Reason
- Approval Authority
- Effective Date
- Expiration Date
- Version
- Status

---

# Enterprise Availability States

Each enterprise feature mapping shall use one of these states:

- Included
- Limited
- Optional
- Add-On
- Contract Based
- Contract Only
- Customer Specific
- Workspace Specific
- Restricted
- Unavailable
- Deprecated
- Retired

---

# Enterprise Override Rules

- Enterprise overrides shall never be applied without an approved contract or authorized billing decision.
- Every override shall reference a valid Customer ID, Workspace ID and Contract ID.
- Overrides shall not modify the canonical plan definition.
- Overrides shall exist as separate versioned entitlement records.
- Overrides shall have effective and expiration dates where applicable.
- Expired overrides shall be disabled automatically by the entitlement infrastructure.
- Historical overrides shall never be deleted.
- All changes shall be auditable.
- Workspace isolation shall always be preserved.
- Reseller and OEM rights shall require explicit contractual approval.
- Hyper Enterprise shall not automatically grant OEM licensing rights.
- OEM licensing shall remain governed by separate OEM agreements and pricing.

---

# Enterprise API Rules

- Enterprise through Hyper Enterprise receive API platform eligibility.
- API usage shall be separately metered according to the canonical API usage architecture.
- Enterprise contracts may define custom API throughput and rate limits.
- Contract overrides shall not bypass authentication, authorization or workspace isolation.
- Large API usage may require custom pricing or a separate enterprise agreement.
- Standalone API access remains separate from application-plan API entitlement.
- OEM API rights require a separate OEM agreement.
- Exact API usage package quantities, prices and consumption values shall not be defined here while API metering remains pending benchmarking.

---

# Enterprise Billing Rules

- Enterprise plans may use monthly or annual billing.
- Annual billing rules and discounts shall be obtained from the canonical Pricing Engine.
- Enterprise contracts may include custom invoicing.
- Purchase orders may be supported.
- Multi-year agreements may define approved custom pricing.
- Dedicated infrastructure may be billed separately.
- Private deployment may be billed separately.
- Professional services may be billed separately.
- OEM licensing shall not be included automatically in an enterprise subscription.
- Commercial values shall not be duplicated in this feature-mapping document.

---

# Dependencies

This mapping depends on:

- Product Registry
- Service Registry
- Feature Registry
- Core Feature Registry
- Feature Availability Matrix
- Plan Feature Mapping
- Batch Upload Limits
- API Feature Mapping
- Enterprise Pricing
- Subscription Entitlements
- Enterprise Contracts
- Action Unit Accounting
- API Metering
- API Authentication
- API Authorization
- Workspace Isolation

---

# Enforcement Boundary

This document defines enterprise feature availability and override rules only.

Executable enforcement belongs to:

- Subscription Entitlement Infrastructure
- Enterprise Contract Validation
- API Authorization
- Workspace Authorization
- Usage Metering
- Batch Upload Admission
- Infrastructure Assignment
- Billing Enforcement

This definition document does not:

- Activate subscriptions
- Grant access directly
- Process API requests
- Create runtime jobs
- Start workers
- Create queues
- Consume usage units
- Apply contract overrides
- Assign infrastructure
- Process invoices or payments

---

# Runtime Eligibility

**Current Component:** Enterprise Feature Mapping document
**Runtime Eligible:** No
**Reason:** Canonical architecture and entitlement-definition document only
**URRS Requirement:** Not applicable

Executable enterprise entitlement, contract enforcement, usage-control or infrastructure-assignment components shall receive separate runtime and URRS assessment when implemented.

---

# Governance Rules

- Enterprise mappings shall be configuration-driven.
- Enterprise limits shall not be hard-coded.
- Every mapping shall reference canonical identifiers.
- Commercial values owned elsewhere shall not be duplicated here.
- Contract overrides shall require formal approval.
- Changes shall be version-controlled and auditable.
- Historical mappings shall remain traceable.
- Least-privilege access shall apply.
- Customer and workspace isolation shall be preserved.
- Enterprise subscriptions shall not automatically grant reseller or OEM rights.
- OEM licensing shall remain separate from Hyper Enterprise.

---

# Architecture Status

Status: Approved Enterprise Feature Mapping

Implementation Status: Architecture Defined

Runtime Eligibility: Not Runtime Eligible

URRS Requirement: Not Applicable

Production Status: Not Implemented

---

End of Enterprise Feature Mapping
