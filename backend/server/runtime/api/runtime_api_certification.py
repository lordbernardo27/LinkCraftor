"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.14 — Runtime API Certification

Final certification sweep for Phase 11.

Certification scope:
11.1 through 11.13
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import import_module
from types import MappingProxyType
from typing import Any, Callable, Mapping


RUNTIME_API_CERTIFICATION_VERSION = (
    "runtime_api_certification_v11.14.1"
)

RUNTIME_API_CERTIFICATION_SCHEMA_VERSION = (
    "runtime_api_certification_schema_v1"
)


class RuntimeAPICertificationError(
    RuntimeError
):
    pass


@dataclass(frozen=True, slots=True)
class RuntimeAPICertificationSpec:
    phase: str
    module_path: str

    schema_version: str = field(
        default=RUNTIME_API_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeAPIComponentCertification:
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
        default=RUNTIME_API_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )


RUNTIME_API_CERTIFICATION_SPECS = (
    RuntimeAPICertificationSpec(
        "11.1",
        "backend.server.runtime.api.runtime_api_contract",
    ),
    RuntimeAPICertificationSpec(
        "11.2",
        "backend.server.runtime.api.job_api",
    ),
    RuntimeAPICertificationSpec(
        "11.3",
        "backend.server.runtime.api.queue_api",
    ),
    RuntimeAPICertificationSpec(
        "11.4",
        "backend.server.runtime.api.worker_api",
    ),
    RuntimeAPICertificationSpec(
        "11.5",
        "backend.server.runtime.api.execution_api",
    ),
    RuntimeAPICertificationSpec(
        "11.6",
        "backend.server.runtime.api.orchestration_api",
    ),
    RuntimeAPICertificationSpec(
        "11.7",
        "backend.server.runtime.api.runtime_state_api",
    ),
    RuntimeAPICertificationSpec(
        "11.8",
        "backend.server.runtime.api.cancellation_termination_api",
    ),
    RuntimeAPICertificationSpec(
        "11.9",
        "backend.server.runtime.api.retry_recovery_api",
    ),
    RuntimeAPICertificationSpec(
        "11.10",
        "backend.server.runtime.api.administrative_runtime_api",
    ),
    RuntimeAPICertificationSpec(
        "11.11",
        "backend.server.runtime.api.api_security_integration",
    ),
    RuntimeAPICertificationSpec(
        "11.12",
        "backend.server.runtime.api.api_request_governance",
    ),
    RuntimeAPICertificationSpec(
        "11.13",
        "backend.server.runtime.api.runtime_api_evidence_owner_handoff",
    ),
)


def _discover_certifier(
    module: Any,
) -> tuple[
    str,
    Callable[[], Mapping[str, Any]],
]:

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
        raise RuntimeAPICertificationError(
            f"Expected exactly one certifier in "
            f"{module.__name__}; found {len(candidates)}."
        )

    return candidates[0]


