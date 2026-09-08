# LinkCraftor Security Policy Hierarchy

## Document Control

| Field | Value |
|---|---|
| Architecture | Platform Security Architecture |
| Component | 1.1.12 Security Policy Hierarchy |
| Platform | LinkCraftor |
| Status | Foundational Security Governance Definition |
| Version | 1.0.0 |
| Classification | Internal Architecture |
| Canonical Location | `backend/infra/security/architecture/security_policy_hierarchy.md` |

## 1. Purpose

This document defines the canonical Security Policy Hierarchy for LinkCraftor.

The hierarchy establishes how security requirements flow from high-level
governance into enforceable technical and operational controls.

The purpose is to prevent:

- Conflicting security requirements
- Uncontrolled policy creation
- Ambiguous authority
- Duplicate policy layers
- Unapproved exceptions
- Untraceable technical requirements
- Security controls without governance
- Governance statements without implementation

## 2. Security Policy Hierarchy Objective

The hierarchy must ensure that every material LinkCraftor security requirement
can be traced from governance intent to implementation and verification.

The hierarchy must support:

- Authority
- Consistency
- Traceability
- Ownership
- Versioning
- Enforcement
- Exception governance
- Evidence
- Certification

## 3. Canonical Security Policy Hierarchy

The canonical LinkCraftor hierarchy is:

1. Platform Security Architecture
2. Security Governance Policies
3. Domain Security Policies
4. Security Standards
5. Security Control Requirements
6. Security Procedures and Runbooks
7. Technical Configurations and Enforcement
8. Verification and Evidence
9. Certification and Assurance Records

Lower levels must conform to higher levels.

A lower-level artifact may add precision but must not weaken a higher-level
requirement without an approved exception.

## 4. Level 1 — Platform Security Architecture

The Platform Security Architecture is the highest internal security design
authority.

It defines:

- Security mission
- Security objectives
- Architecture principles
- Trust model
- Defense-in-depth model
- Zero-trust principles
- Secure-by-design requirements
- Secure-by-default requirements
- Least privilege
- Separation of duties
- Fail-secure behavior
- Standards framework
- Governance structure

All security policies and controls must conform to the PSA.

## 5. Level 2 — Security Governance Policies

Security Governance Policies define enterprise-wide mandatory security rules.

Examples may include:

- Information Security Policy
- Access Control Policy
- Secure Development Policy
- Vulnerability Management Policy
- Incident Response Policy
- Cryptography Policy
- Data Protection Policy
- Backup and Recovery Policy
- Third-Party Security Policy
- Logging and Monitoring Policy

Governance policies state what must be achieved and who is accountable.

## 6. Level 3 — Domain Security Policies

Domain Security Policies translate enterprise security requirements into
specific control domains.

Domains may include:

- Identity and Authentication
- Authorization and Entitlements
- Privileged Access
- Tenant Isolation
- API Security
- Application Security
- Frontend Security
- Cloud Security
- Infrastructure Security
- Network Security
- Runtime Security
- Queue and Worker Security
- Upload Security
- Data Security
- Database Security
- Secrets and Key Management
- Logging and Detection
- Vulnerability Management
- Incident Response
- Recovery
- Third-Party Security
- AI Security

Domain policies must remain subordinate to governance policies and the PSA.

## 7. Level 4 — Security Standards

Security Standards define mandatory technical or procedural requirements.

Examples include:

- Password standard
- MFA standard
- TLS standard
- Encryption standard
- Logging standard
- Session standard
- API authentication standard
- Cloud hardening standard
- Database access standard
- Backup standard
- Secure coding standard
- Dependency management standard

Standards must be sufficiently precise to be testable.

## 8. Level 5 — Security Control Requirements

Security Control Requirements define individual enforceable requirements.

Examples include:

- All privileged accounts require MFA.
- Cross-tenant data access is prohibited.
- Production secrets must not be stored in source code.
- Authorization must be enforced server-side.
- Critical security events must be logged.
- Unsupported TLS protocols must be disabled.
- Production databases must not be publicly accessible.

Each control requirement should eventually have:

- Identifier
- Owner
- Scope
- Enforcement mechanism
- Evidence source
- Verification method
- Status

## 9. Level 6 — Security Procedures and Runbooks

Procedures and runbooks define how authorized personnel or systems execute
security-sensitive processes.

Examples include:

- Incident response runbook
- Key rotation procedure
- Privileged access approval procedure
- Backup restoration procedure
- Vulnerability remediation procedure
- Security exception procedure
- Production access procedure
- Certificate rotation procedure

Procedures must not override policy.

## 10. Level 7 — Technical Configuration and Enforcement

Technical configuration represents the actual implementation of security policy.

Examples include:

- IAM roles
- Authorization rules
- Firewall rules
- WAF policies
- Security groups
- TLS configuration
- Database permissions
- Secret policies
- Storage permissions
- Queue permissions
- Runtime restrictions
- CI/CD gates
- Code-level security checks

Technical implementation must trace back to a valid control requirement.

## 11. Level 8 — Verification and Evidence

Security controls must produce verifiable evidence.

Evidence may include:

- Automated tests
- Configuration scans
- Runtime telemetry
- Audit logs
- Security scans
- Access reviews
- Deployment records
- Policy evaluation results
- Incident records
- Backup verification
- Penetration test results
- Certification artifacts

Evidence demonstrates whether the policy hierarchy is actually enforced.

## 12. Level 9 — Certification and Assurance Records

Certification and assurance records document the verified security state.

Examples include:

- Internal security certification
- Phase certification
- Independent assessment
- Audit report
- Penetration test attestation
- Compliance assessment
- Security exception closure
- Control effectiveness review

Certification must be evidence-based.

## 13. Authority Rule

Higher levels have greater governance authority.

The order of authority is:

Platform Security Architecture
→ Governance Policy
→ Domain Policy
→ Standard
→ Control Requirement
→ Procedure
→ Technical Enforcement
→ Evidence
→ Certification

Lower-level artifacts cannot silently contradict higher-level requirements.

## 14. Conflict Resolution Rule

When two security requirements conflict:

1. Identify the authoritative source.
2. Determine which requirement is higher in the hierarchy.
3. Determine whether one requirement is stricter.
4. Apply the higher-authority requirement.
5. Apply the stricter requirement where compatible.
6. Escalate unresolved conflicts.
7. Record the decision.
8. Update affected artifacts.

Conflicts must not be resolved informally.

## 15. Stronger-Control Rule

A lower-level implementation may enforce a stronger control than the minimum
requirement.

It may not enforce a weaker control without:

- Risk assessment
- Approved exception
- Defined compensating controls
- Expiration where practical
- Evidence
- Review

## 16. Mandatory vs Advisory Content

Security documents must distinguish between mandatory and advisory language.

Mandatory language includes:

- Must
- Must not
- Required
- Prohibited

Advisory language includes:

- Should
- May
- Recommended
- Consider

Critical controls should avoid ambiguous language.

## 17. Policy Scope Rule

Every security policy must define its scope.

Scope may include:

- Platform-wide
- Environment
- Service
- Application
- API
- Tenant
- Workspace
- Data classification
- Infrastructure layer
- Team
- Operational process

Unclear scope must be treated as a governance defect.

## 18. Policy Ownership Rule

Every policy must eventually have a designated owner.

The owner is responsible for:

- Policy accuracy
- Periodic review
- Change approval coordination
- Exception oversight
- Evidence expectations
- Stakeholder coordination
- Retirement or replacement

Detailed Security Control Ownership is defined separately in PSA 1.1.13.

## 19. Policy Approval Rule

Material security policies must receive formal approval before becoming
authoritative.

Approval must identify:

