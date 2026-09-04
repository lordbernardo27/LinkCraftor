# LinkCraftor Separation-of-Duties Principles

## Document Control

| Field | Value |
|---|---|
| Architecture | Platform Security Architecture |
| Component | 1.1.9 Separation-of-Duties Principles |
| Platform | LinkCraftor |
| Status | Foundational Security Definition |
| Version | 1.0.0 |
| Classification | Internal Architecture |
| Canonical Location | `backend/infra/security/architecture/separation_of_duties_principles.md` |

## 1. Purpose

This document defines the canonical Separation-of-Duties principles for
LinkCraftor.

Critical security, operational, financial, deployment, recovery, and
administrative activities must not depend on one identity holding every
capability required to initiate, approve, execute, and conceal a sensitive
action.

Responsibilities must be separated where concentration of privilege would
create unacceptable risk.

## 2. Separation-of-Duties Objective

The objective is to reduce:

- Unauthorized privileged actions
- Fraud
- Insider risk
- Accidental misuse
- Undetected configuration changes
- Unauthorized production changes
- Unauthorized recovery actions
- Security-control bypass
- Evidence tampering
- Single-person control over high-risk processes

## 3. Core Separation Rule

Where risk warrants it, critical activities must separate:

- Request from approval
- Approval from execution
- Execution from verification
- Development from production administration
- Deployment from deployment approval
- Security administration from security evidence review
- Backup administration from restore approval
- Billing operations from technical administration
- Support access from unrestricted platform administration

No single identity should control an entire high-risk lifecycle where practical.

## 4. Dual-Control Principle

High-risk actions should require independent participation by more than one
authorized identity where technically and operationally appropriate.

Dual control may apply to:

- Production break-glass access
- Recovery-key use
- Root credential access
- Destructive production actions
- Critical security-policy overrides
- Sensitive data exports
- Privileged support access
- Backup restoration
- Security-control disablement
- High-risk infrastructure changes

## 5. Independent Approval

Approval must be independent from the person or process requesting a sensitive
change where practical.

Approval must validate:

- Business justification
- Security impact
- Requested privilege
- Scope
- Environment
- Tenant impact
- Data impact
- Duration
- Rollback or recovery plan
- Evidence requirements

Self-approval should be prohibited for high-risk changes unless explicitly
authorized by emergency procedure.

## 6. Development and Production Separation

Development responsibilities must be separated from unrestricted production
administration.

Developers should not automatically receive:

- Production administrator access
- Production database superuser access
- Production secret-administrator access
- Security-system administration
- Recovery-system administration

Production access must be explicitly authorized and audited.

## 7. Deployment Separation

Deployment workflows should separate:

- Code author
- Code reviewer
- Release approver
- Deployment identity
- Production verifier

Where full separation is not practical, compensating controls must provide
review, auditability, and rollback capability.

## 8. Security Administration Separation

Security administration must not automatically grant unrestricted control over
all business and production functions.

Distinct responsibilities may include:

- Security policy administration
- Detection rule administration
- Incident response
- Vulnerability management
- Secrets administration
- Security evidence review
- Audit review
- Certification

Security administrators must not be able to silently erase required evidence
of their own privileged actions.

## 9. Identity and Access Management Separation

Identity lifecycle duties should separate where practical:

- User creation
- Role assignment
- Privilege approval
- Privilege activation
- Privilege review
- Privilege revocation

High-risk privileged-role assignments should require independent approval.

## 10. Privileged Access Separation

Privileged access must distinguish between:

- Requestor
- Approver
- Privileged user
- Reviewer
- Audit function

Standing privileged access should be minimized.

Temporary privilege should expire automatically where practical.

## 11. Tenant Administration Separation

Tenant and workspace administration must remain bounded.

A tenant administrator must not automatically gain:

- Platform-owner access
- Cross-tenant access
- Security-system administration
- Infrastructure administration
- Production database administration
- Recovery-system administration

Tenant administration must remain tenant-scoped.

## 12. Database Responsibility Separation

