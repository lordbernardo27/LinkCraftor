# LinkCraftor Service and Microservice Inventory

## Document Control

Architecture: Platform Security Architecture
Phase: 3 - Asset Inventory & Attack-Surface Management
Component: 3.1.5 Service and Microservice Inventory
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

This component establishes the security inventory of LinkCraftor services and
microservices.

It does not create a replacement runtime service registry.

The authoritative runtime service-registration system remains:

backend/server/runtime/runtime_service_registry.py

## 2. Universal Runtime Authority

The Universal Runtime Service Registry remains authoritative for:

- live runtime service registration.
- service logical keys.
- runtime service objects.
- runtime service types.
- capabilities.
- dependencies.
- startup order.
- dependency validation.
- registry sealing.
- runtime snapshots.

PSA 3.1.5 must not duplicate or replace this subsystem.

## 3. Security Inventory Responsibility

PSA 3.1.5 provides persistent security inventory information that the runtime
registry is not responsible for.

This includes:

- persistent security identity.
- environment.
- service classification.
- application relationships.
- security lifecycle status.
- exposure metadata.
- authentication requirements.
- tenant awareness.
- ownership references.
- security evidence.
- source provenance.

## 4. Relationship

The relationship is:

Universal Runtime Service Registry
→ Security Inventory Bridge
→ PSA 3.1.5 Security Service Inventory

The bridge reads runtime metadata.

The bridge must never mutate the Universal Runtime registry.

## 5. Canonical Security Service Record

Every security service record must contain:

- security_service_id.
- service_key.
- service_name.
- service_kind.
- environment.
- status.
- source.
- architecture_id.
- component_id.
- first_seen_at.
- last_seen_at.

Optional metadata may include:

- runtime_service_type.
- runtime_capabilities.
- runtime_dependencies.
- runtime_startup_order.
- application_reference.
- product_reference.
- company_reference.
- repository_reference.
- deployment_reference.
- api_references.
- data_asset_references.
- owner_reference.
- technical_owner_reference.
- security_owner_reference.
- criticality.
- internet_exposed.
- authentication_required.
- tenant_aware.
- externally_callable.
- evidence.
- notes.

## 6. Identifier

Canonical security service IDs use:

SEC-SVC-XXXX

The security ID does not replace the runtime service_key.

## 7. Service Kinds

Canonical service kinds are:

- runtime-service.
- microservice.
- worker-service.
- background-service.
- internal-service.
- edge-service.
- integration-service.
- platform-service.
- other.

## 8. Status

Canonical security inventory statuses are:

- discovered.
- active.
- inactive.
- degraded.
- failed.
- deprecated.
- unauthorized.
- quarantined.
- decommissioning.
- decommissioned.

## 9. Environment

Canonical environments are:

- development.
- testing.
- staging.
- production.
- shared.
- internal.
- unknown.

## 10. Runtime Snapshot Bridge

PSA 3.1.5 may ingest immutable RuntimeServiceRegistry snapshots.

Runtime metadata may include:

- service_key.
- service_type.
- capabilities.
- dependencies.
- startup_order.
- registered_at.

Runtime state remains authoritative in the Universal Runtime.

## 11. Application Boundary

Applications remain authoritative under 3.1.4 Application Inventory.

A service may reference an application.

A service does not replace application identity.

## 12. API Boundary

API inventory remains authoritative under 3.1.6 API Inventory.

A service may expose APIs.

Service identity does not replace API identity.

## 13. Ownership Boundary

Ownership references may be stored here.

Authoritative Asset Ownership Assignment remains 3.1.16.

## 14. Criticality Boundary

Known criticality may be stored here.

Authoritative Asset Criticality Classification remains 3.1.17.

## 15. Security Requirements

3.1.5 must:

- preserve stable SEC-SVC identity.
- preserve runtime service_key independently.
- reject duplicate security identities.
- preserve first-seen timestamps.
- persist security inventory.
- support runtime snapshot ingestion.
- preserve runtime dependencies.
- preserve runtime capabilities.
- preserve startup order.
- support environment filtering.
- support service-kind filtering.
- identify unauthorized services.
- identify internet-exposed services.
- never mutate the Universal Runtime registry.
- integrate with the Central Architecture Registry.

## 16. Sensitive Information

The inventory must not contain:

- passwords.
- API secrets.
- private keys.
- access tokens.
- service credentials.
- raw authentication secrets.

## 17. Completion Boundary

3.1.5 establishes Service and Microservice Inventory capability.

It does not claim:

- automatic discovery of every deployed microservice.
- live service health monitoring.
- API inventory completion.
- ownership certification.
- criticality certification.
- internet-exposure discovery.
- vulnerability scanning.
- shadow-service detection.
- complete attack-surface certification.

## 18. Completion Statement

This component establishes the persistent security inventory layer for
LinkCraftor services and microservices while preserving the Universal Runtime
Service Registry as the authoritative runtime subsystem.
