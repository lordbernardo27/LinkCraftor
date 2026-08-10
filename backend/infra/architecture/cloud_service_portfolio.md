# LinkCraftor Cloud Service Portfolio

Version: 1.1
Status: Canonical
Phase: Cloud Infrastructure Architecture
Section: 1.1.3 Cloud Service Portfolio
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical portfolio of AWS services approved,
conditionally approved, deferred, or prohibited for LinkCraftor.

It is the authoritative reference for cloud-service selection across all
LinkCraftor environments, workloads, pipelines, APIs, plugins, enterprise
tenants, and future global infrastructure.

---

# Service Status Definitions

## Approved

The service is authorized for implementation when required by the relevant
architecture and deployment phase.

## Conditionally Approved

The service may be used only after architecture, security, cost, data,
operational, and governance review.

## Future

The service is approved in principle but is not required for the current
launch infrastructure.

## Not Approved

The service must not be introduced without formal architecture approval.

---

# 1. Cloud Organization and Governance

| AWS Service | Status | Approved Use |
|---|---|---|
| AWS Organizations | Approved | Multi-account cloud organization |
| AWS Control Tower | Future | Enterprise landing zone and account governance |
| AWS Resource Access Manager | Conditionally Approved | Controlled cross-account resource sharing |
| AWS Service Catalog | Future | Governed infrastructure products |
| AWS Config | Approved | Configuration tracking and compliance evidence |
| AWS CloudFormation | Conditionally Approved | AWS-native infrastructure provisioning |
| AWS Systems Manager | Approved | Fleet operations, configuration, patching, and automation |
| AWS License Manager | Future | Enterprise software-license governance |

---

# 2. Identity and Access

| AWS Service | Status | Approved Use |
|---|---|---|
| AWS Identity and Access Management | Approved | Roles, policies, permissions, and service identities |
| AWS IAM Identity Center | Approved | Workforce access to AWS accounts |
| Amazon Cognito | Conditionally Approved | Customer identity only when selected by Identity Architecture |
| AWS Security Token Service | Approved | Temporary credentials and role assumption |
| AWS Directory Service | Future | Enterprise directory integration |
| AWS Organizations Service Control Policies | Approved | Account-level permission boundaries |

---

# 3. Networking and Connectivity

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon VPC | Approved | Isolated cloud networks |
| VPC Subnets | Approved | Public, private, data, runtime, and management segmentation |
| Internet Gateway | Approved | Controlled public connectivity |
| NAT Gateway | Approved | Controlled private-subnet egress |
| VPC Endpoints | Approved | Private access to supported AWS services |
| AWS PrivateLink | Future | Private service and enterprise connectivity |
| AWS Transit Gateway | Future | Multi-VPC and multi-region network interconnection |
| AWS Direct Connect | Future | Dedicated enterprise connectivity |
| AWS Client VPN | Conditionally Approved | Controlled administrative connectivity |
| AWS Network Firewall | Future | Managed network traffic inspection |
| VPC Flow Logs | Approved | Network traffic evidence and monitoring |
| Route 53 Resolver | Approved | Internal DNS and hybrid DNS resolution |

---

# 4. DNS, Edge, and Global Traffic

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon Route 53 | Approved | Public DNS, private DNS, routing, and health checks |
| Amazon CloudFront | Approved | CDN, edge caching, and static asset delivery |
| AWS Global Accelerator | Future | Global traffic acceleration and failover |
| AWS WAF | Approved | Web application traffic protection |
| AWS Shield Standard | Approved | Baseline DDoS protection |
| AWS Shield Advanced | Future | Enterprise DDoS protection |
| AWS Certificate Manager | Approved | Public and private TLS certificate management |

---

# 5. Load Balancing and API Entry

| AWS Service | Status | Approved Use |
|---|---|---|
| Application Load Balancer | Approved | HTTP and HTTPS application routing |
| Network Load Balancer | Conditionally Approved | High-throughput TCP and specialized workloads |
| Gateway Load Balancer | Future | Virtual network appliances |
| Amazon API Gateway | Approved | Public and private API entry infrastructure |
| AWS App Mesh | Future | Service mesh when justified |
| AWS Cloud Map | Conditionally Approved | Service discovery where required |

---

# 6. Compute and Containers

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon EC2 | Approved | General-purpose and specialized compute |
| Amazon EC2 Auto Scaling | Approved | Elastic compute scaling |
| Amazon ECS | Approved | Primary managed container orchestration |
| AWS Fargate | Approved | Serverless ECS workloads where cost-effective |
| Amazon EKS | Future | Kubernetes workloads requiring EKS capabilities |
| AWS Lambda | Conditionally Approved | Short, stateless, event-driven functions |
| AWS Batch | Conditionally Approved | Large asynchronous batch workloads |
| Amazon Lightsail | Not Approved | Not suitable for canonical enterprise infrastructure |
| EC2 Spot Instances | Conditionally Approved | Fault-tolerant and interruptible workloads |
| Dedicated Hosts | Future | Compliance or licensing-driven workloads |

---

# 7. Container and Artifact Management

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon Elastic Container Registry | Approved | Container image storage and promotion |
| AWS CodeArtifact | Conditionally Approved | Private software-package repositories |
| Amazon S3 Artifact Storage | Approved | Versioned deployment and build artifacts |
| AWS Signer | Future | Artifact and code signing |

---

# 8. Object, File, and Block Storage

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon S3 | Approved | Documents, HTML stores, evidence, backups, artifacts, and static assets |
| Amazon S3 Glacier | Approved | Long-term archive storage |
| Amazon EFS | Conditionally Approved | Shared persistent file storage |
| Amazon EBS | Approved | EC2 block storage |
| Amazon FSx | Future | Specialized enterprise file systems |
| AWS Storage Gateway | Future | Hybrid storage integration |
| AWS DataSync | Future | Managed bulk data transfer |

---

# 9. Relational and NoSQL Databases

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon RDS for PostgreSQL | Approved | Primary relational database |
| Amazon Aurora PostgreSQL-Compatible | Future | Large-scale managed relational database |
| Amazon RDS Proxy | Conditionally Approved | Database connection pooling |
| Amazon DynamoDB | Conditionally Approved | High-scale key-value and metadata workloads |
| Amazon DocumentDB | Not Approved | Requires explicit architecture justification |
| Amazon Neptune | Future | Knowledge graph workloads |
| Amazon Keyspaces | Future | Cassandra-compatible workloads |
| Amazon Timestream | Future | Time-series operational metrics |

---

# 10. Cache and Search

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon ElastiCache for Redis | Approved | Cache, sessions, counters, coordination, and rate limits |
| Amazon MemoryDB for Redis | Future | Durable Redis-compatible workloads |
| Amazon OpenSearch Service | Conditionally Approved | Search, analytics, and log-search workloads |
| Amazon CloudSearch | Not Approved | OpenSearch is preferred when search infrastructure is required |

---

# 11. Messaging, Events, and Queue Infrastructure

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon SQS | Approved | Durable distributed job queues |
| Amazon SNS | Approved | Fan-out notifications and event distribution |
| Amazon EventBridge | Approved | Event routing and scheduled events |
| Amazon MQ | Future | Broker compatibility requirements |
| Amazon Kinesis Data Streams | Future | High-throughput ordered event streaming |
| Amazon Kinesis Firehose | Future | Managed event delivery |
| Amazon MSK | Future | Kafka-compatible event infrastructure |
| AWS Step Functions | Conditionally Approved | Managed workflow orchestration |
| Amazon EventBridge Scheduler | Approved | Managed scheduled execution |

---

# 12. Upload and Data Transfer Infrastructure

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon S3 Multipart Upload | Approved | Large and resumable uploads |
| Amazon S3 Transfer Acceleration | Future | Global accelerated uploads |
| AWS Transfer Family | Future | Managed SFTP, FTPS, and FTP integrations |
| AWS Snow Family | Future | Exceptional offline enterprise migrations |
| AWS DataSync | Future | Large managed data transfers |

---

# 13. Monitoring, Logging, and Audit

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon CloudWatch Metrics | Approved | Infrastructure and service metrics |
| Amazon CloudWatch Logs | Approved | Centralized operational logs |
| Amazon CloudWatch Alarms | Approved | Threshold and anomaly alerting |
| AWS CloudTrail | Approved | AWS API and account audit records |
| AWS X-Ray | Conditionally Approved | Distributed tracing |
| Amazon Managed Service for Prometheus | Future | Large-scale Prometheus monitoring |
| Amazon Managed Grafana | Future | Enterprise visualization |
| AWS Distro for OpenTelemetry | Conditionally Approved | Metrics, logs, and traces collection |
| AWS Health Dashboard | Approved | AWS service health monitoring |

---

# 14. Security and Threat Detection

| AWS Service | Status | Approved Use |
|---|---|---|
| AWS Key Management Service | Approved | Encryption-key management |
| AWS Secrets Manager | Approved | Secret storage and rotation |
| AWS Systems Manager Parameter Store | Approved | Non-secret and limited secure configuration |
| Amazon GuardDuty | Approved | Cloud threat detection |
| AWS Security Hub | Approved | Central security posture |
| Amazon Inspector | Approved | Workload and image vulnerability scanning |
| Amazon Macie | Future | Sensitive-data discovery in S3 |
| AWS Firewall Manager | Future | Centralized firewall governance |
| AWS Audit Manager | Future | Compliance evidence automation |
| AWS Artifact | Approved | AWS compliance documentation access |
| Amazon Detective | Future | Security investigation |
| AWS IAM Access Analyzer | Approved | External and unintended access detection |

---

# 15. Backup, Recovery, and Resilience

| AWS Service | Status | Approved Use |
|---|---|---|
| AWS Backup | Approved | Central backup policy and recovery |
| Amazon S3 Versioning | Approved | Object recovery and version protection |
| Amazon S3 Object Lock | Conditionally Approved | Immutable evidence and backup retention |
| AWS Elastic Disaster Recovery | Future | Cross-region workload recovery |
| AWS Resilience Hub | Future | Resilience assessment and validation |
| AWS Fault Injection Service | Future | Controlled resilience and chaos testing |

---

# 16. Deployment and Developer Infrastructure

| AWS Service | Status | Approved Use |
|---|---|---|
| AWS CodeBuild | Conditionally Approved | Managed build execution |
| AWS CodeDeploy | Conditionally Approved | Managed workload deployment |
| AWS CodePipeline | Conditionally Approved | AWS-native delivery pipelines |
| GitHub Actions | Approved | Primary external CI/CD integration |
| AWS Cloud Development Kit | Conditionally Approved | Infrastructure as Code |
| AWS CloudFormation | Conditionally Approved | Infrastructure as Code |
| Terraform with AWS Provider | Approved | Primary portable infrastructure provisioning strategy |

---

# 17. Cost Management and FinOps

| AWS Service | Status | Approved Use |
|---|---|---|
| AWS Cost Explorer | Approved | Cost analysis |
| AWS Budgets | Approved | Budget controls and alerts |
| AWS Cost and Usage Report | Approved | Detailed cost accounting |
| AWS Cost Anomaly Detection | Approved | Unexpected-spend detection |
| AWS Compute Optimizer | Approved | Resource-rightsizing recommendations |
| AWS Savings Plans | Future | Committed compute discounts |
| Reserved Instances | Future | Predictable workload cost reduction |
| AWS Billing Conductor | Future | Enterprise billing allocation |

---

# 18. AI and Machine Learning Infrastructure

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon Bedrock | Future | Managed foundation-model access |
| Amazon SageMaker AI | Future | Model training, hosting, and lifecycle management |
| Amazon EC2 GPU Instances | Future | Specialized AI inference and training |
| AWS Inferentia Instances | Future | Cost-optimized supported inference workloads |
| Amazon Comprehend | Conditionally Approved | Managed NLP only after quality and cost evaluation |
| Amazon Textract | Conditionally Approved | OCR and structured-document extraction |
| Amazon Rekognition | Not Approved | No current canonical LinkCraftor requirement |

The proprietary LinkCraftor or LangCraftor model remains future-only and is
not part of the current launch infrastructure.

---

