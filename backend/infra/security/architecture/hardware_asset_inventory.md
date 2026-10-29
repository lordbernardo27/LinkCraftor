# LinkCraftor Hardware Asset Inventory

## Document Control

Architecture: Platform Security Architecture
Phase: 3 - Asset Inventory & Attack-Surface Management
Component: 3.1.1 Hardware Asset Inventory
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

This component establishes the canonical LinkCraftor security inventory for
hardware assets that host, administer, build, operate, access, monitor, or
otherwise materially interact with the LinkCraftor platform.

The purpose is to ensure that security-relevant hardware is identifiable,
traceable, governed, and available to later attack-surface, ownership,
criticality, vulnerability, incident, and certification processes.

## 2. Scope

Hardware assets may include:

- Developer workstations.
- Administrative workstations.
- Physical servers.
- Virtual-machine hosts where hardware identity is security relevant.
- Build hosts.
- Deployment hosts.
- Operations workstations.
- Security workstations.
- Network appliances.
- Hardware security modules.
- Storage appliances.
- Backup appliances.
- Future corporate-managed devices.

Cloud logical resources are governed separately by PSA 3.1.3.

Software is governed separately by PSA 3.1.2.

## 3. Canonical Hardware Asset Record

Every registered hardware asset must have:

- asset_id.
- asset_type.
- asset_name.
- architecture_id.
- environment.
- status.
- source.
- first_seen_at.
- last_seen_at.

A record may additionally contain:

- hostname.
- manufacturer.
- model.
- serial_reference.
- operating_system.
- operating_system_version.
- network_zone.
- physical_location_reference.
- cloud_host_reference.
- managed_by.
- owner.
- criticality.
- internet_exposed.
- notes.
- evidence.

## 4. Asset Identifier

Hardware Asset IDs use:

SEC-HW-XXXX

The identifier must be stable for the lifetime of the registered asset.

## 5. Asset Status

Canonical lifecycle states are:

- discovered.
- active.
- inactive.
- quarantined.
- decommissioning.
- decommissioned.
- unauthorized.

## 6. Environment

Examples include:

- development.
- testing.
- staging.
- production.
- corporate.
- security.
- unknown.

Environment does not imply trust.

## 7. Discovery Versus Authorization

Discovery of an asset does not mean that the asset is authorized.

Authorization, ownership, and criticality are governed independently.

PSA 3.1.16 will provide authoritative ownership assignment.

PSA 3.1.17 will provide authoritative criticality classification.

PSA 3.1.19 will govern unauthorized-asset removal.

## 8. Security Requirements

Hardware inventory must:

- preserve stable identity.
- prevent duplicate Asset IDs.
- preserve source provenance.
- record lifecycle state.
- support updates without losing identity.
- support active and unauthorized-asset queries.
- remain available for security certification.
- integrate with the Central Architecture Registry.

## 9. Sensitive Information

The inventory must not store passwords, raw private keys, access tokens,
recovery secrets, or unrestricted credential material.

Sensitive serial numbers or physical-location details should be minimized or
referenced rather than unnecessarily duplicated.

## 10. Relationship to Later PSA Components

This registry becomes an evidence source for:

- 3.1.13 Internet-Exposed Asset Discovery.
- 3.1.14 Shadow Infrastructure Detection.
- 3.1.16 Asset Ownership Assignment.
- 3.1.17 Asset Criticality Classification.
- 3.1.18 Attack-Surface Monitoring.
- 3.1.19 Unauthorized Asset Removal.
- 3.1.20 Asset and Attack-Surface Certification.
- Phase 25 Security Logging and Detection.
- Phase 26 Vulnerability and Exposure Management.
- Phase 28 Incident Response.
- Phase 31 Owner Security Control Tower.

## 11. Central Architecture Integration

Component 3.1.1 is registered under:

platform-security-architecture

The operational implementation is:

SecurityHardwareAssetRegistry

## 12. Completion Boundary

3.1.1 establishes hardware inventory capability.

It does not claim:

- software inventory.
- cloud-resource inventory.
- automatic internet discovery.
- shadow-infrastructure detection.
- vulnerability scanning.
- ownership certification.
- criticality certification.
- complete attack-surface certification.

Those responsibilities belong to later PSA components.

## 13. Completion Statement

This component establishes the canonical LinkCraftor Hardware Asset Inventory.
