# LinkCraftor Least-Privilege Principles

## Document Control

| Field | Value |
|---|---|
| Architecture | Platform Security Architecture |
| Component | 1.1.8 Least-Privilege Principles |
| Platform | LinkCraftor |
| Status | Foundational Security Definition |
| Version | 1.0.0 |
| Classification | Internal Architecture |
| Canonical Location | `backend/infra/security/architecture/least_privilege_principles.md` |

## 1. Purpose

This document defines the canonical Least-Privilege principles for LinkCraftor.

Every user, service, worker, scheduler, orchestrator, runtime, database identity,
integration, administrative account, and automated process must receive only
the permissions necessary to perform its approved function.

Privilege must never be broader than required by design.

## 2. Least-Privilege Objective

The objective is to reduce attack surface, lateral movement, accidental misuse,
cross-tenant exposure, and blast radius.

Privileges must be:

- Explicit
- Minimal
- Scoped
- Purpose-bound
- Reviewable
- Revocable
- Auditable
- Time-limited where appropriate

## 3. Minimum Necessary Access

Access must be granted only to the resources and operations required.

Permission design must consider:

- Resource
- Action
- Tenant
- Workspace
- Environment
- Service
- Data class
- Time period
- Administrative sensitivity
- Business purpose

Broad access must require explicit justification.

## 4. Default Minimal Permission

New identities must start with no privilege or the minimum safe baseline.

Privilege must be added only when a defined function requires it.

The following must not be defaults:

- Administrator access
- Wildcard permissions
- Cross-workspace access
- Cross-tenant access
- Production access
- Database superuser access
- Infrastructure administrator access
- Security-system administration
- Recovery-system administration

## 5. User Least Privilege

Customer and workspace users must only receive capabilities required by their
assigned role and approved membership.

Controls must consider:

- Organization role
- Workspace role
- Resource ownership
- Feature entitlement
- Subscription entitlement
- Explicit delegation
- Administrative scope

Membership in one workspace must not grant access to another workspace.

## 6. Administrative Least Privilege

Administrative identities require stricter privilege control.

Administrative access must:

- Use separate privileged identities where appropriate
- Avoid shared administrator accounts
- Minimize standing privilege
- Use role-specific administrative permissions
- Require strong authentication
- Be auditable
- Be revocable
- Be time-bound where practical
- Support approval where risk warrants it

Platform owner status must not imply unrestricted day-to-day access.

## 7. Service Least Privilege

Each service must use a dedicated identity where practical.

Service permissions must be limited to:

- Required APIs
- Required queues
- Required storage
- Required databases
- Required secrets
- Required network paths
- Required tenant context
- Required actions

One service must not inherit access merely because another service has it.

## 8. Runtime Least Privilege

Runtime handlers and workloads must receive only the capabilities required for
their registered responsibility.

Runtime privilege must control:

- Allowed handler
- Allowed job type
- Tenant
- Workspace
- Storage access
- Database access
- Queue access
- Network access
- Filesystem access
- Secret access
- Resource limits

Runtime workers must not execute with platform-wide administrative privilege.

## 9. Queue and Worker Least Privilege

Queue producers and consumers must use scoped permissions.

A worker must only be able to:

- Consume approved queues
- Process approved job types
- Access authorized tenant resources
- Access authorized workspace resources
- Invoke approved downstream services
- Write to approved stores

A worker compromise must not automatically provide broad platform access.

## 10. Database Least Privilege

Database identities must use minimum required grants.

Application identities must not normally receive:

- Superuser privileges
- Database ownership
- Unrestricted schema modification
- Unrestricted cross-tenant access
- Unnecessary administrative commands

Read-only, read-write, migration, administrative, and backup responsibilities
should use separate permissions where appropriate.

## 11. Storage Least Privilege

Storage access must be scoped to approved buckets, paths, objects, and actions.

Identities should receive only required operations such as:

- Read
- Write
- Delete
- List
- Version access
- Restore

Global storage administration must not be granted to ordinary services.

## 12. Tenant and Workspace Least Privilege

Permissions must remain bounded by tenant and workspace context.

A valid role without valid tenant or workspace scope must not grant access.

Cross-tenant and cross-workspace capabilities require:

- Explicit design
- Explicit authorization
- Strong audit evidence
- Independent review where appropriate

## 13. API Least Privilege

API permissions and scopes must be narrowly defined.

API credentials must avoid:

- Global wildcard scopes
- Unnecessary write access
- Unnecessary administrative actions
- Cross-tenant access
- Permanent broad access

Scopes should correspond to concrete capabilities.

## 14. Secret Least Privilege

Secret access must be limited to identities that require a specific secret.

Controls must support:

- Secret-specific access
- Environment-specific access
- Workload-specific access
- Rotation
- Revocation
- Audit logging

A service must not receive all platform secrets merely because it requires one.

## 15. Infrastructure Least Privilege

Cloud and infrastructure identities must use narrowly scoped permissions.

Separate privileges should exist for:

- Deployment
- Runtime
- Networking
- Storage
- Databases
- Security
- Monitoring
- Backup
- Recovery
- Billing

Infrastructure administrator permissions must not be used for routine runtime
operations.

## 16. Environment Least Privilege

Development, test, staging, and production privileges must be separate.

Development access must not imply production access.

Production privilege must require explicit authorization.

Environment-specific credentials and identities should be used where practical.

## 17. Deployment Least Privilege

Deployment identities must receive only the permissions necessary to deploy
approved resources and applications.