- Policy name
- Version
- Owner
- Approver
- Effective date
- Scope
- Superseded version
- Review date

Draft policy must not be treated as enforced policy unless explicitly designated.

## 20. Policy Versioning Rule

Security policies must be version-controlled.

Version records should include:

- Version number
- Change date
- Change summary
- Author
- Reviewer
- Approver
- Effective date
- Superseded version
- Migration impact

Detailed architecture versioning is addressed in PSA 1.1.16.

## 21. Policy Lifecycle

The policy lifecycle is:

1. Need identified
2. Draft created
3. Risk and architecture review
4. Stakeholder review
5. Approval
6. Publication
7. Implementation
8. Verification
9. Monitoring
10. Periodic review
11. Revision or retirement

No material policy should bypass lifecycle governance without emergency
authorization.

## 22. Policy Review Frequency

Security policies must be reviewed:

- Periodically
- After material architecture change
- After significant security incident
- After major regulatory change
- After significant threat-model change
- After major platform expansion
- After relevant external-standard changes

Review frequency should reflect risk.

## 23. Policy Change Classification

Policy changes should eventually be classified as:

- Editorial
- Patch
- Minor
- Major
- Emergency

The classification must determine review, approval, migration, and communication
requirements.

## 24. Policy-to-Control Traceability

Every material security policy requirement should eventually trace to one or
more implementation controls.

The traceability path should support:

Policy
→ Standard
→ Control
→ Implementation
→ Evidence
→ Verification
→ Certification

Missing traceability is a security governance gap.

## 25. Control-to-Policy Traceability

Every material security control should trace upward to a legitimate requirement.

Controls without policy basis should be reviewed for:

- Necessity
- Scope
- Ownership
- Duplication
- Conflict
- Retirement

## 26. Policy Enforcement Rule

A policy is not complete merely because it is documented.

Where technically possible, mandatory policy requirements should be enforced by:

- Code
- Configuration
- Identity policy
- Infrastructure policy
- CI/CD gates
- Runtime controls
- Automated verification
- Deployment controls

Manual enforcement should be minimized for critical controls.

## 27. Policy Evidence Rule

Mandatory policies must define or reference suitable evidence.

Evidence may prove:

- Control exists
- Control is enabled
- Control is correctly scoped
- Control operates as intended
- Control failures are detected
- Exceptions are controlled

## 28. Policy Exception Rule

A policy exception must never silently redefine the policy.

Exceptions must be:

- Explicit
- Documented
- Risk-assessed
- Approved
- Scoped
- Time-limited where practical
- Monitored
- Reviewed
- Revoked when no longer needed

Detailed exception governance is addressed in PSA 1.1.17.

## 29. Emergency Policy Override

Emergency override of policy must be exceptional.

It requires, where applicable:

- Strong authentication
- Explicit activation
- Reason capture
- Minimum necessary scope
- Time limitation
- Logging
- Alerting
- Post-event review
- Formal closure

Emergency behavior must not create permanent policy drift.

## 30. Policy Drift

Policy drift occurs when implementation no longer matches approved policy.

Examples include:

- Changed configuration
- Disabled enforcement
- New undocumented privilege
- Unreviewed infrastructure change
- Deprecated standard still in use
- Policy updated without implementation migration

Policy drift must be detectable and remediated.

## 31. Policy Duplication

Duplicate policies should be avoided.

Where overlapping policies exist:

- Authority must be explicit.
- Scope must be differentiated.
- Conflicts must be resolved.
- Redundant requirements should be consolidated.
- Superseded policies should be retired.

## 32. Policy Retirement

Retired policies must not remain silently active.

Retirement should record:

- Policy identifier
- Final version
- Retirement date
- Replacement policy
- Migration requirements
- Archived evidence
- Approval

## 33. Regulatory and Contractual Requirements

External requirements may impose mandatory security obligations.

These may include:

- Privacy law
- Customer contracts
- Payment security obligations
- Industry requirements
- Audit commitments

