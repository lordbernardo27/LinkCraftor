# LinkCraftor Residual Risk Tracking

## Document Control

Architecture: Platform Security Architecture
Component: 2.1.18 Residual Risk Tracking
Version: 1.0.0
Status: Active Security Architecture

## 1. Purpose

Residual Risk Tracking keeps the remaining security risk visible after controls
and treatment have been considered.

## 2. Core Rule

Implementation of a security control does not automatically eliminate risk.

Residual risk must be measured, recorded, reviewed, and governed.

## 3. Residual Risk Record

Each assessment should preserve:

- Assessment ID.
- Risk ID.
- Inherent score.
- Inherent severity.
- Control effectiveness.
- Residual score.
- Residual severity.
- Assessor.
- Evidence.
- Assessment time.

## 4. Residual Risk Lifecycle

Score
-> Apply Verified Controls
-> Calculate Residual Risk
-> Record
-> Review
-> Accept, Treat Further, Monitor, or Escalate

## 5. Increased Residual Risk

Residual risk may increase when:

- Control effectiveness decreases.
- Exposure increases.
- Threat conditions change.
- Tenant scope expands.
- New attack paths are identified.
- New evidence emerges.

## 6. Integration

Residual Risk Tracking integrates with:

- Security Risk Scoring Engine.
- Security Risk Registry.
- Risk Acceptance Workflow.
- Risk Treatment Registry.
- Owner Security Control Tower.

## 7. Completion Statement

This component establishes canonical LinkCraftor Residual Risk Tracking.
