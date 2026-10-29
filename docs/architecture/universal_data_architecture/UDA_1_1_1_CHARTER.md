# UNIVERSAL DATA ARCHITECTURE CHARTER

Document ID: UDA-1.1.1
Architecture: Universal Data Architecture
Phase: 1 — Data Architecture Foundation
Status: ACTIVE
Authority: Platform-wide
Canonical Location: docs/architecture/universal_data_architecture
Version: 1.0

## 1. Purpose

The Universal Data Architecture (UDA) establishes the authoritative architecture for how LinkCraftor defines, identifies, owns, stores, relates, moves, transforms, versions, governs, retrieves, derives, analyzes, protects, monitors, retains, archives, and deletes data across the platform.

The UDA exists to ensure that LinkCraftor data remains consistent, identifiable, governed, traceable, interoperable, scalable, recoverable, and suitable for production, enterprise, and future global operation.

## 2. Scope

The UDA applies to all persistent or materially reusable data generated, received, transformed, stored, indexed, replicated, analyzed, learned from, or exposed by LinkCraftor.

This includes, but is not limited to:

- users
- accounts
- tenants
- organizations
- workspaces
- domains
- websites
- site pages
- URLs
- uploaded documents
- extracted content
- canonical article bodies
- phrases
- keywords
- anchors
- targets
- target pools
- linking recommendations
- internal links
- semantic links
- external links
- semantic intelligence
- embeddings
- vectors
- graphs
- entities
- concepts
- scores
- classifications
- reasoning outputs
- explainability evidence
- learning data
- memory data
- AI evaluation data
- API data
- integration data
- plugin synchronization data
- workflow state
- runtime data
- jobs
- queues
- events
- subscriptions
- plans
- usage
- billing data
- AU transactions
- entitlements
- analytics
- reporting
- audit records
- lineage
- provenance
- incidents
- backups
- migrations
- operational metadata

Future LinkCraftor systems automatically fall under the authority of the UDA unless explicitly exempted through an approved architecture exception.

## 3. Authority

The Universal Data Architecture is the authoritative architecture for LinkCraftor platform data.

Individual services, engines, pipelines, APIs, plugins, workers, integrations, or developers must not independently establish competing canonical definitions for platform data.

Where the UDA defines a canonical identity, schema, ownership rule, relationship, lifecycle rule, or source of truth, downstream and upstream systems must conform to that definition or use an approved compatibility or migration mechanism.

## 4. Canonical Data Governance Rule

Every persistent LinkCraftor dataset must be able to identify:

1. What the data represents.
2. Who owns the data.
3. Which system is authoritative for the data.
4. Which canonical entity the data belongs to.
5. Which tenant and workspace scope applies.
6. Which schema governs the data.
7. How the data is uniquely identified.
8. Where the data is stored.
9. Which systems and identities may access the data.
10. How long the data is retained.
11. What created or modified the data.
12. How its lineage and provenance are traced.
13. Whether it can be reconstructed if lost.
14. How it can be archived or deleted.
15. How schema and version changes are governed.

A dataset that cannot answer these questions is not fully governed by the UDA.

## 5. Data Categories

The UDA recognizes the following high-level categories:

### Canonical Data
The authoritative representation of a platform entity or fact.

### Derived Data
Data computed, inferred, transformed, summarized, or enriched from canonical or other governed sources.

### Cached Data
A temporary copy created primarily to improve performance.

### Indexed Data
A representation optimized for search, lookup, retrieval, ranking, or filtering.

### Replicated Data
An authorized copy maintained for resilience, availability, geographic distribution, or performance.

### Temporary Data
Short-lived processing data that is not intended to become an authoritative persistent source.

### Archived Data
Historical data retained outside normal active operational use.

Detailed rules for these categories are defined in UDA Phase 1.1.3.

## 6. Architectural Boundaries

The UDA governs data architecture but does not replace other LinkCraftor architectures.

The UDA integrates with and establishes data requirements for:

- Universal Runtime Infrastructure
- Orchestration Architecture
- API Architecture
- Identity and Access Architecture
- Platform Security Architecture
- Cloud and Infrastructure Architecture
- Observability and Monitoring Architecture
- SupportOps Architecture
- Billing Architecture
- AI and Intelligence Architecture
- Plugin and Integration Architecture

Each architecture remains authoritative within its own domain.

## 7. Security Data Asset Inventory Integration

The UDA supplies canonical data metadata to:

PSA 3.1.7 — Security Data Asset Inventory.

The security inventory may associate governed UDA data assets with:

- SEC-DATA IDs
- security status
- exposure
- sensitivity
- security ownership
- criticality
- security evidence

The UDA remains authoritative for canonical data identity, structure, ownership, relationships, lifecycle, lineage, and metadata.

The Platform Security Architecture remains authoritative for security posture, security exposure, security criticality, security control state, and associated security evidence.

Neither architecture may create an incompatible duplicate source of truth for the same concern.

## 8. Evolution Principle

The UDA must support continued evolution of LinkCraftor.

The following may change over time:

- schemas
- databases
- storage technologies
- indexes
- pipelines
- services
- APIs
- AI models
- infrastructure
- deployment architecture
- products and integrations

Such changes must preserve or intentionally migrate:

- canonical identity
- ownership
- relationships
- provenance
- compatibility
- governance
- isolation
- lineage
- canonical truth

## 9. Scale Principle

The UDA must support LinkCraftor's progression through:

development
→ testing
→ production
→ SaaS
→ enterprise SaaS
→ large-scale platform
→ global platform

The architecture must avoid premature infrastructure complexity while preserving the ability to scale without fundamental data-model redesign.

## 10. Registration Requirement

Any new system that persists LinkCraftor data must ultimately register or define:

- dataset identity
- data owner
- canonical status
- schema
- storage location
- tenant/workspace scope
- relationships
- lifecycle
- classification
- access requirements
- lineage expectations
- recovery expectations

Unregistered or undocumented persistent data stores are architecture violations unless explicitly approved through the UDA exception process.

## 11. Source-of-Truth Principle

Canonical truth must be explicit.

Caches, indexes, replicas, analytical projections, derived datasets, temporary stores, exports, and materialized views must never silently become competing authoritative sources.

Where multiple copies exist, the architecture must identify:

- the canonical source
- the purpose of each copy
- synchronization behavior
- rebuild behavior
- failure behavior
- ownership

## 12. Certification Requirement

UDA Phase 1.1.1 is considered complete only when:

- this charter exists at the canonical architecture location
- its scope covers all current and future LinkCraftor persistent data
- its authority is explicit
- its boundaries with other architectures are explicit
- its canonical-data principle is explicit
- its evolution and scale principles are explicit
- its Security Data Asset Inventory integration is recognized
- the file is version controlled in the LinkCraftor repository

## 13. Governing Statement

All persistent or materially reusable data generated, received, transformed, stored, indexed, replicated, analyzed, learned from, or exposed by LinkCraftor falls under the Universal Data Architecture and must conform to its canonical identity, ownership, schema, lifecycle, lineage, isolation, governance, interoperability, and source-of-truth requirements.

