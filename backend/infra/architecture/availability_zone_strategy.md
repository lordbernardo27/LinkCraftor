# LinkCraftor Availability Zone Strategy

Version: 1.0
Status: Canonical
Phase: Cloud Infrastructure Architecture
Section: 1.1.5 Availability Zone Strategy
Cloud Provider: Amazon Web Services
Primary Region: eu-west-1
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical Availability Zone strategy for LinkCraftor.

It establishes how infrastructure must be distributed across independent
failure domains within an AWS Region to provide availability, resilience,
scalability, and controlled recovery.

---

# Canonical Availability Zone Model

LinkCraftor shall use a minimum three-zone architecture for production where
the selected AWS services support it.

Canonical logical zone identifiers:

- AZ-A
- AZ-B
- AZ-C

These logical identifiers must be mapped through Infrastructure as Code to
available Availability Zone IDs in the selected AWS account.

Application code must not depend directly on Availability Zone names such as:

- eu-west-1a
- eu-west-1b
- eu-west-1c

AWS Availability Zone letter mappings may differ between AWS accounts.

---

# Environment Strategy

## Development

Development may use:

- Local infrastructure
- One Availability Zone for low-cost cloud testing
- Multiple Availability Zones only when testing zone-aware behavior

Development must not be treated as evidence of production resilience.

## Testing

Testing may use one or more Availability Zones depending on the test objective.

Resilience, failover, networking, database, queue, and recovery tests must use
multiple zones where required.

## Staging

Staging should use at least two Availability Zones.

Staging must reproduce the production zone topology as closely as practical
before production certification.

## Production

Production shall use at least three Availability Zones where supported.

A production workload must not depend on one Availability Zone unless:

1. The service itself is regionally managed.
2. No multi-zone alternative exists.
3. The risk is documented.
4. Recovery controls are defined.
5. Architecture approval is recorded.

---

# Zone Distribution Principles

Infrastructure must be distributed according to these principles:

- Public subnets across all production zones
- Private application subnets across all production zones
- Private runtime and worker subnets across all production zones
- Private data subnets across all production zones
- Load-balancer nodes across multiple zones
- Container tasks and compute instances distributed across zones
- Database standby or cluster nodes distributed across zones
- Cache nodes distributed across zones where supported
- NAT and egress architecture designed for zone resilience
- Monitoring capable of detecting zone-specific degradation

---

# Subnet Allocation Model

Each production Availability Zone should contain logically separated subnet
classes.

## Public Subnet

Approved uses:

- Public load-balancer interfaces
- NAT gateways where selected
- Controlled internet-facing infrastructure

Application services must not be placed directly in public subnets unless
explicitly approved.

## Private Application Subnet

Approved uses:

- Backend API compute
- Frontend application compute
- Internal services
- Container workloads

## Private Runtime Subnet

Approved uses:

- Universal Runtime workers
- Background processing
- Batch processing
- Scheduled processing
- Pipeline workers

## Private Data Subnet

Approved uses:

- Relational databases
- Cache infrastructure
- Internal data services
- Other protected managed data systems

## Management Subnet

A dedicated management subnet may be introduced where justified for:

- Controlled administrative tooling
- Inspection infrastructure
- Internal operational services

---

# Workload Placement Rules

## Stateless Workloads

Stateless workloads must:

- Run across multiple Availability Zones
- Avoid zone-specific local state
- Support automatic replacement
- Support health-based traffic removal
- Support horizontal scaling across zones

## Stateful Workloads

Stateful workloads must:

- Use managed multi-zone capabilities where available
- Maintain documented replication and recovery behavior
- Avoid unreplicated zone-local storage
- Define recovery point and recovery time objectives
- Be tested for zone loss

## Worker Fleets

Worker fleets must:

- Distribute workers across multiple zones
- Avoid assigning an entire pipeline to one zone
- Support replacement in healthy zones
- Continue processing after one-zone loss
- Preserve queue ownership and job-recovery guarantees

## Upload Infrastructure

Upload infrastructure must:

- Remain accessible if one zone fails
- Use regional object storage where practical
- Avoid storing the only copy of an upload on local compute storage
- Support resumable and retryable uploads
- preserve upload-session state outside a single worker or zone

---

# Database Availability Zone Strategy

Production relational databases must use a multi-zone configuration where
supported.

Requirements:

- Primary and standby infrastructure must not occupy the same failure domain.
- Database subnet groups must span multiple Availability Zones.
- Automated failover must be enabled where supported and approved.
- Database clients must use stable managed endpoints.
- Failover behavior must be tested.
- Backups must remain independent of a single zone.
- Read replicas must not be treated as backups.

---

# Cache Availability Zone Strategy

Production cache infrastructure must be evaluated for:

- Multi-zone replication
- Automatic failover
- Node replacement
- Cache-loss tolerance
- Session persistence requirements
- Data durability requirements

