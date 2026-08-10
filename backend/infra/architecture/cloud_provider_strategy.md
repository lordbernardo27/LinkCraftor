# LinkCraftor Cloud Provider Strategy

Version: 1.1
Status: Canonical
Phase: Cloud Infrastructure Architecture
Section: 1.1.2 Cloud Provider Strategy

---

# Purpose

This document defines the official cloud provider strategy for LinkCraftor.

It establishes the approved cloud provider, the cloud services that may be
used, future expansion policies, and governance rules.

---

# Approved Cloud Provider

Amazon Web Services (AWS)

AWS is the official and primary cloud platform for LinkCraftor.

LinkCraftor shall use AWS as its canonical production cloud provider unless
a future architecture-governance decision explicitly approves an additional
provider.

The use of AWS as the primary provider does not require LinkCraftor business
logic to become unnecessarily dependent on provider-specific implementation
details where portable architecture is practical.

---

# Selection Objectives

The cloud platform shall provide:

- Enterprise-grade reliability
- Global scalability
- High availability
- Multi-Availability-Zone deployment
- Multi-region deployment
- Regional disaster-recovery capability
- Controlled cross-region replication
- Managed infrastructure
- Strong security
- Mature AI ecosystem
- Enterprise networking
- Cost optimization capabilities
- Long-term platform growth

---

# Approved Core AWS Services

## Networking

- Amazon VPC
- Route 53
- Elastic Load Balancer
- AWS Global Accelerator (Future)

## Compute

- Amazon EC2
- AWS Lambda (when appropriate)
- Amazon ECS
- Amazon EKS (Future)

## Storage

- Amazon S3
- Amazon EFS
- Amazon EBS
- Amazon S3 Glacier

## Databases

- Amazon RDS
- Amazon ElastiCache
- Amazon DynamoDB (where appropriate)

## Identity and Organization Governance

- AWS IAM
- AWS IAM Identity Center
- AWS Organizations
- AWS Control Tower (Future, when organizational scale justifies adoption)

## Security

- AWS KMS
- AWS Secrets Manager
- AWS Certificate Manager
- AWS WAF
- AWS Shield

## Monitoring

- Amazon CloudWatch
- AWS CloudTrail

---

# Future AWS Services

The platform may adopt additional AWS services provided they:

- Improve scalability
- Improve reliability
- Improve security
- Reduce operational complexity
- Support enterprise growth

---

# Provider Resilience Policy

AWS must support LinkCraftor's required resilience architecture through:

- Multiple Availability Zones
- Multiple AWS Regions
- Regional managed services where appropriate
- Cross-region backup and replication where approved
- Disaster-recovery infrastructure
- Health-based routing and failover capabilities
- Regional monitoring and observability
- Secure cross-account and cross-region operations

Specific primary, backup, disaster-recovery, and future expansion Regions are
defined by the canonical Region Strategy rather than this provider document.

---

# Multi-Cloud Policy

Current Strategy:

Single Primary Cloud Provider (AWS)

LinkCraftor does not require active multi-cloud production deployment for
launch.

Future Strategy:

Multi-cloud support may be considered only if there is a demonstrated
business, regulatory, resilience, customer, or technical requirement.

Any future second-cloud adoption must be approved through architecture
governance and must not weaken security, observability, data governance,
runtime reliability, or operational control.

---

# Vendor Lock-In Policy

Where practical:

- Use open standards.
- Prefer portable application architecture.
- Keep business logic independent of cloud-specific APIs whenever reasonable.

---

# Governance

All new cloud services introduced into LinkCraftor must be reviewed for:

- Security
- Cost
- Scalability
- Availability
- Regional support
- Data residency
- Operational impact
- Disaster-recovery implications
- Service quotas
- Long-term maintainability

before adoption.

AWS accounts and workloads must follow the canonical LinkCraftor account,
environment, ownership, logging, security, and resource-governance standards.

The detailed list and lifecycle classification of approved AWS services is
maintained by the Cloud Service Portfolio.

---

# Runtime Eligibility

This Cloud Provider Strategy is an architecture and governance artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Executable cloud operations introduced later, including provisioning,
inventory, compliance, failover, recovery, or provider-health workflows, must
be assessed separately under the Universal Runtime Registration Standard where
applicable.

---

# Canonical Rule

AWS is the official cloud provider for LinkCraftor.

Any deviation from this strategy requires approval through the official
architecture governance process.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL

