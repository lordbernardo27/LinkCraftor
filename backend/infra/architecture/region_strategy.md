# LinkCraftor AWS Region Strategy

Version: 1.0
Status: Canonical
Phase: Cloud Infrastructure Architecture
Section: 1.1.4 Region Strategy
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical AWS Region strategy for LinkCraftor.

It governs primary deployment, disaster recovery, data placement, regional
expansion, latency validation, service availability, and multi-region adoption.

---

# Regional Architecture Model

LinkCraftor shall use a phased regional deployment model:

1. Single primary production Region at launch.
2. Multi-Availability-Zone deployment within the primary Region.
3. Secondary disaster-recovery Region when required.
4. Additional Regions only after workload, customer, compliance, and latency
   requirements justify expansion.
5. Active-active multi-region operation only after formal certification.

---

# Primary Launch Region

Region Name:

Europe (Ireland)

AWS Region Code:

eu-west-1

Status:

Canonical Primary Launch Region

Approved Uses:

- Production application infrastructure
- Staging infrastructure
- Backend API workloads
- Universal Runtime workloads
- Worker fleets
- Upload infrastructure
- Queue infrastructure
- Primary databases
- Object and file storage
- Monitoring and operational infrastructure

---

# Primary Region Selection Basis

Europe (Ireland) is selected as the initial primary Region because it provides:

- Broad AWS service availability
- Mature AWS infrastructure
- Multiple Availability Zones
- Support for enterprise cloud workloads
- Suitable connectivity for initial international deployment
- A practical foundation for later European and global expansion

This selection remains subject to deployment-time validation of:

- Ghana latency
- Target-market latency
- Service availability
- Service quotas
- Data-residency requirements
- Cost
- Disaster-recovery compatibility

---

# Secondary Disaster-Recovery Region

Region Name:

Europe (Frankfurt)

AWS Region Code:

eu-central-1

Status:

Approved Secondary Region

Initial Purpose:

- Disaster-recovery readiness
- Cross-region backup replication
- Recovery artifact storage
- Infrastructure recovery testing
- Future warm-standby or pilot-light deployment

The secondary Region must not become active production infrastructure until
the relevant availability, recovery, security, data, and cost phases are
completed.

---

# Africa Region Strategy

Candidate Region:

Africa (Cape Town)

AWS Region Code:

af-south-1

Status:

Future Regional Candidate

Potential Uses:

- African customer latency optimization
- Regional enterprise deployments
- African data-residency requirements
- Regional disaster recovery
- Regional upload acceleration
- Future active regional workloads

Cape Town must not automatically replace the primary Region solely because it
is located in Africa.

Adoption requires measured validation of:

- End-user latency from Ghana and other target countries
- Service availability
- Service quotas
- Cost
- Network routing
- Disaster-recovery compatibility
- Customer demand
- Regulatory requirements

---

# Environment Region Rules

## Development

Local development remains the default.

Cloud development resources, when required, shall use the approved development
account and the primary Region unless a test specifically requires another
Region.

## Testing

Testing shall use the primary Region by default.

Regional behavior may be tested in approved non-production Regions.

## Staging

Staging shall use the primary Region and reflect the production regional
configuration as closely as practical.

## Production

Production shall initially use the primary Region with Multi-Availability-Zone
deployment where supported and justified.

Production data must not be copied into another Region without approved data,
security, retention, residency, and recovery controls.

---

# Region Selection Criteria

Any AWS Region considered for LinkCraftor must be evaluated against:

1. Availability of required AWS services
2. Number and suitability of Availability Zones
3. Latency to target users
4. Data-residency and regulatory requirements
5. Service quotas and scaling capacity
6. Infrastructure and data-transfer costs
7. Disaster-recovery compatibility
8. Cross-region replication support
9. Enterprise customer requirements
10. Operational supportability
11. Security-service availability
12. AI and specialized-compute availability
13. Sustainability and long-term AWS investment
14. Business-continuity requirements

---

# Regional Latency Validation

Before production deployment, LinkCraftor must perform latency measurements
from:

- Ghana
- West Africa
- Europe
- North America
- Other initial target markets

Measurements must include:

- DNS resolution
- CDN response
- API latency
- Upload latency
- Download latency
- Database-dependent request latency
- Queue submission latency
- End-to-end document-processing initiation time

The selected primary Region may be revised before production launch if measured
evidence demonstrates that another approved Region is materially better.

---

# Data Residency

Data placement must follow the Universal Data Architecture, Platform Security
Architecture, customer contracts, and applicable legal requirements.

The Region Strategy does not independently authorize cross-region movement of:

- Customer documents
- Reconstructed website content
- Personal data
- Authentication data
- Billing records
- Audit evidence
- Backups
- Encryption keys
- Enterprise tenant data

---

# Multi-Region Readiness

The infrastructure must be designed so that future regional expansion does not
require replacement of the core application architecture.

Regional portability requires:

- Infrastructure as Code
- Region-parameterized configuration
- Region-independent application logic where practical
- Region-specific secrets
- Region-specific encryption keys
- Region-specific resource names
- Controlled data replication
- Global traffic-routing readiness
- Regional observability
- Regional cost allocation
- Regional failover procedures

---

# Prohibited Practices

LinkCraftor must not:

- Hard-code AWS Region values throughout application code.
- Create production resources in arbitrary Regions.
- Enable cross-region data replication without approval.
- Use a Region lacking required security or recovery controls.
- Assume geographic proximity guarantees lower latency.
- Operate active-active multi-region production before certification.
- Mix development and production resources across uncontrolled Regions.
- use the default AWS Region without explicit configuration.

---

# Configuration Standard

The selected Region must be supplied through controlled configuration such as:

- Infrastructure as Code variables
- AWS account configuration
- Deployment environment configuration
- Approved environment variables
- Central configuration registries

Canonical variable names:

AWS_REGION

AWS_DEFAULT_REGION

LINKCRAFTOR_PRIMARY_REGION

LINKCRAFTOR_SECONDARY_REGION

Initial canonical values:

LINKCRAFTOR_PRIMARY_REGION=eu-west-1

LINKCRAFTOR_SECONDARY_REGION=eu-central-1

These values must not yet be added to production configuration until the
relevant environment and Infrastructure as Code phases are implemented.

---

# Runtime Eligibility

This Region Strategy is an architecture and policy artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future executable regional health checks, replication jobs, failover tests,
latency tests, and recovery operations may require Universal Runtime
Registration Standard assessment.

---

# Canonical Decision

Primary Launch Region:

eu-west-1 — Europe (Ireland)

Secondary Disaster-Recovery Region:

eu-central-1 — Europe (Frankfurt)

Future African Regional Candidate:

af-south-1 — Africa (Cape Town)

The final production activation decision remains subject to documented
deployment-time latency, service, quota, cost, security, compliance, and
resilience validation.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
