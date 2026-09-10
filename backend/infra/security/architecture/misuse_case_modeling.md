# LinkCraftor Misuse-Case Modeling

## Document Control

Architecture: Platform Security Architecture
Component: 2.1.14 Misuse-Case Modeling
Version: 1.0.0
Status: Active Security Architecture

## 1. Purpose

Misuse-Case Modeling identifies unsafe, unauthorized, unintended, or
policy-violating uses of LinkCraftor capabilities.

## 2. Misuse Categories

Misuse may include:

- Incorrect privilege use.
- Wrong-tenant operation.
- Unsafe administrative action.
- Unauthorized export.
- Unauthorized publication.
- Insecure configuration.
- Unsafe API invocation.
- Excessive data access.
- Incorrect AI action.
- Misuse of automation.
- Misuse of credentials.
- Unapproved operational bypass.

## 3. Misuse Case Attributes

Each misuse case should record:

- Misuse Case ID.
- Actor.
- Capability.
- Intended behavior.
- Misuse behavior.
- Preconditions.
- Security impact.
- Required controls.
- Related risks.
- Status.

## 4. Abuse Versus Misuse

Abuse generally involves deliberate exploitation.

Misuse may be deliberate or accidental and may involve legitimate
functionality used in an unauthorized or unsafe manner.

## 5. Privileged Misuse

Administrative and owner capabilities require explicit misuse analysis because
legitimate privileged functions may cause high-impact outcomes.

## 6. AI Misuse

AI-generated recommendations, outputs, or actions must not bypass deterministic
authorization or safety controls.

## 7. Risk Relationship

Material misuse cases may create Security Risk Registry records.

## 8. Integration

Misuse cases are registered in:

- Central Architecture Registry.
- Security Misuse Case Registry.
- Security Risk Modeling Bridge.

## 9. Completion Statement

This component establishes canonical LinkCraftor Misuse-Case Modeling.
