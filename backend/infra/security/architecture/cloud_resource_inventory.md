# LinkCraftor Cloud Resource Inventory

## Document Control

Architecture: Platform Security Architecture
Phase: 3 - Asset Inventory & Attack-Surface Management
Component: 3.1.3 Cloud Resource Inventory
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture
Cloud Provider: Amazon Web Services

## 1. Purpose

This component establishes the operational security inventory for LinkCraftor
cloud resources.

It does not redefine LinkCraftor cloud architecture.

The authoritative cloud organization and service-policy sources remain:

- backend/infra/architecture/cloud_resource_organization.md
- backend/infra/architecture/cloud_service_portfolio.md

3.1.3 operationalizes inventory records against those existing architectural
rules.

## 2. Existing Architecture Reuse

Cloud Resource Organization remains authoritative for:

- AWS Organizations structure.
- AWS account boundaries.
- environment isolation.
- resource hierarchy.
- mandatory cloud metadata.
- account lifecycle.
- resource lifecycle.
- production boundaries.
- infrastructure ownership expectations.

Cloud Service Portfolio remains authoritative for:

- approved AWS services.
- conditionally approved AWS services.
- future AWS services.
- not-approved AWS services.
- cloud service adoption policy.

3.1.3 must not create competing definitions.

## 3. Canonical Resource Hierarchy

The operational inventory preserves the existing hierarchy:

AWS Organization
→ AWS Account
→ AWS Region
→ Environment
→ Resource Type
→ Individual Resource

## 4. Canonical Cloud Resource Record

Every cloud resource must contain:

- cloud_resource_id.
- provider.
- provider_resource_type.
- resource_name.
- account_reference.
- region.
- environment.
- status.
- source.
- architecture_id.
- component_id.
- first_seen_at.
- last_seen_at.

Optional metadata may include:

- provider_resource_id.
- service_name.
- organizational_unit.
- region_role.
- platform_domain.
- owner_reference.
- technical_owner_reference.
- operational_owner_reference.
- security_owner_reference.
- cost_owner_reference.
- data_owner_reference.
- portfolio_status.
- lifecycle_state.
- internet_exposed.
- managed.
- temporary.
- expires_at.
- tags.
- evidence.
- notes.

## 5. Identifier

Canonical LinkCraftor cloud inventory identifiers use:

SEC-CLD-XXXX

This is the LinkCraftor security inventory identity.

It does not replace AWS ARNs, AWS resource IDs, account IDs, or provider-native
identifiers.

Provider identifiers may be referenced separately.

## 6. Provider

Initial canonical provider:

aws

The schema allows controlled future provider expansion without changing the
security inventory identity model.

## 7. Environment

Canonical environments are:

- development.
- testing.
- staging.
- production.
- sandbox.
- shared.
- security.
- infrastructure.
- deployment.
- management.
- unknown.

## 8. Resource Status

Canonical inventory statuses are:

- discovered.
- active.
- inactive.
- unauthorized.
- quarantined.
- decommissioning.
- decommissioned.

Discovery does not imply authorization.

## 9. Portfolio Status

Where applicable, a resource may record the service-policy decision associated
with its AWS service:

- approved.
- conditionally-approved.
- future.
- not-approved.
- unclassified.

The Cloud Service Portfolio remains authoritative for the actual policy.

The inventory records the observed or evaluated status and does not replace
that source.

## 10. Managed State

A resource may be marked as managed or unmanaged.

An unmanaged resource is not automatically deleted.

Unmanaged and unauthorized resource handling belongs to later attack-surface
and unauthorized-asset controls.

## 11. Ownership Boundary

The existing cloud architecture requires cloud resources to have ownership.

3.1.3 may preserve owner references as inventory metadata.

Authoritative security-wide Asset Ownership Assignment is delivered by 3.1.16.

3.1.3 therefore does not claim completion of 3.1.16.

## 12. Criticality Boundary

3.1.3 may preserve an existing criticality reference if one exists.

Authoritative Asset Criticality Classification is delivered by 3.1.17.

## 13. Security Requirements

The Cloud Resource Inventory must:

- preserve stable inventory identity.
- reject duplicate inventory IDs.
- preserve provider identity separately.
- preserve account and region context.
- preserve environment.
- preserve source provenance.
- preserve first-seen timestamps.
- support lifecycle updates.
- identify unauthorized resources.
- identify unmanaged resources.
- support environment queries.
- support region queries.
- support account queries.
- support provider-resource-type queries.
- persist inventory evidence.
- integrate with the Central Architecture Registry.

## 14. Sensitive Information

The inventory must not store:

- AWS access keys.
- AWS secret access keys.
- temporary credentials.
- private keys.
- passwords.
- authentication tokens.
- raw secret values.

AWS account IDs should not be unnecessarily embedded in architecture
documentation.

Operational inventory may use controlled account references.

## 15. Later Phase Relationships

The registry becomes evidence for:

- 3.1.13 Internet-Exposed Asset Discovery.
- 3.1.14 Shadow Infrastructure Detection.
- 3.1.16 Asset Ownership Assignment.
- 3.1.17 Asset Criticality Classification.
- 3.1.18 Attack-Surface Monitoring.
- 3.1.19 Unauthorized Asset Removal.
- 3.1.20 Asset and Attack-Surface Certification.
- Phase 15 Cloud & Infrastructure Security.
- Phase 16 Infrastructure-as-Code & Configuration Security.
- Phase 17 Network, Edge, DNS & Communication Security.
- Phase 19 Runtime Security.
- Phase 25 Security Logging and Detection.
- Phase 26 Vulnerability and Exposure Management.
- Phase 28 Incident Response.
- Phase 31 Owner Security Control Tower.

## 16. Completion Boundary

3.1.3 establishes the operational Cloud Resource Inventory.

It does not claim:

- live AWS API discovery.
- automatic AWS Config ingestion.
- automatic CloudTrail ingestion.
- shadow-infrastructure detection.
- internet-exposure discovery.
- ownership certification.
- criticality certification.
- vulnerability scanning.
- unauthorized-resource removal.
- complete attack-surface certification.

## 17. Completion Statement

This component establishes the canonical operational LinkCraftor Cloud Resource
Inventory while preserving the existing Cloud Resource Organization and Cloud
Service Portfolio as authoritative architectural sources.