Deployment identities must not automatically receive:

- Customer data access
- Security-administrator access
- Backup access
- Billing access
- Unrelated infrastructure access

Deployment privileges should be revocable and auditable.

## 18. Integration Least Privilege

External integrations must receive minimum required scopes.

Examples include:

- WordPress
- Future CMS integrations
- Payment providers
- Email providers
- AI providers
- Analytics providers
- Webhooks
- External APIs

Unused scopes must remain disabled.

## 19. Support Least Privilege

Support personnel must not receive unrestricted customer access.

Support access should be:

- Role-specific
- Tenant-specific where required
- Time-limited where appropriate
- Approved where sensitive
- Audited
- Revocable
- Visible to security oversight

Customer impersonation must use dedicated controls.

## 20. Security-System Least Privilege

Security systems require protected privilege boundaries.

Access to:

- Security logs
- SIEM
- Vulnerability data
- Incident evidence
- Secrets
- Security configuration
- Detection rules
- Forensic evidence

must be separately controlled.

Security operators must not automatically receive unrelated business privileges.

## 21. Recovery Least Privilege

Backup and recovery systems must use separate privilege boundaries.

Recovery identities should have only the capabilities needed to:

- Read protected backups
- Validate integrity
- Restore approved resources
- Perform recovery operations
- Record evidence

Recovery privilege must not become a general production administrator role.

## 22. Just-in-Time Privilege

High-risk privilege should be temporary where practical.

Just-in-time privilege may be used for:

- Production administration
- Database administration
- Security administration
- Infrastructure administration
- Emergency response
- Recovery operations

Temporary privilege must expire automatically.

## 23. Privilege Elevation

Privilege elevation must be explicit.

Elevation should require applicable controls such as:

- Strong authentication
- Step-up authentication
- Approval
- Reason capture
- Time limit
- Scope definition
- Audit logging

Silent elevation is prohibited.

## 24. Privilege Revocation

Privileges must be revocable promptly.

Revocation must occur when:

- Employment or role ends
- Workspace membership ends
- Tenant membership ends
- Integration disconnects
- Service is retired
- Credential is compromised
- Security incident occurs
- Temporary privilege expires
- Business need ends

Revocation must not depend solely on credential expiration.

## 25. Privilege Review

Privileges must be reviewed periodically.

Reviews should identify:

- Excess permissions
- Dormant accounts
- Unused roles
- Broad wildcard permissions
- Long-lived administrative access
- Cross-tenant capabilities
- Unused API scopes
- Unused secrets access
- Orphaned service identities

Unnecessary privilege must be removed.

## 26. Privilege Separation

Distinct responsibilities should use distinct permissions.

Where appropriate, separate:

- Read from write
- Runtime from deployment
- Deployment from approval
- Security administration from business administration
- Database use from database administration
- Backup creation from backup restoration
- Support access from platform ownership
- Billing administration from technical administration

## 27. Least-Privilege Failure Rule

If required privilege cannot be determined or validated:

1. Access must be denied.
2. Processing must stop safely.
3. Privilege must not be broadened automatically.
4. Security evidence must be recorded.
5. Alerts must be generated where appropriate.

A permission error must never trigger fallback to a more privileged identity.

## 28. Privilege Exception Governance

Exceptions to least privilege must be formally controlled.

Exceptions must be:

- Explicit
- Documented
- Risk-assessed
- Approved
- Scoped
- Time-limited where possible
- Audited
- Reviewed
- Revoked when no longer required

Permanent broad privileges require exceptional justification.

## 29. Owner Control Tower Visibility

The Owner's Security Control Tower must eventually expose least-privilege
governance including:

- Broad permissions
- Wildcard privileges
- Standing administrative access
- Dormant privileged accounts
- Excess service privileges
- Cross-tenant privileges
- Production access
- Just-in-time privilege events
- Privilege elevation
- Privilege revocation
- Privilege exceptions
- Overdue privilege reviews
- Certification status

Owner monitoring remains read-only by default.

## 30. Relationship to Later PSA Phases

This component defines foundational least-privilege principles.

Later PSA phases implement detailed controls through:

- Authorization and Entitlement Security
- Privileged Access Management
- Tenant Isolation
- Session and Token Security
- API Security
- Cloud IAM
- Runtime Security
- Database Security
- Secrets Management
- Infrastructure Security
- Security Monitoring
- Incident Response

This document does not certify those later operational controls as implemented.

## 31. Completion Criteria

Step 1.1.8 is complete when:

- Minimum necessary access is defined.
- Default minimal permission is defined.
- User least privilege is defined.
- Administrative least privilege is defined.
- Service least privilege is defined.
- Runtime least privilege is defined.
- Queue and worker least privilege is defined.
- Database least privilege is defined.
- Storage least privilege is defined.
- Tenant and workspace least privilege are defined.
- API least privilege is defined.
- Secret least privilege is defined.
- Infrastructure least privilege is defined.
- Environment separation is defined.
- Deployment least privilege is defined.
- Integration least privilege is defined.
- Support least privilege is defined.
- Just-in-time privilege is defined.
- Privilege elevation is controlled.
- Privilege revocation is defined.
- Privilege review is defined.
- Privilege separation is defined.
- Exception governance is defined.
- Owner Control Tower visibility is defined.
- The document passes structural verification.

## Certification Statement

This document defines the canonical LinkCraftor Least-Privilege Principles.

It establishes foundational privilege rules but does not certify later
operational privilege controls as implemented.
