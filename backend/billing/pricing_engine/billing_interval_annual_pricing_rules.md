# Billing Interval & Annual Pricing Rules

**Version:** 1.0.0  
**Status:** Canonical  
**Architecture Phase:** 2.2.2  
**Last Updated:** 2026-09-11  

---

## 1. Purpose

This document defines the canonical billing-interval architecture for LinkCraftor subscription plans.

It governs:

- monthly billing,
- annual billing,
- annual subscription discounts,
- interval transitions,
- renewal behavior,
- pricing-effective-date behavior,
- annual-price derivation,
- rounding,
- proration boundaries,
- interaction with add-ons,
- interaction with promotions,
- payment-provider boundaries,
- versioning and historical reproducibility.

This document does not own the canonical monthly price of any subscription plan.

Canonical monthly base subscription prices are owned by:

`backend/billing/pricing_engine/plan_pricing.md`

---

## 2. Billing Interval Authority

The Pricing Engine recognizes two standard subscription billing intervals:

1. Monthly
2. Annual

No other recurring billing interval is canonical unless explicitly introduced through a future approved pricing architecture version.

Billing intervals must be represented independently from:

- subscription plan identity,
- entitlement limits,
- application AU allowances,
- document top-ups,
- AU top-ups,
- seat expansion,
- workspace expansion,
- API usage,
- marketplace pricing,
- OEM pricing,
- enterprise contract overrides.

---

## 3. Monthly Billing

Monthly billing uses the canonical monthly base subscription price defined by `plan_pricing.md`.

For a monthly subscription:

**Monthly Charge = Canonical Monthly Base Price**

Monthly subscriptions renew once per monthly billing cycle unless:

- cancelled,
- suspended,
- terminated,
- changed to another billing interval,
- changed to another plan,
- replaced by an approved contract-specific arrangement.

The payment provider must not independently determine the canonical monthly price.

---

## 4. Annual Billing

Annual billing is an alternative billing interval for the same underlying subscription plan.

Annual billing does not create a separate subscription-plan identity.

The annual subscription price is derived from the canonical monthly base price.

Canonical annual pricing rule:

**Annual List Price = Monthly Base Price × 12**

Canonical annual discount:

**20%**

Canonical annual subscription-price formula:

**Annual Subscription Price = Monthly Base Price × 12 × 0.80**

The 0.80 multiplier represents payment of 80% of the undiscounted twelve-month subscription value.

---

## 5. Annual Discount Scope

The canonical 20% annual discount applies to:

- the base subscription price only.

The annual discount does not automatically apply to:

- additional document purchases,
- document bundles,
- application AU top-ups,
- additional seats,
- workspace expansion packages,
- API usage packages,
- API-only access charges,
- marketplace charges,
- OEM charges,
- professional-service fees,
- contract-specific charges,
- one-time fees,
- taxes,
- externally imposed charges.

Any annual discount outside the base subscription requires an independently approved pricing rule.

---

## 6. Canonical Annual Pricing Reference

The authoritative monthly base prices remain owned by `plan_pricing.md`.

For validation purposes, the currently approved annual subscription values are:

| Plan | Annual Subscription Price |
|---|---:|
| Starter | $470.40 |
| Pro | $1,910.40 |
| Business | $4,790.40 |
| Enterprise | $9,590.40 |
| Growth Enterprise | $19,200.00 |
| Scale Enterprise | $48,000.00 |
| Hyper Enterprise | $96,000.00 |

These values are derived references, not independent canonical base-price records.

If a monthly base price changes, annual pricing must be recalculated using the canonical annual-pricing formula rather than independently edited.

---

## 7. Annual Billing Commitment

An annual subscription represents one annual billing commitment.

Unless another approved contract explicitly overrides this rule:

- payment is collected for the annual subscription period,
- the annual billing period begins on the subscription effective date,
- the next renewal date is one year after the effective billing date,
- access remains governed by subscription status and entitlement rules.

Annual billing does not imply unlimited usage.

Usage-dependent limits remain governed independently by their canonical entitlement and metering architectures.

---

## 8. Monthly-to-Annual Transition

A customer may transition from monthly billing to annual billing.

The Pricing Engine must determine:

- effective date,
- remaining monthly-period treatment,
- any applicable credit,
- annual charge,
- new annual renewal date.

The architecture must not assume that every monthly-to-annual transition occurs only at the end of the current billing period.

The executable billing implementation must support both:

1. next-renewal transition, and
2. approved immediate transition with proration or credit handling.

The commercial policy selecting the applicable transition mode may be configured separately.

---

## 9. Annual-to-Monthly Transition

A customer may request transition from annual billing to monthly billing.

Default architectural behavior:

- the annual subscription remains active until the end of the already-paid annual term,
- monthly billing begins at the next renewal boundary.

Immediate annual-to-monthly conversion must not automatically create a refund.

Any refund, credit, or early-conversion rule requires an explicit approved billing policy.

---

## 10. Plan Changes Within Monthly Billing

Monthly plan upgrades or downgrades must be handled separately from billing-interval selection.

The Pricing Engine must preserve:

- previous plan,
- new plan,
- effective date,
- price version,
- billing interval,
- proration decision,
- adjustment amount,
- renewal boundary.

The final monetary adjustment is determined by the approved proration architecture and executable billing implementation.

---

## 11. Plan Changes Within Annual Billing

Annual-plan upgrades or downgrades must preserve the active annual billing context.

The Pricing Engine must retain:

- original annual plan,
- replacement plan,
- original annual price version,
- replacement price version,
- remaining service period,
- adjustment policy,
- proration result,
- next renewal date.

Annual upgrades must not be treated as entirely new subscriptions unless the approved billing policy explicitly requires replacement.

Annual downgrades should ordinarily take effect at the next renewal boundary unless another approved policy allows earlier application.

---

## 12. Proration Boundary

This document defines the architectural boundary for proration but does not implement the proration calculator.

Proration may be required for:

- plan upgrades,
- plan downgrades where permitted,
- monthly-to-annual conversion,
- annual-plan upgrades,
- seat changes where separately governed,
- workspace changes where separately governed,
- contract amendments.

Proration logic must be implemented as an executable pricing/billing component.

The payment provider may execute an approved proration result but must not independently define LinkCraftor proration policy.

---

## 13. Proration Inputs

A future executable proration component must be capable of receiving, at minimum:

- current plan,
- target plan,
- current billing interval,
- target billing interval,
- current price version,
- target price version,
- current billing-period start,
- current billing-period end,
- transition effective date,
- amount already paid,
- applicable credit,
- applicable charge,
- currency,
- rounding rule.

---

## 14. Rounding Rules

Canonical monetary calculations use USD unless another currency architecture explicitly applies.

Currency values must be rounded to the currency's supported minor unit at the final charge boundary.

For USD:

**2 decimal places**

Intermediate calculations may retain higher precision.

Rounding should occur only where necessary to produce a final billable amount.

The Pricing Engine must avoid repeated intermediate rounding that can create cumulative billing errors.

---

## 15. Price Version Preservation

A subscription must retain enough pricing metadata to reconstruct how the charged amount was determined.

At minimum, billing records should preserve:

- plan identifier,
- pricing version,
- billing interval,
- base price,
- annual-discount version where applicable,
- effective date,
- currency,
- final charged amount.

Historical transactions must remain reproducible after future pricing changes.

---

## 16. Pricing Effective Dates

New pricing does not automatically rewrite historical billing records.

A pricing version must have an effective date.

When pricing changes:

- new subscriptions use the applicable active pricing version,
- existing subscriptions follow the approved migration/grandfathering policy,
- historical invoices retain their original pricing version,
- annual renewals use the pricing version authorized for that renewal event.

Pricing changes must never be inferred solely from the currently displayed website price.

---

## 17. Existing Subscriber Treatment

Existing-subscriber treatment may include:

- immediate migration,
- renewal-time migration,
- grandfathering,
- contract-specific continuation.

The selected treatment must be explicit and versioned.

The Pricing Engine must not silently migrate existing subscribers to a new price solely because the canonical current price changed.

---

## 18. Add-On Interval Separation

Subscription billing interval and add-on billing cadence are separate concepts.

Examples include:

- additional seats,
- workspace packages,
- API access,
- API usage,
- document top-ups,
- application AU top-ups.

An annual base subscription does not automatically convert every add-on into an annually discounted charge.

Each add-on follows its own canonical pricing architecture.

---

## 19. API Pricing Separation

API pricing is not derived from the subscription billing interval.

The approved architecture currently distinguishes:

- subscription eligibility for API access,
- API-only access pricing,
- API usage pricing,
- API metering.

Final API usage packages and exact API consumption rules remain suspended pending API consumption benchmarking.

Annual subscription billing must not create unapproved API discounts.

---

## 20. Application AU Separation

Application AU consumption and subscription billing interval are independent.

The annual discount does not modify the canonical per-AU top-up price unless a separate approved AU pricing rule explicitly does so.

Included application AU quantities remain suspended pending real engine-consumption benchmarking.

---

## 21. Promotion Interaction

Promotional pricing is independent from annual billing.

A promotion must explicitly specify whether it:

- applies to monthly billing,
- applies to annual billing,
- may stack with the annual discount,
- replaces the annual discount,
- applies before or after another discount.

No promotion may be assumed to stack with the 20% annual discount unless the promotion architecture explicitly permits it.

---

## 22. Trial Interaction

A free or discounted trial must not redefine the canonical billing interval.

Trial configuration must separately define:

- eligible plans,
- trial duration,
- payment requirement,
- post-trial billing interval,
- post-trial price,
- conversion behavior.

Trial pricing rules are owned by the dedicated Trial Pricing Rules architecture.

---

## 23. Contract Pricing

Enterprise or negotiated contract pricing may override standard billing-interval behavior where explicitly approved.

Contract-specific pricing must preserve:

- contract identifier,
- plan or product reference,
- agreed billing interval,
- agreed price,
- effective date,
- renewal terms,
- contract pricing version.

Contract overrides must never mutate the canonical public plan-pricing records.

---

## 24. Tax Boundary

Taxes are not part of the canonical base-price or annual-discount formula.

Applicable taxes are calculated through the approved tax architecture.

The annual-price calculation must produce the pre-tax subscription amount unless another approved jurisdiction-specific rule explicitly requires tax-inclusive pricing.

---

## 25. Payment Provider Boundary

Stripe or any future payment provider is an execution layer.

The provider may:

- create recurring billing schedules,
- collect monthly payments,
- collect annual payments,
- apply approved credits,
- apply approved prorations,
- create invoices,
- process refunds where authorized.

The provider must not be treated as the canonical source of:

- plan prices,
- annual discount percentage,
- interval policy,
- proration policy,
- grandfathering policy,
- price versioning.

LinkCraftor billing architecture remains the source of truth.

---

## 26. Failure Handling

Billing-interval resolution must fail safely when required pricing data is unavailable or inconsistent.

The executable Pricing Engine must not invent:

- a monthly price,
- an annual discount,
- an annual price,
- a proration amount,
- a billing interval.

A billing operation with unresolved canonical pricing must be rejected or suspended for correction rather than guessed.

---

## 27. Audit Requirements

Each billing-interval transaction should be traceable to:

- customer/account,
- subscription,
- plan,
- billing interval,
- pricing version,
- effective rule,
- calculation inputs,
- final amount,
- timestamp,
- responsible executable component.

Manual overrides must additionally identify:

- override reason,
- authorized actor,
- approval evidence.

---

## 28. Dependencies

This architecture depends on:

- Plan Pricing
- Product Catalog
- Subscription Architecture
- Pricing Versioning
- Pricing Governance
- Proration Architecture
- Tax Architecture
- Payment Provider Adapter
- Invoice Architecture
- Usage Metering Infrastructure

Some downstream dependencies may be implemented in later billing phases.

---

## 29. Enforcement Boundary

This document is an architecture/configuration artifact.

It does not itself:

- charge customers,
- calculate live invoices,
- calculate live proration,
- modify subscriptions,
- collect payment,
- issue refunds,
- update Stripe,
- enforce entitlements.

Those responsibilities belong to future executable billing components.

---

## 30. Runtime Eligibility

**Runtime Eligible:** No

This Markdown document defines canonical architecture and configuration policy only.

A future executable Billing Interval Resolver, Annual Pricing Calculator, Proration Calculator, or Subscription Transition Service may become runtime eligible.

---

## 31. Universal Runtime Registration System

**URRS Requirement:** Not Applicable to this document.

Future executable components derived from this architecture must receive an independent URRS assessment before runtime activation.

Potential future runtime components include:

- Billing Interval Resolver
- Annual Pricing Calculator
- Subscription Interval Transition Service
- Proration Calculator
- Renewal Pricing Resolver

---

## 32. Governance

Changes to any of the following require approved pricing governance:

- supported billing intervals,
- annual discount percentage,
- annual-price formula,
- rounding rules,
- transition behavior,
- proration policy,
- renewal behavior,
- grandfathering behavior,
- annual-discount scope.

Changes must be versioned and must not silently alter historical billing records.

---

## 33. Canonical Rules Summary

The canonical billing-interval rules are:

1. Monthly and Annual are the standard subscription billing intervals.
2. Monthly pricing comes from the canonical Plan Pricing architecture.
3. Annual billing receives a 20% discount on base subscription only.
4. Annual price is calculated as Monthly Base Price × 12 × 0.80.
5. Add-ons do not automatically inherit the annual discount.
6. Historical price versions must remain reproducible.
7. Billing transitions must preserve effective dates and pricing versions.
8. Proration requires an explicit executable billing component.
9. Payment providers execute approved billing rules but do not define them.
10. This architecture is non-runtime and does not require URRS registration.

---

## 34. Architecture Status

**Architecture Phase:** 2.2.2  
**Component:** Billing Interval & Annual Pricing Rules  
**Status:** BUILT + VERIFIED  
**Runtime Eligible:** No  
**URRS Requirement:** Not Applicable  

---

## 35. Next Architecture Component

**Phase 2.2.3 — Trial Pricing Rules**

