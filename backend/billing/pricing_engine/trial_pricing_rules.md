# Trial Pricing Rules

**Version:** 1.0.0  
**Status:** Canonical  
**Architecture Phase:** 2.2.3  
**Last Updated:** 2026-09-11  

---

## 1. Purpose

This document defines the canonical Trial Pricing Rules architecture for LinkCraftor.

It governs:

- trial eligibility,
- trial duration configuration,
- free and discounted trials,
- trial start and end boundaries,
- payment-method requirements,
- trial-to-paid conversion,
- trial billing interval,
- plan eligibility,
- entitlement behavior,
- trial cancellation,
- abuse prevention,
- trial extensions,
- trial versioning,
- trial auditability.

This architecture does not itself define permanent base subscription prices.

Canonical plan prices are owned by:

`backend/billing/pricing_engine/plan_pricing.md`

Billing-interval rules are owned by:

`backend/billing/pricing_engine/billing_interval_annual_pricing_rules.md`

---

## 2. Trial Pricing Authority

Trial pricing is a separate commercial pricing layer.

A trial must not modify the canonical public subscription price of a plan.

Trial configuration must be represented independently from:

- plan pricing,
- annual billing discount,
- document top-ups,
- application AU top-ups,
- seat pricing,
- workspace pricing,
- API pricing,
- promotion pricing,
- enterprise contract pricing,
- marketplace pricing,
- OEM pricing.

Trial pricing affects the temporary acquisition/conversion period only.

---

## 3. Supported Trial Types

The Trial Pricing architecture must support, at minimum:

1. Free Trial
2. Discounted Trial
3. No-Trial Configuration
4. Contract-Specific Trial
5. Promotional Trial Override

Each trial type must have an explicit configuration record.

---

## 4. Free Trial

A free trial grants temporary access without charging the standard subscription price during the approved trial period.

A free trial configuration must define:

- eligible plan,
- trial duration,
- trial start rule,
- trial end rule,
- entitlement profile,
- payment-method requirement,
- post-trial conversion rule,
- post-trial billing interval,
- cancellation behavior,
- trial version.

Free trial access must not permanently alter the underlying plan price.

---

## 5. Discounted Trial

A discounted trial allows a customer to pay a temporary reduced amount during the trial period.

A discounted trial must define:

- eligible plan,
- standard price reference,
- trial price,
- discount type,
- trial duration,
- billing interval during trial,
- post-trial standard price,
- post-trial billing interval,
- conversion behavior.

The discounted trial amount must be stored separately from the canonical standard subscription price.

---

## 6. Trial Plan Eligibility

Trial eligibility must be explicitly configured per plan.

No plan should be assumed to include a trial by default.

The Trial Pricing Rules must support independent eligibility for:

- Starter,
- Pro,
- Business,
- Enterprise,
- Growth Enterprise,
- Scale Enterprise,
- Hyper Enterprise.

Current commercial trial eligibility remains configurable until explicitly approved.

No legacy trial-plan eligibility must be treated as canonical solely because it appeared in an older architecture document.

---

## 7. Trial Duration

Trial duration must be an explicit configurable value.

The architecture must support duration in:

- days,
- or another explicitly approved time unit.

The system must not hard-code a trial duration unless that duration has been commercially approved.

Current trial duration remains configurable pending explicit commercial approval.

---

## 8. Trial Start Boundary

A trial may begin only after a valid trial-start event.

Supported start events may include:

- account creation,
- subscription activation,
- explicit Start Trial action,
- successful payment-method authorization,
- administrative activation,
- approved promotional activation.

The active start rule must be explicit in the trial configuration.

---

## 9. Trial End Boundary

A trial must have a deterministic end boundary.

Trial expiration must be based on:

- trial start timestamp,
- approved trial duration,
- applicable timezone handling,
- approved extension rules.

A trial must not continue indefinitely because of missing expiration logic.

---

## 10. Payment Method Requirement

The architecture must support both:

1. Trial requiring payment method before activation
2. Trial not requiring payment method before activation

Payment-method requirements must be configured explicitly.

A payment provider must not independently decide whether LinkCraftor requires a card or payment method for a trial.

---

## 11. Trial-to-Paid Conversion

Every trial configuration must define what happens at trial expiration.

Supported outcomes may include:

1. automatic conversion to paid subscription,
2. conversion only after explicit customer approval,
3. access suspension pending payment,
4. downgrade to a separately approved free state,
5. trial termination.

The applicable outcome must be explicit.

---

## 12. Post-Trial Pricing

Post-trial pricing must resolve through the canonical Pricing Engine.

A trial must not embed a permanent independent copy of the plan price.

At conversion, the system must resolve:

- plan,
- active pricing version,
- billing interval,
- applicable promotion if any,
- approved contract override if any,
- currency,
- tax treatment.

The canonical plan price remains owned by `plan_pricing.md`.

---

## 13. Post-Trial Billing Interval

Trial expiration must resolve to an approved billing interval.

Supported standard intervals are:

- Monthly
- Annual

The selected post-trial interval must follow the Billing Interval & Annual Pricing Rules architecture.

A trial must not silently place a customer into annual billing unless explicitly configured and authorized.

---

## 14. Annual Discount Interaction

A trial is separate from the canonical 20% annual billing discount.

If a customer converts to annual billing after trial:

- the annual billing price must be resolved using the active annual pricing rules,
- the trial must not alter the canonical 20% annual discount,
- any additional trial-specific discount must be independently authorized.

Trial discounts and annual discounts must not automatically stack.

---

## 15. Promotion Interaction

Trial pricing and promotional pricing are separate pricing layers.

A promotion must explicitly state whether it may:

- create a trial,
- extend a trial,
- reduce a trial price,
- stack with a trial,
- replace a trial,
- alter conversion pricing.

No promotion may automatically modify trial rules.

---

## 16. Trial Entitlements

Trial entitlements must be explicitly defined.

A trial may provide:

- full plan entitlements,
- reduced entitlements,
- feature-limited entitlements,
- usage-limited entitlements,
- time-limited feature access.

Trial entitlement configuration must not silently modify the permanent entitlement definition of the underlying plan.

The Product Catalog and entitlement architecture remain the source of truth for permanent plan capabilities.

---

## 17. Trial Usage Limits

Trials may impose separate temporary limits on:

- document capacity,
- application AU usage,
- workspaces,
- seats,
- API access,
- feature usage,
- processing volume.

Trial-specific limits must be explicit.

They must not overwrite the standard plan entitlement configuration.

---

## 18. Included Application AU During Trial

Included application AU quantities for standard plans remain suspended pending real engine-consumption benchmarking.

Therefore trial AU allowances must also remain configurable and must not be frozen using unvalidated assumptions.

Any future trial AU allowance must reference approved AU metering and consumption benchmarks.

---

## 19. API Access During Trial

API access during a trial must be explicitly configured.

A trial must not automatically grant API access solely because the underlying plan may eventually qualify for API access.

If API trial access is permitted, the configuration must define:

- eligible API products,
- access duration,
- usage limits,
- metering behavior,
- post-trial API behavior.

Final API usage package and consumption rules remain suspended pending API consumption benchmarking.

---

## 20. Trial Cancellation

A customer must be able to cancel a trial according to approved cancellation policy.

Cancellation behavior must define:

- immediate access termination or end-of-trial access,
- whether scheduled conversion is cancelled,
- whether stored payment authorization remains,
- whether the account remains active without subscription.

Cancellation must not create an unauthorized charge.

---

## 21. Failed Trial Conversion

If an automatic trial conversion is configured and payment fails, the architecture must support:

- conversion failure state,
- payment retry handling,
- grace period if approved,
- access restriction,
- suspension,
- notification,
- eventual cancellation.

The payment provider may execute payment attempts but must not define LinkCraftor's conversion-failure policy.

---

## 22. Trial Extensions

Trial extensions must be controlled.

An extension must record:

- original trial end,
- new trial end,
- extension duration,
- reason,
- authorized actor or rule,
- approval source,
- timestamp.

Trial extensions must not silently modify the original trial history.

---

## 23. Manual Trial Overrides

Authorized administrators may require the ability to:

- grant a trial,
- deny a trial,
- extend a trial,
- terminate a trial,
- convert a trial,
- override a trial configuration.

Manual overrides must be audited.

---

## 24. Trial Abuse Prevention

The architecture must support trial-abuse controls.

Potential controls include:

- one trial per account,
- one trial per verified organization,
- payment-method fingerprint checks,
- domain checks,
- workspace ownership checks,
- identity/account correlation,
- repeated signup detection,
- suspicious-account detection.

Trial abuse controls must integrate with approved identity, fraud, and account security architecture.

---

## 25. Repeat Trial Eligibility

Repeat trials must not be assumed to be allowed.

The architecture must support:

- first-trial-only eligibility,
- cooldown periods,
- campaign-specific repeat trials,
- administrative exceptions,
- contract-specific trials.

Repeat trial eligibility must be policy-driven.

---

## 26. Trial Grace Period

A post-trial grace period is optional.

If used, it must explicitly define:

- duration,
- allowed features,
- allowed usage,
- payment-retry behavior,
- conversion behavior,
- suspension boundary.

No grace period is canonical until explicitly approved.

---

## 27. Trial State Model

The future executable trial system should support states such as:

- ELIGIBLE
- NOT_ELIGIBLE
- SCHEDULED
- ACTIVE
- EXTENDED
- EXPIRING
- CONVERSION_PENDING
- CONVERTED
- PAYMENT_FAILED
- CANCELLED
- EXPIRED
- TERMINATED

State transitions must be deterministic and auditable.

---

## 28. Trial Pricing Versioning

Every trial configuration must be versioned.

A trial record should preserve:

- trial-rule version,
- eligible plan,
- trial type,
- duration,
- trial price if applicable,
- billing interval,
- entitlement profile,
- conversion rule,
- effective date.

Existing active trials must remain reproducible after future trial-policy changes.

---

## 29. Trial Effective Dates

Trial configurations must support effective dates.

A newly introduced trial rule must not silently rewrite already-active trials.

Historical trial records must retain the rules under which they were created.

---

## 30. Grandfathering

Active trials may continue under their original trial rules when pricing or trial policy changes.

The architecture must support:

- immediate migration,
- end-of-trial migration,
- grandfathered completion,
- administrative override.

The selected treatment must be explicit.

---

## 31. Currency

Trial charges, if any, must use an approved billing currency.

Standard USD rounding follows the Billing Interval & Annual Pricing Rules architecture.

Trial pricing must not independently redefine currency rounding behavior.

---

## 32. Tax Boundary

Trial charges may be subject to tax where applicable.

Tax treatment is owned by the approved tax architecture.

A free trial with no taxable charge must not generate an artificial subscription amount solely for tax calculation.

---

## 33. Payment Provider Boundary

Stripe or another payment provider may:

- create trialing subscriptions,
- store payment methods,
- schedule conversion,
- process post-trial payment,
- report failed payment,
- terminate payment schedules.

The payment provider must not be the canonical source of:

- trial eligibility,
- trial duration,
- trial entitlement policy,
- trial conversion policy,
- trial abuse policy,
- trial versioning.

LinkCraftor remains the source of truth.

---

## 34. Failure Handling

The executable trial system must fail safely.

If required trial configuration cannot be resolved, it must not invent:

- trial duration,
- trial price,
- eligible plan,
- conversion price,
- billing interval,
- entitlement limits.

Invalid trial activation should be rejected or suspended for correction.

---

## 35. Audit Requirements

Each trial should be traceable to:

- account,
- user,
- organization where applicable,
- plan,
- trial type,
- trial-rule version,
- start timestamp,
- end timestamp,
- entitlement profile,
- payment-method state,
- conversion outcome,
- cancellation state,
- manual overrides,
- responsible runtime component.

---

## 36. Dependencies

This architecture depends on:

- Plan Pricing
- Billing Interval & Annual Pricing Rules
- Product Catalog
- Subscription Architecture
- Entitlement Architecture
- Promotion Pricing
- Pricing Versioning
- Pricing Governance
- Payment Provider Adapter
- Tax Architecture
- Identity and Account Security Architecture
- Fraud/Abuse Detection Architecture

Some dependencies may be implemented in later phases.

---

## 37. Enforcement Boundary

This document does not itself:

- start trials,
- end trials,
- charge customers,
- convert subscriptions,
- enforce trial entitlements,
- perform payment retries,
- block trial abuse,
- modify payment-provider subscriptions.

Those responsibilities belong to future executable services.

---

## 38. Runtime Eligibility

**Runtime Eligible:** No

This Markdown document defines canonical trial pricing architecture and policy only.

Future executable trial services may become runtime eligible.

---

## 39. Universal Runtime Registration System

**URRS Requirement:** Not Applicable to this document.

Future executable components derived from this architecture must receive independent URRS assessment before runtime activation.

Potential runtime components include:

- Trial Eligibility Resolver
- Trial Configuration Loader
- Trial State Manager
- Trial Conversion Service
- Trial Expiration Worker
- Trial Abuse Validator

---

## 40. Governance

Changes to the following require approved pricing governance:

- trial eligibility,
- trial type,
- trial duration,
- trial price,
- payment-method requirement,
- trial entitlement policy,
- conversion behavior,
- post-trial interval,
- repeat-trial policy,
- trial extension rules.

Changes must be versioned.

---

## 41. Current Commercial Decision Status

The following are intentionally not frozen by this architecture until separately approved:

- exact trial duration,
- exact plan eligibility,
- payment-method requirement,
- automatic vs manual conversion,
- trial-specific entitlement limits,
- trial-specific AU allowances,
- repeat-trial policy,
- grace-period duration.

Legacy trial assumptions are not automatically canonical.

---

## 42. Canonical Rules Summary

1. Trial pricing is separate from canonical plan pricing.
2. Trials must be explicitly configured per eligible plan.
3. No exact trial duration is canonical until commercially approved.
4. Trial discounts must not modify permanent plan prices.
5. Post-trial pricing resolves through the canonical Pricing Engine.
6. Trial and annual discounts do not automatically stack.
7. Trial entitlements must remain separate from permanent plan entitlements.
8. Historical trial configurations must remain reproducible.
9. Payment providers execute approved trial rules but do not define them.
10. This architecture is non-runtime and does not require URRS registration.

---

## 43. Architecture Status

**Architecture Phase:** 2.2.3  
**Component:** Trial Pricing Rules  
**Status:** BUILT — PENDING VERIFICATION  
**Runtime Eligible:** No  
**URRS Requirement:** Not Applicable  

---

## 44. Next Architecture Component

**Phase 2.2.4 — Promotion Pricing**
