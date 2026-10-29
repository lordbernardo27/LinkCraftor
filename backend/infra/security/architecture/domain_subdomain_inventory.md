# LinkCraftor Security Domain and Subdomain Inventory

## Document Control

Architecture: Platform Security Architecture
Phase: 3 - Asset Inventory & Attack-Surface Management
Component: 3.1.9 Domain and Subdomain Inventory
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

PSA 3.1.9 establishes the persistent security inventory of domains,
subdomains, and other governed hostnames known to LinkCraftor.

It does not replace the Connect Domain pipeline, DNS provider, registrar,
workspace system, domain normalization authority, certificate authority,
or external attack-surface discovery systems.

## 2. Existing Domain Authority

Canonical domain normalization remains owned by:

backend/server/pipelines/connect_domain/
website_knowledge_pipeline/coordinator.py

The canonical helper is:

_normalize_domain()

The existing authority:

- lowercases input.
- removes HTTP and HTTPS schemes.
- removes URL paths.
- removes trailing dots.
- removes a leading www.
- requires a hostname containing a dot.
- rejects malformed domain inputs.

PSA must reuse this normalization authority rather than create a competing
normalization algorithm.

## 3. Workspace Identity Authority

The existing Connect Domain system also owns:

_resolve_workspace_id()

and:

_workspace_id_from_domain()

Default workspace identity is derived from the normalized domain.

PSA 3.1.9 does not create or alter workspace identities.

## 4. Canonical Workspace Profile

The Connect Domain coordinator persists:

backend/server/data/workspaces/<workspace_id>/workspace_profile.json

Current canonical workspace profile schema:

workspace_profile_v2

Relevant fields include:

- workspace_id.
- workspace_name.
- workspace_mode.
- domain.
- site_url.
- source_type.
- connection_status.
- created_at.
- connected_at.
- updated_at.

This operational profile remains authoritative.

## 5. Live Domain Connection Authority

The Website Knowledge Pipeline persists:

backend/server/data/live_domains/
live_domain_<workspace_id>.json

Relevant fields include:

- workspace_id.
- domain.
- source_type.
- status.
- connection_status.
- connected_at.
- updated_at.
- pipeline.

This operational record remains authoritative.

## 6. Security Identifier

Security domain inventory identifiers use:

SEC-DOM-XXXX

SEC-DOM does not replace:

- domain names.
- DNS names.
- workspace IDs.
- registrar identifiers.
- DNS provider identifiers.
- certificate identifiers.

## 7. Inventory Types

Canonical inventory types are:

- domain.
- subdomain.
- hostname.
- service-hostname.
- internal-hostname.
- external-hostname.
- other.

The type is security inventory metadata.

PSA does not attempt to derive registrable-domain boundaries using an
independent public-suffix implementation.

## 8. Required Metadata

Each security domain record contains:

- security_domain_id.
- hostname.
- domain_type.
- environment.
- status.
- source_authority.
- architecture_id.
- component_id.
- first_seen_at.
- last_seen_at.

## 9. Optional Metadata

Optional fields include:

- workspace_id.
- workspace_name.
- workspace_profile_reference.
- site_url.
- source_type.
- connection_status.
- connected_at.
- exposure.
- externally_reachable.
- company_id.
- product_id.
- registrar_reference.
- dns_provider_reference.
- certificate_reference.
- parent_domain_reference.
- ownership_reference.
- criticality.
- evidence.
- notes.

## 10. Status

Canonical statuses:

- discovered.
- active.
- inactive.
- pending.
- unauthorized.
- quarantined.
- deprecated.
- decommissioning.
- decommissioned.

## 11. Environment

Canonical environments:

- development.
- testing.
- staging.
- production.
- shared.
- internal.
- unknown.

## 12. Exposure

Exposure metadata may include:

- unknown.
- internal.
- restricted.
- external.
- internet-exposed.

Authoritative Internet-Exposed Asset Discovery remains PSA 3.1.13.

## 13. Subdomain Boundary

3.1.9 inventories known subdomains.

It does not claim comprehensive subdomain discovery.

Shadow infrastructure detection remains 3.1.14.

Internet-exposed discovery remains 3.1.13.

## 14. DNS Boundary

3.1.9 may preserve DNS provider references or DNS evidence.

Full DNS and communication security remains Phase 17.

## 15. Certificate Boundary

Certificate references may be preserved.

Certificate Inventory remains PSA 3.1.10.

Cryptographic certificate governance remains Phase 24.

## 16. Ownership Boundary

Ownership references may be stored.

Authoritative Asset Ownership Assignment remains PSA 3.1.16.

## 17. Criticality Boundary

Criticality metadata may be stored.

Authoritative Asset Criticality Classification remains PSA 3.1.17.

## 18. Domain and Brand Security Boundary

Full domain, email, and brand security remains Phase 18.

3.1.9 only establishes inventory.

## 19. Security Requirements

PSA 3.1.9 must:

- preserve stable SEC-DOM identity.
- use canonical Connect Domain normalization.
- preserve workspace relationships.
- preserve source authority.
- persist security inventory metadata.
- support domain and subdomain records.
- support environment filtering.
- support status filtering.
- support source-authority filtering.
- identify unauthorized domain records.
- identify internet-exposed records when evidence exists.
- never mutate Connect Domain operational records.
- never create DNS records.
- never change registrar configuration.
- never create workspaces.
- integrate with the Central Architecture Registry.

## 20. Completion Boundary

3.1.9 establishes Domain and Subdomain Inventory capability.

It does not claim completion of:

- DNS security.
- certificate security.
- registrar security.
- automatic subdomain discovery.
- external attack-surface discovery.
- shadow infrastructure detection.
- ownership certification.
- criticality certification.
- brand protection.

## 21. Completion Statement

PSA 3.1.9 provides a persistent security-governance projection of domains
and subdomains while preserving the canonical Connect Domain system as the
owner of operational domain truth.
