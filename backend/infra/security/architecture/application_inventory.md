# LinkCraftor Application Inventory

## Document Control

Architecture: Platform Security Architecture
Phase: 3 - Asset Inventory & Attack-Surface Management
Component: 3.1.4 Application Inventory
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

This component establishes the canonical security inventory of LinkCraftor
applications.

An application is a deployable or user-facing software system that performs a
defined product, staff, administrative, operational, owner, or platform
function.

## 2. Scope

Application records may represent:

- Customer-facing web applications.
- Administrative applications.
- Staff operations applications.
- Owner applications.
- Internal operational applications.
- Background platform applications.
- Plugin applications.
- Integration-facing applications.
- Future mobile applications.
- Future desktop applications.

## 3. Boundary With Other Phase 3 Inventories

3.1.4 inventories applications.

It does not replace:

- 3.1.2 Software Asset Inventory.
- 3.1.5 Service and Microservice Inventory.
- 3.1.6 API Inventory.
- 3.1.11 Third-Party Integration Inventory.
- 3.1.12 Open-Source Component Inventory.

Applications may contain services, APIs, software assets, integrations, and
dependencies, but those are inventoried authoritatively by their respective
components.

## 4. Canonical Application Record

Every application must contain:

- application_id.
- application_name.
- application_type.
- environment.
- status.
- source.
- architecture_id.
- component_id.
- first_seen_at.
- last_seen_at.

Optional metadata may include:

- product_reference.
- company_reference.
- workspace_scope.
- repository_reference.
- frontend_reference.
- backend_reference.
- deployment_reference.
- runtime_reference.
- cloud_resource_references.
- service_references.
- api_references.
- data_asset_references.
- identity_boundary_reference.
- owner_reference.
- technical_owner_reference.
- security_owner_reference.
- criticality.
- internet_exposed.
- authentication_required.
- tenant_aware.
- notes.
- evidence.

## 5. Identifier

Canonical Application Inventory identifiers use:

SEC-APP-XXXX

The identifier remains stable for the lifetime of the application record.

## 6. Application Types

Initial canonical types are:

- customer-web.
- staff-web.
- owner-web.
- admin-web.
- internal-platform.
- plugin.
- integration-application.
- mobile.
- desktop.
- background-application.
- other.

## 7. Application Status

Canonical lifecycle statuses are:

- discovered.
- active.
- inactive.
- deprecated.
- unauthorized.
- quarantined.
- decommissioning.
- decommissioned.

## 8. Environment

Canonical environments are:

- development.
- testing.
- staging.
- production.
- shared.
- internal.
- unknown.

## 9. Security Requirements

The Application Inventory must:

- preserve stable application identity.
- reject duplicate application IDs.
- preserve source provenance.
- preserve first-seen timestamps.
- support lifecycle transitions.
- support environment filtering.
- support application-type filtering.
- identify unauthorized applications.
- identify internet-exposed applications.
- identify tenant-aware applications.
- persist inventory evidence.
- integrate with the Central Architecture Registry.

## 10. Application Identity Versus Service Identity

An application may contain multiple services.

Application identity must not be used as a substitute for service or
microservice identity.

Service and Microservice Inventory is governed by 3.1.5.

## 11. Application Identity Versus API Identity

An application may expose one or more APIs.

Application identity must not be used as a substitute for API inventory.

API Inventory is governed by 3.1.6.

## 12. Ownership Boundary

Application ownership metadata may be preserved in this inventory.

Authoritative Phase 3 Asset Ownership Assignment is governed by 3.1.16.

## 13. Criticality Boundary

Application criticality metadata may be preserved if already known.

Authoritative Asset Criticality Classification is governed by 3.1.17.

## 14. Sensitive Information

The inventory must not contain:

- passwords.
- raw access tokens.
- private keys.
- API secrets.
- authentication credentials.
- recovery secrets.

References to secret-management systems may be stored as non-secret metadata.

## 15. Relationship to Later PSA Components

This registry becomes evidence for:

- 3.1.13 Internet-Exposed Asset Discovery.
- 3.1.14 Shadow Infrastructure Detection.
- 3.1.15 Shadow API Detection.
- 3.1.16 Asset Ownership Assignment.
- 3.1.17 Asset Criticality Classification.
- 3.1.18 Attack-Surface Monitoring.
- 3.1.19 Unauthorized Asset Removal.
- 3.1.20 Asset and Attack-Surface Certification.
- Phase 4 Identity, Authentication & Account Security.
- Phase 5 Authorization & Entitlement Security.
- Phase 9 API Security.
- Phase 10 Application & Business-Logic Security.
- Phase 11 Frontend Security.
- Phase 25 Security Logging and Detection.
- Phase 26 Vulnerability Management.
- Phase 28 Incident Response.
- Phase 31 Owner Security Control Tower.

## 16. Completion Boundary

3.1.4 establishes Application Inventory capability.

It does not claim:

- automatic application discovery.
- service inventory completion.
- API inventory completion.
- ownership certification.
- criticality certification.
- internet-exposure discovery.
- shadow-application discovery.
- vulnerability scanning.
- complete attack-surface certification.

## 17. Completion Statement

This component establishes the canonical LinkCraftor Application Inventory.
