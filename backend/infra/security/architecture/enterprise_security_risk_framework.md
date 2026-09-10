# LinkCraftor Enterprise Security Risk Framework

## Document Control

Architecture: Platform Security Architecture
Component: 2.1.1 Enterprise Security Risk Framework
Version: 1.0.0
Status: Active Foundational Risk Architecture
Canonical Architecture ID: platform-security-architecture

## 1. Purpose

This framework establishes the canonical LinkCraftor model for identifying,
recording, owning, assessing, treating, monitoring, escalating, accepting,
closing, and reopening security risk.

## 2. Core Risk Rule

No material security risk may be silently ignored, silently accepted, or
considered resolved without evidence.

Every material risk must have:

- A unique risk ID.
- A clear risk statement.
- An affected architecture, asset, system, or process.
- A Risk Owner.
- A security domain.
- Likelihood.
- Impact.
- Existing controls.
- Treatment state.
- Residual-risk state.
- Evidence.
- Review status.

## 3. Security Risk Lifecycle

Identify
-> Analyze
-> Record
-> Assess
-> Score
-> Prioritize
-> Treat
-> Verify
-> Assess Residual Risk
-> Accept or Escalate
-> Monitor
-> Reassess
-> Close or Reopen

## 4. Risk Sources

Risk may originate from:

- Threat models.
- Vulnerabilities.
- Security incidents.
- Architecture changes.
- Security exceptions.
- Technical debt.
- Penetration testing.
- Code review.
- Infrastructure review.
- Third-party findings.
- Abuse cases.
- Misuse cases.
- Audit findings.
- Operational telemetry.

## 5. Risk Categories

Canonical domains include:

- Identity.
- Authentication.
- Authorization.
- Privileged access.
- Tenant isolation.
- API.
- Application.
- Frontend.
- Data.
- Privacy.
- Database.
- Storage.
- Infrastructure.
- Network.
- Runtime.
- Queue and worker.
- Document processing.
- Cryptography.
- Secrets.
- Supply chain.
- Monitoring.
- Abuse and fraud.
- Incident response.
- Recovery.
- Third party.
- AI and semantic systems.

## 6. Risk Statement

Recommended format:

Because of [weakness or condition], [threat or failure] may affect
[asset/component], causing [security impact].

## 7. Risk Identifier

Formal risks use identifiers in the form:

SEC-RISK-0001

Risk identifiers are unique and must not be reused.

## 8. Risk Ownership

Every material risk requires an accountable Risk Owner.

The Risk Owner is accountable for treatment, escalation, review, and governed
disposition.

## 9. Inherent Risk

Inherent risk represents risk before controls are considered.

## 10. Existing Controls

Controls must be identified and evaluated before residual risk is determined.

The existence of a control does not prove effectiveness.

## 11. Residual Risk

Residual risk is the remaining risk after controls and treatments are applied.

Residual risk must remain visible.

## 12. Likelihood

Canonical qualitative likelihood levels are:

- Rare.
- Unlikely.
- Possible.
- Likely.
- Almost Certain.

## 13. Impact

Canonical qualitative impact levels are:

- Insignificant.
- Minor.
- Moderate.
- Major.
- Severe.

## 14. Risk Severity

Canonical severity levels are:

- Low.
- Medium.
- High.
- Critical.

The detailed scoring methodology belongs to PSA 2.1.15.

## 15. Risk Treatment

Approved treatments are:

- Avoid.
- Mitigate.
- Transfer.
- Accept.

## 16. Risk Status

Canonical lifecycle states may include:

- Identified.
- Assessing.
- Treatment Planned.
- Treatment In Progress.
- Acceptance Pending.
- Accepted.
- Monitoring.
- Mitigated.
- Closed.
- Reopened.
- Superseded.

## 17. Risk Register

The operational Security Risk Registry is the structured system of record for
formal LinkCraftor security-risk records.

## 18. Threat Model Relationship

Threat models created in PSA 2.1.2 through 2.1.10 may create candidate or formal
risk records.

## 19. Security Exception Relationship

A Security Exception does not automatically constitute Risk Acceptance.

Exception records may reference Risk IDs.

## 20. Security Technical Debt Relationship

Security Technical Debt may create or sustain security risk.

Debt records may reference Risk IDs.

## 21. ADR and SARB Relationship

Material architecture decisions arising from security risk may require a
Security ADR and/or SARB review.

## 22. Central Architecture Registry Relationship

This component belongs to:

platform-security-architecture

and is registered with the LinkCraftor Central Architecture Registry.

## 23. Owner Security Control Tower

Security-risk metrics will eventually expose:

- Open risks.
- Critical risks.
- High risks.
- Overdue risks.
- Accepted risks.
- Residual risks.
- Risks without owners.
- Treatment state.
- Risk trend.

## 24. Fail-Secure Rule

Unknown or incomplete security risk must not default to Low or Accepted.

Uncertainty must remain visible and require review.

## 25. Completion Statement

This component defines the canonical Enterprise Security Risk Framework.

The operational Security Risk Registry is integrated separately and does not
replace future PSA 2.1.15 through 2.1.19 specialist components.
