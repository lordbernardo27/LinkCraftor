# LinkCraftor Security Third-Party Integration Inventory

## Document Control

Architecture: Platform Security Architecture
Phase: 3 - Asset Inventory & Attack-Surface Management
Component: 3.1.11 Third-Party Integration Inventory
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

PSA 3.1.11 establishes the persistent security-governance inventory of
third-party providers, vendors, external services, and external integration
relationships used by LinkCraftor.

It does not replace operational integration authorities.

## 2. Distributed Operational Authority Model

LinkCraftor does not require one operational global provider registry.

Existing authorities remain distributed by subsystem.

Examples include:

- Cloud architecture and Cloud Service Portfolio.
- External Resolver provider provenance.
- SupportOps email provider abstractions.
- Billing and subscription integrations.
- Webhook integrations.
- OAuth integrations.
- External APIs.
- Future infrastructure and SaaS providers.

PSA 3.1.11 creates only a unified security projection across those sources.

## 3. Security Identifier

Security third-party integration IDs use:

SEC-3P-XXXX

SEC-3P is a security-governance identifier.

It does not replace:

- vendor IDs.
- provider IDs.
- cloud resource IDs.
- OAuth client IDs.
- webhook IDs.
- API account IDs.
- billing customer IDs.
- integration-specific identifiers.

## 4. Integration Types

Canonical integration types are:

- cloud-provider.
- external-content-provider.
- email-provider.
- payment-provider.
- identity-provider.
- oauth-provider.
- webhook-provider.
- api-provider.
- monitoring-provider.
- storage-provider.
- communications-provider.
- analytics-provider.
- security-provider.
- development-platform.
- commerce-platform.
- cms-platform.
- other.

## 5. Required Metadata

Every record must contain:

- security_third_party_id.
- provider_name.
- integration_type.
- environment.
- status.
- operational_authority.

## 6. Optional Metadata

Optional metadata includes:

- provider_id.
- vendor_name.
- product_name.
- subsystem.
- company_id.
- product_id.
- service_name.
- endpoint_reference.
- domain_reference.
- api_reference.
- cloud_resource_reference.
- application_reference.
- data_access_level.
- data_categories.
- authentication_mode.
- credential_reference.
- credential_storage_authority.
- internet_dependency.
- inbound_data.
- outbound_data.
- webhook_enabled.
- oauth_enabled.
- production_approved.
- security_review_status.
- contract_reference.
- ownership_reference.
- criticality.
- evidence.
- notes.

## 7. Status Values

Canonical statuses are:

- discovered.
- approved.
- active.
- inactive.
- pending-review.
- restricted.
- unauthorized.
- suspended.
- deprecated.
- decommissioning.
- decommissioned.

## 8. Environment Values

Canonical environments are:

- development.
- testing.
- staging.
- production.
- shared.
- internal.
- unknown.

## 9. Credential Boundary

The security inventory must never store:

- API keys.
- OAuth access tokens.
- OAuth refresh tokens.
- passwords.
- private keys.
- client secrets.
- webhook signing secrets.
- cloud access keys.
- payment-provider secret keys.
- SMTP credentials.
- bearer tokens.

The inventory may store non-secret references identifying where credentials
are governed.

## 10. Cloud Provider Boundary

AWS is currently the approved canonical production cloud provider.

Cloud architecture and the Cloud Service Portfolio remain authoritative for
cloud provider and cloud service lifecycle.

PSA 3.1.11 records the security relationship only.

## 11. External Resolver Boundary

External URL/provider datasets remain authoritative for resolver provider
provenance and external URL mappings.

PSA 3.1.11 does not replace the External Resolver dataset.

## 12. Email Provider Boundary

SupportOps email provider abstractions remain authoritative for outbound
email execution.

PSA 3.1.11 does not send email.

## 13. Billing Boundary

Billing and subscription systems remain authoritative for payment provider
execution and billing state.

PSA 3.1.11 does not process payments.

## 14. OAuth Boundary

PSA 3.1.11 may record OAuth provider metadata.

It does not authenticate OAuth sessions, issue tokens, or store OAuth
credentials.

Authentication remains governed by Phase 4 and Phase 8.

## 15. API Boundary

External API relationships may be referenced.

API Inventory remains PSA 3.1.6.

Full API Security remains Phase 9.

## 16. Data Boundary

Third-party data-access metadata may be recorded.

Authoritative Data Asset Inventory remains PSA 3.1.7.

Universal Data Architecture remains the future canonical enterprise data
architecture.

## 17. Ownership Boundary

Ownership references may be stored.

Authoritative Asset Ownership Assignment remains PSA 3.1.16.

## 18. Criticality Boundary

Criticality metadata may be stored.

Authoritative Asset Criticality Classification remains PSA 3.1.17.

## 19. Supply-Chain Boundary

Open-source components are not third-party service integrations.

Open-Source Component Inventory remains PSA 3.1.12.

Software Supply-Chain Security remains Phase 13.

## 20. Third-Party Security Boundary

Comprehensive third-party assurance, adversarial validation, and external
platform certification are not completed by this inventory.

Those controls remain governed by later PSA phases.

## 21. Requirements

PSA 3.1.11 must:

- preserve stable SEC-3P identity.
- persist non-secret provider metadata.
- support distributed operational authorities.
- classify provider/integration type.
- preserve provider provenance.
- record environment.
- record security status.
- record data-access metadata.
- record credential references without credentials.
- support production-approval metadata.
- support internet-dependency metadata.
- identify unauthorized integrations.
- support provider-name lookup.
- support filtering by integration type.
- support filtering by subsystem.
- integrate with the Central Architecture Registry.
- never execute third-party operations.
- never store credentials.

## 22. Completion Statement

PSA 3.1.11 provides a unified security-governance projection of third-party
integrations while preserving each existing subsystem as the operational
authority for its own providers and integrations.
