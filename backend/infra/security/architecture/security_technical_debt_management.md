# LinkCraftor Security Technical Debt Management

## Document Control

| Field | Value |
|---|---|
| Architecture | Platform Security Architecture |
| Component | 1.1.18 Security Technical Debt Management |
| Platform | LinkCraftor |
| Status | Foundational Security Governance Definition |
| Version | 1.0.0 |
| Classification | Internal Architecture |
| Canonical Location | backend/infra/security/architecture/security_technical_debt_management.md |

## 1. Purpose

This document defines the canonical Security Technical Debt Management model
for LinkCraftor.

Security technical debt represents known security weakness, deferred security
work, incomplete security implementation, temporary architectural compromise,
or unresolved control deficiency that creates continuing security risk.

Security debt must be visible, owned, prioritized, monitored, and remediated.

## 2. Security Technical Debt Objective

The governance model exists to ensure that security debt is:

- Explicit
- Identifiable
- Risk-ranked
- Owned
- Time-bounded
- Traceable
- Monitored
- Remediated
- Reviewable
- Auditable
- Escalated when overdue

## 3. Core Security Debt Rule

Known material security debt must not remain undocumented.

If LinkCraftor knowingly accepts unfinished security work, weak implementation,
temporary architecture, unresolved control deficiency, or deferred remediation,
the debt must be recorded and governed.

## 4. Security Technical Debt Definition

Security Technical Debt may include:

- Missing security control
- Partially implemented control
- Outdated security architecture
- Deferred vulnerability remediation
- Legacy insecure component
- Temporary security workaround
- Incomplete migration
- Weak configuration
- Missing security automation
- Missing evidence
- Missing security test coverage
- Incomplete logging
- Incomplete tenant isolation
- Incomplete privileged-access control
- Dependency security weakness
- Unresolved architecture drift

## 5. What Is Not Automatically Security Debt

The following are not automatically Security Technical Debt:

- Cosmetic defects
- Non-security feature backlog
- Pure documentation formatting issues
- Product ideas
- Ordinary feature requests
- Performance improvements with no security consequence

A backlog item becomes security debt when it creates or preserves material
security risk.

## 6. Security Debt Identifier

Every material security debt record should have a unique identifier.

Recommended format:

SEC-DEBT-0001

Examples:

- SEC-DEBT-0001
- SEC-DEBT-0002
- SEC-DEBT-0040

Identifiers must not be reused.

## 7. Security Debt Required Fields

Every material security debt record should contain:

- Debt ID
- Title
- Status
- Security domain
- Description
- Root cause
- Security impact
- Risk level
- Likelihood
- Impact
- Affected assets
- Affected controls
- Debt owner
- Risk owner where applicable
- Detection date
- Target remediation date
- Interim controls
- Dependencies
- Remediation plan
- Evidence
- Related exception
- Related ADR
- Related version
- Review date
- Escalation status
- Closure evidence

## 8. Security Debt Status Model

Security Technical Debt should use explicit lifecycle states.

Statuses may include:

- Identified
- Under Assessment
- Accepted Temporarily
- Planned
- In Remediation
- Verification Pending
- Blocked
- Overdue
- Escalated
- Closed
- Rejected as Debt

## 9. Security Debt Sources

Security debt may originate from:

- Security reviews
- Architecture reviews
- Vulnerability scans
- Penetration testing
- Incident response
- Code review
- Infrastructure review
- Runtime review
- Audit
- Certification
- Change Detection
- Architecture drift detection
- Security exceptions
- Dependency changes
- Operational failures
- Manual discovery

## 10. Debt Owner

Every material security debt item must have an accountable owner.

The Debt Owner is responsible for:

- Maintaining the debt record
- Coordinating remediation
- Tracking dependencies
- Tracking interim controls
- Providing evidence
- Reporting status
- Escalating blockers
- Coordinating closure

Unowned security debt is prohibited.

## 11. Risk Owner

Where residual security risk is being accepted temporarily, a Risk Owner must
be identified.

The Risk Owner is accountable for understanding the risk and ensuring that the
accepted risk remains within authorized tolerance.

## 12. Security Debt Classification

