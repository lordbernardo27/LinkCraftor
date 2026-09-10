# LinkCraftor Risk Acceptance Procedures

## Document Control

Architecture: Platform Security Architecture
Component: 2.1.16 Risk Acceptance Procedures
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

This component defines how LinkCraftor formally accepts residual security risk.

Risk acceptance is a governed decision, not the absence of remediation.

## 2. Core Rule

No material risk may become Accepted without:

- Formal risk identification.
- Risk ownership.
- Risk scoring.
- Residual-risk assessment.
- Explicit acceptance request.
- Authorized approval.
- Expiry or review date.
- Preserved evidence.

## 3. Acceptance Preconditions

A risk must have:

- Risk ID.
- Risk Owner.
- Likelihood.
- Impact.
- Inherent severity.
- Residual severity.
- Existing controls.
- Acceptance rationale.
- Acceptance authority.
- Review or expiry date.

## 4. Acceptance Authority

Acceptance authority increases with severity.

Low and Medium risk may follow delegated governance.

High risk requires elevated approval.

Critical risk requires Platform Owner approval and SARB review unless an
emergency governance procedure explicitly provides otherwise.

## 5. No Silent Acceptance

A risk must never become accepted merely because:

- A deadline passed.
- Remediation is difficult.
- A control does not yet exist.
- No incident has happened.
- The risk has remained open for a long time.

## 6. Acceptance Expiry

Acceptance must be time-bounded unless governance explicitly defines a valid
long-term review mechanism.

Expired acceptance requires reassessment.

## 7. Acceptance Revocation

Acceptance may be revoked when:

- Threat conditions change.
- Exposure increases.
- Control effectiveness declines.
- New evidence emerges.
- A security incident occurs.
- Scope expands.

## 8. Security Exception Relationship

Security Exception and Risk Acceptance are related but distinct.

An exception may require risk acceptance, but approval of one does not silently
approve the other.

## 9. SARB Relationship

High-impact or architectural risk may require SARB review before acceptance.

## 10. Integration

Risk acceptance is operationalized through:

- Security Risk Registry.
- Security Risk Acceptance Workflow.
- SARB governance where required.
- Security Evidence and Telemetry.
- Owner Security Control Tower.

## 11. Completion Statement

This component establishes the canonical LinkCraftor Risk Acceptance Procedure.