# 19. Analytics and Data Processing

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon Athena | Conditionally Approved | Serverless querying of S3 data |
| AWS Glue | Future | Data catalog and managed ETL |
| Amazon Redshift | Future | Enterprise analytics warehouse |
| Amazon EMR | Future | Large-scale distributed processing |
| Amazon QuickSight | Future | Managed business intelligence |
| AWS Lake Formation | Future | Governed data-lake infrastructure |

---

# 20. Enterprise Integration

| AWS Service | Status | Approved Use |
|---|---|---|
| Amazon AppFlow | Future | Managed SaaS data integrations |
| Amazon SES | Approved | Transactional email infrastructure |
| Amazon Pinpoint | Future | Large-scale customer messaging |
| AWS Marketplace | Future | Product and integration distribution |
| AWS Private Marketplace | Future | Enterprise software governance |

---

# Regional and Disaster-Recovery Service Boundary

This Cloud Service Portfolio determines whether an AWS service is approved,
conditionally approved, future, or not approved.

It does not determine the canonical primary Region, disaster-recovery Region,
Availability Zone topology, replication topology, or recovery activation model.

Those decisions are defined by the relevant Region Strategy, Availability Zone
Strategy, Disaster Recovery Architecture, data architecture, and
workload-specific infrastructure designs.

The existence of a designated disaster-recovery Region does not automatically
make every cross-region AWS service a launch requirement.

Services such as:

- AWS Global Accelerator
- AWS Transit Gateway
- AWS Elastic Disaster Recovery
- AWS Resilience Hub
- AWS Fault Injection Service

must retain their portfolio status until the architecture phase that depends on
them explicitly approves activation.

A service classified as Future must not be promoted to launch infrastructure
solely because it could support multi-region or disaster-recovery operations.

---

# Selection Rules

A service may be introduced only when:

1. Its use case is documented.
2. Existing approved services cannot meet the requirement adequately.
3. Security impact is assessed.
4. Data residency and classification requirements are assessed.
5. Availability and recovery requirements are defined.
6. Expected cost is estimated.
7. Monitoring and ownership are assigned.
8. Infrastructure as Code support is provided.
9. Vendor-lock-in implications are documented.
10. Architecture approval is recorded.

---

# Prohibited Adoption Rules

LinkCraftor must not:

- Adopt overlapping AWS services without documented justification.
- Introduce a service solely because it is available.
- Use production services without monitoring and cost controls.
- Store secrets in source code, container images, or unsecured configuration.
- Create unmanaged production resources manually where Infrastructure as Code is required.
- Use lower-environment resources for production workloads.
- introduce future services before their architecture stage is approved.

---

# Current Launch Preference

The launch infrastructure should prefer the smallest reliable AWS service set
that supports the approved production requirements.

Initial preference:

- Route 53
- CloudFront
- AWS Certificate Manager
- AWS WAF
- Application Load Balancer
- Amazon VPC
- Amazon ECS
- AWS Fargate or EC2 as selected by workload assessment
- Amazon ECR
- Amazon S3
- Amazon RDS for PostgreSQL
- Amazon ElastiCache for Redis
- Amazon SQS
- Amazon SNS
- Amazon EventBridge
- AWS IAM
- AWS KMS
- AWS Secrets Manager
- Amazon CloudWatch
- AWS CloudTrail
- AWS Backup
- AWS Budgets
- AWS Cost Anomaly Detection

This list is an architectural preference, not proof that every service must be
activated at launch.

Cross-region, disaster-recovery, and global-traffic services must be activated
only when required by the certified regional, resilience, recovery, networking,
or workload architecture.

The Cloud Service Portfolio does not independently authorize cross-region data
replication or disaster-recovery activation.

---

# Runtime Eligibility

This Cloud Service Portfolio is a policy and registry-definition artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Individual executable cloud operations introduced in later phases may require
Universal Runtime Registration Standard eligibility assessment.

---

# Canonical Rule

Only services classified as Approved or Conditionally Approved may be
introduced into LinkCraftor.

A Conditionally Approved service requires documented approval before use.

Future services must remain unimplemented until their dependent architecture
and implementation phase is approved.

Any unlisted AWS service is treated as Not Approved until reviewed.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL

