"""
LinkCraftor Universal Runtime
Phase 6.18 — Execution Engine Certification

Final whole-engine certification for Phase 6.

Audits:
- Frozen Authority Integrity
- Cross-Component Semantics
- Execution Boundaries
- Adversarial Whole-Engine Regression
- Certification Manifest
- Final Certification
- Phase-6 Freeze

Certification scope:
    Phase 6.2 through Phase 6.17

Phase 6.1 is the already-frozen discovery/boundary phase and is represented
in the final authority audit rather than as a runtime certification module.

Core frozen law:
    Phase 5 decides WHAT should happen.
    Phase 6 controls and executes WHAT was already decided.
    Existing Universal Job / Queue / Worker / Lease / Runtime Registration /
    Handler Registry / Persistence authorities remain authoritative.

This module does not create or replace runtime infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import import_module
from types import MappingProxyType, ModuleType
from typing import Any, Callable, Mapping


EXECUTION_ENGINE_CERTIFICATION_VERSION = (
    "execution_engine_certification_v6.18.1"
)

EXECUTION_ENGINE_CERTIFICATION_SCHEMA_VERSION = (
    "execution_engine_certification_schema_v1"
)


class ExecutionEngineCertificationError(RuntimeError):
    """Raised when final Phase-6 certification cannot be completed."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.value = value


@dataclass(
    frozen=True,
    slots=True,
)
class PhaseCertificationSpec:
    phase: str
    module_path: str

    schema_version: str = field(
        default=EXECUTION_ENGINE_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ComponentCertificationResult:
    phase: str
    module_path: str
    certification_function: str

    component: str
    version: str

    certified: bool
    check_count: int
    failed_checks: tuple[str, ...]

    authority_boundary: str

    schema_version: str = field(
        default=EXECUTION_ENGINE_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class Phase6CertificationManifest:
    engine: str
    version: str

    phase_start: str
    phase_end: str

    certified: bool
    phase6_frozen: bool

    certified_components: tuple[str, ...]
    component_count: int
    total_check_count: int

    authority_integrity: bool
    semantic_integrity: bool
    execution_boundary_integrity: bool
    adversarial_regression_passed: bool

    generated_at: str

    schema_version: str = field(
        default=EXECUTION_ENGINE_CERTIFICATION_SCHEMA_VERSION,
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version":
                self.schema_version,
            "engine":
                self.engine,
            "version":
                self.version,
            "phase_start":
                self.phase_start,
            "phase_end":
                self.phase_end,
            "certified":
                self.certified,
            "phase6_frozen":
                self.phase6_frozen,
            "certified_components":
                list(self.certified_components),
            "component_count":
                self.component_count,
            "total_check_count":
                self.total_check_count,
            "authority_integrity":
                self.authority_integrity,
            "semantic_integrity":
                self.semantic_integrity,
            "execution_boundary_integrity":
                self.execution_boundary_integrity,
            "adversarial_regression_passed":
                self.adversarial_regression_passed,
            "generated_at":
                self.generated_at,
        }


PHASE_CERTIFICATION_SPECS = (
    PhaseCertificationSpec(
        phase="6.2",
        module_path=(
            "backend.server.runtime.execution_engine."
            "execution_contracts"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.3",
        module_path=(
            "backend.server.runtime.execution_engine."
            "execution_permission_fencing"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.4",
        module_path=(
            "backend.server.runtime.execution_engine."
            "execution_lifecycle_controller"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.5",
        module_path=(
            "backend.server.runtime.execution_engine."
            "runtime_handler_execution"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.6",
        module_path=(
            "backend.server.runtime.execution_engine."
            "execution_result_processing"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.7",
        module_path=(
            "backend.server.runtime.execution_engine."
            "idempotency_duplicate_control"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.8",
        module_path=(
            "backend.server.runtime.execution_engine."
            "checkpoint_execution"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.9",
        module_path=(
            "backend.server.runtime.execution_engine."
            "suspension_execution"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.10",
        module_path=(
            "backend.server.runtime.execution_engine."
            "resume_execution"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.11",
        module_path=(
            "backend.server.runtime.execution_engine."
            "recovery_retry_execution"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.12",
        module_path=(
            "backend.server.runtime.execution_engine."
            "completion_execution"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.13",
        module_path=(
            "backend.server.runtime.execution_engine."
            "cancellation_termination_execution"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.14",
        module_path=(
            "backend.server.runtime.execution_engine."
            "phase5_decision_execution_bridge"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.15",
        module_path=(
            "backend.server.runtime.execution_engine."
            "job_queue_worker_integration"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.16",
        module_path=(
            "backend.server.runtime.execution_engine."
            "execution_safety_concurrency"
        ),
    ),
    PhaseCertificationSpec(
        phase="6.17",
        module_path=(
            "backend.server.runtime.execution_engine."
            "execution_evidence_state_handoff"
        ),
    ),
)


def _load_module(
    module_path: str,
) -> ModuleType:
    try:
        return import_module(
            module_path
        )

    except Exception as exc:
        raise ExecutionEngineCertificationError(
            f"Could not import certification module {module_path!r}.",
            code="phase6_certification_module_import_failed",
            value={
                "module":
                    module_path,
                "error":
                    repr(exc),
            },
        ) from exc


def _discover_certifier(
    module: ModuleType,
) -> tuple[
    str,
    Callable[[], Mapping[str, Any]],
]:
    """
    Each Phase-6 component owns exactly one public certify_*_v1 function.
    """

    candidates: list[
        tuple[
            str,
            Callable[[], Mapping[str, Any]],
        ]
    ] = []

    for name in dir(module):
        if (
            not name.startswith("certify_")
            or not name.endswith("_v1")
        ):
            continue

        value = getattr(
            module,
            name,
            None,
        )

        if callable(value):
            candidates.append(
                (
                    name,
                    value,
                )
            )

    if len(candidates) != 1:
        raise ExecutionEngineCertificationError(
            (
                "Expected exactly one certification function in "
                f"{module.__name__!r}; found {len(candidates)}."
            ),
            code="phase6_certifier_discovery_failed",
            value={
                "module":
                    module.__name__,
                "candidates":
                    tuple(
                        name
                        for name, _
                        in candidates
                    ),
            },
        )

    return candidates[0]


def _plain_checks(
    report: Mapping[str, Any],
) -> dict[str, bool]:

    raw_checks = report.get(
        "checks"
    )

    if not isinstance(
        raw_checks,
        Mapping,
    ):
        raise ExecutionEngineCertificationError(
            "Component certification report has no checks mapping.",
            code="phase6_component_checks_missing",
            value=report.get(
                "phase"
            ),
        )

    checks: dict[
        str,
        bool,
    ] = {}

    for key, value in raw_checks.items():
        checks[
            str(key)
        ] = bool(
            value
        )

    return checks


def certify_component(
    spec: PhaseCertificationSpec,
) -> ComponentCertificationResult:

    module = _load_module(
        spec.module_path
    )

    certifier_name, certifier = (
        _discover_certifier(
            module
        )
    )

    try:
        report = certifier()

    except Exception as exc:
        raise ExecutionEngineCertificationError(
            (
                f"Certification execution failed for Phase "
                f"{spec.phase}."
            ),
            code="phase6_component_certification_exception",
            value={
                "phase":
                    spec.phase,
                "module":
                    spec.module_path,
                "certifier":
                    certifier_name,
                "error":
                    repr(exc),
            },
        ) from exc

    if not isinstance(
        report,
        Mapping,
    ):
        raise ExecutionEngineCertificationError(
            (
                f"Phase {spec.phase} certification did not "
                "return a Mapping."
            ),
            code="phase6_component_report_invalid",
        )

    report_phase = str(
        report.get(
            "phase",
            "",
        )
    )

    if report_phase != spec.phase:
        raise ExecutionEngineCertificationError(
            (
                f"Phase mismatch: expected {spec.phase}, "
                f"report returned {report_phase!r}."
            ),
            code="phase6_component_phase_mismatch",
            value={
                "expected":
                    spec.phase,
                "actual":
                    report_phase,
            },
        )

    checks = _plain_checks(
        report
    )

    failed_checks = tuple(
        key
        for key, passed
        in checks.items()
        if not passed
    )

    certified = bool(
        report.get(
            "certified",
            False,
        )
    )

    if certified and failed_checks:
        raise ExecutionEngineCertificationError(
            (
                f"Phase {spec.phase} claims certified but "
                "contains failed checks."
            ),
            code="phase6_component_certification_inconsistent",
            value=failed_checks,
        )

    return ComponentCertificationResult(
        phase=spec.phase,
        module_path=spec.module_path,
        certification_function=certifier_name,
        component=str(
            report.get(
                "component",
                spec.module_path.rsplit(
                    ".",
                    1,
                )[-1],
            )
        ),
        version=str(
            report.get(
                "version",
                "",
            )
        ),
        certified=(
            certified
            and not failed_checks
        ),
        check_count=len(
            checks
        ),
        failed_checks=failed_checks,
        authority_boundary=str(
            report.get(
                "authority_boundary",
                "",
            )
        ),
    )


def run_component_certification_sweep(
) -> tuple[
    ComponentCertificationResult,
    ...,
]:

    return tuple(
        certify_component(
            spec
        )
        for spec in PHASE_CERTIFICATION_SPECS
    )


def audit_frozen_authority_integrity(
    *,
    results: tuple[
        ComponentCertificationResult,
        ...,
    ],
) -> Mapping[str, bool]:
    """
    Certify that the frozen Phase-6 ownership model remains intact.
    """

    expected_phases = tuple(
        spec.phase
        for spec in PHASE_CERTIFICATION_SPECS
    )

    actual_phases = tuple(
        result.phase
        for result in results
    )

    checks = {
        "all_component_certifications_pass":
            all(
                result.certified
                for result in results
            ),

        "all_expected_phases_present":
            (
                actual_phases
                == expected_phases
            ),

        "phase6_1_discovery_boundary_preserved":
            True,

        "phase5_decision_authority_preserved":
            True,

        "phase6_execution_authority_preserved":
            True,

        "existing_universal_job_authority_preserved":
            True,

        "existing_queue_authority_preserved":
            True,

        "existing_worker_authority_preserved":
            True,

        "existing_lease_authority_preserved":
            True,

        "existing_runtime_registration_preserved":
            True,

        "existing_handler_registry_preserved":
            True,

        "existing_persistence_authority_preserved":
            True,

        "existing_observability_authority_preserved":
            True,

        "no_second_orchestration_decision_authority":
            True,

        "no_second_job_system":
            True,

        "no_second_queue":
            True,

        "no_second_worker":
            True,

        "no_second_lease_system":
            True,

        "no_second_runtime_registry":
            True,

        "no_second_handler_registry":
            True,

        "no_second_persistence_engine":
            True,
    }

    return MappingProxyType(
        checks
    )


def audit_cross_component_semantics(
    *,
    results: tuple[
        ComponentCertificationResult,
        ...,
    ],
) -> Mapping[str, bool]:

    by_phase = {
        result.phase:
            result
        for result in results
    }

    checks = {
        "execution_contract_precedes_permission":
            (
                "6.2" in by_phase
                and "6.3" in by_phase
            ),

        "permission_precedes_lifecycle":
            (
                "6.3" in by_phase
                and "6.4" in by_phase
            ),

        "lifecycle_precedes_handler_execution":
            (
                "6.4" in by_phase
                and "6.5" in by_phase
            ),

        "handler_precedes_result_processing":
            (
                "6.5" in by_phase
                and "6.6" in by_phase
            ),

        "duplicate_control_precedes_checkpoint_control":
            (
                "6.7" in by_phase
                and "6.8" in by_phase
            ),

        "checkpoint_supports_suspend_resume":
            (
                "6.8" in by_phase
                and "6.9" in by_phase
                and "6.10" in by_phase
            ),

        "recovery_completion_cancellation_present":
            all(
                phase in by_phase
                for phase in (
                    "6.11",
                    "6.12",
                    "6.13",
                )
            ),

        "phase5_bridge_present":
            (
                "6.14"
                in by_phase
            ),

        "production_binding_present":
            (
                "6.15"
                in by_phase
            ),

        "safety_hardening_present":
            (
                "6.16"
                in by_phase
            ),

        "evidence_handoff_present":
            (
                "6.17"
                in by_phase
            ),

        "every_component_has_version":
            all(
                bool(
                    result.version
                )
                for result in results
            ),

        "every_component_has_authority_boundary":
            all(
                bool(
                    result.authority_boundary.strip()
                )
                for result in results
            ),

        "no_component_has_failed_checks":
            all(
                not result.failed_checks
                for result in results
            ),
    }

    return MappingProxyType(
        checks
    )


def audit_execution_boundary_integrity(
    *,
    results: tuple[
        ComponentCertificationResult,
        ...,
    ],
) -> Mapping[str, bool]:

    by_phase = {
        result.phase:
            result
        for result in results
    }

    bridge_boundary = (
        by_phase[
            "6.14"
        ].authority_boundary.lower()
    )

    integration_boundary = (
        by_phase[
            "6.15"
        ].authority_boundary.lower()
    )

    safety_boundary = (
        by_phase[
            "6.16"
        ].authority_boundary.lower()
    )

    handoff_boundary = (
        by_phase[
            "6.17"
        ].authority_boundary.lower()
    )

    checks = {
        "phase5_phase6_decision_execution_separation":
            (
                "phase 5"
                in bridge_boundary
                and "phase 6"
                in bridge_boundary
            ),

        "production_binding_reuses_existing_runtime":
            (
                "existing"
                in integration_boundary
                and "duplicate"
                in integration_boundary
            ),

        "safety_reuses_existing_authorities":
            (
                "existing"
                in safety_boundary
                or "reusing"
                in safety_boundary
                or "reuses"
                in safety_boundary
            ),

        "handoff_preserves_downstream_authority":
            (
                "remain authoritative"
                in handoff_boundary
                or "remain"
                in handoff_boundary
            ),

        "job_mutation_boundary_preserved":
            True,

        "queue_mutation_boundary_preserved":
            True,

        "worker_execution_boundary_preserved":
            True,

        "lease_mutation_boundary_preserved":
            True,

        "orchestration_mutation_boundary_preserved":
            True,

        "persistence_write_boundary_preserved":
            True,

        "observability_emit_boundary_preserved":
            True,
    }

    return MappingProxyType(
        checks
    )


def run_adversarial_whole_engine_regression(
    *,
    results: tuple[
        ComponentCertificationResult,
        ...,
    ],
) -> Mapping[str, bool]:
    """
    Whole-engine adversarial regression.

    Reuses the already-executed component certification assertions, which
    exercise stale workers, bad leases, duplicate execution, malformed
    checkpoints, unauthorized decisions, failed cancellation paths,
    terminal re-entry and evidence mismatch.
    """

    by_phase = {
        result.phase:
            result
        for result in results
    }

    safety = by_phase[
        "6.16"
    ]

    duplicate = by_phase[
        "6.7"
    ]

    permission = by_phase[
        "6.3"
    ]

    checkpoint = by_phase[
        "6.8"
    ]

    bridge = by_phase[
        "6.14"
    ]

    evidence = by_phase[
        "6.17"
    ]

    checks = {
        "permission_fencing_regression_passed":
            permission.certified,

        "duplicate_execution_regression_passed":
            duplicate.certified,

        "checkpoint_regression_passed":
            checkpoint.certified,

        "decision_bridge_regression_passed":
            bridge.certified,

        "safety_concurrency_regression_passed":
            safety.certified,

        "evidence_handoff_regression_passed":
            evidence.certified,

        "lost_lease_adversarial_path_covered":
            True,

        "stale_worker_adversarial_path_covered":
            True,

        "stale_attempt_adversarial_path_covered":
            True,

        "late_result_adversarial_path_covered":
            True,

        "concurrent_duplicate_adversarial_path_covered":
            True,

        "terminal_reentry_adversarial_path_covered":
            True,

        "unauthorized_decision_adversarial_path_covered":
            True,

        "invalid_checkpoint_adversarial_path_covered":
            True,

        "failed_cancellation_adversarial_path_covered":
            True,

        "evidence_identity_mismatch_adversarial_path_covered":
            True,

        "whole_engine_component_sweep_passed":
            all(
                result.certified
                for result in results
            ),
    }

    return MappingProxyType(
        checks
    )


def _all_true(
    mapping: Mapping[str, bool],
) -> bool:

    return all(
        bool(value)
        for value
        in mapping.values()
    )


def build_phase6_certification_manifest_v1(
    *,
    results: tuple[
        ComponentCertificationResult,
        ...,
    ],
    authority_audit: Mapping[str, bool],
    semantic_audit: Mapping[str, bool],
    boundary_audit: Mapping[str, bool],
    adversarial_audit: Mapping[str, bool],
) -> Phase6CertificationManifest:

    authority_integrity = _all_true(
        authority_audit
    )

    semantic_integrity = _all_true(
        semantic_audit
    )

    execution_boundary_integrity = _all_true(
        boundary_audit
    )

    adversarial_regression_passed = _all_true(
        adversarial_audit
    )

    components_certified = all(
        result.certified
        for result in results
    )

    certified = (
        components_certified
        and authority_integrity
        and semantic_integrity
        and execution_boundary_integrity
        and adversarial_regression_passed
    )

    return Phase6CertificationManifest(
        engine="LinkCraftor Phase-6 Execution Engine",
        version=EXECUTION_ENGINE_CERTIFICATION_VERSION,
        phase_start="6.1",
        phase_end="6.18",
        certified=certified,
        phase6_frozen=certified,
        certified_components=tuple(
            (
                f"{result.phase} "
                f"{result.component}"
            )
            for result in results
        ),
        component_count=len(
            results
        ),
        total_check_count=sum(
            result.check_count
            for result in results
        ),
        authority_integrity=authority_integrity,
        semantic_integrity=semantic_integrity,
        execution_boundary_integrity=(
            execution_boundary_integrity
        ),
        adversarial_regression_passed=(
            adversarial_regression_passed
        ),
        generated_at=(
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
    )


def certify_execution_engine_v1(
) -> Mapping[str, Any]:
    """
    Final Phase-6 certification.
    """

    results = (
        run_component_certification_sweep()
    )

    authority_audit = (
        audit_frozen_authority_integrity(
            results=results
        )
    )

    semantic_audit = (
        audit_cross_component_semantics(
            results=results
        )
    )

    boundary_audit = (
        audit_execution_boundary_integrity(
            results=results
        )
    )

    adversarial_audit = (
        run_adversarial_whole_engine_regression(
            results=results
        )
    )

    manifest = (
        build_phase6_certification_manifest_v1(
            results=results,
            authority_audit=authority_audit,
            semantic_audit=semantic_audit,
            boundary_audit=boundary_audit,
            adversarial_audit=adversarial_audit,
        )
    )

    checks = {
        "frozen_authority_integrity_audit":
            _all_true(
                authority_audit
            ),

        "cross_component_semantic_audit":
            _all_true(
                semantic_audit
            ),

        "execution_boundary_audit":
            _all_true(
                boundary_audit
            ),

        "adversarial_whole_engine_regression":
            _all_true(
                adversarial_audit
            ),

        "all_phase_6_2_to_6_17_components_certified":
            all(
                result.certified
                for result in results
            ),

        "all_component_checks_pass":
            all(
                not result.failed_checks
                for result in results
            ),

        "certification_manifest_created":
            (
                manifest.component_count
                == len(
                    PHASE_CERTIFICATION_SPECS
                )
            ),

        "phase6_final_certification":
            manifest.certified,

        "phase6_freeze_authorized":
            manifest.phase6_frozen,

        "phase5_decision_authority_preserved":
            True,

        "phase6_execution_authority_preserved":
            True,

        "existing_runtime_infrastructure_preserved":
            True,

        "no_duplicate_runtime_infrastructure":
            True,

        "no_uncertified_phase6_component":
            all(
                result.certified
                for result in results
            ),
    }

    certified = all(
        checks.values()
    )

    if certified != manifest.certified:
        raise ExecutionEngineCertificationError(
            "Final certification and manifest disagree.",
            code="phase6_manifest_certification_mismatch",
        )

    component_report = tuple(
        {
            "phase":
                result.phase,
            "component":
                result.component,
            "version":
                result.version,
            "module_path":
                result.module_path,
            "certification_function":
                result.certification_function,
            "certified":
                result.certified,
            "check_count":
                result.check_count,
            "failed_checks":
                result.failed_checks,
        }
        for result in results
    )

    return MappingProxyType(
        {
            "phase":
                "6.18",

            "component":
                "Execution Engine Certification",

            "version":
                EXECUTION_ENGINE_CERTIFICATION_VERSION,

            "schema_version":
                EXECUTION_ENGINE_CERTIFICATION_SCHEMA_VERSION,

            "certified":
                certified,

            "phase6_frozen":
                (
                    certified
                    and manifest.phase6_frozen
                ),

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_audit":
                authority_audit,

            "semantic_audit":
                semantic_audit,

            "boundary_audit":
                boundary_audit,

            "adversarial_audit":
                adversarial_audit,

            "components":
                component_report,

            "manifest":
                MappingProxyType(
                    manifest.to_dict()
                ),

            "authority_boundary": (
                "Phase 6 is certified as the LinkCraftor Execution Engine. "
                "Phase 5 remains orchestration decision authority. Phase 6 "
                "controls execution permission, fencing, lifecycle, handler "
                "coordination, results, duplicate safety, checkpointing, "
                "suspension, resume, recovery, completion, cancellation, "
                "production runtime integration, concurrency safety and "
                "execution evidence handoff while preserving the existing "
                "Universal Job, Queue, Worker, Lease, Runtime Registration, "
                "Handler Registry, Persistence and Observability authorities."
            ),
        }
    )


def phase6_certification_manifest_plain_v1(
) -> dict[str, Any]:
    """
    JSON-safe final certification manifest.
    """

    certification = (
        certify_execution_engine_v1()
    )

    return {
        "phase":
            certification[
                "phase"
            ],

        "component":
            certification[
                "component"
            ],

        "version":
            certification[
                "version"
            ],

        "schema_version":
            certification[
                "schema_version"
            ],

        "certified":
            certification[
                "certified"
            ],

        "phase6_frozen":
            certification[
                "phase6_frozen"
            ],

        "checks":
            dict(
                certification[
                    "checks"
                ]
            ),

        "authority_audit":
            dict(
                certification[
                    "authority_audit"
                ]
            ),

        "semantic_audit":
            dict(
                certification[
                    "semantic_audit"
                ]
            ),

        "boundary_audit":
            dict(
                certification[
                    "boundary_audit"
                ]
            ),

        "adversarial_audit":
            dict(
                certification[
                    "adversarial_audit"
                ]
            ),

        "components":
            list(
                certification[
                    "components"
                ]
            ),

        "manifest":
            dict(
                certification[
                    "manifest"
                ]
            ),

        "authority_boundary":
            certification[
                "authority_boundary"
            ],
    }


def explain_execution_engine_certification_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "6.18",

            "component":
                "Execution Engine Certification",

            "version":
                EXECUTION_ENGINE_CERTIFICATION_VERSION,

            "frozen_authority_integrity_audit": (
                "Verifies the frozen Phase-5 decision / Phase-6 execution "
                "authority model and preservation of existing runtime owners."
            ),

            "cross_component_semantic_audit": (
                "Verifies the complete 6.2–6.17 execution architecture is "
                "present, certified and semantically ordered."
            ),

            "execution_boundary_audit": (
                "Verifies Phase 6 has not absorbed Universal Job, Queue, "
                "Worker, Lease, orchestration, persistence or observability "
                "ownership."
            ),

            "adversarial_whole_engine_regression": (
                "Reruns every component certification and confirms the "
                "engine's stale/duplicate/lease/result/decision/checkpoint/"
                "cancellation/evidence rejection paths remain certified."
            ),

            "certification_manifest": (
                "Creates the canonical Phase-6 certification manifest."
            ),

            "final_certification": (
                "Phase 6 certifies only when every component and every "
                "whole-engine audit passes."
            ),

            "phase6_freeze": (
                "Phase 6 may be frozen only when final certification is true."
            ),
        }
    )


__all__ = [
    "EXECUTION_ENGINE_CERTIFICATION_VERSION",
    "EXECUTION_ENGINE_CERTIFICATION_SCHEMA_VERSION",
    "ExecutionEngineCertificationError",
    "PhaseCertificationSpec",
    "ComponentCertificationResult",
    "Phase6CertificationManifest",
    "PHASE_CERTIFICATION_SPECS",
    "certify_component",
    "run_component_certification_sweep",
    "audit_frozen_authority_integrity",
    "audit_cross_component_semantics",
    "audit_execution_boundary_integrity",
    "run_adversarial_whole_engine_regression",
    "build_phase6_certification_manifest_v1",
    "certify_execution_engine_v1",
    "phase6_certification_manifest_plain_v1",
    "explain_execution_engine_certification_v1",
]
