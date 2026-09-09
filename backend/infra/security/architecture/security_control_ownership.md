# LinkCraftor Security Control Ownership

## Document Control

| Field | Value |
|---|---|
| Architecture | Platform Security Architecture |
| Component | 1.1.13 Security Control Ownership |
| Platform | LinkCraftor |
| Status | Foundational Security Governance Definition |
| Version | 1.0.0 |
| Classification | Internal Architecture |
| Canonical Location | `backend/infra/security/architecture/security_control_ownership.md` |

## 1. Purpose

This document defines the canonical Security Control Ownership model for
LinkCraftor.

Every material security control must have clear accountability.

Security controls must not exist without an identifiable owner responsible for
their design intent, implementation coordination, evidence, review, exception
handling, and lifecycle.

## 2. Security Control Ownership Objective

The ownership model exists to prevent:

- Unowned security controls
- Ambiguous accountability
- Duplicate responsibility
- Security gaps between teams
- Controls without maintenance
- Controls without evidence
- Controls without review
- Controls without escalation
- Controls silently becoming obsolete
- Exceptions without responsible oversight

## 3. Core Ownership Rule

Every material LinkCraftor security control must eventually have one clearly
designated accountable owner.

The owner may delegate operational tasks, but accountability must remain
explicit.

A control must not be considered fully governed if ownership is unknown.

## 4. Control Ownership Model

Each security control should eventually define:

- Control identifier
- Control name
- Control objective
- Security domain
- Accountable owner
- Operational custodian
- Technical implementer
- Reviewer
- Approver where applicable
- Scope
- Environment
- Evidence source
- Verification method
- Exception authority
- Escalation path
- Review frequency
- Current status

## 5. Accountable Owner

The Accountable Owner is responsible for the control's overall security outcome.

Responsibilities include:

- Ensuring the control has a valid objective
- Confirming scope
- Ensuring implementation exists
- Ensuring evidence exists
- Coordinating verification
- Reviewing deficiencies
- Approving or escalating remediation
- Monitoring exceptions
- Supporting certification
- Initiating retirement or replacement when appropriate

Accountability cannot be silently transferred.

## 6. Operational Custodian

The Operational Custodian manages the day-to-day operation of the control.

Responsibilities may include:

- Routine operation
- Monitoring
- Maintenance
- Configuration updates
- Evidence generation
- Incident escalation
- Operational reporting

The custodian does not automatically become the accountable owner.

## 7. Technical Implementer

The Technical Implementer builds or configures the control.

Examples include:

- Backend engineer
- Infrastructure engineer
- Security engineer
- DevOps engineer
- Database engineer
- Platform engineer

Implementation authority does not automatically include approval authority.

## 8. Independent Reviewer

Material security controls should have an independent reviewer where risk
warrants it.

The reviewer evaluates:

- Design correctness
- Implementation correctness
- Scope
- Evidence
- Exceptions
- Control effectiveness
- Residual risk

The reviewer should not simply validate their own implementation.

## 9. Control Approver

Certain controls may require formal approval before becoming authoritative or
production-active.

Approval may be required for:

- Privileged access controls
- Authentication changes
- Authorization changes
- Tenant-isolation changes
- Cryptographic controls
- Security-policy enforcement
- Production firewall changes
- Recovery controls
- High-risk security exceptions

Approval authority must be explicitly defined.

## 10. RACI Model

Where useful, LinkCraftor may use a RACI-style responsibility model:

- Responsible — performs the work
- Accountable — owns the outcome
- Consulted — provides required input
- Informed — receives relevant status

Each material security control should have exactly one clearly accountable role,
even if multiple parties are responsible for execution.

## 11. No Shared Accountability Ambiguity

Multiple teams may participate in a control, but accountability must not become
ambiguous.

Statements such as:

- "Engineering owns it"
- "Security owns it"
- "Infrastructure handles it"

are insufficient unless a specific accountable role is defined.

## 12. Platform Security Owner

The Platform Security Owner is responsible for overarching security governance.

Responsibilities may include:

- Maintaining the Platform Security Architecture
- Coordinating security policy
- Overseeing security control ownership
- Tracking critical security gaps
- Coordinating security certification
- Monitoring exception governance
- Escalating systemic security risk

This role does not automatically execute every security control.

## 13. Domain Security Owners

