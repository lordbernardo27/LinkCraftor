# LinkCraftor Security Certificate Inventory

## Document Control

Architecture: Platform Security Architecture
Phase: 3 - Asset Inventory & Attack-Surface Management
Component: 3.1.10 Certificate Inventory
Version: 1.0.0
Status: Active Security Architecture
Architecture ID: platform-security-architecture

## 1. Purpose

PSA 3.1.10 establishes a persistent security-governance inventory of
certificates known to the LinkCraftor platform.

This component inventories certificate metadata only.

It does not issue certificates, terminate TLS, renew certificates, manage
private keys, operate ACME, replace a certificate authority, or replace
cloud / edge certificate-management services.

## 2. Security Certificate Identity

Canonical security certificate IDs use:

SEC-CERT-XXXX

SEC-CERT identifiers are security inventory identifiers only.

They do not replace:

- certificate serial numbers.
- X.509 fingerprints.
- certificate authority identifiers.
- cloud certificate resource IDs.
- ACME account identifiers.
- domain identifiers.

## 3. Certificate Types

Canonical certificate types are:

- tls-server.
- tls-client.
- mutual-tls.
- code-signing.
- email.
- intermediate-ca.
- root-ca.
- internal-service.
- wildcard.
- other.

## 4. Required Metadata

Every certificate inventory record must contain:

- security_certificate_id.
- certificate_type.
- subject.
- environment.
- status.
- source_authority.

## 5. Optional Metadata

Optional metadata may include:

- common_name.
- subject_alternative_names.
- issuer.
- serial_number.
- fingerprint.
- fingerprint_algorithm.
- signature_algorithm.
- public_key_algorithm.
- not_before.
- not_after.
- hostname.
- domain_reference.
- service_reference.
- application_reference.
- cloud_resource_reference.
- certificate_authority_reference.
- managed_by.
- renewal_mode.
- auto_renew.
- externally_exposed.
- evidence.
- notes.

## 6. Status Values

Canonical statuses are:

- discovered.
- active.
- pending.
- expiring.
- expired.
- revoked.
- invalid.
- unauthorized.
- quarantined.
- superseded.
- decommissioning.
- decommissioned.

## 7. Environment Values

Canonical environments are:

- development.
- testing.
- staging.
- production.
- shared.
- internal.
- unknown.

## 8. Validity and Expiry

The inventory may track:

- not_before.
- not_after.
- days_until_expiry.
- expiry_state.

Expiry state is security inventory metadata.

Certificate renewal automation is not implemented by 3.1.10.

## 9. Domain Relationship

Certificates may reference domains or subdomains inventoried under PSA 3.1.9.

Example:

SEC-CERT-0001
    -> domain_reference
        -> SEC-DOM-0001

PSA 3.1.10 does not create domains or modify Connect Domain records.

## 10. Private Key Prohibition

This inventory must never store:

- private keys.
- private key material.
- private key PEM.
- PKCS#12 private key payloads.
- passphrases.
- ACME account private keys.
- certificate-management secrets.
- HSM secrets.
- TLS session secrets.

Only non-secret certificate metadata may be stored.

## 11. Certificate Authority Boundary

The inventory may reference a certificate authority.

It does not become a certificate authority.

It does not sign certificates.

It does not issue certificates.

It does not revoke certificates.

## 12. ACME Boundary

The inventory may record ACME-related metadata or renewal mode.

It does not operate an ACME client.

It does not create or manage ACME accounts.

## 13. TLS Boundary

The inventory does not terminate TLS.

Network, edge, DNS and communication security remain governed by Phase 17.

## 14. Cryptography Boundary

Full cryptographic key and certificate governance remains Phase 24.

PSA 3.1.10 establishes inventory only.

## 15. Domain Security Boundary

Domain and Subdomain Inventory remains PSA 3.1.9.

Domain, Email and Brand Security remains Phase 18.

## 16. Ownership Boundary

Ownership references may be recorded.

Authoritative Asset Ownership Assignment remains PSA 3.1.16.

## 17. Criticality Boundary

Criticality metadata may be recorded.

Authoritative Asset Criticality Classification remains PSA 3.1.17.

## 18. Internet Exposure Boundary

The inventory may mark certificates as externally exposed when evidence exists.

Authoritative Internet-Exposed Asset Discovery remains PSA 3.1.13.

## 19. Requirements

PSA 3.1.10 must:

- preserve stable SEC-CERT identity.
- persist non-secret certificate metadata.
- track certificate type.
- track certificate subject.
- support issuer metadata.
- support serial number metadata.
- support fingerprint metadata.
- support validity dates.
- support domain references.
- support environment filtering.
- support status filtering.
- identify expired certificates.
- identify expiring certificates.
- identify unauthorized certificates.
- prohibit private-key persistence.
- prohibit certificate issuance authority.
- integrate with the Central Architecture Registry.

## 20. Completion Boundary

3.1.10 establishes Certificate Inventory capability.

It does not claim completion of:

- certificate issuance.
- certificate renewal automation.
- CA operations.
- ACME automation.
- TLS termination.
- private key management.
- HSM management.
- cryptographic policy enforcement.
- certificate revocation automation.

## 21. Completion Statement

PSA 3.1.10 provides a persistent, non-secret security inventory of
certificate metadata while preserving external and future certificate
management authorities as the owners of operational certificate lifecycle.