Critical authoritative data must not exist only in a cache.

---

# Queue and Event Infrastructure

Regionally managed queue and event services are preferred where practical.

Queue-dependent workloads must:

- Avoid zone-specific queue ownership
- Support workers from multiple zones
- Continue accepting jobs during zone degradation
- Preserve retry and dead-letter behavior
- Expose zone-related processing failures to observability systems

---

# Storage Availability Zone Strategy

## Object Storage

Regional object storage is the preferred durable storage for:

- Uploaded documents
- Reconstructed website content
- Universal article bodies
- Runtime evidence
- Certification artifacts
- Backups
- Deployment artifacts

## Block Storage

Block storage must not contain the only durable copy of critical platform data.

Zone-bound block volumes require:

- Automated snapshots
- Replacement procedures
- Recovery testing
- Documented ownership

## Shared File Storage

Shared file storage must use multi-zone or regional capabilities where
supported and required.

---

# Zone Failure Policy

LinkCraftor must be designed to tolerate the complete loss of one production
Availability Zone without causing total platform failure.

During a zone failure:

- Traffic must be removed from unhealthy infrastructure.
- New compute must start in healthy zones.
- Queue processing must continue.
- Uploads must remain recoverable.
- Databases must fail over where supported.
- Critical data must remain available.
- Monitoring must identify the affected zone.
- Operational alerts must be raised.
- Recovery actions must be auditable.

Temporary performance degradation may be accepted, but complete platform
unavailability must not result from the loss of one zone after production
resilience certification.

---

# Capacity Reservation Rule

Healthy Availability Zones must retain enough spare capacity to absorb
critical workloads from one failed zone.

Capacity planning must account for:

- Normal traffic
- Peak traffic
- Worker backlog
- Upload bursts
- Database failover
- Cache failover
- Zone evacuation
- Deployment overlap
- Recovery operations

The platform must not operate all zones continuously at maximum capacity.

---

# Zone Balancing

LinkCraftor must monitor and control:

- Compute count per zone
- Container tasks per zone
- Worker count per zone
- Request volume per zone
- Queue-processing capacity per zone
- Database node placement
- Cache node placement
- Network traffic per zone
- NAT and egress dependency per zone
- Resource saturation per zone

Significant zone imbalance must trigger investigation or automated correction
where appropriate.

---

# Availability Zone Identification

Infrastructure as Code must discover available zones dynamically.

Preferred configuration model:

- Use Availability Zone IDs where stable cross-account identification is needed.
- Use logical zone aliases inside LinkCraftor architecture.
- Map aliases to account-specific AWS zones during provisioning.
- Exclude zones that do not support required instance types or services.
- Never assume that the letter suffix identifies the same physical zone across accounts.

Canonical logical aliases:

LINKCRAFTOR_AZ_A

LINKCRAFTOR_AZ_B

LINKCRAFTOR_AZ_C

Actual values must be assigned during the Infrastructure as Code phase.

---

# Availability Zone Selection Criteria

Each selected zone must be evaluated for:

1. Required service availability
2. Required compute instance availability
3. Capacity and quota availability
4. Network connectivity
5. Database support
6. Cache support
7. Load-balancer support
8. Cost implications
9. Operational consistency
10. Failure-domain independence

---

# Failure Testing Requirements

Before production certification, LinkCraftor must test:

- Loss of one application zone
- Loss of worker capacity in one zone
- Loss of database primary infrastructure
- Loss of cache nodes in one zone
- Load-balancer target removal
- NAT or egress failure
- Zone-specific deployment failure
- Queue-processing reduction
- Upload interruption and recovery
- Capacity rebalancing into healthy zones

Test evidence must be retained.

---

# Prohibited Practices

LinkCraftor must not:

- Deploy all production compute into one Availability Zone.
- Hard-code zone letters throughout application code.
- Store critical data only on zone-local storage.
- Route all outbound traffic through one unprotected zone dependency.
- Assign all workers for a critical pipeline to one zone.
- Treat a read replica as a backup.
- claim Multi-AZ resilience without failure testing.
- Depend on manual recovery as the only zone-failure control.

---

# Runtime Eligibility

This Availability Zone Strategy is an architecture and policy artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future executable zone health checks, failover tests, capacity rebalancing,
recovery jobs, and certification scans may require Universal Runtime
Registration Standard assessment.

---

# Canonical Decision

Primary production topology:

- Minimum three logical Availability Zones
- Multi-zone public, private application, runtime, and data subnets
- Multi-zone stateless compute
- Multi-zone worker distribution
- Multi-zone managed database configuration where supported
- Zone-independent durable object storage
- Sufficient healthy-zone capacity to withstand one-zone loss

Specific Availability Zone names and IDs must be assigned dynamically during
Infrastructure as Code implementation.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
