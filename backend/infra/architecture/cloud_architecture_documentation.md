# LinkCraftor Cloud Architecture Documentation

Version: 1.0
Status: Canonical
Phase: Cloud Infrastructure Architecture
Section: 1.1.9 Cloud Architecture Documentation
Cloud Provider: Amazon Web Services
Runtime Eligibility: Not Runtime Eligible / N/A

---

# Purpose

This document defines the canonical documentation standard for the LinkCraftor
Cloud Infrastructure Architecture.

It governs how cloud architecture decisions, strategies, standards, policies,
certifications, diagrams, evidence, and architecture changes are documented,
versioned, approved, superseded, referenced, and retained.

The objective is to ensure that LinkCraftor has one authoritative, traceable,
reviewable, and auditable cloud architecture record.

---

# Documentation Principles

Cloud architecture documentation must be:

- Authoritative
- Versioned
- Reviewable
- Traceable
- Consistent
- Explicit about status
- Explicit about ownership
- Explicit about approval
- Explicit about supersession
- Stored in source control where appropriate
- Free of secrets and sensitive credentials
- Aligned with current canonical architecture
- Distinguishable from executable configuration
- Retained as evidence of architectural decisions

Architecture documentation must not rely on undocumented tribal knowledge.

---

# Canonical Documentation Location

Canonical cloud architecture documents shall reside under:

backend/infra/architecture/

Supporting evidence may reside under:

backend/infra/evidence/

Executable infrastructure configuration shall remain separate from architecture
documentation.

Architecture documents must not be confused with Terraform modules, scripts,
runtime configuration, or deployment artifacts.

---

# Canonical Document Types

Cloud Infrastructure Architecture documentation may include:

- Architecture vision
- Provider strategy
- Service portfolio
- Region strategy
- Availability Zone strategy
- Resource organization
- Naming standards
- Configuration standards
- Architecture documentation standards
- Architecture Decision Records
- Policies
- Standards
- Diagrams
- Topology models
- Certification records
- Review reports
- Migration records
- Deprecation records
- Supersession records
- Evidence references

Each document type must identify its architectural purpose.

---

# Mandatory Document Metadata

Every canonical cloud architecture document should identify, where applicable:

- Title
- Version
- Status
- Phase
- Section
- Cloud provider
- Runtime eligibility
- Owner or architecture authority
- Approved By
- Approval or certification state
- Related architecture dependencies
- Superseded version where applicable

Where a document is not runtime executable, it must state:

Runtime Eligibility: Not Runtime Eligible / N/A

---

# Canonical Document Status Values

Canonical status values are:

- Draft
- Proposed
- Review
- Canonical
- Superseded
- Deprecated
- Retired
- Archived

Only documents explicitly marked:

Status: Canonical

may be treated as active canonical cloud architecture authority.

A Draft, Proposed, Review, Superseded, Deprecated, Retired, or Archived
document must not silently override an active Canonical document.

---

# Canonical Authority

The active canonical architecture is the set of cloud architecture documents
currently marked Canonical and not superseded by later approved architecture.

Where two documents appear to conflict, the following precedence applies:

1. Later explicitly approved and versioned correction
2. Explicit supersession record
3. More specific architecture document over a general document
4. Current canonical phase-specific decision
5. Older canonical document only where no later approved decision exists

An older document must not remain operationally authoritative after a later
canonical architecture explicitly supersedes it.

---

# Versioning

Architecture documents must use explicit versions.

Recommended format:

Major.Minor

Examples:

1.0
1.1
2.0

A minor version may be used for:

- Clarification
- Non-breaking refinement
- Additional constraints
- Corrective alignment
- Regional or operational clarification

A major version should be used when:

- Core architectural direction changes
- Ownership boundaries change materially
- Provider strategy changes materially
- Environment model changes materially
- Security model changes materially
- Runtime or deployment topology changes materially

Version increments must reflect meaningful architectural change.

---

# Change History

Material architecture changes should be traceable.

A document may include a change history containing:

- Version
- Date
- Change summary
- Reason
- Approver
- Superseded version
- Related decision record

A separate change history section is recommended where a document has multiple
material revisions.

Git history complements but does not replace explicit architectural versioning.

---

# Architecture Decision Records

Material architecture decisions may be recorded as Architecture Decision Records
(ADRs).

An ADR should identify:

- ADR identifier
- Title
- Status
- Context
- Decision
- Rationale
- Alternatives considered
- Consequences
- Dependencies
- Security impact
- Cost impact
- Operational impact
- Migration impact
- Superseded decision where applicable
- Approval

ADRs must not knowingly contradict active canonical architecture.

Where an ADR changes canonical architecture, the affected canonical document
must be updated or explicitly superseded.

---

# ADR Status Values

ADR status values may include:

- Proposed
- Accepted
- Superseded
- Rejected
- Deprecated

Accepted does not automatically mean the ADR replaces all related architecture.

Its scope must be explicit.

---

# Cross-Document References

Cloud architecture documents must reference related architecture where the
relationship materially affects interpretation.

Examples include:

- Cloud Architecture Vision
- Cloud Provider Strategy
- Cloud Service Portfolio
- Region Strategy
- Availability Zone Strategy
- Cloud Resource Organization
- Cloud Naming Standards
- Infrastructure Configuration Standards
- Identity and Access Architecture
- Security Architecture
- Data Architecture
- Universal Runtime Architecture
- Deployment Architecture

Cross-document references must not create circular authority.

A document may depend on another document without duplicating its entire
content.

---

# Current Phase 1 Architecture Set

The Phase 1 Cloud Foundation canonical architecture includes:

1.1.1 Cloud Architecture Design / Vision
1.1.2 Cloud Provider Strategy
1.1.3 Cloud Service Selection Standards / Cloud Service Portfolio
1.1.4 Region Strategy
1.1.5 Availability Zone Strategy
1.1.6 Resource Organization Model / Cloud Resource Organization
1.1.7 Cloud Naming Standards
1.1.8 Infrastructure Configuration Standards
1.1.9 Cloud Architecture Documentation
1.1.10 Cloud Foundation Certification

Each phase artifact must remain distinguishable and independently reviewable.

---

# Regional Architecture Authority

Current regional authority is:

Primary production:
- eu-west-1
- Europe (Ireland)
- RegionRole=primary

Disaster recovery:
- us-east-1
- US East (N. Virginia)
- RegionRole=disaster-recovery

Future African expansion:
- af-south-1
- Africa (Cape Town)
- RegionRole=future

The former Frankfurt architecture is not canonical.

Older references to:

- eu-central-1
- Europe (Frankfurt)
- euc1
- secondary as a canonical RegionRole

must not override the current Region Strategy and related canonical documents.

---

# Documentation Conflict Resolution

If a conflict is discovered:

1. Identify the conflicting documents.
2. Determine their versions and statuses.
3. Identify the latest approved decision.
4. Determine whether the conflict is editorial or architectural.
5. Update or supersede the outdated document.
6. Preserve traceability to the prior version.
7. Verify dependent documents.
8. Record evidence of the correction.

Conflicting documents must not both remain active Canonical authorities for the
same decision.

---

# Superseded Documentation

Superseded documents must remain identifiable.

A superseded document should record:

- Status: Superseded
- Superseded date
- Superseded by
- Replacement document
- Replacement version
- Reason where material

Superseded documents may be retained for history, audit, incident analysis, and
architecture traceability.

They must not remain indistinguishable from current canonical documents.

---

# Deprecated Documentation

Deprecated documents remain recognized but are scheduled for retirement or
replacement.

A deprecated document must identify:

- Reason for deprecation
- Replacement where known
- Migration or transition requirement
- Expected retirement condition

Deprecated architecture must not be used for new infrastructure unless
explicitly approved.

---

# Retired Documentation

A retired architecture document is no longer an active architecture authority.

Retired documents may be retained for:

- Historical traceability
- Audit
- Incident analysis
- Migration evidence
- Legal or compliance retention

Retired architecture must not be used to authorize new infrastructure.

---

# Architecture Diagrams

Architecture diagrams should be used where visual representation materially
improves understanding.

Diagrams may represent:

- Cloud topology
- Account hierarchy
- Region topology
- Availability Zone model
- Network boundaries
- Identity flows
- Data flows
- Runtime topology
- Deployment flow
- Trust boundaries
- Disaster-recovery flow

A diagram must not contradict its governing text.

Where a diagram conflicts with canonical text, the conflict must be corrected
rather than silently choosing one representation.

---

# Diagram Versioning

Material diagrams must be versioned or traceable to the version of the
architecture document they represent.

Screenshots of AWS console state must not be treated as canonical architecture
diagrams.

---

# Architecture Registry

The Cloud Infrastructure Architecture should maintain an architecture registry
or equivalent index.

The registry should identify:

- Document title
- Section
- Version
- Status
- Owner
- Location
- Dependencies
- Superseded version
- Certification state

The registry is an index of architecture authority.

It must not silently create a second conflicting architecture truth.

---

# Source Control

Canonical cloud architecture documentation should be version-controlled.

Git history must preserve:

- Authorship where available
- Change history
- Review history
- Commit history
- Recovery of prior versions

Source control does not replace explicit document status and version metadata.

A file being present in Git does not automatically make it Canonical.

---

# Review and Approval

Material cloud architecture documents must undergo review appropriate to their
impact.

Review may include:

- Architecture review
- Security review
- Data review
- Reliability review
- Cost review
- Operational review
- Deployment review

Approval authority must be explicit.

For Phase 1 canonical documents:

Approved By:
LinkCraftor Architecture

unless a later governance architecture defines a more specific approval model.

---

# Evidence and Certification

Architecture verification and certification evidence should identify:

- Architecture section
- Document version
- Review result
- Verification date
- Validation performed
- Issues found
- Corrections applied
- Final status
- Approver where applicable

Evidence must not be confused with the architecture document itself.

Certification evidence may be stored separately under:

backend/infra/evidence/

---

# Certification Relationship

Certification does not replace architecture.

Certification confirms that the architecture:

- Exists
- Is coherent
- Is internally consistent
- Has required metadata
- Has no known unresolved blocking conflicts
- Has passed the required review

A later material architecture change may require recertification.

---

# Documentation Drift

Documentation drift exists when canonical architecture no longer reflects the
approved implementation or when related canonical documents contradict each
other.

Documentation drift must be:

- Detected
- Classified
- Corrected
- Reviewed
- Recertified where material

Implementation must not silently redefine architecture merely because deployed
infrastructure differs from documentation.

---

# Sensitive Information Rules

Cloud architecture documentation must not contain:

- Passwords
- Secrets
- API tokens
- Private keys
- Recovery credentials
- Session credentials
- Personal access tokens
- Database passwords
- Private signing material
- Unnecessary AWS account IDs
- Customer-sensitive identifiers
- Confidential customer data

Sensitive values must be represented symbolically or referenced through
approved secure systems.

---

# AWS Account IDs

Specific AWS account IDs should not be embedded in general architecture
documents unless a narrowly scoped controlled artifact explicitly requires
them.

Architecture should use canonical account-role identifiers such as:

LINKCRAFTOR-PRODUCTION
LINKCRAFTOR-SECURITY
LINKCRAFTOR-DEPLOYMENT

rather than numeric AWS account IDs.

---

# Implementation References

Architecture documents may reference executable implementation locations.

Examples:

backend/infra/terraform/
backend/infra/environments/
backend/infra/modules/
backend/infra/policies/
backend/infra/security/
backend/infra/tests/

Architecture documentation must not duplicate executable implementation where a
reference is sufficient.

---

# Architecture vs Implementation

Architecture answers:

- What
- Why
- Boundary
- Authority
- Constraints
- Required behavior

Implementation answers:

- Exact Terraform resources
- Exact module composition
- Exact AWS IDs
- Exact generated names
- Exact deployment execution
- Exact runtime wiring

Architecture must not be mistaken for deployed infrastructure.

---

# Backup and Retention

Canonical architecture documents should be protected through:

- Source control
- Repository backup
- Version history
- Approved retention

Deleted or superseded architecture must remain recoverable where required for
audit, investigation, compliance, or migration.

---

# Prohibited Practices

LinkCraftor Cloud Infrastructure Architecture documentation must not:

- Maintain two conflicting active canonical documents for the same decision
- Treat Draft documents as Canonical
- Allow superseded documents to remain indistinguishable from active documents
- Embed secrets or credentials
- Store unnecessary numeric AWS account IDs
- Treat AWS console screenshots as canonical architecture
- Let implementation silently redefine architecture
- Use obsolete Frankfurt regional architecture as current authority
- Use "secondary" as a canonical RegionRole
- Create undocumented cloud architecture decisions
- Use unversioned material architecture changes
- Delete historical architecture without approved retention consideration

---

# Runtime Eligibility

This Cloud Architecture Documentation standard is an architecture and governance
artifact.

Runtime Eligibility:

Not Runtime Eligible / N/A

Future executable architecture-registry checks, documentation-drift scans,
metadata validation, dependency validation, supersession checks, and
certification jobs may require Universal Runtime Registration Standard
assessment.

---

# Canonical Decision

LinkCraftor shall maintain:

- Versioned cloud architecture documentation
- Explicit document status
- Explicit ownership and approval
- Controlled architecture supersession
- Architecture Decision Records for material decisions where appropriate
- Cross-document dependency references
- Architecture registry/index capability
- Separate architecture and implementation artifacts
- Evidence-backed certification
- Documentation-drift detection
- Source-controlled architecture history
- Sensitive-information exclusion
- Conflict-resolution rules
- Historical retention of superseded architecture

The current canonical architecture must always be distinguishable from draft,
deprecated, superseded, retired, and historical architecture.

No older architecture document may silently override a later approved canonical
decision.

---

Approved By:
LinkCraftor Architecture

Status:
CANONICAL