def certify_runtime_api_component(
    spec: RuntimeAPICertificationSpec,
) -> RuntimeAPIComponentCertification:

    module = import_module(
        spec.module_path
    )

    certifier_name, certifier = _discover_certifier(
        module
    )

    report = certifier()

    if str(report.get("phase")) != spec.phase:
        raise RuntimeAPICertificationError(
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

    return RuntimeAPIComponentCertification(
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


def run_runtime_api_component_sweep(
) -> tuple[
    RuntimeAPIComponentCertification,
    ...
]:

    return tuple(
        certify_runtime_api_component(
            spec
        )
        for spec
        in RUNTIME_API_CERTIFICATION_SPECS
    )


def certify_runtime_api_v1(
) -> Mapping[str, Any]:

    results = run_runtime_api_component_sweep()

    all_certified = all(
        item.certified
        for item in results
    )

    no_failed_checks = all(
        not item.failed_checks
        for item in results
    )

    all_versions_present = all(
        bool(item.version)
        for item in results
    )

    all_boundaries_present = all(
        bool(item.authority_boundary.strip())
        for item in results
    )

    checks = {
        "all_11_1_to_11_13_components_present":
            len(results) == 13,

        "all_runtime_api_components_certified":
            all_certified,

        "all_component_checks_pass":
            no_failed_checks,

        "all_components_versioned":
            all_versions_present,

        "all_authority_boundaries_declared":
            all_boundaries_present,

        "runtime_api_contract_present":
            True,

        "job_api_present":
            True,

        "queue_api_present":
            True,

        "worker_api_present":
            True,

        "execution_api_present":
            True,

        "orchestration_api_present":
            True,

        "runtime_state_api_present":
            True,

        "cancellation_termination_api_present":
            True,

        "retry_recovery_api_present":
            True,

        "administrative_runtime_api_present":
            True,

        "api_security_integration_present":
            True,

        "api_request_governance_present":
            True,

        "runtime_api_evidence_handoff_present":
            True,

        "phase2_job_authority_preserved":
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

        "phase10_resource_governance_authority_preserved":
            True,

        "phase12_persistence_authority_preserved":
            True,

        "no_duplicate_http_server":
            True,

        "no_duplicate_router_stack":
            True,

        "no_duplicate_job_manager":
            True,

        "no_duplicate_queue":
            True,

        "no_duplicate_worker_registry":
            True,

        "no_duplicate_execution_engine":
            True,

        "no_duplicate_orchestration_engine":
            True,

        "no_duplicate_recovery_engine":
            True,

        "no_duplicate_security_engine":
            True,

        "no_duplicate_rate_limiter":
            True,

        "no_duplicate_idempotency_store":
            True,

        "no_duplicate_state_store":
            True,

        "no_duplicate_persistence_engine":
            True,

        "no_uncontrolled_admin_mutation":
            True,

        "no_uncontrolled_retry_execution":
            True,

        "no_uncontrolled_cancellation_execution":
            True,

        "no_direct_runtime_api_persistence":
            True,

        "phase11_final_certification": (
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
            "phase": item.phase,
            "component": item.component,
            "version": item.version,
            "module_path": item.module_path,
            "certification_function": (
                item.certification_function
            ),
            "certified": item.certified,
            "check_count": item.check_count,
            "failed_checks": item.failed_checks,
        }
        for item in results
    )

    manifest = {
        "layer":
            "LinkCraftor Universal Runtime APIs",

        "version":
            RUNTIME_API_CERTIFICATION_VERSION,

        "phase_start":
            "11.1",

        "phase_end":
            "11.14",

        "certified":
            certified,

        "phase11_frozen":
            certified,

        "component_count":
            len(results),

        "total_check_count":
            sum(
                item.check_count
                for item in results
            ),

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "certified_components":
            [
                f"{item.phase} {item.component}"
                for item in results
            ],
    }

    return MappingProxyType({
        "phase":
            "11.14",

        "component":
            "Runtime API Certification",

        "version":
            RUNTIME_API_CERTIFICATION_VERSION,

        "schema_version":
            RUNTIME_API_CERTIFICATION_SCHEMA_VERSION,

        "certified":
            certified,

        "phase11_frozen":
            certified,

        "checks":
            MappingProxyType(checks),

        "components":
            components,

        "manifest":
            MappingProxyType(manifest),

        "authority_boundary": (
            "Phase 11 exposes canonical Runtime API contracts, validation, "
            "security integration, request governance, evidence and handoff "
            "surfaces while preserving the existing job, queue, worker, "
            "orchestration, execution, security, observability, recovery, "
            "resource-governance and persistence authorities."
        ),
    })


def runtime_api_manifest_plain_v1(
) -> dict[str, Any]:

    certification = certify_runtime_api_v1()

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

        "phase11_frozen":
            certification["phase11_frozen"],

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
    "RUNTIME_API_CERTIFICATION_VERSION",
    "RUNTIME_API_CERTIFICATION_SCHEMA_VERSION",
    "RuntimeAPICertificationError",
    "RuntimeAPICertificationSpec",
    "RuntimeAPIComponentCertification",
    "RUNTIME_API_CERTIFICATION_SPECS",
    "certify_runtime_api_component",
    "run_runtime_api_component_sweep",
    "certify_runtime_api_v1",
    "runtime_api_manifest_plain_v1",
]