Database responsibilities should distinguish:

- Application access
- Schema migration
- Database administration
- Backup creation
- Backup restoration
- Audit review

Ordinary application identities must not perform database administrative
functions.

## 13. Storage Responsibility Separation

Storage responsibilities should distinguish:

- Routine application access
- Storage administration
- Retention policy administration
- Deletion approval
- Backup administration
- Recovery access

Destructive storage actions should receive stronger controls where risk
warrants it.

## 14. Secrets and Key Separation

Cryptographic and secret-management responsibilities should separate:

- Secret creation
- Secret consumption
- Secret rotation
- Key administration
- Key recovery
- Certificate administration
- Access review

A workload consuming a secret must not automatically receive secret-management
authority.

## 15. Infrastructure Separation

Infrastructure responsibilities should be segmented across areas such as:

- Network administration
- Compute administration
- Storage administration
- Database administration
- IAM administration
- Security administration
- Backup administration
- Recovery administration
- Billing administration

One operational identity should not automatically receive unrestricted access
across all infrastructure domains.

## 16. Network and Security-Control Separation

Network operators and security-control administrators should have distinct
privileges where practical.

Changes to:

- Firewalls
- WAF rules
- Egress controls
- DNS
- Private networking
- Security groups
- Network access controls

must be independently reviewable.

## 17. Backup and Recovery Separation

Backup and recovery responsibilities require strong separation.

Where practical, separate:

- Backup creation
- Backup administration
- Backup deletion
- Restore request
- Restore approval
- Restore execution
- Restore verification

An identity that compromises production should not automatically be able to
destroy recovery capability.

## 18. Incident Response Separation

Incident response may require emergency privilege, but accountability must
remain intact.

Incident functions may distinguish:

- Incident commander
- Investigator
- Containment operator
- Recovery operator
- Evidence custodian
- Communications owner

Emergency authority must remain auditable.

## 19. Evidence and Audit Separation

Security evidence must be independently reviewable.

The identity performing a high-risk action should not have unrestricted ability
to alter or delete the audit evidence recording that action.

Evidence systems should enforce:

- Restricted write permissions
- Protected retention
- Integrity controls
- Reviewer access
- Administrative audit trails

## 20. Support Operations Separation

Support access must remain distinct from platform administration.

Support personnel should not automatically receive:

- Production database administration
- Cross-tenant access
- Infrastructure administration
- Security-administrator access
- Billing administrator access
- Recovery administrator access

Sensitive support actions should be approved and audited where required.

## 21. Billing and Financial Separation

Billing and financial responsibilities should be separated from unrelated
technical privileges.

Functions may include:

- Subscription administration
- Refund approval
- Payment configuration
- Financial reporting
- Billing-system administration
- Technical production administration

High-risk financial changes should require independent authorization.

## 22. Owner Privilege Separation

Platform ownership does not require unrestricted operational privilege for
every routine action.

Owner capabilities should distinguish:

- Read-only oversight
- Security oversight
- Business administration
- Production administration
- Recovery authority
- Billing authority
- Emergency authority

Owner Control Tower monitoring should remain read-only by default.

## 23. Machine and Automation Separation

Automation identities must have separate responsibilities.

Examples include:

- CI build identity
- Release identity
- Deployment identity
- Migration identity
- Scheduler identity
- Worker identity
- Backup identity
- Security-scanner identity

One automation credential must not become a universal platform credential.

## 24. Queue and Worker Separation

Queue producers, queue consumers, and worker administrators should have
separate capabilities where practical.

A worker should not automatically be able to:

- Reconfigure its queue
- Create arbitrary privileged jobs
- Modify security policy
- Grant itself additional privileges
- Access unrelated tenants
- Disable its audit logging

## 25. Security Exception Separation

Security exceptions must not be requested, approved, implemented, and closed
by the same identity for high-risk cases.

Exception governance should distinguish:

- Requestor
- Risk reviewer
- Approver
- Implementer
- Reviewer
- Closure authority

