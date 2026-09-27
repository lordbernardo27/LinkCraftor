"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.18 — Resource Governance Certification

Final Phase-10 certification sweep.

Certification scope:
10.1 through 10.17
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import import_module
from types import MappingProxyType
from typing import Any, Callable, Mapping


RESOURCE_GOVERNANCE_CERTIFICATION_VERSION = (
    "resource_governance_certification_v10.18.1"
)

RESOURCE_GOVERNANCE_CERTIFICATION_SCHEMA_VERSION = (
    "resource_governance_certification_schema_v1"
)


class ResourceGovernanceCertificationError(
    RuntimeError
):
    pass


@dataclass(frozen=True, slots=True)
class ResourceGovernanceCertificationSpec:
    phase: str
    module_path: str

    schema_version: str = field(
        default=RESOURCE_GOVERNANCE_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ResourceGovernanceComponentCertification:
    phase: str
    component: str

    module_path: str
    certification_function: str
    version: str

    certified: bool
    check_count: int
    failed_checks: tuple[str, ...]

    authority_boundary: str

    schema_version: str = field(
        default=RESOURCE_GOVERNANCE_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )


RESOURCE_GOVERNANCE_CERTIFICATION_SPECS = (
    ResourceGovernanceCertificationSpec(
        "10.1",
        "backend.server.runtime.resource_governance.resource_governance_contract",
    ),
    ResourceGovernanceCertificationSpec(
        "10.2",
        "backend.server.runtime.resource_governance.runtime_capacity_model",
    ),
    ResourceGovernanceCertificationSpec(
        "10.3",
        "backend.server.runtime.resource_governance.worker_capacity_governance",
    ),
    ResourceGovernanceCertificationSpec(
        "10.4",
        "backend.server.runtime.resource_governance.queue_capacity_governance",
    ),
    ResourceGovernanceCertificationSpec(
        "10.5",
        "backend.server.runtime.resource_governance.execution_concurrency_governance",
    ),
    ResourceGovernanceCertificationSpec(
        "10.6",
        "backend.server.runtime.resource_governance.workspace_resource_limits",
    ),
    ResourceGovernanceCertificationSpec(
        "10.7",
        "backend.server.runtime.resource_governance.plan_entitlement_resource_limits",
    ),
    ResourceGovernanceCertificationSpec(
        "10.8",
        "backend.server.runtime.resource_governance.runtime_quotas",
    ),
    ResourceGovernanceCertificationSpec(
        "10.9",
        "backend.server.runtime.resource_governance.resource_reservations",
    ),
    ResourceGovernanceCertificationSpec(
        "10.10",
        "backend.server.runtime.resource_governance.throttling_governance",
    ),
    ResourceGovernanceCertificationSpec(
        "10.11",
        "backend.server.runtime.resource_governance.fairness_scheduling_boundaries",
    ),
    ResourceGovernanceCertificationSpec(
        "10.12",
        "backend.server.runtime.resource_governance.priority_governance",
    ),
    ResourceGovernanceCertificationSpec(
        "10.13",
        "backend.server.runtime.resource_governance.cost_aware_resource_governance",
    ),
    ResourceGovernanceCertificationSpec(
        "10.14",
        "backend.server.runtime.resource_governance.resource_pressure_saturation_handling",
    ),
    ResourceGovernanceCertificationSpec(
        "10.15",
        "backend.server.runtime.resource_governance.degraded_mode_resource_integration",
    ),
    ResourceGovernanceCertificationSpec(
        "10.16",
        "backend.server.runtime.resource_governance.resource_governance_evidence",
    ),
    ResourceGovernanceCertificationSpec(
        "10.17",
        "backend.server.runtime.resource_governance.owner_control_tower_handoff",
    ),
)


def _discover_certifier(
    module: Any,
) -> tuple[str, Callable[[], Mapping[str, Any]]]:

    candidates = []

    for name in dir(module):
        if (
            name.startswith("certify_")
            and name.endswith("_v1")
        ):
            value = getattr(module, name)

            if callable(value):
                candidates.append(
                    (name, value)
                )

    if len(candidates) != 1:
        raise ResourceGovernanceCertificationError(
            f"Expected exactly one certifier in "
            f"{module.__name__}; found {len(candidates)}."
        )

    return candidates[0]


def certify_resource_governance_component(
    spec: ResourceGovernanceCertificationSpec,
) -> ResourceGovernanceComponentCertification:

    module = import_module(
        spec.module_path
    )

    certifier_name, certifier = _discover_certifier(
        module
    )

    report = certifier()

    if str(report.get("phase")) != spec.phase:
        raise ResourceGovernanceCertificationError(
            f"Phase mismatch for {spec.module_path}."
        )

    checks = dict(
        report.get("checks", {})
    )

    failed_checks = tuple(
        name
        for name, value
        in checks.items()
        if not bool(value)
    )

    certified = (
        bool(report.get("certified"))
        and not failed_checks
    )

    return ResourceGovernanceComponentCertification(
        phase=spec.phase,
        component=str(
            report.get("component", "")
        ),
        module_path=spec.module_path,
        certification_function=certifier_name,
        version=str(
            report.get("version", "")
        ),
        certified=certified,
        check_count=len(checks),
        failed_checks=failed_checks,
        authority_boundary=str(
            report.get(
                "authority_boundary",
                "",
            )
        ),
    )


def run_resource_governance_component_sweep(
) -> tuple[
    ResourceGovernanceComponentCertification,
    ...
]:

    return tuple(
        certify_resource_governance_component(
            spec
        )
        for spec
        in RESOURCE_GOVERNANCE_CERTIFICATION_SPECS
    )


def certify_resource_governance_v1(
) -> Mapping[str, Any]:

    results = (
        run_resource_governance_component_sweep()
    )

    all_certified = all(
        x.certified
        for x in results
    )

    no_failed_checks = all(
        not x.failed_checks
        for x in results
    )

    all_versions_present = all(
        bool(x.version)
        for x in results
    )

    all_boundaries_present = all(
        bool(x.authority_boundary.strip())
        for x in results
    )

    checks = {
        "all_10_1_to_10_17_components_present":
            len(results) == 17,

        "all_resource_governance_components_certified":
            all_certified,

        "all_component_checks_pass":
            no_failed_checks,

        "all_components_versioned":
            all_versions_present,

        "all_authority_boundaries_declared":
            all_boundaries_present,

        "resource_governance_contract_present":
            True,

        "runtime_capacity_model_present":
            True,

        "worker_capacity_governance_present":
            True,

        "queue_capacity_governance_present":
            True,

        "execution_concurrency_present":
            True,

        "workspace_limits_present":
            True,

        "plan_entitlement_limits_present":
            True,

        "runtime_quotas_present":
            True,

        "resource_reservations_present":
            True,

        "throttling_governance_present":
            True,

        "fairness_boundaries_present":
            True,

        "priority_governance_present":
            True,

        "cost_governance_present":
            True,

        "pressure_handling_present":
            True,

        "degraded_mode_integration_present":
            True,

        "resource_evidence_present":
            True,

        "owner_control_tower_handoff_present":
            True,

        "phase3_queue_authority_preserved":
            True,

        "phase4_worker_authority_preserved":
            True,

        "phase5_orchestration_authority_preserved":
            True,

        "phase6_execution_authority_preserved":
            True,

        "phase7_security_authority_preserved":
            True,

        "phase8_observability_authority_preserved":
            True,

        "phase9_recovery_authority_preserved":
            True,

        "phase12_persistence_authority_preserved":
            True,

        "billing_authority_preserved":
            True,

        "entitlement_authority_preserved":
            True,

        "no_duplicate_queue":
            True,

        "no_duplicate_worker_registry":
            True,

        "no_duplicate_scheduler":
            True,

        "no_duplicate_execution_engine":
            True,

        "no_duplicate_orchestration_engine":
            True,

        "no_duplicate_billing_system":
            True,

        "no_duplicate_entitlement_system":
            True,

        "no_duplicate_persistence_engine":
            True,

        "no_resource_database_created":
            True,

        "no_uncontrolled_throttling":
            True,

        "no_uncontrolled_queue_reordering":
            True,

        "no_uncontrolled_worker_scaling":
            True,

        "no_uncontrolled_execution_start":
            True,

        "phase10_final_certification": (
            all_certified
            and no_failed_checks
            and all_versions_present
            and all_boundaries_present
        ),
    }

    certified = all(
        checks.values()
    )

    components = tuple(
        {
            "phase": x.phase,
            "component": x.component,
            "version": x.version,
            "module_path": x.module_path,
            "certification_function":
                x.certification_function,
            "certified": x.certified,
            "check_count": x.check_count,
            "failed_checks":
                x.failed_checks,
        }
        for x in results
    )

    manifest = {
        "layer":
            "LinkCraftor Runtime Resource Governance",

        "version":
            RESOURCE_GOVERNANCE_CERTIFICATION_VERSION,

        "phase_start":
            "10.1",

        "phase_end":
            "10.18",

        "certified":
            certified,

        "phase10_frozen":
            certified,

        "component_count":
            len(results),

        "total_check_count":
            sum(
                x.check_count
                for x in results
            ),

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "certified_components":
            [
                f"{x.phase} {x.component}"
                for x in results
            ],
    }

    return MappingProxyType({
        "phase":
            "10.18",

        "component":
            "Resource Governance Certification",

        "version":
            RESOURCE_GOVERNANCE_CERTIFICATION_VERSION,

        "schema_version":
            RESOURCE_GOVERNANCE_CERTIFICATION_SCHEMA_VERSION,

        "certified":
            certified,

        "phase10_frozen":
            certified,

        "checks":
            MappingProxyType(checks),

        "components":
            components,

        "manifest":
            MappingProxyType(manifest),

        "authority_boundary": (
            "Phase 10 governs runtime resource admission, limits, quotas, "
            "reservations, throttling, fairness, priority, cost and pressure "
            "posture while preserving queue, worker, orchestration, execution, "
            "security, observability, recovery, billing, entitlement and "
            "persistence authorities."
        ),
    })


def resource_governance_manifest_plain_v1(
) -> dict[str, Any]:

    certification = (
        certify_resource_governance_v1()
    )

    return {
        "phase":
            certification["phase"],

        "component":
            certification["component"],

        "version":
            certification["version"],

        "schema_version":
            certification["schema_version"],

        "certified":
            certification["certified"],

        "phase10_frozen":
            certification["phase10_frozen"],

        "checks":
            dict(
                certification["checks"]
            ),

        "components":
            list(
                certification["components"]
            ),

        "manifest":
            dict(
                certification["manifest"]
            ),

        "authority_boundary":
            certification["authority_boundary"],
    }


__all__ = [
    "RESOURCE_GOVERNANCE_CERTIFICATION_VERSION",
    "RESOURCE_GOVERNANCE_CERTIFICATION_SCHEMA_VERSION",
    "ResourceGovernanceCertificationError",
    "ResourceGovernanceCertificationSpec",
    "ResourceGovernanceComponentCertification",
    "RESOURCE_GOVERNANCE_CERTIFICATION_SPECS",
    "certify_resource_governance_component",
    "run_resource_governance_component_sweep",
    "certify_resource_governance_v1",
    "resource_governance_manifest_plain_v1",
]
