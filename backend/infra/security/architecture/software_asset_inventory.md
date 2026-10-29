# LinkCraftor Software Asset Inventory

## Document Control

Architecture: Platform Security Architecture
Phase: 3 - Asset Inventory & Attack-Surface Management
Component: 3.1.2 Software Asset Inventory
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

This component establishes the canonical LinkCraftor inventory for
security-relevant software assets.

The inventory provides a controlled record of software that builds, operates,
administers, supports, protects, observes, or otherwise materially participates
in the LinkCraftor platform.

## 2. Scope

Software assets may include:

- Operating systems.
- Runtime environments.
- Database engines.
- Web servers.
- Reverse proxies.
- Queue software.
- Worker runtimes.
- Build tools.
- Deployment tools.
- Security tools.
- Monitoring agents.
- Backup software.
- Administrative tools.
- Developer tooling where security relevant.
- Platform infrastructure software.

## 3. Boundary With Later Components

3.1.2 inventories software assets.

It does not replace:

- 3.1.4 Application Inventory.
- 3.1.5 Service and Microservice Inventory.
- 3.1.6 API Inventory.
- 3.1.11 Third-Party Integration Inventory.
- 3.1.12 Open-Source Component Inventory.

Open-source libraries and package-level dependency inventory belong
authoritatively to 3.1.12.

## 4. Canonical Software Asset Record

Every software asset must contain:

- software_asset_id.
- software_name.
- software_type.
- environment.
- status.
- source.
- architecture_id.
- component_id.
- first_seen_at.
- last_seen_at.

Optional metadata may include:

- version.
- vendor.
- installation_scope.
- host_reference.
- runtime_reference.
- deployment_reference.
- license_reference.
- managed_by.
- owner.
- criticality.
- support_status.
- internet_exposed.
- notes.
- evidence.

## 5. Identifier

Canonical identifiers use:

SEC-SW-XXXX

The identifier remains stable for the lifetime of the inventory record.

## 6. Software Types

Canonical initial software types are:

- operating-system.
- runtime.
- database-engine.
- web-server.
- reverse-proxy.
- queue-platform.
- worker-runtime.
- build-tool.
- deployment-tool.
- security-tool.
- monitoring-tool.
- backup-tool.
- administrative-tool.
- development-tool.
- infrastructure-software.
- other.

## 7. Lifecycle Status

Canonical statuses are:

- discovered.
- active.
- inactive.
- unsupported.
- prohibited.
- quarantined.
- decommissioning.
- decommissioned.

## 8. Environment

Canonical environments are:

- development.
- testing.
- staging.
- production.
- corporate.
- security.
- shared.
- unknown.

## 9. Security Requirements

The Software Asset Inventory must:

- preserve stable software identity.
- reject duplicate IDs.
- preserve provenance.
- support version recording.
- preserve first-seen timestamps.
- record lifecycle status.
- identify unsupported or prohibited software.
- support environment filtering.
- support persistent storage.
- integrate with the Central Architecture Registry.

## 10. Unsupported Software

Software may be classified as unsupported when:

- vendor support has ended.
- security support has ended.
- the version is obsolete.
- required patches cannot be obtained.
- internal platform support has ended.

Unsupported status does not automatically remove an asset.

Remediation belongs to later vulnerability, patch, and exposure-management
processes.

## 11. Prohibited Software

Software may be classified as prohibited where governance explicitly prevents
its use.

Detection of prohibited software does not automatically authorize deletion.

## 12. Sensitive Information

The registry must not contain:

- passwords.
- private keys.
- authentication tokens.
- API secrets.
- database credentials.
- recovery secrets.

Credential references may be recorded only as non-secret identifiers where
necessary.

## 13. Relationship to Later PSA Components

This registry becomes evidence for:

- 3.1.16 Asset Ownership Assignment.
- 3.1.17 Asset Criticality Classification.
- 3.1.18 Attack-Surface Monitoring.
- 3.1.19 Unauthorized Asset Removal.
- 3.1.20 Asset and Attack-Surface Certification.
- Phase 13 Software Supply-Chain Security.
- Phase 19 Runtime Security.
- Phase 25 Security Logging and Detection.
- Phase 26 Vulnerability and Patch Management.
- Phase 28 Incident Response.
- Phase 31 Owner Security Control Tower.

## 14. Central Architecture Integration

Component 3.1.2 is registered under:

platform-security-architecture

The operational implementation is:

SecuritySoftwareAssetRegistry

## 15. Completion Boundary

3.1.2 establishes the Software Asset Inventory capability.

It does not claim:

- automatic software discovery.
- SBOM completion.
- open-source dependency certification.
- vulnerability scanning.
- patch enforcement.
- application inventory completion.
- complete attack-surface certification.

## 16. Completion Statement

This component establishes the canonical LinkCraftor Software Asset Inventory.