## 26. Change Management Separation

Material security-sensitive changes should separate:

- Change author
- Reviewer
- Approver
- Deployment executor
- Post-deployment verifier

Critical changes must retain traceable evidence across these roles.

## 27. Emergency Access

Emergency access may temporarily reduce normal separation but must not eliminate
accountability.

Break-glass access must include:

- Strong authentication
- Explicit activation
- Reason capture
- Time limitation
- Audit logging
- Alerting
- Post-event review
- Prompt revocation

Emergency access must not become routine access.

## 28. Compensating Controls

Full separation may not always be practical, especially during early-stage
operations.

Where duties cannot be fully separated, compensating controls must be used,
such as:

- Mandatory peer review
- Strong authentication
- Time-limited privilege
- Detailed logging
- Immutable evidence
- Real-time alerts
- Post-action review
- Automated policy checks
- Restricted scope

Reduced separation must be explicitly documented.

## 29. Separation-of-Duties Conflict Detection

LinkCraftor must eventually identify dangerous combinations of permissions.

Examples include:

- Request + approve
- Approve + deploy
- Deploy + erase audit logs
- Security admin + audit deletion
- Backup admin + backup deletion + production admin
- Billing admin + refund approval
- Support access + unrestricted cross-tenant access
- IAM admin + privileged-access reviewer

Conflicting privilege combinations must be reviewable.

## 30. Separation-of-Duties Exception Governance

Exceptions must be:

- Explicit
- Documented
- Risk-assessed
- Approved
- Scoped
- Time-limited where possible
- Audited
- Reviewed
- Revoked when no longer necessary

Permanent concentration of high-risk duties requires exceptional justification.

## 31. Failure Rule

If required independent approval or duty separation cannot be validated:

1. The sensitive action must not proceed.
2. Privilege must not broaden automatically.
3. Evidence must be recorded.
4. Relevant stakeholders must be alerted where appropriate.
5. Emergency procedure may be used only when explicitly authorized.

## 32. Owner Control Tower Visibility

The Owner's Security Control Tower must eventually expose Separation-of-Duties
governance including:

- Conflicting role combinations
- Self-approved privileged changes
- Missing independent approvals
- Break-glass activations
- Duties concentrated in one identity
- Production access conflicts
- Security evidence conflicts
- Backup and recovery conflicts
- Billing privilege conflicts
- Support privilege conflicts
- Separation exceptions
- Overdue separation reviews
- Certification status

Owner monitoring remains read-only by default.

## 33. Relationship to Later PSA Phases

This component defines foundational Separation-of-Duties requirements.

Later PSA phases implement detailed controls through:

- Authorization and Entitlement Security
- Privileged Access Management
- Cloud IAM
- CI/CD Security
- Production Access Security
- Database Security
- Secrets and Key Management
- Security Logging
- Incident Response
- Backup and Recovery
- Security Governance
- Owner Control Tower

This document does not certify those later controls as implemented.

## 34. Completion Criteria

Step 1.1.9 is complete when:

- The core separation rule is defined.
- Dual control is defined.
- Independent approval is defined.
- Development and production separation is defined.
- Deployment separation is defined.
- Security administration separation is defined.
- IAM separation is defined.
- Privileged access separation is defined.
- Tenant administration separation is defined.
- Database and storage separation are defined.
- Secrets and key separation is defined.
- Infrastructure separation is defined.
- Backup and recovery separation are defined.
- Incident-response separation is defined.
- Evidence and audit separation are defined.
- Support separation is defined.
- Billing separation is defined.
- Owner privilege separation is defined.
- Automation separation is defined.
- Change-management separation is defined.
- Emergency access is defined.
- Compensating controls are defined.
- Conflict detection is defined.
- Exception governance is defined.
- Owner Control Tower visibility is defined.
- The document passes structural verification.

## Certification Statement

This document defines the canonical LinkCraftor Separation-of-Duties Principles.

It establishes foundational duty-separation requirements but does not certify
later operational controls as implemented.