Applicable external requirements must be mapped into the LinkCraftor hierarchy
rather than maintained as disconnected obligations.

## 34. External Standards Relationship

External standards such as NIST, ISO/IEC, CIS, OWASP, SOC 2, and PCI DSS are
reference frameworks or external obligations depending on applicability.

They do not override LinkCraftor internal governance unless a legal, contractual,
or certification obligation requires it.

The Security Standards Framework is defined in PSA 1.1.11.

## 35. Architecture Decision Relationship

Architecture decisions that affect security policy must be documented through
the appropriate architecture decision process.

A security-sensitive architecture decision must not silently modify policy.

Detailed Security Architecture Decision Records are defined in PSA 1.1.15.

## 36. Documentation Relationship

Security policy artifacts must reside within controlled documentation
governance.

Documentation must support:

- Canonical location
- Version
- Ownership
- Approval
- Change history
- Searchability
- Traceability
- Archival

Detailed Security Architecture Documentation governance is defined in PSA 1.1.14.

## 37. Security Technical Debt Relationship

When implementation cannot yet meet policy, the gap becomes security technical
debt unless governed as an approved exception.

The gap must not be hidden.

Detailed Security Technical Debt Management is defined in PSA 1.1.18.

## 38. Architecture Review Relationship

Material policy changes may require architecture review when they affect:

- Trust boundaries
- Identity
- Authorization
- Tenant isolation
- Data protection
- Cryptography
- Infrastructure
- Runtime
- External integrations
- Recovery
- Security monitoring

Detailed review governance is defined in PSA 1.1.19.

## 39. Owner Control Tower Visibility

The Owner's Security Control Tower must eventually expose policy-governance
status including:

- Active policies
- Draft policies
- Policy owners
- Policy versions
- Pending approvals
- Expired reviews
- Policy conflicts
- Unmapped controls
- Policy drift
- Policy exceptions
- Emergency overrides
- Retired policies
- Evidence gaps
- Certification status

Owner monitoring remains read-only by default.

## 40. Hierarchy Enforcement Principle

The policy hierarchy must remain enforceable and auditable.

Security governance must prevent:

- Lower levels weakening higher levels
- Unapproved policy changes
- Untracked exceptions
- Unowned policies
- Conflicting active policies
- Controls without policy basis
- Policies without implementation
- Certification without evidence

## 41. Relationship to Later PSA Phases

Later PSA phases implement domain policies, standards, controls, procedures,
technical enforcement, verification, and certification.

This component defines the governance hierarchy those later artifacts must
follow.

It does not itself certify all policies or controls as implemented.

## 42. Completion Criteria

Step 1.1.12 is complete when:

- The canonical security policy hierarchy is defined.
- All hierarchy levels are defined.
- Authority rules are defined.
- Conflict resolution is defined.
- Stronger-control behavior is defined.
- Mandatory and advisory language is defined.
- Scope requirements are defined.
- Ownership requirements are defined.
- Approval requirements are defined.
- Versioning requirements are defined.
- Policy lifecycle is defined.
- Review requirements are defined.
- Policy change classification is defined.
- Policy-to-control traceability is defined.
- Control-to-policy traceability is defined.
- Enforcement requirements are defined.
- Evidence requirements are defined.
- Exception rules are defined.
- Emergency override is defined.
- Policy drift is defined.
- Duplication and retirement rules are defined.
- External requirements mapping is defined.
- Standards relationship is defined.
- Architecture decision relationship is defined.
- Documentation relationship is defined.
- Technical debt relationship is defined.
- Architecture review relationship is defined.
- Owner Control Tower visibility is defined.
- The document passes structural verification.

## Certification Statement

This document defines the canonical LinkCraftor Security Policy Hierarchy.

It establishes the governance relationship between architecture, policies,
standards, controls, procedures, enforcement, evidence, and certification.

It does not certify later operational security controls as implemented.
