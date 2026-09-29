"""
Universal Runtime Owner Control Tower
Phase 1.3 — Runtime Owner Architecture Registry

Canonical registry for the Owner-facing Universal Runtime architecture.

This registry:
- declares Runtime Owner sections,
- declares absorbed legacy routes,
- declares preserved cross-tower integrations,
- declares allowed control paths,
- declares forbidden direct-control paths.

It does NOT execute runtime operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


RUNTIME_OWNER_ARCHITECTURE_REGISTRY_VERSION = (
    "runtime_owner_architecture_registry_v1.3.1"
)

RUNTIME_OWNER_ARCHITECTURE_REGISTRY_SCHEMA_VERSION = (
    "runtime_owner_architecture_registry_schema_v1"
)


class RuntimeOwnerSection(str, Enum):
    OVERVIEW = "overview"
    JOBS = "jobs"
    QUEUES = "queues"
    WORKERS_LEASES = "workers_leases"
    ORCHESTRATION = "orchestration"
    EXECUTION = "execution"
    RELIABILITY_RECOVERY = "reliability_recovery"
    RESOURCE_GOVERNANCE = "resource_governance"
    RUNTIME_APIS = "runtime_apis"
    PERSISTENCE_STATE_INTEGRITY = "persistence_state_integrity"
    OBSERVABILITY = "observability"
    SECURITY = "security"
    OWNER_ACTIONS = "owner_actions"
    EVIDENCE_AUDIT = "evidence_audit"


class RuntimeOwnerAccessMode(str, Enum):
    MONITOR = "MONITOR"
    INSPECT = "INSPECT"
    GOVERNED_CONTROL = "GOVERNED_CONTROL"
    CROSS_TOWER_HANDOFF = "CROSS_TOWER_HANDOFF"


@dataclass(frozen=True, slots=True)
class RuntimeOwnerSectionDefinition:
    key: RuntimeOwnerSection
    title: str
    access_modes: tuple[RuntimeOwnerAccessMode, ...]
    runtime_authority: str
    owner_tower_role: str


@dataclass(frozen=True, slots=True)
class RuntimeOwnerLegacyRoute:
    legacy_route: str
    canonical_section: RuntimeOwnerSection
    preserve_compatibility: bool
    legacy_label: str


@dataclass(frozen=True, slots=True)
class RuntimeOwnerCrossTowerIntegration:
    owner_page: str
    purpose: str
    runtime_relationship: str


RUNTIME_OWNER_SECTIONS = (
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.OVERVIEW,
        title="Runtime Overview",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
        ),
        runtime_authority="universal_runtime_infrastructure",
        owner_tower_role="Aggregate runtime health and owner attention signals.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.JOBS,
        title="Jobs",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
            RuntimeOwnerAccessMode.GOVERNED_CONTROL,
        ),
        runtime_authority="phase2_job_infrastructure",
        owner_tower_role="Inspect and govern runtime jobs through runtime APIs.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.QUEUES,
        title="Queues",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
            RuntimeOwnerAccessMode.GOVERNED_CONTROL,
        ),
        runtime_authority="phase3_queue_infrastructure",
        owner_tower_role="Inspect queue state and approved administrative controls.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.WORKERS_LEASES,
        title="Workers & Leases",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
        ),
        runtime_authority="phase4_worker_infrastructure",
        owner_tower_role="Monitor workers, capacity, assignments and leases.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.ORCHESTRATION,
        title="Orchestration",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
        ),
        runtime_authority="phase5_runtime_orchestration",
        owner_tower_role="Inspect orchestration progress, dependencies and readiness.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.EXECUTION,
        title="Execution",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
            RuntimeOwnerAccessMode.GOVERNED_CONTROL,
        ),
        runtime_authority="phase6_execution_engine",
        owner_tower_role="Inspect execution state and invoke approved controls.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.RELIABILITY_RECOVERY,
        title="Reliability & Recovery",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
            RuntimeOwnerAccessMode.GOVERNED_CONTROL,
        ),
        runtime_authority="phase9_reliability_recovery",
        owner_tower_role="Inspect recovery decisions and approved interventions.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.RESOURCE_GOVERNANCE,
        title="Resource Governance",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
        ),
        runtime_authority="phase10_resource_governance",
        owner_tower_role="Monitor limits, quotas, concurrency and saturation.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.RUNTIME_APIS,
        title="Runtime APIs",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
        ),
        runtime_authority="phase11_runtime_apis",
        owner_tower_role="Monitor runtime API health and administrative activity.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.PERSISTENCE_STATE_INTEGRITY,
        title="Persistence & State Integrity",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
        ),
        runtime_authority="phase12_persistence_state_integrity",
        owner_tower_role="Monitor durable state, integrity and corruption signals.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.OBSERVABILITY,
        title="Runtime Observability",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.CROSS_TOWER_HANDOFF,
        ),
        runtime_authority="phase8_observability",
        owner_tower_role="Surface runtime telemetry and hand off to diagnostics.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.SECURITY,
        title="Runtime Security",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.CROSS_TOWER_HANDOFF,
        ),
        runtime_authority="phase7_runtime_security",
        owner_tower_role="Surface runtime security status without replacing Security & Access.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.OWNER_ACTIONS,
        title="Runtime Owner Actions",
        access_modes=(
            RuntimeOwnerAccessMode.GOVERNED_CONTROL,
        ),
        runtime_authority="phase11_runtime_administrative_apis",
        owner_tower_role="Submit authenticated and authorized Owner actions.",
    ),
    RuntimeOwnerSectionDefinition(
        key=RuntimeOwnerSection.EVIDENCE_AUDIT,
        title="Runtime Evidence & Audit",
        access_modes=(
            RuntimeOwnerAccessMode.MONITOR,
            RuntimeOwnerAccessMode.INSPECT,
            RuntimeOwnerAccessMode.CROSS_TOWER_HANDOFF,
        ),
        runtime_authority="runtime_evidence_and_owner_audit",
        owner_tower_role="Expose evidence and hand off to the Audit Log Viewer.",
    ),
)


RUNTIME_OWNER_LEGACY_ROUTES = (
    RuntimeOwnerLegacyRoute(
        legacy_route="queues",
        canonical_section=RuntimeOwnerSection.QUEUES,
        preserve_compatibility=True,
        legacy_label="Orchestration & Queues",
    ),
    RuntimeOwnerLegacyRoute(
        legacy_route="jobs",
        canonical_section=RuntimeOwnerSection.JOBS,
        preserve_compatibility=True,
        legacy_label="Async Jobs",
    ),
    RuntimeOwnerLegacyRoute(
        legacy_route="workers",
        canonical_section=RuntimeOwnerSection.WORKERS_LEASES,
        preserve_compatibility=True,
        legacy_label="Workers & Clusters",
    ),
    RuntimeOwnerLegacyRoute(
        legacy_route="recovery",
        canonical_section=RuntimeOwnerSection.RELIABILITY_RECOVERY,
        preserve_compatibility=True,
        legacy_label="Recovery Vault",
    ),
    RuntimeOwnerLegacyRoute(
        legacy_route="selfhealing",
        canonical_section=RuntimeOwnerSection.RELIABILITY_RECOVERY,
        preserve_compatibility=True,
        legacy_label="Self-Healing Ops",
    ),
)


RUNTIME_OWNER_CROSS_TOWER_INTEGRATIONS = (
    RuntimeOwnerCrossTowerIntegration(
        owner_page="dashboard",
        purpose="Owner Dashboard Overview",
        runtime_relationship="Publish runtime summary and owner-attention signals.",
    ),
    RuntimeOwnerCrossTowerIntegration(
        owner_page="logs",
        purpose="Logs & Diagnostics",
        runtime_relationship="Deep runtime logs, traces and diagnostics.",
    ),
    RuntimeOwnerCrossTowerIntegration(
        owner_page="cloud",
        purpose="Infrastructure & Cloud",
        runtime_relationship="Runtime infrastructure dependency visibility.",
    ),
    RuntimeOwnerCrossTowerIntegration(
        owner_page="security",
        purpose="Security & Access",
        runtime_relationship="Runtime authentication, authorization and security handoff.",
    ),
    RuntimeOwnerCrossTowerIntegration(
        owner_page="audit",
        purpose="Audit Log Viewer",
        runtime_relationship="Owner and staff runtime action audit history.",
    ),
    RuntimeOwnerCrossTowerIntegration(
        owner_page="incident",
        purpose="Incident Management",
        runtime_relationship="Escalate runtime incidents requiring operational response.",
    ),
)


FORBIDDEN_RUNTIME_OWNER_PATHS = (
    "direct_database_mutation",
    "direct_queue_internal_mutation",
    "direct_worker_internal_mutation",
    "direct_execution_engine_mutation",
    "direct_persistence_store_mutation",
    "authorization_bypass",
    "audit_bypass",
    "recovery_governance_bypass",
)


REQUIRED_RUNTIME_OWNER_CONTROL_PATH = (
    "owner_ui",
    "owner_runtime_api",
    "authentication",
    "authorization",
    "runtime_authority",
    "evidence",
    "audit",
)


def runtime_owner_architecture_snapshot() -> Mapping[str, Any]:
    return MappingProxyType({
        "version": RUNTIME_OWNER_ARCHITECTURE_REGISTRY_VERSION,
        "schema_version": RUNTIME_OWNER_ARCHITECTURE_REGISTRY_SCHEMA_VERSION,
        "canonical_page_key": "runtime",
        "canonical_page_id": "runtimePage",
        "canonical_title": "Universal Runtime Command Center",
        "section_count": len(RUNTIME_OWNER_SECTIONS),
        "legacy_route_count": len(RUNTIME_OWNER_LEGACY_ROUTES),
        "cross_tower_integration_count": len(
            RUNTIME_OWNER_CROSS_TOWER_INTEGRATIONS
        ),
        "sections": RUNTIME_OWNER_SECTIONS,
        "legacy_routes": RUNTIME_OWNER_LEGACY_ROUTES,
        "cross_tower_integrations": RUNTIME_OWNER_CROSS_TOWER_INTEGRATIONS,
        "forbidden_paths": FORBIDDEN_RUNTIME_OWNER_PATHS,
        "required_control_path": REQUIRED_RUNTIME_OWNER_CONTROL_PATH,
    })


def certify_runtime_owner_architecture_registry_v1() -> Mapping[str, Any]:

    section_keys = tuple(
        definition.key
        for definition in RUNTIME_OWNER_SECTIONS
    )

    legacy_routes = tuple(
        definition.legacy_route
        for definition in RUNTIME_OWNER_LEGACY_ROUTES
    )

    cross_pages = tuple(
        definition.owner_page
        for definition in RUNTIME_OWNER_CROSS_TOWER_INTEGRATIONS
    )

    required_sections = tuple(RuntimeOwnerSection)

    checks = {
        "registry_version_present":
            bool(RUNTIME_OWNER_ARCHITECTURE_REGISTRY_VERSION),

        "schema_version_present":
            bool(RUNTIME_OWNER_ARCHITECTURE_REGISTRY_SCHEMA_VERSION),

        "canonical_runtime_page_declared": True,

        "all_runtime_owner_sections_declared":
            set(section_keys) == set(required_sections),

        "runtime_overview_declared":
            RuntimeOwnerSection.OVERVIEW in section_keys,

        "jobs_declared":
            RuntimeOwnerSection.JOBS in section_keys,

        "queues_declared":
            RuntimeOwnerSection.QUEUES in section_keys,

        "workers_leases_declared":
            RuntimeOwnerSection.WORKERS_LEASES in section_keys,

        "orchestration_declared":
            RuntimeOwnerSection.ORCHESTRATION in section_keys,

        "execution_declared":
            RuntimeOwnerSection.EXECUTION in section_keys,

        "recovery_declared":
            RuntimeOwnerSection.RELIABILITY_RECOVERY in section_keys,

        "resource_governance_declared":
            RuntimeOwnerSection.RESOURCE_GOVERNANCE in section_keys,

        "runtime_apis_declared":
            RuntimeOwnerSection.RUNTIME_APIS in section_keys,

        "persistence_declared":
            RuntimeOwnerSection.PERSISTENCE_STATE_INTEGRITY in section_keys,

        "observability_declared":
            RuntimeOwnerSection.OBSERVABILITY in section_keys,

        "security_declared":
            RuntimeOwnerSection.SECURITY in section_keys,

        "owner_actions_declared":
            RuntimeOwnerSection.OWNER_ACTIONS in section_keys,

        "evidence_audit_declared":
            RuntimeOwnerSection.EVIDENCE_AUDIT in section_keys,

        "legacy_queues_absorbed":
            "queues" in legacy_routes,

        "legacy_jobs_absorbed":
            "jobs" in legacy_routes,

        "legacy_workers_absorbed":
            "workers" in legacy_routes,

        "legacy_recovery_absorbed":
            "recovery" in legacy_routes,

        "legacy_selfhealing_absorbed":
            "selfhealing" in legacy_routes,

        "dashboard_handoff_preserved":
            "dashboard" in cross_pages,

        "logs_handoff_preserved":
            "logs" in cross_pages,

        "cloud_handoff_preserved":
            "cloud" in cross_pages,

        "security_handoff_preserved":
            "security" in cross_pages,

        "audit_handoff_preserved":
            "audit" in cross_pages,

        "incident_handoff_preserved":
            "incident" in cross_pages,

        "direct_database_mutation_forbidden":
            "direct_database_mutation" in FORBIDDEN_RUNTIME_OWNER_PATHS,

        "direct_queue_mutation_forbidden":
            "direct_queue_internal_mutation" in FORBIDDEN_RUNTIME_OWNER_PATHS,

        "direct_worker_mutation_forbidden":
            "direct_worker_internal_mutation" in FORBIDDEN_RUNTIME_OWNER_PATHS,

        "direct_execution_mutation_forbidden":
            "direct_execution_engine_mutation" in FORBIDDEN_RUNTIME_OWNER_PATHS,

        "direct_persistence_mutation_forbidden":
            "direct_persistence_store_mutation" in FORBIDDEN_RUNTIME_OWNER_PATHS,

        "authorization_bypass_forbidden":
            "authorization_bypass" in FORBIDDEN_RUNTIME_OWNER_PATHS,

        "audit_bypass_forbidden":
            "audit_bypass" in FORBIDDEN_RUNTIME_OWNER_PATHS,

        "required_owner_api_path_declared":
            REQUIRED_RUNTIME_OWNER_CONTROL_PATH[1] == "owner_runtime_api",

        "authentication_required":
            "authentication" in REQUIRED_RUNTIME_OWNER_CONTROL_PATH,

        "authorization_required":
            "authorization" in REQUIRED_RUNTIME_OWNER_CONTROL_PATH,

        "runtime_authority_preserved":
            "runtime_authority" in REQUIRED_RUNTIME_OWNER_CONTROL_PATH,

        "evidence_required":
            "evidence" in REQUIRED_RUNTIME_OWNER_CONTROL_PATH,

        "audit_required":
            "audit" in REQUIRED_RUNTIME_OWNER_CONTROL_PATH,

        "no_runtime_operation_execution_in_registry": True,
    }

    return MappingProxyType({
        "phase": "1.3",
        "component": "Runtime Owner Architecture Registry",
        "version": RUNTIME_OWNER_ARCHITECTURE_REGISTRY_VERSION,
        "schema_version": RUNTIME_OWNER_ARCHITECTURE_REGISTRY_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "section_count": len(RUNTIME_OWNER_SECTIONS),
        "legacy_route_count": len(RUNTIME_OWNER_LEGACY_ROUTES),
        "cross_tower_integration_count": len(
            RUNTIME_OWNER_CROSS_TOWER_INTEGRATIONS
        ),
        "authority_boundary": (
            "The Runtime Owner Architecture Registry declares Owner-facing "
            "runtime structure and governance only. It does not replace or "
            "execute Universal Runtime authorities."
        ),
    })


__all__ = [
    "RUNTIME_OWNER_ARCHITECTURE_REGISTRY_VERSION",
    "RUNTIME_OWNER_ARCHITECTURE_REGISTRY_SCHEMA_VERSION",
    "RuntimeOwnerSection",
    "RuntimeOwnerAccessMode",
    "RuntimeOwnerSectionDefinition",
    "RuntimeOwnerLegacyRoute",
    "RuntimeOwnerCrossTowerIntegration",
    "RUNTIME_OWNER_SECTIONS",
    "RUNTIME_OWNER_LEGACY_ROUTES",
    "RUNTIME_OWNER_CROSS_TOWER_INTEGRATIONS",
    "FORBIDDEN_RUNTIME_OWNER_PATHS",
    "REQUIRED_RUNTIME_OWNER_CONTROL_PATH",
    "runtime_owner_architecture_snapshot",
    "certify_runtime_owner_architecture_registry_v1",
]
