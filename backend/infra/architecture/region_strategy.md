# LinkCraftor AWS Region Strategy

Version: 1.1
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
3. A designated disaster-recovery Region maintained for backup, recovery,
   replication, recovery testing, and controlled failover.
4. The disaster-recovery Region shall not operate normal production workloads
   from day one unless explicitly activated through an approved recovery event
   or certified recovery test.
5. Additional Regions may be adopted only after workload, customer, compliance,
   latency, residency, and business requirements justify expansion.
6. Active-active multi-region production operation is deferred until formally
   designed, tested, and certified.

---

# Primary Launch Region

Region Name:

Europe (Ireland)

AWS Region Code:

eu-west-1

Status:

Canonical Primary Launch Region

Approved Uses:

- Primary production application infrastructure
- Amazon ECS and AWS Fargate production services
- Backend API infrastructure and workloads
- Universal Runtime workloads
- Worker fleets
- Upload infrastructure
- Queue and event infrastructure
- Amazon RDS for PostgreSQL primary databases
- Amazon S3 production storage
- Amazon CloudFront origin infrastructure
- Amazon Route 53 integrations
- Monitoring and operational infrastructure
- Staging infrastructure where defined by the environment architecture

Ireland is the normal production-serving Region for LinkCraftor at launch.

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

# Disaster-Recovery Region

Region Name:

US East (N. Virginia)

AWS Region Code:

us-east-1

Status:

Canonical Disaster-Recovery Region

Initial Purpose:

- Disaster-recovery readiness
- Backup infrastructure
- Cross-region backup replication where approved
- Recovery artifact storage
- Emergency regional failover
- Infrastructure recovery testing
- Restore or promotion of replicated services during a recovery event
- Future cross-region replication
- Future pilot-light or warm-standby infrastructure where justified

The disaster-recovery Region is not a second active production Region at
launch.

During normal operation, customer production workloads shall be served from
the primary Ireland Region.

US East (N. Virginia) may become production-serving infrastructure only during:

- An approved disaster-recovery event
- A controlled regional failover
- A certified recovery exercise
- An explicitly approved future multi-region architecture

Activation must follow the applicable recovery, security, data, networking,
observability, cost, and governance controls.

The existence of this disaster-recovery Region does not independently
authorize replication of customer or regulated data.

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

Production shall initially use the primary Ireland Region with
Multi-Availability-Zone deployment where supported and justified.

The N. Virginia disaster-recovery Region shall remain non-primary during
normal operation and must not independently serve normal production traffic
until an approved failover or recovery process activates it.

Production data must not be copied or replicated into another Region without
approved data, security, retention, residency, encryption, compliance, and
recovery controls.

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

# Regional Failover Model

Normal Operation:

Primary Production Region:

eu-west-1 — Europe (Ireland)

Disaster-Recovery Region:

us-east-1 — US East (N. Virginia)

Under normal conditions, production traffic and production-serving workloads
remain in Ireland.

If Ireland experiences a qualifying major regional outage or a recovery event
is otherwise formally declared, LinkCraftor may activate the N. Virginia
disaster-recovery environment through controlled recovery procedures.

The recovery sequence may include:

1. Confirm the regional incident.
2. Protect against split-brain or conflicting writes.
3. Validate the latest approved recovery state.
4. Restore, promote, or activate required replicated infrastructure.
5. Validate databases, object stores, queues, secrets, configuration, and
   application dependencies.
6. Redirect approved traffic to the recovery environment.
7. Verify application, API, runtime, security, and observability health.
8. Continue recovery-region operation until primary-region restoration or
   controlled failback is approved.

Failover must never be treated as an uncontrolled DNS-only switch.

Detailed RPO, RTO, replication topology, database promotion, data recovery,
traffic failover, and failback procedures belong to the Disaster Recovery
Architecture and workload-specific recovery designs.

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

LINKCRAFTOR_DR_REGION

Compatibility alias:

LINKCRAFTOR_SECONDARY_REGION

Initial canonical values:

LINKCRAFTOR_PRIMARY_REGION=eu-west-1

LINKCRAFTOR_DR_REGION=us-east-1

LINKCRAFTOR_SECONDARY_REGION=us-east-1

LINKCRAFTOR_DR_REGION is the preferred canonical variable for the designated
disaster-recovery Region.

LINKCRAFTOR_SECONDARY_REGION is retained only as a compatibility alias and
must resolve to the same Region unless a later architecture revision removes
the alias.

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

Primary Production Region:

eu-west-1 — Europe (Ireland)

Role:

Primary production-serving Region at launch.

Canonical Disaster-Recovery Region:

us-east-1 — US East (N. Virginia)

Role:

Backup, recovery, emergency failover, recovery testing, and future approved
cross-region replication. It is not a second active production Region during
normal launch operation.

Future African Regional Candidate:

af-south-1 — Africa (Cape Town)

Role:

Potential future African regional expansion subject to measured customer,
latency, residency, service, cost, compliance, and operational requirements.

The production architecture therefore begins as:

Ireland (eu-west-1)
    Primary production
        |
        | controlled recovery / approved replication
        v
N. Virginia (us-east-1)
    Disaster recovery

Cape Town (af-south-1)
    Future African regional candidate

The final infrastructure activation of disaster-recovery capabilities remains
subject to the required data, networking, security, backup, replication,
recovery, Infrastructure as Code, monitoring, testing, and governance phases.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL

