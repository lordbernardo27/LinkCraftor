# LinkCraftor Data Asset Inventory

## Document Control

Architecture: Platform Security Architecture
Phase: 3 - Asset Inventory & Attack-Surface Management
Component: 3.1.7 Data Asset Inventory
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

This component establishes the persistent security inventory of LinkCraftor
data assets.

It is a security-governance view of existing and future authoritative data
systems.

It does not create a replacement database, storage system, data catalog,
Universal Data Architecture, state-store registry, or persistence registry.

## 2. Architectural Principle

Operational data systems own and manage operational data.

PSA 3.1.7 owns only the security inventory of those data assets.

The Universal Data Architecture, when implemented, will remain the future
authoritative enterprise data architecture.

PSA 3.1.7 will consume UDA metadata rather than replace UDA.

## 3. Current Operational Authorities

Current operational authorities include:

- backend/server/runtime/runtime_state_store.py
- backend/server/runtime/runtime_persistence.py

Other existing data authorities may include:

- Universal Unified Content Document systems.
- Universal Article Body Store systems.
- website content stores.
- uploaded-document content stores.
- semantic context persistence.
- semantic memory persistence.
- workspace-scoped data stores.
- audit and operational stores.
- application-specific canonical stores.

Each operational system remains authoritative for its own records.

## 4. Future Universal Data Architecture

The future Universal Data Architecture may become authoritative for:

- canonical data domains.
- enterprise data catalog.
- datasets.
- schemas.
- data lineage.
- data ownership.
- storage topology.
- data flows.
- retention metadata.
- canonical data classifications.
- canonical data-governance metadata.

When UDA exists, PSA 3.1.7 must integrate through metadata exchange or
registry projection.

PSA 3.1.7 must not duplicate UDA responsibilities.

## 5. Relationship

Current Data Authorities
        +
Future Universal Data Architecture
        |
        v
PSA 3.1.7 Security Data Asset Inventory

PSA receives metadata only.

PSA does not become the operational data plane.

## 6. Runtime State Store Authority

RuntimeStateStoreRegistry remains authoritative for:

- logical runtime state stores.
- store identifiers.
- state domains.
- state partitions.
- runtime state-store registration.
- runtime state-store snapshots.

## 7. Runtime Persistence Authority

RuntimePersistenceRegistry remains authoritative for:

- approved persistence backends.
- persistence backend identifiers.
- active persistence backend selection.
- persistence registry snapshots.

## 8. Canonical Security Data Asset Record

Every security data asset record must contain:

- security_data_asset_id.
- asset_key.
- asset_name.
- asset_kind.
- environment.
- status.
- source.
- source_authority.
- architecture_id.
- component_id.
- first_seen_at.
- last_seen_at.

Optional metadata may include:

- logical_domain.
- partition.
- backend_id.
- active_backend.
- application_reference.
- service_reference.
- product_reference.
- company_reference.
- workspace_scope.
- schema_reference.
- dataset_reference.
- data_domain_reference.
- lineage_reference.
- storage_reference.
- retention_reference.
- sensitivity.
- classification.
- contains_customer_data.
- contains_personal_data.
- contains_credentials.
- encryption_reference.
- owner_reference.
- technical_owner_reference.
- security_owner_reference.
- criticality.
- uda_asset_id.
- uda_domain_id.
- uda_dataset_id.
- uda_schema_id.
- uda_lineage_id.
- evidence.
- notes.

## 9. Identifier

Canonical security data asset identifiers use:

SEC-DATA-XXXX

The SEC-DATA identifier does not replace:

- runtime store identifiers.
- persistence backend identifiers.
- UDA identifiers.
- dataset identifiers.
- schema identifiers.
- application identifiers.

## 10. Asset Kinds

Canonical kinds include:

- runtime-state-store.
- persistence-backend.
- semantic-context-store.
- semantic-memory-store.
- document-content-store.
- unified-content-store.
- dataset.
- database.
- cache.
- object-store.
- file-store.
- index.
- queue-data-store.
- audit-data-store.
- workspace-data-store.
- data-domain.
- data-schema.
- data-lineage-record.
- other.

## 11. Status

Canonical statuses include:

- discovered.
- active.
- inactive.
- deprecated.
- unauthorized.
- quarantined.
- decommissioning.
- decommissioned.

## 12. Environment

Canonical environments include:

- development.
- testing.
- staging.
- production.
- shared.
- internal.
- unknown.

## 13. Runtime State Store Snapshot Contract

PSA may consume:

- generation.
- store_ids.
- domains.
- captured_at.
- fingerprint.

These values remain owned by Universal Runtime.

## 14. Persistence Registry Snapshot Contract

PSA may consume:

- generation.
- active_backend_id.
- backend_ids.
- captured_at.
- fingerprint.

These values remain owned by Universal Runtime.

## 15. UDA Integration Contract

PSA 3.1.7 must support future ingestion of UDA metadata without schema
replacement.

UDA-compatible references include:

- uda_asset_id.
- uda_domain_id.
- uda_dataset_id.
- uda_schema_id.
- uda_lineage_id.

These are foreign references into UDA.

PSA must not assign canonical UDA identity.

## 16. Source Authority

Each data asset must identify its operational source authority.

Examples:

- runtime-state-store-registry.
- runtime-persistence-registry.
- universal-data-architecture.
- universal-unified-content-document.
- universal-article-body-store.
- semantic-context-persistence.
- semantic-memory-persistence.
- workspace-store.

The source authority tells security governance which system owns the
operational truth.

## 17. Application Boundary

Application identity remains governed by 3.1.4.

## 18. Service Boundary

Service identity remains governed by 3.1.5.

## 19. Ownership Boundary

Ownership references may be stored here.

Authoritative Asset Ownership Assignment remains 3.1.16 until a later
enterprise data-governance authority is integrated.

## 20. Criticality Boundary

Criticality metadata may be stored here.

Authoritative Asset Criticality Classification remains 3.1.17.

## 21. Data Governance Boundary

PSA 3.1.7 is not the enterprise data-governance system.

The future Universal Data Architecture may own canonical enterprise data
cataloging, lineage, domain modeling, schema governance, and data governance.

PSA consumes the subset needed for security governance.

## 22. Security Requirements

3.1.7 must:

- preserve stable SEC-DATA identity.
- preserve operational identifiers.
- preserve source authority.
- ingest runtime state-store snapshots.
- ingest persistence-registry snapshots.
- accept future UDA metadata.
- preserve first-seen timestamps.
- persist security inventory metadata.
- support environment filtering.
- support asset-kind filtering.
- identify unauthorized data assets.
- never mutate Universal Runtime registries.
- never mutate future UDA registries.
- integrate with the Central Architecture Registry.

## 23. Sensitive Information

The security inventory must not persist:

- raw customer content.
- article bodies.
- uploaded document contents.
- passwords.
- bearer tokens.
- API secrets.
- private keys.
- session credentials.
- database passwords.
- raw authentication secrets.

Only metadata required for asset security governance is allowed.

## 24. Completion Boundary

3.1.7 establishes Data Asset Inventory capability.

It does not claim:

- Universal Data Architecture implementation.
- enterprise data catalog completion.
- data lineage completion.
- schema-governance completion.
- production database selection.
- encryption completion.
- privacy classification completion.
- retention enforcement.
- backup-security certification.
- database-security certification.
- ownership certification.
- criticality certification.
- data-loss-prevention completion.

## 25. Completion Statement

PSA 3.1.7 provides the security inventory view of current LinkCraftor data
assets and is explicitly compatible with the future Universal Data
Architecture without duplicating or replacing that architecture.
