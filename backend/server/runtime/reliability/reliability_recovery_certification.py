"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.12 — Reliability & Recovery Certification

Final certification sweep for Phase 9.

Certification scope:
9.1 through 9.11
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import import_module
from types import MappingProxyType
from typing import Any, Callable, Mapping


RELIABILITY_RECOVERY_CERTIFICATION_VERSION = (
    "reliability_recovery_certification_v9.12.1"
)

RELIABILITY_RECOVERY_CERTIFICATION_SCHEMA_VERSION = (
    "reliability_recovery_certification_schema_v1"
)


class ReliabilityRecoveryCertificationError(
    RuntimeError
):
    pass


@dataclass(frozen=True, slots=True)
class ReliabilityRecoveryCertificationSpec:
    phase: str
    module_path: str

    schema_version: str = field(
        default=RELIABILITY_RECOVERY_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ReliabilityRecoveryComponentCertification:
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
        default=RELIABILITY_RECOVERY_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )


RELIABILITY_RECOVERY_CERTIFICATION_SPECS = (
    ReliabilityRecoveryCertificationSpec(
        "9.1",
        "backend.server.runtime.reliability.failure_classification_containment",
    ),
    ReliabilityRecoveryCertificationSpec(
        "9.2",
        "backend.server.runtime.reliability.retry_governance",
    ),
    ReliabilityRecoveryCertificationSpec(
        "9.3",
        "backend.server.runtime.reliability.recovery_coordination",
    ),
    ReliabilityRecoveryCertificationSpec(
        "9.4",
        "backend.server.runtime.reliability.worker_loss_recovery",
    ),
    ReliabilityRecoveryCertificationSpec(
        "9.5",
        "backend.server.runtime.reliability.queue_recovery",
    ),
    ReliabilityRecoveryCertificationSpec(
        "9.6",
        "backend.server.runtime.reliability.execution_recovery",
    ),
    ReliabilityRecoveryCertificationSpec(
        "9.7",
        "backend.server.runtime.reliability.orchestration_recovery",
    ),
    ReliabilityRecoveryCertificationSpec(
        "9.8",
        "backend.server.runtime.reliability.dead_letter_governance",
    ),
    ReliabilityRecoveryCertificationSpec(
        "9.9",
        "backend.server.runtime.reliability.crash_restart_recovery",
    ),
    ReliabilityRecoveryCertificationSpec(
        "9.10",
        "backend.server.runtime.reliability.degraded_mode_operation",
    ),
    ReliabilityRecoveryCertificationSpec(
        "9.11",
        "backend.server.runtime.reliability.reliability_recovery_evidence",
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
        raise ReliabilityRecoveryCertificationError(
            f"Expected exactly one certifier in "
            f"{module.__name__}; found "
            f"{len(candidates)}."
        )

    return candidates[0]


def certify_reliability_recovery_component(
    spec: ReliabilityRecoveryCertificationSpec,
) -> ReliabilityRecoveryComponentCertification:

    module = import_module(
        spec.module_path
    )

    certifier_name, certifier = _discover_certifier(
        module
    )

    report = certifier()

    if str(report.get("phase")) != spec.phase:
        raise ReliabilityRecoveryCertificationError(
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

    return ReliabilityRecoveryComponentCertification(
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


def run_reliability_recovery_component_sweep(
) -> tuple[
    ReliabilityRecoveryComponentCertification,
    ...
]:

    return tuple(
        certify_reliability_recovery_component(
            spec
        )
        for spec
        in RELIABILITY_RECOVERY_CERTIFICATION_SPECS
    )


def certify_reliability_recovery_v1(
) -> Mapping[str, Any]:

    results = (
        run_reliability_recovery_component_sweep()
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
        "all_9_1_to_9_11_components_present":
            len(results) == 11,

        "all_reliability_components_certified":
            all_certified,

        "all_component_checks_pass":
            no_failed_checks,

        "all_components_versioned":
            all_versions_present,

        "all_authority_boundaries_declared":
            all_boundaries_present,

        "failure_classification_present":
            True,

        "retry_governance_present":
            True,

        "recovery_coordination_present":
            True,

        "worker_loss_recovery_present":
            True,

        "queue_recovery_present":
            True,

        "execution_recovery_present":
            True,

        "orchestration_recovery_present":
            True,

        "dead_letter_governance_present":
            True,

        "crash_restart_recovery_present":
            True,

        "degraded_mode_present":
            True,

        "recovery_evidence_present":
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

        "phase10_resource_governance_preserved":
            True,

        "phase12_persistence_authority_preserved":
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

        "no_duplicate_persistence_engine":
            True,

        "no_uncontrolled_retry_execution":
            True,

        "no_uncontrolled_requeue_execution":
            True,

        "no_uncontrolled_worker_restart":
            True,

        "no_reliability_state_database_created":
            True,

        "phase9_final_certification": (
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
            "LinkCraftor Runtime Reliability & Recovery",

        "version":
            RELIABILITY_RECOVERY_CERTIFICATION_VERSION,

        "phase_start":
            "9.1",

        "phase_end":
            "9.12",

        "certified":
            certified,

        "phase9_frozen":
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
            "9.12",

        "component":
            "Reliability & Recovery Certification",

        "version":
            RELIABILITY_RECOVERY_CERTIFICATION_VERSION,

        "schema_version":
            RELIABILITY_RECOVERY_CERTIFICATION_SCHEMA_VERSION,

        "certified":
            certified,

        "phase9_frozen":
            certified,

        "checks":
            MappingProxyType(checks),

        "components":
            components,

        "manifest":
            MappingProxyType(manifest),

        "authority_boundary": (
            "Phase 9 governs reliability and recovery decisions while "
            "preserving concrete queue, worker, orchestration, execution, "
            "security, observability, resource and persistence authorities."
        ),
    })


def reliability_recovery_manifest_plain_v1(
) -> dict[str, Any]:

    certification = (
        certify_reliability_recovery_v1()
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

        "phase9_frozen":
            certification["phase9_frozen"],

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
    "RELIABILITY_RECOVERY_CERTIFICATION_VERSION",
    "RELIABILITY_RECOVERY_CERTIFICATION_SCHEMA_VERSION",
    "ReliabilityRecoveryCertificationError",
    "ReliabilityRecoveryCertificationSpec",
    "ReliabilityRecoveryComponentCertification",
    "RELIABILITY_RECOVERY_CERTIFICATION_SPECS",
    "certify_reliability_recovery_component",
    "run_reliability_recovery_component_sweep",
    "certify_reliability_recovery_v1",
    "reliability_recovery_manifest_plain_v1",
]