Each major security domain should eventually have an accountable owner.

Domains include:

- Identity and Authentication
- Authorization and Entitlements
- Privileged Access
- Tenant Isolation
- Session and Token Security
- API Security
- Application Security
- Frontend Security
- Cloud Security
- Infrastructure Security
- Network Security
- Runtime Security
- Queue and Worker Security
- Upload and Document Security
- Data Security
- Database Security
- Cryptography and Secrets
- Logging and Detection
- Vulnerability Management
- Abuse and Fraud Protection
- Incident Response
- Recovery
- Third-Party Security
- AI Security

## 14. Identity Control Ownership

Identity controls should have clearly defined ownership for:

- Account lifecycle
- Authentication
- MFA
- Password policy
- Federation
- Identity provider configuration
- Account recovery
- Authentication logging

Ownership must distinguish platform identity governance from ordinary user
administration.

## 15. Authorization Control Ownership

Authorization controls must define accountability for:

- Role definitions
- Permission models
- Entitlements
- Resource-level authorization
- Tenant authorization
- Workspace authorization
- Privilege escalation prevention
- Authorization policy changes

Authorization failures must have a clear escalation owner.

## 16. Privileged Access Control Ownership

Privileged-access controls require explicit ownership.

Responsibilities include:

- Privileged role definition
- Approval process
- Temporary elevation
- Break-glass access
- Privilege review
- Privilege revocation
- Audit evidence

No privileged-access system should exist without accountable governance.

## 17. Tenant Isolation Ownership

Tenant and workspace isolation must have explicit ownership.

The owner is accountable for:

- Isolation design
- Cross-tenant prevention
- Workspace boundaries
- Tenant-scoped authorization
- Tenant-aware storage
- Tenant-aware runtime execution
- Verification evidence
- Isolation incident escalation

## 18. API Security Ownership

API security ownership should cover:

- Authentication
- Authorization
- Schema validation
- Rate limiting
- Abuse protection
- API inventory
- API versioning
- Sensitive endpoint governance
- API security testing

## 19. Application Security Ownership

Application security ownership should include:

- Secure design
- Secure coding requirements
- Input validation
- Business-logic protection
- Error handling
- Security testing
- Vulnerability remediation
- Application security evidence

## 20. Cloud and Infrastructure Ownership

Cloud and infrastructure controls must have accountable owners for:

- IAM
- Network boundaries
- Security groups
- Encryption
- Logging
- Compute security
- Storage security
- Backup
- Infrastructure configuration
- Environment separation

Cloud-provider responsibility does not replace LinkCraftor accountability.

## 21. Runtime and Workload Ownership

Runtime controls must define ownership for:

- Runtime registration
- Runtime handlers
- Workload identity
- Execution permissions
- Runtime isolation
- Runtime validation
- Failure containment
- Runtime evidence

## 22. Queue and Worker Ownership

Queue and worker controls must define accountability for:

- Queue permissions
- Worker identity
- Worker capability
- Job validation
- Tenant context propagation
- Replay protection
- Failure handling
- Worker isolation
- Queue evidence

## 23. Upload and Document Security Ownership

Upload and document-processing controls must have ownership for:

- File validation
- MIME validation
- Size limits
- Archive handling
- Malware protection
- Parser safety
- Quarantine
- Document isolation
- Processing evidence

## 24. Data Security Ownership

Data-security ownership should cover:

- Data classification
- Data access
- Encryption
- Retention
- Deletion
- Privacy controls
- Data export
- Sensitive data handling
- Data incident escalation

## 25. Database Ownership

Database security controls must distinguish:

- Database administration
- Access-control ownership
- Schema security
- Tenant filtering
- Backup
- Restore
- Encryption
- Audit logging

Database administration alone does not imply security governance ownership.

## 26. Cryptography and Secrets Ownership

Cryptographic and secret controls must define ownership for:

- Key lifecycle
- Secret lifecycle
- Certificate lifecycle
- Rotation
- Revocation
- Recovery
- Algorithm standards
- Cryptographic configuration

Workloads consuming secrets must not automatically own secret governance.

## 27. Logging and Detection Ownership

Security logging and detection must have accountable owners for:

- Event requirements
- Log integrity
- Retention
- Alerting
- Detection logic
- Telemetry health
- Evidence preservation
- Detection failure escalation

