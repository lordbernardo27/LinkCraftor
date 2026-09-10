# LinkCraftor Product Threat Model

## Document Control

Architecture: Platform Security Architecture
Component: 2.1.3 Product Threat Model
Version: 1.0.0
Status: Active Threat Architecture

## 1. Purpose

This model identifies security threats arising from LinkCraftor product
features, workflows, customer interactions, and product-level business logic.

## 2. Product Scope

Product scope includes:

- LinkCraftor web application.
- Editor.
- Linking workflows.
- Document analysis.
- Domain connection.
- WordPress experience.
- Generative Visibility.
- Topic and semantic intelligence.
- Customer settings.
- Subscription-controlled capabilities.

## 3. Product Threat Actors

Relevant actors include:

- Anonymous attackers.
- Malicious users.
- Compromised customers.
- Fraud actors.
- Automated bots.
- Privileged insiders.
- Compromised integrations.

## 4. Product Threat Categories

Threats include:

- Business-logic abuse.
- Unauthorized feature access.
- Entitlement bypass.
- Workspace manipulation.
- Cross-user information disclosure.
- Unsafe document processing.
- Workflow tampering.
- Billing abuse.
- Resource abuse.
- Malicious integration activity.
- Unsafe export or publication actions.

## 5. Product Assets

Important assets include:

- Customer documents.
- Linking recommendations.
- Domain data.
- Workspace configuration.
- Subscription state.
- AU balances.
- API entitlements.
- WordPress credentials.
- GI prompt and result data.

## 6. Product Threat Scenarios

Examples include:

- User accesses a feature outside their entitlement.
- Manipulated workspace identifier exposes another tenant.
- Malicious document causes unsafe processing.
- Publishing workflow sends content to the wrong destination.
- Billing state is altered to obtain unauthorized usage.
- Automation is abused to create resource exhaustion.

## 7. Security Risk Relationship

Material product threats may become formal Security Risk Registry records.

## 8. Integration

This threat model is registered in:

- Central Architecture Registry.
- Security Threat Model Registry.

## 9. Completion Statement

This component establishes the canonical LinkCraftor Product Threat Model.
