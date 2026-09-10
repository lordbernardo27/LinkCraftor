# LinkCraftor Attack-Path Modeling

## Document Control

Architecture: Platform Security Architecture
Component: 2.1.12 Attack-Path Modeling
Version: 1.0.0
Status: Active Security Architecture

## 1. Purpose

Attack-Path Modeling identifies sequences of weaknesses, trust-boundary
crossings, privileges, identities, services, and resources that may allow an
attacker to progress toward a security objective.

## 2. Attack Path

An attack path may include:

Entry Point
-> Initial Access
-> Authentication Bypass or Compromise
-> Privilege Expansion
-> Trust Boundary Crossing
-> Lateral Movement
-> Target Asset
-> Security Impact

## 3. Path Attributes

Each attack path should record:

- Attack Path ID.
- Entry point.
- Threat actor.
- Preconditions.
- Ordered steps.
- Trust boundaries crossed.
- Required privileges.
- Controls encountered.
- Target asset.
- Potential impact.
- Related threat models.
- Related risks.
- Status.

## 4. Chained Risk Rule

Several individually moderate weaknesses may form a High or Critical attack
path when chained together.

## 5. Tenant Attack Paths

Cross-tenant attack paths require explicit consideration of:

- Workspace identifiers.
- Authorization boundaries.
- Cache boundaries.
- Queue boundaries.
- Worker boundaries.
- Search boundaries.
- Vector boundaries.
- Storage boundaries.

## 6. Privilege Escalation Paths

Attack paths must consider vertical and horizontal privilege escalation.

## 7. Infrastructure Paths

Infrastructure paths may include:

Internet
-> Exposed Service
-> Runtime
-> IAM Role
-> Secret
-> Database or Storage

## 8. Risk Relationship

Material attack paths may create Security Risk Registry records.

## 9. Integration

Attack paths are registered in:

- Central Architecture Registry.
- Security Attack Path Registry.
- Security Risk Modeling Bridge.

## 10. Completion Statement

This component establishes canonical LinkCraftor Attack-Path Modeling.
