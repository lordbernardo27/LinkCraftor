# LinkCraftor Security Risk Scoring

## Document Control

Architecture: Platform Security Architecture
Component: 2.1.15 Security Risk Scoring
Version: 1.0.0
Status: Active Security Architecture

## 1. Purpose

This component defines the canonical Security Risk Scoring model used to
convert likelihood and impact into a consistent risk severity.

## 2. Likelihood Scale

Likelihood:

1 - Rare
2 - Unlikely
3 - Possible
4 - Likely
5 - Almost Certain

## 3. Impact Scale

Impact:

1 - Insignificant
2 - Minor
3 - Moderate
4 - Major
5 - Severe

## 4. Base Risk Score

Base Risk Score:

Likelihood x Impact

Possible score range:

1 through 25

## 5. Severity Bands

Canonical severity bands:

1-4   = Low
5-9   = Medium
10-16 = High
17-25 = Critical

## 6. Inherent Risk

Inherent risk is calculated before effective controls are credited.

## 7. Control Effectiveness

Control effectiveness may be represented as a percentage from 0 through 100.

Control effectiveness must be evidence-supported.

## 8. Residual Score

Residual Score is calculated from the inherent score after applying verified
control effectiveness.

Residual Score must never be less than 1 while the risk remains open.

## 9. Fail-Secure Scoring

Missing likelihood, impact, or required assessment context must not
automatically produce Low risk.

Unassessed risk remains unscored.

## 10. Critical Override

Certain conditions may justify Critical classification independent of the
numerical matrix, including credible platform-wide or cross-tenant compromise.

Such overrides must be explicitly recorded and governed.

## 11. Risk Registry Integration

The scoring engine may write:

- likelihood.
- impact.
- inherent_score.
- inherent_severity.
- control_effectiveness.
- residual_score.
- residual_severity.
- severity.

to the Security Risk Registry.

## 12. Completion Statement

This component establishes the canonical LinkCraftor Security Risk Scoring
model and operational scoring engine.
