# LinkCraftor Defense-in-Depth Strategy

## Document Control

| Field | Value |
|---|---|
| Architecture | Platform Security Architecture |
| Component | 1.1.4 Defense-in-Depth Strategy |
| Platform | LinkCraftor |
| Status | Foundational Security Strategy |
| Version | 1.0.0 |
| Classification | Internal Architecture |
| Canonical Location | `backend/infra/security/architecture/defense_in_depth_strategy.md` |

## 1. Purpose

This document defines the canonical LinkCraftor defense-in-depth strategy.

LinkCraftor must never depend on one security control, one network boundary,
one authentication mechanism, or one monitoring system to protect the platform.

Security must be enforced through multiple independent and complementary layers.

## 2. Defense-in-Depth Objective

The objective is to ensure that compromise or failure of one control does not
automatically result in compromise of the complete platform.

Each critical asset must be protected by multiple controls covering:

- Prevention
- Detection
- Containment
- Recovery
- Auditability

## 3. Core Defense Layers

LinkCraftor uses the following canonical defense layers:

1. External and Edge Protection
2. Identity and Authentication
3. Authorization and Entitlement
4. Tenant and Workspace Isolation
5. API Security
6. Application and Business-Logic Security
7. Runtime and Workload Security
8. Queue, Worker and Orchestration Security
9. Document and Upload Security
10. Data and Storage Security
11. Cryptography and Secret Protection
12. Infrastructure and Network Security
13. Monitoring and Detection
14. Incident Response and Containment
15. Backup, Recovery and Resilience
16. Governance and Continuous Assurance

## 4. Layer 1 — External and Edge Protection

The edge layer protects LinkCraftor before traffic reaches internal services.

Controls include:

- DNS protection
- Domain protection
- TLS
- Web application firewall
- DDoS protection
- Bot filtering
- Request filtering
- Rate limiting
- IP and reputation controls where appropriate
- Public endpoint minimization

Edge protection must not replace application-level authorization.

## 5. Layer 2 — Identity and Authentication

Every protected operation must originate from a validated identity where
identity is required.

Controls include:

- Strong authentication
- Multi-factor authentication
- Passkeys where supported
- Session protection
- Token validation
- Service identity
- Machine identity
- Compromised credential detection
- Account recovery protection

Authentication proves identity but does not automatically grant access.

## 6. Layer 3 — Authorization and Entitlement

Every protected request must be authorized independently after authentication.

Controls include:

- Role-based access control
- Attribute-based controls where required
- Resource ownership checks
- Workspace authorization
- Organization authorization
- API scopes
- Subscription entitlements
- Feature permissions
- Administrative permission boundaries
- Default-deny behavior

Authorization must be enforced server-side.

## 7. Layer 4 — Tenant and Workspace Isolation

Tenant isolation provides a separate defense layer even when authentication and
authorization already exist.

Controls include:

- Workspace-bound resources
- Tenant-aware data access
- Tenant-aware storage paths
- Tenant-aware queues
- Tenant-aware worker execution
- Tenant-aware indexes
- Tenant-aware caches
- Cross-tenant access rejection
- Isolation testing
- Tenant deletion verification

No tenant identifier supplied by a client is trusted without server-side
verification.

## 8. Layer 5 — API Security

APIs must independently protect platform capabilities.

Controls include:

- API authentication
- API authorization
- Input schema validation
- Output validation
- Request size limits
- Rate limits
- Quotas
- Replay protection
- Object-level authorization
- API key protection
- API version controls
- API audit logging

Internal APIs must not be considered trusted merely because they are internal.

## 9. Layer 6 — Application and Business-Logic Security

Applications must protect against technical and workflow-level attacks.

Controls include:

- Input validation
- Output encoding
- Injection protection
- SSRF protection
- CSRF protection
- XSS protection
- Path traversal protection
- Deserialization protection
- Business-logic validation
- Workflow state validation
- Secure error handling

Application security must remain effective even if edge filtering is bypassed.

## 10. Layer 7 — Runtime and Workload Security

Runtime infrastructure must independently constrain execution.

Controls include:

- Registered runtime handlers
- Workload identities
- Container isolation
- Sandbox controls
- Non-root execution where applicable
- Minimal runtime permissions
- Resource limits
- Runtime integrity validation
- Runtime behavior monitoring
- Compromise containment

Compromise of one workload must not provide unrestricted access to other
workloads.

## 11. Layer 8 — Queue, Worker and Orchestration Security

Asynchronous processing must enforce the same security boundaries as synchronous
requests.

Controls include:

- Queue authentication
- Queue authorization
- Worker identity
- Scheduler identity
- Orchestrator identity
- Tenant-bound jobs
- Workspace-bound jobs
- Message integrity
- Replay protection
- Duplicate execution controls
- Poison message handling
- Dead-letter queue controls
- Worker privilege restrictions

A message is not trusted merely because it exists inside an internal queue.

## 12. Layer 9 — Document and Upload Security

Files and connected content must be treated as hostile until validated.

Controls include:

- File type validation
- MIME validation
- Magic-byte validation
- File size limits
- Archive protection
- Malware detection
- Parser isolation
- Conversion sandboxing
- Quarantine
- Resource limits
- Temporary file protection
- Secure cleanup
- Content provenance

Unsafe content must not reach canonical processing pipelines without passing
required security gates.

## 13. Layer 10 — Data and Storage Security

Persistent data must remain protected even if an application layer is
compromised.

Controls include:

- Data classification
- Access restrictions
- Database authorization
- Row-level controls where required
- Storage access policies
- Tenant isolation
- Encryption at rest
- Integrity checks
- Retention controls
- Secure deletion
- Backup protection

Direct access to persistent stores must remain restricted.

## 14. Layer 11 — Cryptography and Secret Protection

Sensitive security material must receive dedicated protection.

Controls include:

- Approved cryptographic algorithms
- Key management
- Key rotation
- Certificate lifecycle management
- Secret storage
- Secret rotation
- Runtime secret injection
- Secret leakage detection
- Digital signatures
- Integrity hashing

Secrets must never be embedded in source code or exposed in logs.

## 15. Layer 12 — Infrastructure and Network Security

Infrastructure must constrain communication and administrative access.

Controls include:

- Environment separation
- Network segmentation
- Private networking
- Firewall controls
- Egress restrictions
- Service-to-service encryption
- Cloud permission boundaries
- Infrastructure policy enforcement
- Configuration drift detection
- Administrative access restrictions

Network location must not serve as proof of trust.

## 16. Layer 13 — Monitoring and Detection

Preventive controls must be supported by detection controls.

Detection must cover:

- Authentication attacks
- Authorization failures
- Cross-tenant access attempts
- Privilege escalation
- API abuse
- Malicious uploads
- Runtime anomalies
- Data access anomalies
- Infrastructure changes
- Secret leakage
- Security control failures

Critical security controls must produce observable telemetry.

## 17. Layer 14 — Incident Response and Containment

When prevention and detection reveal a compromise, LinkCraftor must contain it.

Controls include:

- Incident classification
- Account suspension
- Session revocation
- Credential revocation
- Key revocation
- Workload isolation
- Tenant isolation
- Deployment freeze
- Regional isolation
- Forensic evidence preservation

Containment must minimize blast radius.

## 18. Layer 15 — Backup, Recovery and Resilience

Recovery is a security control.

Controls include:

- Encrypted backups
- Immutable backups where required
- Isolated backup access
- Recovery verification
- Restore testing
- Disaster recovery
- Multi-region recovery
- Key and secret recovery
- Recovery audit evidence

Recovery procedures must not bypass normal security controls.

## 19. Layer 16 — Governance and Continuous Assurance

Security governance provides the final defense layer.

Controls include:

- Security architecture governance
- Control ownership
- Security standards
- Policy enforcement
- Risk tracking
- Exception governance
- Security technical debt management
- Security testing
- Control verification
- Certification

Controls must be continuously reviewed for effectiveness.

## 20. Control Independence Rule

Critical assets must not rely exclusively on controls sharing one failure mode.

Where practical:

- Authentication and authorization must be separate checks.
- API authorization and database isolation must both exist.
- Edge filtering and application validation must both exist.
- Preventive controls and detection controls must both exist.
- Production access controls and audit monitoring must both exist.
- Backup protection and production protection must be independently enforced.

## 21. Blast-Radius Reduction Rule

Every architecture must minimize the impact of compromise.

Blast-radius reduction includes:

- Tenant isolation
- Workspace isolation
- Service isolation
- Least privilege
- Environment separation
- Account separation
- Region boundaries
- Resource quotas
- Network segmentation
- Runtime sandboxing

A compromise must be prevented from spreading unnecessarily.

## 22. Security Gate Rule

Critical transitions must pass security gates.

Examples include:

- Internet → application
- Application → API
- API → service
- Service → data store
- Scheduler → queue
- Queue → worker
- Worker → canonical store
- Uploaded file → parser
- Parsed content → canonical pipeline
- Deployment artifact → production
- Administrator → privileged action

Each gate must validate the security context required for that transition.

## 23. Failure Containment Rule

When one security layer fails:

1. Adjacent security layers must remain effective.
2. Access must remain restricted where possible.
3. The failure must be detected.
4. Evidence must be preserved.
5. The affected component must be containable.
6. Recovery must use controlled procedures.

## 24. Defense Coverage Requirement

Every critical LinkCraftor asset must map to:

- At least one preventive control
- At least one detection control
- At least one containment mechanism
- At least one recovery mechanism
- At least one audit or evidence source

Unmapped critical assets are security gaps.

## 25. Owner Control Tower Visibility

The Owner's Security Control Tower must eventually expose defense-in-depth
status including:

- Failed security layers
- Degraded security layers
- Disabled security controls
- Cross-layer protection gaps
- Critical assets lacking multiple controls
- Active security incidents
- Containment status
- Recovery readiness
- Certification status

Owner visibility remains read-only by default.

## 26. Relationship to Other PSA Components

This strategy establishes the layered model used by later PSA stages.

Later components implement the individual controls for:

- Zero Trust
- Secure by Design
- Secure by Default
- Least Privilege
- Separation of Duties
- Fail-Secure behavior
- Identity security
- API security
- Tenant isolation
- Data security
- Infrastructure security
- Detection
- Incident response
- Recovery

This document does not replace those detailed implementations.

## 27. Completion Criteria

Step 1.1.4 is complete when:

- The defense-in-depth objective is documented.
- Canonical defense layers are defined.
- Each major platform security boundary has layered controls.
- Tenant and workspace isolation are represented.
- Runtime and worker protection are represented.
- Document-processing protection is represented.
- Data and infrastructure protection are represented.
- Detection and response layers are represented.
- Recovery protection is represented.
- Control independence is defined.
- Blast-radius reduction is defined.
- Security gate behavior is defined.
- Defense coverage requirements are defined.
- Owner Control Tower visibility is defined.
- The document passes structural verification.

## Certification Statement

This document defines the canonical LinkCraftor Defense-in-Depth Strategy.

It establishes the security layering model but does not certify later
operational security controls as implemented.