Security debt should be classified by security significance.

Potential classes include:

- Low
- Medium
- High
- Critical

Classification should consider:

- Exploitability
- Exposure
- Tenant impact
- Data impact
- Privilege impact
- Authentication impact
- Authorization impact
- Availability impact
- Detection weakness
- Recovery weakness
- Regulatory impact where applicable

## 13. Risk Assessment

Each material debt item should include a risk assessment covering:

- Threat
- Likelihood
- Impact
- Existing controls
- Missing controls
- Interim controls
- Residual risk
- Risk owner
- Escalation threshold

## 14. Root Cause

Security debt should identify its root cause.

Examples include:

- Legacy architecture
- Time pressure
- Dependency limitation
- Migration delay
- Missing capability
- Incomplete refactoring
- Unsupported component
- Configuration gap
- Missing automation
- Historical design decision
- Resource constraint

The root cause should not be confused with the security symptom.

## 15. Interim Controls

Where immediate remediation is not possible, interim controls should reduce
risk.

Examples may include:

- Additional monitoring
- Reduced privilege
- Access restriction
- Network restriction
- Feature restriction
- Manual review
- Temporary isolation
- Shortened token lifetime
- Increased logging
- Stronger authentication
- Operational approval

Interim controls must be owned and verifiable.

## 16. Remediation Plan

Every material debt record should have a remediation plan.

The plan should define:

- Required work
- Responsible implementer
- Debt owner
- Dependencies
- Target date
- Validation method
- Evidence
- Rollback where relevant
- Closure criteria

## 17. Target Remediation Date

Material security debt must have a target remediation date.

Open-ended debt is prohibited unless formally governed through authorized risk
acceptance and periodic review.

## 18. Remediation Priority

Security debt remediation should be prioritized according to:

- Risk level
- Exploitability
- User impact
- Tenant impact
- Data sensitivity
- Privilege exposure
- External exposure
- Existing compensating controls
- Incident history
- Regulatory relevance
- Dependency urgency

## 19. Critical Security Debt

Critical Security Technical Debt requires immediate escalation.

Examples may include:

- Known cross-tenant access path
- Authentication bypass
- Authorization bypass
- Exposed production secret
- Uncontrolled privileged access
- Critical unpatched remotely exploitable vulnerability
- Broken encryption
- Failed security logging for critical systems
- Unrecoverable backup deficiency
- Major fail-open condition

Critical debt should not remain in a normal backlog.

## 20. High-Risk Security Debt

High-risk debt requires accelerated remediation and management visibility.

It should receive:

- Named owner
- Short remediation deadline
- Frequent review
- Interim controls
- Escalation
- Certification impact evaluation

## 21. Medium and Low Security Debt

Medium and Low debt may use longer remediation windows where justified.

They still require:

- Ownership
- Risk classification
- Target date
- Review
- Closure evidence

Low severity must not be used to hide accumulated systemic weakness.

## 22. Debt Aging

Security debt must be monitored for age.

Age should be measured from the date the debt was formally identified.

Older unresolved debt should receive increasing scrutiny.

## 23. Overdue Debt

Security debt becomes overdue when the target remediation date is missed without
approved revision.

Overdue debt must be surfaced and reviewed.

## 24. Repeated Deferral

Repeated remediation deferral is a governance warning.

Repeated deferrals should trigger:

- Risk reassessment
- Escalation
- Review of root cause
- Review of interim controls
- Review of resource allocation
- Potential Architecture Review Board review

## 25. Debt Escalation

Security debt should be escalated when:

- Risk increases
- Target date is missed
- Interim controls fail
- Security incident occurs
- Scope expands
- Dependency worsens
- Similar debt repeats
- Critical architecture is affected

## 26. Security Debt and Security Exceptions

Security debt and security exceptions are related but distinct.

A Security Exception is an approved temporary deviation from a requirement.

Security Technical Debt is unresolved security work or weakness that requires
remediation.

An exception may create or expose technical debt.

An exception must reference related debt where applicable.

## 27. Security Debt and Security ADRs

A Security ADR may intentionally accept temporary architecture that creates
security debt.

Where this occurs, the ADR should identify:

- Debt created
- Risk
- Owner
- Target remediation
- Interim controls
- Review trigger

## 28. Security Debt and Architecture Versioning

Security debt may arise when architecture migration is incomplete.

Examples include:

- Old version remains active
- Migration partially complete
- Version mismatch
- Deprecated component remains in use
- New controls not fully deployed

Version-related debt must identify the affected architecture version.

## 29. Security Debt and Change Detection

Architecture Change Detection should eventually identify changes that create or
reveal security debt.

Examples include:

- Implementation diverges from architecture
- Required control disappears
- New dependency introduces weakness
- Security configuration weakens
- Production component becomes undocumented
- Version migration remains incomplete

## 30. Security Debt and Architecture Drift

Architecture drift that creates material security risk must become tracked
Security Technical Debt if it cannot be corrected immediately.

The record should identify:

- Expected architecture
- Actual implementation
- Difference
- Security impact
- Remediation path

## 31. Security Debt and Vulnerability Management

Deferred vulnerability remediation may create security debt.

The debt should identify:

- Vulnerability
- Severity
- Affected asset
- Reason remediation is delayed
- Interim controls
- Patch or fix target
- Evidence
- Risk owner

## 32. Security Debt and Identity

Identity-related debt may include:

- Missing MFA enforcement
- Legacy authentication
- Weak recovery process
- Incomplete account lifecycle controls
- Stale service identities
- Incomplete identity logging

## 33. Security Debt and Authorization

Authorization-related debt may include:

- Excessive permissions
- Missing resource-level authorization
- Legacy role model
- Incomplete entitlement review
- Hard-coded authorization logic
- Missing privilege separation

## 34. Security Debt and Tenant Isolation

Tenant-isolation security debt must be treated with heightened severity.

Examples include:

- Missing tenant filter
- Shared storage without required isolation
- Worker execution without tenant context
- Cross-workspace authorization ambiguity
- Shared cache exposure

## 35. Security Debt and Privileged Access

Privileged-access debt may include:

- Permanent elevated accounts
- Shared admin credentials
- Missing privileged-session logging
- Missing just-in-time elevation
- Incomplete privileged review
- Uncontrolled emergency access

## 36. Security Debt and Cryptography

Cryptographic debt may include:

- Deprecated algorithms
- Delayed key rotation
- Legacy key storage
- Missing encryption
- Expired certificates
- Weak certificate governance
- Incomplete secret rotation

## 37. Security Debt and Logging

Logging and detection debt may include:

- Missing critical event logging
- Incomplete security telemetry
- Missing alerting
- Insufficient retention
- Weak evidence integrity
- Undetected telemetry failure

## 38. Security Debt and Infrastructure

Infrastructure security debt may include:

- Legacy network exposure
- Overly broad security groups
- Weak IAM
- Unmanaged infrastructure
- Configuration drift
- Missing infrastructure scanning
- Unsupported operating systems

## 39. Security Debt and Runtime

Runtime security debt may include:

- Missing workload identity
- Excess runtime privilege
- Incomplete runtime validation
- Missing isolation
- Unregistered execution path
- Weak failure containment

## 40. Security Debt and Third Parties

Third-party security debt may arise from:

- Unsupported provider controls
- Weak provider security
- Deprecated integration
- Missing vendor review
- Unresolved provider vulnerability
- Excessive third-party privilege
- Missing exit or replacement strategy

## 41. Security Debt and Recovery

Recovery-related debt may include:

- Untested backups
- Missing restore automation
- Incomplete disaster-recovery plan
- Recovery dependency weakness
- Missing ransomware protection
- Unvalidated recovery objectives

## 42. Debt Evidence

Every material security debt item should preserve evidence.

Evidence may include:

- Scan result
- Test failure
- Architecture diff
- Incident record
- Exception record
- Code reference
- Configuration reference
- Review finding
- Audit finding
- Remediation test
- Closure verification

## 43. Debt Verification

Security debt must not be closed solely because remediation work was reported as
finished.

Closure verification should confirm:

- Required remediation exists
- Risk has been reduced or removed
- Interim controls are retired where appropriate
- Tests pass
- Evidence exists
- Related exceptions are closed or updated
- Related architecture is synchronized
- Registry status is updated

