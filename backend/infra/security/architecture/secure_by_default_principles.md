# LinkCraftor Secure-by-Default Principles

## Document Control

| Field | Value |
|---|---|
| Architecture | Platform Security Architecture |
| Component | 1.1.7 Secure-by-Default Principles |
| Platform | LinkCraftor |
| Status | Foundational Security Definition |
| Version | 1.0.0 |
| Classification | Internal Architecture |
| Canonical Location | `backend/infra/security/architecture/secure_by_default_principles.md` |

## 1. Purpose

This document defines the canonical Secure-by-Default principles for LinkCraftor.

New users, services, workloads, APIs, storage resources, integrations,
administrative capabilities, and infrastructure must begin from the safest
reasonable configuration.

Security must not depend on customers or operators manually enabling basic
protection after deployment.

## 2. Secure-by-Default Objective

The objective is to ensure that default configuration minimizes exposure,
privilege, data disclosure, and unsafe execution.

Defaults must favor:

- Deny over allow
- Private over public
- Least privilege over broad access
- Authentication over anonymous access
- Explicit authorization over implicit trust
- Encryption over plaintext
- Minimal data collection over unnecessary retention
- Safe failure over permissive fallback
- Auditable actions over invisible actions
- Restricted administrative access over standing privilege

## 3. Default Deny

Protected capabilities must deny access by default.

Access is permitted only when required security conditions are explicitly
satisfied.

This applies to:

- APIs
- Administrative functions
- Tenant resources
- Workspace resources
- Databases
- Storage
- Queues
- Worker execution
- Runtime handlers
- Infrastructure
- Internal services

Unknown or incomplete authorization state must result in denial.

## 4. Private by Default

Resources must not become publicly accessible unless public exposure is an
explicit design requirement.

Private-by-default applies to:

- Object storage
- Databases
- Internal APIs
- Queues
- Administrative interfaces
- Monitoring systems
- Backup systems
- Security systems
- Runtime services
- Internal dashboards
- Secrets stores

Public exposure must require explicit configuration and review.

## 5. Authentication Enabled by Default

Protected capabilities must require authentication unless deliberately
classified as public.

Authentication must be enabled by default for:

- Customer accounts
- Administrative interfaces
- Owner interfaces
- APIs
- Internal services
- Worker controls
- Scheduler controls
- Deployment systems
- Security systems
- Recovery systems

Anonymous administrative access is prohibited.

## 6. Authorization Required by Default

Authentication must not automatically provide access.

Every protected operation must require explicit authorization based on
applicable context.

Authorization defaults must include:

- Resource-level checks
- Tenant checks
- Workspace checks
- Role checks
- Permission checks
- Entitlement checks
- Administrative privilege checks

Missing authorization data must result in denial.

## 7. Least Privilege by Default

New identities must begin with the minimum required permissions.

This applies to:

- Users
- Workspace members
- Organization members
- Support personnel
- Administrators
- Services
- Workers
- Schedulers
- Orchestrators
- Deployment identities
- Database identities

Broad wildcard permissions must not be the default.

## 8. Tenant Isolation by Default

Tenant and workspace resources must be isolated automatically.

New resources must inherit secure tenant context where applicable.

Default behavior must prevent:

- Cross-tenant reads
- Cross-tenant writes
- Cross-workspace reads
- Cross-workspace writes
- Cross-tenant queue execution
- Cross-tenant storage access
- Cross-tenant cache leakage
- Cross-tenant search exposure

Tenant context must never be optional for tenant-scoped resources.

## 9. Encryption by Default

Sensitive traffic and storage must use encryption by default where supported.

Default encryption applies to:

- Public traffic
- Service-to-service traffic where required
- Databases
- Object storage
- Backups
- Secrets
- Sensitive files
- Security evidence
- Administrative sessions

Disabling required encryption must not be a normal user-facing option.

## 10. Secure Session Defaults

Sessions must begin with secure configuration.

Defaults include:

- Secure cookies
- HttpOnly cookies where applicable
- SameSite protection
- Session expiration
- Inactivity timeout where applicable
- Token expiration
- Session revocation capability
- Rotation after sensitive events
- No credentials in URLs

Long-lived permanent sessions must not be the default.

## 11. Secure API Defaults

New APIs must inherit secure behavior.

Defaults include:

- Authentication required
- Authorization required
- Schema validation
- Request size limits
- Rate limiting
- Safe error responses
- Audit logging
- Version control
- No wildcard privileged scopes
- No unauthenticated write operations

Internal APIs are not exempt from secure defaults.

## 12. Secure Runtime Defaults

Runtime handlers and workloads must begin with constrained execution.

Defaults include:

- Registered handlers only
- Explicit workload identity
- Minimal permissions
- Resource limits
- Tenant context where applicable
- Workspace context where applicable
- Safe retry policy
- Auditable execution
- Restricted filesystem access
- Restricted network access where practical

Unknown workloads must not execute automatically.

## 13. Secure Queue and Worker Defaults

Asynchronous infrastructure must use secure defaults.

Defaults include:

- Authenticated producers
- Authenticated consumers
- Scoped worker permissions
- Message integrity validation
- Tenant-bound jobs
- Workspace-bound jobs
- Duplicate-execution protection
- Dead-letter handling
- Poison-message isolation
- Maximum retry thresholds
- Resource limits

Malformed or unauthorized messages must be rejected.

## 14. Secure Upload Defaults

Uploads must be treated as untrusted by default.

Defaults include:

- File size limits
- File count limits
- Approved type validation
- MIME validation
- Magic-byte validation
- Archive limits
- Malware checks where required
- Parser isolation
- Temporary storage restrictions
- Quarantine on uncertainty
- Secure cleanup

Unknown file types must not be processed automatically.

## 15. Secure Storage Defaults

Storage must begin with restrictive access.

Defaults include:

- Private access
- Explicit identities
- Minimal permissions
- Encryption
- Tenant-aware paths where applicable
- Versioning where required
- Access logging
- Retention policy
- Secure deletion controls
- No anonymous write access

## 16. Secure Database Defaults

Database access must be restrictive by default.

Defaults include:

- Dedicated application identities
- No shared superuser use
- Minimal grants
- Network restrictions
- TLS where required
- Audit logging
- Tenant-aware controls where applicable
- No public database exposure
- Controlled schema changes
- Protected backups

## 17. Secure Secret Defaults

Secrets must never be exposed through insecure defaults.

Defaults include:

- Dedicated secret storage
- No secrets in source code
- No secrets in logs
- No secrets in client bundles
- Limited runtime injection
- Rotation capability
- Environment separation
- Minimal secret access
- Auditability

Placeholder or development secrets must not be reused in production.

## 18. Secure Infrastructure Defaults

New infrastructure must begin from hardened baseline configuration.

Defaults include:

- Private networking where practical
- Restricted inbound access
- Restricted administrative access
- Minimal cloud permissions
- Encryption
- Logging
- Monitoring
- No broad public exposure
- Environment separation
- Configuration tracking

Security-sensitive infrastructure changes require review.

## 19. Secure Administrative Defaults

Administrative capabilities must begin restricted.

Defaults include:

- No anonymous access
- Strong authentication
- MFA where required
- Minimal standing privilege
- Auditable actions
- Session expiration
- Reason capture for sensitive actions where applicable
- No shared administrative accounts
- No customer impersonation without explicit controls

## 20. Secure Logging Defaults

Security-relevant logging must be enabled by default.

Default logging should cover:

- Authentication
- Authorization
- Administrative actions
- Cross-tenant failures
- Security-control failures
- Privilege changes
- Sensitive configuration changes
- Production access
- Security incidents

Logs must not expose secrets or unnecessary sensitive data.

## 21. Minimal Data Defaults

Products and services should collect and retain only data needed for approved
purposes.

Defaults should minimize:

- Personal data collection
- Sensitive metadata
- Diagnostic data
- Retention period
- Duplicated data
- Unnecessary logging
- Third-party data sharing

Additional data collection requires an explicit purpose.

## 22. Safe Error Defaults

Error behavior must minimize security exposure.

Defaults include:

- Generic external errors
- Detailed internal diagnostics only where protected
- No stack traces to unauthorized users
- No secret disclosure
- No internal path disclosure
- No database credential disclosure
- No policy bypass on error

Failure must not result in broader access.

## 23. Safe Feature Defaults

New features must launch in the safest reasonable configuration.

Examples:

- Sharing disabled until configured
- Public access disabled until configured
- External integrations disabled until connected
- High-risk automation disabled until authorized
- Administrative privileges disabled until granted
- Experimental capabilities restricted
- Sensitive exports restricted
- Broad API scopes disabled

## 24. Safe Integration Defaults

External integrations must begin with minimum access.

Defaults include:

- Minimum scopes
- Explicit workspace connection
- Explicit tenant association
- Verified callback endpoints
- Signed webhooks where supported
- Secret protection
- Disabled unused capabilities
- Revocable credentials

Integrations must not receive platform-wide access by default.

## 25. Safe Recovery Defaults

Recovery systems must preserve security.

Defaults include:

- Encrypted backups
- Restricted restore permissions
- Separate recovery credentials
- Audit logging
- Integrity verification
- No automatic privilege expansion
- No public backup exposure
- Controlled restore procedures

Recovery must not bypass tenant or authorization boundaries.

## 26. Configuration Drift Protection

Secure defaults must remain effective after deployment.

LinkCraftor must eventually detect material drift such as:

- Public storage exposure
- Disabled authentication
- Disabled logging
- Broad permissions
- Unencrypted resources
- Open network ports
- Long-lived credentials
- Disabled tenant checks
- Disabled rate limits
- Unsafe production settings

Drift from an approved secure baseline must be detectable.

## 27. Default Override Governance

Security-sensitive defaults may only be overridden deliberately.

Overrides must be:

- Explicit
- Authorized
- Documented
- Risk-assessed where required
- Auditable
- Reversible
- Time-limited where appropriate
- Reviewed periodically

Silent insecure overrides are prohibited.

## 28. Owner Control Tower Visibility

The Owner's Security Control Tower must eventually expose secure-default status
including:

- Resources using insecure defaults
- Publicly exposed internal resources
- Missing authentication
- Missing authorization
- Broad permissions
- Disabled encryption
- Disabled security logging
- Long-lived credentials
- Default overrides
- Configuration drift
- Certification status

Owner monitoring remains read-only by default.

## 29. Relationship to Other PSA Components

This component defines Secure-by-Default behavior.

Later PSA phases implement detailed controls for:

- Identity
- Authorization
- Tenant isolation
- API security
- Runtime security
- Storage
- Cryptography
- Infrastructure
- Monitoring
- Vulnerability management
- Recovery
- Security certification

This document does not certify those later controls as implemented.

## 30. Completion Criteria

Step 1.1.7 is complete when:

- Default-deny behavior is defined.
- Private-by-default behavior is defined.
- Authentication-by-default is defined.
- Authorization-by-default is defined.
- Least-privilege defaults are defined.
- Tenant-isolation defaults are defined.
- Encryption defaults are defined.
- Secure session defaults are defined.
- API defaults are defined.
- Runtime defaults are defined.
- Queue and worker defaults are defined.
- Upload defaults are defined.
- Storage and database defaults are defined.
- Secret defaults are defined.
- Infrastructure defaults are defined.
- Administrative defaults are defined.
- Logging defaults are defined.
- Minimal-data defaults are defined.
- Safe failure defaults are defined.
- Override governance is defined.
- Owner Control Tower visibility is defined.
- The document passes structural verification.

## Certification Statement

This document defines the canonical LinkCraftor Secure-by-Default Principles.

It establishes required secure default behavior but does not certify later
operational security controls as implemented.