## 28. Vulnerability Management Ownership

Vulnerability management controls must define ownership for:

- Vulnerability discovery
- Classification
- Prioritization
- Remediation
- Verification
- Exception handling
- Risk acceptance
- Closure evidence

Discovery and remediation may be performed by different roles.

## 29. Incident Response Ownership

Incident-response ownership must distinguish roles such as:

- Incident commander
- Investigator
- Containment operator
- Recovery operator
- Evidence custodian
- Communications owner

The incident lifecycle must have clear accountability.

## 30. Backup and Recovery Ownership

Backup and recovery controls must define accountability for:

- Backup policy
- Backup creation
- Backup monitoring
- Restore authorization
- Restore execution
- Recovery testing
- Recovery evidence

Ownership should respect separation-of-duties requirements.

## 31. Third-Party Control Ownership

Every material third-party dependency should have an accountable internal owner.

Examples include:

- AWS
- Stripe
- WordPress integrations
- Email providers
- Authentication providers
- AI providers
- Analytics providers
- External APIs

Third-party operation does not eliminate LinkCraftor responsibility.

## 32. AI Security Control Ownership

Where AI systems are used, ownership should cover:

- Provider access
- Prompt/data handling
- Model integration security
- Output validation
- Tenant isolation
- Abuse controls
- Provider failure behavior
- AI-specific incident escalation

## 33. Control Owner Assignment

Control ownership must be assigned deliberately.

Assignment should consider:

- Technical competence
- Organizational authority
- Operational responsibility
- Risk level
- Separation of duties
- Conflict of interest
- Availability
- Escalation capability

Ownership must not be assigned solely because someone created the control.

## 34. Ownership Acceptance

A designated owner should explicitly accept ownership where formal governance is
required.

Ownership records should eventually include:

- Owner identity or role
- Assignment date
- Scope
- Responsibilities
- Approval
- Review date

## 35. Ownership Transfer

Ownership transfer must be controlled.

A transfer should record:

- Existing owner
- New owner
- Effective date
- Reason
- Outstanding issues
- Open exceptions
- Evidence status
- Approval where required

A control must not become ownerless during transfer.

## 36. Owner Unavailability

If a control owner becomes unavailable:

1. An alternate responsible authority must be identified.
2. Critical operations must continue securely.
3. Open exceptions must remain governed.
4. Review obligations must not silently lapse.
5. Permanent reassignment must occur where appropriate.

## 37. Ownership Review

Control ownership must be reviewed periodically.

Review should confirm:

- Owner still exists
- Owner still has authority
- Scope is accurate
- Control remains applicable
- Evidence is current
- Exceptions are valid
- Review frequency remains appropriate
- Escalation path remains valid

## 38. Ownership and Separation of Duties

Ownership must conform to Separation-of-Duties Principles.

A control owner should not automatically have unrestricted ability to:

- Implement
- Approve
- Disable
- Delete evidence
- Approve their own exception
- Certify their own high-risk control

High-risk controls require appropriate independence.

## 39. Ownership and Least Privilege

Control ownership does not automatically grant operational privilege.

An owner may be accountable for a control without possessing unrestricted
technical access to the controlled system.

Privileges must remain separately governed.

## 40. Ownership and Policy Hierarchy

Control ownership must align with the Security Policy Hierarchy.

The ownership chain should support:

Architecture
→ Policy
→ Standard
→ Control
→ Implementation
→ Evidence
→ Verification
→ Certification

Each layer must have suitable accountability.

## 41. Ownership and Evidence

Every material control owner must ensure suitable evidence exists.

Evidence may include:

- Configuration state
- Source code
- Automated tests
- Security scan results
- Runtime telemetry
- Audit logs
- Access reviews
- Change records
- Incident records
- Recovery tests

The owner is accountable for evidence availability, not necessarily for
personally generating every artifact.

## 42. Ownership and Exceptions

Every security exception must identify the affected control owner.

The owner must be aware of:

- Exception scope
- Risk
- Compensating controls
- Expiration
- Review requirements
- Closure status

The control owner must not silently approve their own high-risk exception where
independent approval is required.

## 43. Ownership and Security Technical Debt

Security technical debt must identify an accountable owner.

The owner must coordinate:

- Risk classification
- Remediation plan
- Target date
- Interim protection
- Evidence
- Escalation
- Closure

Unowned security debt is prohibited.

## 44. Ownership and Incident Escalation

Each control must define how control failure is escalated.

Escalation should identify:

- Operational responder
- Control owner
- Security authority
- Platform owner where required
- Incident-management path

Critical failures must not depend on ad hoc discovery of responsibility.

## 45. Ownership and Change Management

Material control changes require owner participation.

Changes may require:

- Owner review
- Security review
- Architecture review
- Independent approval
- Testing
- Evidence update
- Documentation update
- Recertification

## 46. Ownership and Control Retirement

Controls must not be retired solely because they appear unused.

Retirement should verify:

- Requirement no longer applies
- Replacement exists where necessary
- Dependent controls are understood
- Evidence is archived
- Exceptions are resolved
- Approval is recorded

## 47. Orphaned Control Detection

LinkCraftor must eventually detect controls with:

- No owner
- Invalid owner
- Inactive owner
- Missing reviewer
- Missing escalation path
- Expired ownership review

Orphaned critical controls must be escalated.

## 48. Conflicting Ownership Detection

LinkCraftor should eventually detect problematic ownership combinations.

Examples include:

- Same person owns and independently certifies a high-risk control
- Same person approves their own exception
- Same person controls production and destroys audit evidence
- Same person owns backup deletion and recovery approval
- Same person approves and executes critical privilege changes

Conflicts must be reviewed against Separation-of-Duties Principles.

## 49. Security Control Ownership Registry

LinkCraftor should eventually maintain a Security Control Ownership Registry.

Each record should include:

- Control ID
- Control name
- Domain
- Accountable owner
- Custodian
- Implementer
- Reviewer
- Scope
- Environment
- Evidence source
- Exception status
- Review date
- Escalation path
- Certification status

The registry becomes the canonical ownership reference.

## 50. Ownership Status Model

Control ownership status may include:

- Assigned
- Pending acceptance
- Active
- Under review
- Transfer pending
- Temporarily delegated
- Orphaned
- Retired

Critical controls must not remain orphaned.

## 51. Owner Control Tower Visibility

The Owner's Security Control Tower must eventually expose:

- Total security controls
- Controls by domain
- Accountable owners
- Orphaned controls
- Pending ownership assignments
- Ownership conflicts
- Overdue ownership reviews
- Controls with missing evidence
- Controls with open exceptions
- Controls with security technical debt
- Ownership transfers
- Critical control failures
- Certification status

Owner monitoring remains read-only by default.

## 52. Relationship to Later PSA Phases

This component defines the foundational ownership model.

Later PSA phases implement detailed ownership across:

- Identity
- Authorization
- Infrastructure
- Applications
- APIs
- Runtime
- Workers
- Data
- Cryptography
- Detection
- Vulnerability management
- Incident response
- Recovery
- Third parties
- AI
- Certification

This document does not certify those operational ownership assignments as
implemented.

## 53. Completion Criteria

Step 1.1.13 is complete when:

- The core ownership rule is defined.
- The ownership model is defined.
- Accountable owner responsibilities are defined.
- Custodian responsibilities are defined.
- Implementer responsibilities are defined.
- Independent reviewer responsibilities are defined.
- Approval responsibilities are defined.
- RACI support is defined.
- Platform Security Owner is defined.
- Domain ownership is defined.
- Major security domains have ownership requirements.
- Ownership assignment is defined.
- Ownership acceptance is defined.
- Ownership transfer is defined.
- Owner unavailability is defined.
- Ownership review is defined.
- Separation-of-duties relationship is defined.
- Least-privilege relationship is defined.
- Policy hierarchy relationship is defined.
- Evidence responsibility is defined.
- Exception ownership is defined.
- Technical debt ownership is defined.
- Incident escalation is defined.
- Change-management ownership is defined.
- Retirement governance is defined.
- Orphaned-control detection is defined.
- Conflicting ownership detection is defined.
- Security Control Ownership Registry is defined.
- Ownership status model is defined.
- Owner Control Tower visibility is defined.
- The document passes structural verification.

## Certification Statement

This document defines the canonical LinkCraftor Security Control Ownership model.

It establishes foundational control-accountability requirements but does not
certify all later operational control assignments as implemented.