## 44. Debt Closure

A security debt item may be closed when:

- Remediation is complete
- Verification passes
- Evidence is captured
- Residual risk is acceptable
- Related exception state is resolved
- Required documentation is updated

## 45. Debt Reopening

Closed security debt may be reopened when:

- Remediation regresses
- Control fails
- Similar vulnerability reappears
- Architecture changes invalidate closure
- Evidence proves closure was incomplete

## 46. Debt Registry

LinkCraftor should eventually maintain a Security Technical Debt Registry.

Each record should include:

- Debt ID
- Title
- Status
- Security domain
- Risk level
- Description
- Root cause
- Owner
- Risk owner
- Affected controls
- Affected assets
- Detection date
- Target remediation date
- Interim controls
- Related exception
- Related ADR
- Related architecture version
- Review date
- Escalation status
- Evidence status
- Closure date

## 47. Debt Registry Authority

The Security Technical Debt Registry should become the canonical source for
security debt state.

Informal notes, tickets, and messages must not override the canonical registry.

## 48. Orphaned Security Debt

Security debt must not remain active without:

- Owner
- Risk classification
- Target remediation date
- Remediation path

Orphaned debt must be escalated.

## 49. Duplicate Debt Detection

The future system should detect duplicate or overlapping security debt.

Duplicates should be:

- Linked
- Consolidated where appropriate
- Assigned clear ownership
- Prevented from distorting metrics

## 50. Security Debt Dependency Tracking

Debt records should identify blocking dependencies.

Examples include:

- External provider
- Architecture migration
- Infrastructure change
- API change
- Database migration
- New security capability
- Vendor fix
- Credential rotation

## 51. Security Debt Metrics

The system should eventually measure:

- Total open debt
- Debt by risk level
- Debt by security domain
- Debt by owner
- Debt by age
- Overdue debt
- Critical debt
- High-risk debt
- Debt linked to exceptions
- Debt linked to incidents
- Debt linked to architecture drift
- Average remediation time
- Reopened debt
- Repeated debt patterns

## 52. Security Debt Trend

Security debt should be evaluated as a trend, not only as individual findings.

Important signals include:

- Debt increasing month over month
- Critical debt accumulating
- Repeated overdue remediation
- Recurring root causes
- Repeated control failures
- Excessive exception-driven debt

## 53. Security Debt Budget

LinkCraftor may eventually establish a Security Debt Budget.

The budget may define acceptable thresholds for:

- Total open debt
- High-risk debt
- Critical debt
- Maximum debt age
- Maximum overdue items
- Repeated deferrals

A debt budget must not permit known critical risk to remain unmanaged.

## 54. Security Debt Quality Gate

Security debt should affect release and certification gates.

Potential blocking conditions include:

- Unresolved critical debt
- Critical tenant-isolation debt
- Critical authentication debt
- Critical authorization debt
- Uncontrolled privileged-access debt
- Critical exposed-secret debt
- Critical recovery debt

## 55. Release Impact

Material security debt should be evaluated before production release.

Possible outcomes include:

- Release allowed
- Release allowed with approved exception
- Release requires remediation
- Release blocked

## 56. Certification Impact

Security certification must account for unresolved security debt.

Certification should evaluate:

- Debt count
- Severity
- Age
- Ownership
- Interim controls
- Remediation status
- Exception status
- Evidence

Unresolved critical security debt may block certification.

## 57. Architecture Review Board Relationship

The Security Architecture Review Board may review:

- Critical debt
- Long-lived high-risk debt
- Repeatedly deferred debt
- Architecture-wide debt
- Cross-domain debt
- Debt requiring major architecture change

Detailed board governance is defined in PSA 1.1.19.

## 58. Security Debt Review Frequency

Security debt must be reviewed periodically.

Review frequency should increase with risk.

A future policy may define examples such as:

- Critical: continuous or immediate management
- High: weekly
- Medium: monthly
- Low: quarterly

Final operational frequencies may be defined later.

## 59. Owner Control Tower Visibility

The Owner's Security Control Tower must eventually expose:

- Total security debt
- Open debt
- Critical debt
- High-risk debt
- Medium debt
- Low debt
- Overdue debt
- Debt by domain
- Debt by owner
- Debt by age
- Debt linked to exceptions
- Debt linked to architecture drift
- Debt linked to incidents
- Repeated deferrals
- Reopened debt
- Remediation progress
- Certification impact

Owner monitoring remains read-only by default.

## 60. Security Debt Escalation Workflow

The future canonical workflow should be:

Debt identified
to Risk classification
to Owner assignment
to Interim-control assessment
to Remediation planning
to Target-date assignment
to Monitoring
to Escalation if overdue
to Remediation
to Verification
to Closure

## 61. Security Debt Failure Behavior

If debt state cannot be determined reliably:

- Do not falsely mark debt closed
- Do not suppress overdue status
- Do not remove risk classification
- Preserve evidence
- Escalate uncertainty
- Require controlled resolution

## 62. Security Debt and Fail-Secure Design

Security debt must not silently justify fail-open behavior.

Where unresolved debt affects a critical control, secure fallback should be
preferred where practical.

## 63. Security Debt and Control Ownership

Every debt item affecting a security control should reference that control's
accountable owner.

The debt owner and control owner may be different roles.

Their responsibilities must remain explicit.

## 64. Security Debt and Documentation

Security debt records are governed security artifacts.

They must comply with documentation requirements for:

- Canonical storage
- Ownership
- Versioning
- Traceability
- Protection
- Review
- Evidence
- Auditability

## 65. Relationship to Later PSA Phases

Later PSA phases may create domain-specific Security Technical Debt.

This foundational component governs debt management across all PSA domains.

It does not certify that a future automated Security Technical Debt Registry or
remediation workflow engine is operationally implemented.

## 66. Completion Criteria

Step 1.1.18 is complete when:

- The core Security Debt rule is defined.
- Security Technical Debt is defined.
- Non-debt distinctions are defined.
- Debt identifiers are defined.
- Required debt fields are defined.
- Debt lifecycle states are defined.
- Debt sources are defined.
- Debt ownership is defined.
- Risk ownership is defined.
- Debt classification is defined.
- Risk assessment is defined.
- Root-cause handling is defined.
- Interim controls are defined.
- Remediation planning is defined.
- Target remediation dates are defined.
- Remediation priority is defined.
- Critical debt handling is defined.
- High-risk debt handling is defined.
- Debt aging is defined.
- Overdue debt is defined.
- Repeated deferral is defined.
- Escalation is defined.
- Exception relationship is defined.
- ADR relationship is defined.
- Versioning relationship is defined.
- Change Detection relationship is defined.
- Architecture drift relationship is defined.
- Vulnerability relationship is defined.
- Tenant-isolation debt is defined.
- Privileged-access debt is defined.
- Cryptographic debt is defined.
- Logging debt is defined.
- Infrastructure debt is defined.
- Runtime debt is defined.
- Third-party debt is defined.
- Recovery debt is defined.
- Evidence is defined.
- Verification is defined.
- Closure is defined.
- Reopening is defined.
- Security Technical Debt Registry is defined.
- Registry authority is defined.
- Orphaned debt is defined.
- Duplicate detection is defined.
- Dependency tracking is defined.
- Debt metrics are defined.
- Debt trends are defined.
- Debt Budget concept is defined.
- Quality-gate impact is defined.
- Release impact is defined.
- Certification impact is defined.
- Architecture Review Board relationship is defined.
- Review frequency is defined.
- Owner Control Tower visibility is defined.
- Escalation workflow is defined.
- Failure behavior is defined.
- Fail-Secure relationship is defined.
- Control Ownership relationship is defined.
- Documentation relationship is defined.
- The document passes structural verification.

## Certification Statement

This document defines the canonical LinkCraftor Security Technical Debt
Management model.

It establishes how security debt is identified, risk-classified, owned,
prioritized, monitored, remediated, verified, escalated, audited, and connected
to security exceptions, architecture governance, releases, and certification.

It does not certify that the future automated Security Technical Debt Registry
and remediation workflow system is operationally implemented.
