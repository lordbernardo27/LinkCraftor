# LinkCraftor Security Identity Inventory

## Document Control

Architecture: Platform Security Architecture
Phase: 3 - Asset Inventory & Attack-Surface Management
Component: 3.1.8 Identity Inventory
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

PSA 3.1.8 establishes a persistent security inventory of identities known to
LinkCraftor.

It does not create a replacement identity provider, account system,
authentication system, authorization system, worker registry, service
registry, role store, permission store, session store, or entitlement system.

## 2. Architectural Principle

Operational identity authorities own identity truth.

PSA 3.1.8 owns only the security-governance projection of those identities.

Identity records are referenced through stable security inventory identities.

## 3. Existing Runtime Identity Contract

The Universal Runtime currently recognizes these canonical principal types:

- USER
- WORKER
- SERVICE
- SYSTEM
- ADMINISTRATOR

These values originate from RuntimePrincipalType.

RuntimePrincipalIdentity is a runtime-facing reference only.

It explicitly does not create a new identity authority.

## 4. Existing Worker Identity Contract

Worker Identity Validation consumes evidence from existing worker
registration, heartbeat, assignment, and lease authorities.

PSA 3.1.8 must not create a competing worker registry.

## 5. Authorization Boundary

Runtime authorization consumes identity and entitlement evidence.

It intentionally does not persist:

- identities.
- roles.
- permissions.

PSA 3.1.8 therefore must not become an authorization or permission engine.

## 6. Staff Role Boundary

StaffRoleDefinition describes staff authorization/organizational roles.

A role definition is not itself an identity.

PSA 3.1.8 may preserve role references as identity metadata but must not
replace the authoritative staff-role or future entitlement system.

## 7. Security Identity Identifier

Canonical security identity IDs use:

SEC-ID-XXXX

SEC-ID does not replace the underlying identity's authoritative ID.

Examples of authoritative IDs may include:

- user IDs.
- worker IDs.
- worker instance IDs.
- service names.
- system identities.
- administrator account IDs.

## 8. Identity Types

Canonical PSA identity types are:

- user.
- worker.
- service.
- system.
- administrator.
- staff.
- integration.
- automation.
- machine.
- external.
- other.

Runtime principal mappings are:

USER -> user
WORKER -> worker
SERVICE -> service
SYSTEM -> system
ADMINISTRATOR -> administrator

## 9. Required Security Inventory Metadata

Every security identity record must contain:

- security_identity_id.
- identity_key.
- identity_name.
- identity_type.
- source_authority.
- environment.
- status.
- human_identity.
- privileged.
- architecture_id.
- component_id.
- first_seen_at.
- last_seen_at.

## 10. Optional Metadata

Optional identity metadata may include:

- authoritative_identity_id.
- principal_type.
- user_id.
- account_id.
- worker_id.
- worker_instance_id.
- service_name.
- organization_id.
- tenant_id.
- workspace_id.
- company_id.
- product_id.
- role_references.
- entitlement_reference.
- authentication_authority_reference.
- authorization_authority_reference.
- identity_provider_reference.
- lifecycle_reference.
- evidence.
- notes.

## 11. Status Values

Canonical statuses are:

- discovered.
- active.
- inactive.
- disabled.
- suspended.
- stale.
- unauthorized.
- quarantined.
- decommissioning.
- decommissioned.

## 12. Environment Values

Canonical environments are:

- development.
- testing.
- staging.
- production.
- shared.
- internal.
- unknown.

## 13. Human and Non-Human Identity Classification

USER, ADMINISTRATOR and staff identities are normally human identities.

WORKER, SERVICE, SYSTEM, automation and machine identities are normally
non-human identities.

The security inventory records this classification but does not authenticate
the subject.

## 14. Privileged Identity Metadata

PSA 3.1.8 may record whether an identity is known to be privileged.

Authoritative privileged-access controls remain governed by later PSA phases,
including Phase 6 Privileged Access and Administrative Security.

## 15. Authentication Boundary

Authentication implementation remains governed by Phase 4.

PSA 3.1.8 does not:

- verify passwords.
- issue authentication tokens.
- validate sessions.
- implement MFA.
- become an identity provider.

## 16. Authorization Boundary

Authorization remains governed by Phase 5 and existing runtime authorization
contracts.

PSA 3.1.8 does not:

- grant permissions.
- assign permissions.
- evaluate entitlements.
- make access-control decisions.

## 17. Privileged Access Boundary

Privileged access remains governed by Phase 6.

The inventory may flag identities as privileged for discovery and governance.

## 18. Tenant and Workspace Boundary

Organization, tenant and workspace references may be preserved as metadata.

Authoritative tenant/workspace isolation remains governed by Phase 7.

## 19. Session Boundary

Sessions and tokens remain governed by Phase 8.

PSA 3.1.8 must never persist raw session tokens or bearer tokens.

## 20. Sensitive Information Prohibition

The security identity inventory must never store:

- passwords.
- password hashes.
- API keys.
- bearer tokens.
- refresh tokens.
- private keys.
- authentication secrets.
- MFA secrets.
- recovery codes.
- raw session credentials.

## 21. Future Shared Identity Architecture

If a future Universal Identity Architecture or shared identity platform is
implemented, PSA 3.1.8 must consume authoritative identity metadata from that
system rather than duplicating it.

The security inventory schema therefore supports source-authority references
and authoritative identity IDs.

## 22. Requirements

PSA 3.1.8 must:

- preserve stable SEC-ID identity.
- preserve underlying authoritative identity IDs.
- preserve source authority.
- support all current RuntimePrincipalType values.
- distinguish human and non-human identities.
- identify privileged identities.
- identify unauthorized identities.
- identify stale identities.
- support environment filtering.
- support identity-type filtering.
- support source-authority filtering.
- persist security inventory metadata.
- never mutate identity authorities.
- never create authentication credentials.
- integrate with the Central Architecture Registry.

## 23. Completion Boundary

3.1.8 establishes identity inventory capability.

It does not claim completion of:

- user authentication.
- account management.
- IAM.
- authorization.
- role management.
- permission management.
- privileged access management.
- SSO.
- federation.
- session security.
- MFA.
- tenant isolation.

## 24. Completion Statement

PSA 3.1.8 provides a persistent security-governance inventory of identities
while preserving existing and future operational identity authorities as the
owners of identity truth.
