# LinkCraftor API Threat Model

## Document Control

Architecture: Platform Security Architecture
Component: 2.1.6 API Threat Model
Version: 1.0.0
Status: Active Threat Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

This model identifies threats affecting LinkCraftor APIs, API consumers,
service interfaces, authentication boundaries, authorization decisions,
request processing, integrations, and externally exposed API capabilities.

## 2. API Scope

Scope includes:

- Public APIs.
- Internal APIs.
- FastAPI endpoints.
- Administrative APIs.
- WordPress integration APIs.
- Future Shopify APIs.
- Webhooks.
- Service-to-service APIs.
- Customer API access.
- API authentication.
- API authorization.
- API metering and quotas.

## 3. API Assets

Important API assets include:

- Access tokens.
- API keys.
- Session credentials.
- Workspace identifiers.
- Tenant identifiers.
- API request payloads.
- API response data.
- Entitlement state.
- AU billing state.
- Administrative operations.
- Integration credentials.

## 4. API Threat Actors

Relevant actors include:

- Anonymous attackers.
- Malicious API customers.
- Compromised users.
- Compromised API keys.
- Bots.
- Fraud actors.
- Compromised integrations.
- Privileged insiders.

## 5. API Threat Categories

Threats include:

- Broken authentication.
- Broken object-level authorization.
- Broken function-level authorization.
- Excessive data exposure.
- Mass assignment.
- Injection.
- Replay.
- Token theft.
- API-key leakage.
- Rate-limit bypass.
- Resource exhaustion.
- Request smuggling.
- Parameter manipulation.
- Webhook forgery.
- Cross-tenant API access.
- Entitlement bypass.

## 6. API Threat Scenarios

Representative scenarios include:

- User changes a workspace identifier and receives another tenant's data.
- Stolen API key is used outside its authorized scope.
- Endpoint performs an administrative function without sufficient privilege.
- Client bypasses plan entitlement through direct API calls.
- Large automated request volume consumes excessive runtime resources.
- Forged webhook causes unauthorized state changes.
- Sensitive data is returned beyond the minimum required API response.

## 7. Authentication Dependency

API authentication must establish a verified caller identity before protected
operations execute.

Detailed authentication architecture belongs to later PSA phases.

## 8. Authorization Dependency

Every protected object and operation must be authorized against the current
identity, tenant, workspace, role, entitlement, and applicable policy.

## 9. Tenant Isolation Dependency

API boundaries must preserve tenant and workspace context end-to-end.

## 10. Security Risk Relationship

Material API threats may create Security Risk Registry records.

## 11. Integration

This model is registered with:

- Central Architecture Registry.
- Security Threat Model Registry.
- Threat-to-Risk integration bridge.

## 12. Completion Statement

This component establishes the canonical LinkCraftor API Threat Model.
