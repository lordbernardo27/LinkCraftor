# Plan Pricing

**Version:** 1.0.0

**Status:** Canonical

**Architecture Phase:** 2.2.1

**Last Updated:** 2026-08-11

---

# Purpose

Plan Pricing defines the canonical base subscription prices for LinkCraftor subscription products.

It establishes the authoritative relationship between:

- subscription plan
- billing currency
- billing interval
- monthly base price
- annual discount policy
- annual contract value
- pricing lifecycle
- pricing version

This document defines pricing configuration only.

It does not execute billing calculations or payment processing.

---

# Pricing Authority

This document is the canonical source for LinkCraftor subscription plan base prices.

Subscription prices shall not be inferred from:

- feature registries
- API product prices
- marketplace prices
- OEM prices
- Action Unit prices
- promotional prices
- historical UI values
- enterprise contract overrides

Those pricing domains remain independently governed.

---

# Canonical Subscription Plans

The canonical LinkCraftor subscription plans are:

1. Starter
2. Pro
3. Business
4. Enterprise
5. Growth Enterprise
6. Scale Enterprise
7. Hyper Enterprise

---

# Base Monthly Pricing

| Plan | Monthly Base Price |
|---|---:|
| Starter | $49 |
| Pro | $199 |
| Business | $799 |
| Enterprise | $1,999 |
| Growth Enterprise | $5,000 |
| Scale Enterprise | $10,000 |
| Hyper Enterprise | $15,000 |

Currency:

**USD**

These values represent base subscription prices before:

- annual discounts
- promotions
- credits
- taxes
- Action Unit top-ups
- API product charges
- marketplace charges
- OEM licensing charges
- negotiated contractual adjustments

---

# Annual Billing Policy

The approved standard annual discount is:

**17%**

Annual billing shall be derived from the canonical monthly base price.

Canonical calculation:

Annual List Price = Monthly Base Price × 12

Annual Discount = Annual List Price × 17%

Annual Subscription Price = Annual List Price − Annual Discount

Equivalent multiplier:

**Annual Subscription Price = Monthly Base Price × 12 × 0.83**

The Pricing Engine implementation shall perform monetary rounding according to the future canonical Money and Rounding Rules.

---

# Reference Annual Pricing

The following values are architectural reference values derived from the approved 17% annual discount.

| Plan | Monthly | 12-Month List Price | 17% Discount | Annual Price |
|---|---:|---:|---:|---:|
| Starter | $49 | $588 | $99.96 | $488.04 |
| Pro | $199 | $2,388 | $405.96 | $1,982.04 |
| Business | $799 | $9,588 | $1,629.96 | $7,958.04 |
| Enterprise | $1,999 | $23,988 | $4,077.96 | $19,910.04 |
| Growth Enterprise | $5,000 | $60,000 | $10,200.00 | $49,800.00 |
| Scale Enterprise | $10,000 | $120,000 | $20,400.00 | $99,600.00 |
| Hyper Enterprise | $15,000 | $180,000 | $30,600.00 | $149,400.00 |

These reference calculations do not constitute an executable pricing calculator.

---

# Pricing Record Requirements

Every canonical plan-price record shall support:

- Pricing Record ID
- Product ID
- Plan ID
- Plan Name
- Currency
- Billing Interval
- Base Price
- Pricing Version
- Effective Date
- Expiration Date
- Status
- Created At
- Approved At
- Superseded By
- Pricing Source

---

# Pricing Record Identity

Pricing records shall have immutable unique identities.

Recommended identity form:

`price_<plan>_<currency>_<interval>_<version>`

Examples:

- `price_starter_usd_monthly_v1`
- `price_pro_usd_monthly_v1`
- `price_business_usd_monthly_v1`
- `price_enterprise_usd_monthly_v1`

A pricing record identity shall not be reused for a materially different price.

---

# Billing Interval

The initial supported subscription billing intervals are:

- Monthly
- Annual

Future billing intervals may include:

- Quarterly
- Multi-Year
- Contract-Specific

Future intervals shall not be introduced without explicit pricing configuration and governance approval.

---

# Currency Policy

Initial canonical subscription currency:

**USD**

Additional currencies may be introduced later through controlled pricing configuration.

Currency conversion shall not modify the canonical USD base price.

Foreign-currency pricing may be:

- explicitly configured
- regionally configured
- contractually configured

Dynamic foreign-exchange conversion shall not automatically become canonical plan pricing.

---

# Pricing Separation

Subscription plan pricing shall remain separate from all other monetary domains.

## Action Units

Action Unit pricing is not included in the monthly subscription price definition.

Included Action Unit allowances, where applicable, are subscription entitlements.

Additional Action Units are separately metered and billed.

## API Products

API product access fees and API Action Unit charges are independent from subscription plan base pricing.

An API price that numerically equals a subscription price does not establish a pricing relationship between the two products.

## Marketplace Products

Marketplace products maintain independent pricing and revenue-share rules.

## OEM Products

OEM licensing remains separate from standard LinkCraftor subscription pricing.

Hyper Enterprise does not automatically grant OEM licensing rights.

## Enterprise Contracts

Approved enterprise contracts may define negotiated commercial terms.

Contract-specific pricing shall not overwrite canonical public plan pricing.

---

# Free Trial Relationship

Starter and Pro may support the approved seven-day free trial.

A free trial:

- does not change the canonical plan price
- does not create a zero-dollar canonical product price
- does not permanently alter subscription pricing
- is governed by trial eligibility and subscription lifecycle rules

Business through Hyper Enterprise are not included in the standard seven-day trial architecture unless explicitly approved in the future.

---

# Promotion Relationship

Promotional pricing shall be applied separately from canonical base pricing.

Promotions may include:

- percentage discounts
- fixed discounts
- introductory pricing
- customer acquisition campaigns
- seasonal campaigns
- approved customer cohorts

Promotional prices shall not replace the canonical base-price record.

---

# Pricing Versioning

Plan prices shall be version-controlled.

A price change shall create a new pricing version.

Historical pricing records shall remain traceable.

Example:

`Starter $49`

may be represented as:

`price_starter_usd_monthly_v1`

If the canonical Starter price changes in the future, the existing record shall not be destructively rewritten.

A new pricing version shall be created.

---

# Effective-Date Rules

Every activated pricing version shall have an effective date.

Future price changes may be scheduled.

Pricing versions shall support:

- future activation
- current activation
- historical retention
- supersession
- retirement

No pricing version shall become active before its approved effective date.

---

# Existing Subscriber Treatment

A future plan-price change does not automatically determine how existing subscribers are treated.

Existing subscriber treatment may include:

- immediate migration
- renewal-time migration
- grandfathered pricing
- contractual pricing
- transition pricing

Those policies belong to subscription pricing lifecycle and migration governance.

---

# Tax Boundary

Canonical plan prices are defined before applicable taxes unless explicitly stated otherwise.

Tax determination, calculation, collection and remittance belong to the future Tax Infrastructure.

---

# Payment Provider Boundary

Canonical plan pricing shall remain payment-provider independent.

Stripe or any future payment provider shall consume approved LinkCraftor pricing configuration.

A payment-provider price identifier shall not become the architectural source of truth for LinkCraftor pricing.

---

# Dependencies

Plan Pricing depends on:

- Product Registry
- Service Registry
- Feature Registry
- Product Versioning
- Product Lifecycle Management
- Billing Configuration Framework
- Billing Governance
- Billing Change Management

Future executable pricing services will additionally depend on:

- Money and Currency Rules
- Rounding Rules
- Discount Engine
- Promotion Engine
- Subscription Engine
- Tax Infrastructure
- Payment Infrastructure
- Action Unit Accounting

---

# Enforcement Boundary

This document defines canonical pricing configuration only.

It does not:

- calculate invoices
- charge customers
- process payments
- calculate taxes
- consume Action Units
- grant entitlements
- apply promotions
- create subscriptions
- renew subscriptions
- create runtime jobs
- create queues
- execute workers

Those responsibilities belong to later executable billing infrastructure.

---

# Runtime Eligibility

**Current Component:** Plan Pricing architecture document

**Runtime Eligible:** No

**Reason:** Canonical pricing definition and configuration architecture only

**URRS Requirement:** Not Applicable

Future executable pricing loaders, resolvers, calculators, discount processors and billing services shall undergo independent URRS assessment before implementation.

---

# Governance Rules

- Every subscription plan shall have an approved canonical base price.
- Canonical pricing shall be configuration-driven.
- Price changes shall be version-controlled.
- Historical prices shall remain traceable.
- API pricing shall remain separate.
- Marketplace pricing shall remain separate.
- OEM pricing shall remain separate.
- Action Unit pricing shall remain separate.
- Promotional pricing shall not overwrite base pricing.
- Contract pricing shall not overwrite public canonical pricing.
- Annual pricing shall derive from approved annual-discount policy.
- Runtime systems shall not hard-code canonical commercial prices.
- Payment providers shall not become the pricing source of truth.

---

# Architecture Status

Status: Approved Plan Pricing

Implementation Status: Pending

Production Status: Not Implemented

---

# Next Phase

Proceed to:

**PHASE 2.2.2 — Billing Interval and Annual Pricing Rules**

---

End of Plan Pricing
