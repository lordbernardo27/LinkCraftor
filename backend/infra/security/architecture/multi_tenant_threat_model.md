# LinkCraftor Multi-Tenant Threat Model

## Document Control

Architecture: Platform Security Architecture
Component: 2.1.7 Multi-Tenant Threat Model
Version: 1.0.0
Status: Active Threat Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

This model identifies threats that may cause one LinkCraftor tenant,
organization, domain, workspace, user, or workload to access or influence
resources belonging to another.

## 2. Tenant Isolation Objective

Tenant context must remain intact through:

Request
-> Authentication
-> Authorization
-> Application
-> Database
-> Storage
-> Cache
-> Search
-> Vector Retrieval
-> Queue
-> Worker
-> Result
-> Logging

## 3. Protected Tenant Assets

Protected assets include:

- Documents.
- Domains.
- Workspace settings.
- Linking intelligence.
- Search indexes.
- Vector embeddings.
- Cache entries.
- Queue payloads.
- Worker results.
- API credentials.
- WordPress connections.
- GI prompts and results.
- Billing and entitlement state.

## 4. Threat Categories

Threats include:

- Workspace identifier tampering.
- Tenant context loss.
- Cross-tenant database queries.
- Cache key collisions.
- Shared search-index leakage.
- Vector-store leakage.
- Queue tenant mismatch.
- Worker context confusion.
- Object-storage path leakage.
- Cross-tenant logging.
- Authorization-policy bypass.
- Administrative tenant confusion.

## 5. Threat Scenarios

Examples include:

- Request changes workspace ID after authentication.
- Database query omits tenant filter.
- Cache entry is keyed without tenant identity.
- Queue job contains forged tenant context.
- Worker restores incorrect workspace state.
- Search result includes another tenant's document.
- Vector retrieval crosses workspace boundaries.
- Storage key allows unauthorized object access.

## 6. Fail-Secure Tenant Rule

Missing, ambiguous, invalid, or contradictory tenant context must not default
to a shared or unrestricted context.

Execution must fail securely.

## 7. Security Risk Relationship

Any credible cross-tenant exposure may require High or Critical risk review
depending on scope and data sensitivity.

Final scoring belongs to PSA 2.1.15.

## 8. Integration

This model is registered with:

- Central Architecture Registry.
- Security Threat Model Registry.
- Threat-to-Risk integration bridge.

## 9. Completion Statement

This component establishes the canonical LinkCraftor Multi-Tenant Threat Model.
